"""
Cache service for managing application caching.
"""

import time
import logging
from typing import Any, Dict, Optional, Tuple
from threading import Lock
from functools import wraps

from ..core.config import settings
from ..core.exceptions import CacheException

logger = logging.getLogger(__name__)


class CacheService:
    """
    Thread-safe in-memory cache service with TTL functionality.
    """
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self._enabled = settings.CACHE_ENABLED
        self._default_ttl = settings.CACHE_DEFAULT_TTL
        
        if self._enabled:
            logger.info("Cache service enabled")
        else:
            logger.info("Cache service disabled")
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if a cache entry has expired."""
        return time.time() > timestamp
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if self._is_expired(timestamp)
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self._enabled:
            return None
        
        with self._lock:
            if key not in self._cache:
                return None
            
            value, timestamp = self._cache[key]
            if self._is_expired(timestamp):
                del self._cache[key]
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL."""
        if not self._enabled:
            return
        
        ttl = ttl or self._default_ttl
        timestamp = time.time() + ttl
        
        with self._lock:
            self._cache[key] = (value, timestamp)
            logger.debug(f"Cached key: {key} with TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self._enabled:
            return False
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache key: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        if not self._enabled:
            return
        
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        if not self._enabled:
            return 0
        
        with self._lock:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
            
            if keys_to_delete:
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
            
            return len(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            self._cleanup_expired()
            total_entries = len(self._cache)
            
            # Calculate memory usage (rough estimate)
            memory_usage = sum(
                len(str(key)) + len(str(value)) 
                for key, (value, _) in self._cache.items()
            )
            
            return {
                "enabled": self._enabled,
                "total_entries": total_entries,
                "memory_usage_bytes": memory_usage,
                "default_ttl": self._default_ttl
            }


# Global cache service instance
cache_service = CacheService()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (uses default if None)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args
            for arg in args:
                key_parts.append(str(arg))
            
            # Add kwargs (sorted for consistency)
            for key, value in sorted(kwargs.items()):
                key_parts.append(f"{key}:{value}")
            
            cache_key = "|".join(key_parts)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 
import os
import time
from typing import Any, Dict, Optional, Tuple
from threading import Lock
import logging
from app.config import CacheConfig

# Configure logging
logging.basicConfig(level=getattr(logging, CacheConfig.get_log_level()))
logger = logging.getLogger(__name__)

class InMemoryCache:
    """
    Thread-safe in-memory cache for production use only.
    Provides TTL (Time To Live) functionality and automatic cache invalidation.
    """
    
    def __init__(self, default_ttl: Optional[int] = None):  # Use config default if None
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl or CacheConfig.DEFAULT_TTL
        self._enabled = CacheConfig.get_cache_enabled()
        
        if self._enabled:
            logger.info("In-memory cache enabled for production environment")
        else:
            logger.info("In-memory cache disabled for non-production environment")
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if a cache entry has expired based on its timestamp."""
        return time.time() > timestamp
    
    def _cleanup_expired(self):
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
        """
        Get a value from cache.
        Returns None if key doesn't exist or has expired.
        """
        if not self._enabled:
            return None
        
        with self._lock:
            if key not in self._cache:
                return None
            
            value, timestamp = self._cache[key]
            if self._is_expired(timestamp):
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache with optional TTL.
        If TTL is None, uses default TTL.
        """
        if not self._enabled:
            return
        
        ttl = ttl or self._default_ttl
        timestamp = time.time() + ttl
        
        with self._lock:
            self._cache[key] = (value, timestamp)
            logger.debug(f"Cached key: {key} with TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        Returns True if key existed and was deleted, False otherwise.
        """
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
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        Returns number of keys invalidated.
        """
        if not self._enabled:
            return 0
        
        with self._lock:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
            
            if keys_to_delete:
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
            
            return len(keys_to_delete)

# Global cache instance
cache = InMemoryCache()

def cache_key_generator(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    """
    # Convert args and kwargs to a string representation
    key_parts = []
    
    # Add args
    for arg in args:
        key_parts.append(str(arg))
    
    # Add kwargs (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    
    return "|".join(key_parts)

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (uses default if None)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{cache_key_generator(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(func_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(func_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        return wrapper
    return decorator 
import os
from typing import Optional
import random
from threading import Lock

class CacheConfig:
    """Configuration for the in-memory caching system"""
    
    # Environment detection
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
    IS_PRODUCTION = ENVIRONMENT == "production"
    
    # Cache settings
    DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour default
    PURA_DATA_TTL = int(os.getenv("CACHE_PURA_DATA_TTL", "1800"))  # 30 minutes
    PURA_GAMBAR_TTL = int(os.getenv("CACHE_PURA_GAMBAR_TTL", "3600"))  # 1 hour
    PURA_DETAIL_TTL = int(os.getenv("CACHE_PURA_DETAIL_TTL", "3600"))  # 1 hour
    FILTER_TTL = int(os.getenv("CACHE_FILTER_TTL", "7200"))  # 2 hours
    
    # Logging
    CACHE_LOGGING = os.getenv("CACHE_LOGGING", "INFO").upper()
    
    @classmethod
    def get_cache_enabled(cls) -> bool:
        """Check if caching is enabled for current environment"""
        return cls.IS_PRODUCTION
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get cache logging level"""
        return cls.CACHE_LOGGING

# Database configuration
class DatabaseConfig:
    """Database connection configuration"""
    
    HOST = os.getenv("MYSQL_HOST", "localhost")
    USER = os.getenv("MYSQL_USER", "root")
    PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    DATABASE = os.getenv("MYSQL_DATABASE", "purabali")
    PORT = int(os.getenv("MYSQL_PORT", "3306"))
    
    @classmethod
    def get_connection_params(cls) -> dict:
        """Get database connection parameters"""
        return {
            "host": cls.HOST,
            "user": cls.USER,
            "password": cls.PASSWORD,
            "database": cls.DATABASE,
            "port": cls.PORT
        }

# Gemini API configuration with key rotation
class GeminiConfig:
    """Gemini API configuration with key rotation system"""
    
    _api_keys: list[str] = []
    _current_key_index: int = 0
    _lock = Lock()
    
    @classmethod
    def _load_api_keys(cls) -> list[str]:
        """Load API keys from environment variables"""
        # Support both single key and multiple keys
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            return [single_key]
        
        # Load multiple keys from comma-separated list
        keys_str = os.getenv("GEMINI_API_KEYS", "")
        if keys_str:
            keys = [key.strip() for key in keys_str.split(",") if key.strip()]
            if keys:
                return keys
        
        # Fallback to single key
        return [single_key] if single_key else []
    
    @classmethod
    def get_api_keys(cls) -> list[str]:
        """Get all available API keys"""
        if not cls._api_keys:
            cls._api_keys = cls._load_api_keys()
        return cls._api_keys.copy()
    
    @classmethod
    def get_next_api_key(cls) -> Optional[str]:
        """Get the next API key in rotation"""
        with cls._lock:
            if not cls._api_keys:
                cls._api_keys = cls._load_api_keys()
            
            if not cls._api_keys:
                return None
            
            # Get current key
            key = cls._api_keys[cls._current_key_index]
            
            # Move to next key
            cls._current_key_index = (cls._current_key_index + 1) % len(cls._api_keys)
            
            return key
    
    @classmethod
    def get_random_api_key(cls) -> Optional[str]:
        """Get a random API key"""
        keys = cls.get_api_keys()
        return random.choice(keys) if keys else None
    
    @classmethod
    def get_current_key_index(cls) -> int:
        """Get the current key index"""
        return cls._current_key_index
    
    @classmethod
    def get_total_keys(cls) -> int:
        """Get the total number of available keys"""
        return len(cls.get_api_keys())
    
    @classmethod
    def reset_rotation(cls) -> None:
        """Reset the rotation to start from the first key"""
        with cls._lock:
            cls._current_key_index = 0 
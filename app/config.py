import os
from typing import Optional

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
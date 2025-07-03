"""
Simple environment-based configuration management (no Pydantic).
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    # Environment
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    APP_NAME = os.environ.get("APP_NAME", "PuraBali RAG Backend")
    VERSION = os.environ.get("APP_VERSION", "1.0.0")

    # Server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    CORS_CREDENTIALS = os.environ.get("CORS_CREDENTIALS", "true").lower() == "true"

    # Database
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "purabali")

    # Cache
    CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
    CACHE_DEFAULT_TTL = int(os.environ.get("CACHE_DEFAULT_TTL", "3600"))
    CACHE_PURA_DATA_TTL = int(os.environ.get("CACHE_PURA_DATA_TTL", "1800"))
    CACHE_PURA_GAMBAR_TTL = int(os.environ.get("CACHE_PURA_GAMBAR_TTL", "3600"))
    CACHE_PURA_DETAIL_TTL = int(os.environ.get("CACHE_PURA_DETAIL_TTL", "3600"))
    CACHE_FILTER_TTL = int(os.environ.get("CACHE_FILTER_TTL", "7200"))
    CACHE_LOG_LEVEL = os.environ.get("CACHE_LOG_LEVEL", "INFO")

    # Gemini
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_API_KEYS = [k.strip() for k in os.environ.get("GEMINI_API_KEYS", "").split(",") if k.strip()]
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", "0.2"))
    GEMINI_TOP_P = float(os.environ.get("GEMINI_TOP_P", "0.9"))
    GEMINI_MAX_TOKENS = int(os.environ.get("GEMINI_MAX_TOKENS", "512"))

    # Model
    MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "./models")
    MODEL_NAME = os.environ.get("MODEL_NAME", "intfloat/multilingual-e5-large")
    MODEL_CACHE_VERSION = os.environ.get("MODEL_CACHE_VERSION", "1.0")

    # Search
    SEARCH_DEFAULT_TOP_K = int(os.environ.get("SEARCH_DEFAULT_TOP_K", "3"))
    SEARCH_MAX_CANDIDATES = int(os.environ.get("SEARCH_MAX_CANDIDATES", "10"))

    @classmethod
    def is_production(cls):
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_development(cls):
        return cls.ENVIRONMENT.lower() == "development"

# Global config instance
settings = Config
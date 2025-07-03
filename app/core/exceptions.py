"""
Custom exception classes for the application.
"""

from typing import Any, Dict, Optional


class PuraBaliException(Exception):
    """Base exception for PuraBali application."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DatabaseException(PuraBaliException):
    """Database-related exceptions."""
    pass


class CacheException(PuraBaliException):
    """Cache-related exceptions."""
    pass


class SearchException(PuraBaliException):
    """Search-related exceptions."""
    pass


class AIException(PuraBaliException):
    """AI/ML-related exceptions."""
    pass


class ConfigurationException(PuraBaliException):
    """Configuration-related exceptions."""
    pass


class ValidationException(PuraBaliException):
    """Data validation exceptions."""
    pass


class NotFoundException(PuraBaliException):
    """Resource not found exceptions."""
    pass


class AuthenticationException(PuraBaliException):
    """Authentication-related exceptions."""
    pass


class RateLimitException(PuraBaliException):
    """Rate limiting exceptions."""
    pass 
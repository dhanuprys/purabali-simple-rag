"""
PuraBali RAG Backend Application

A FastAPI-based backend for Bali temple information system with RAG capabilities.
"""

__version__ = "1.0.0"
__author__ = "PuraBali Team"
__description__ = "Bali Temple Information System with RAG"

from .core.config import settings
from .core.logging import setup_logging

# Setup logging on import
setup_logging()

__all__ = [
    "settings",
    "setup_logging",
]

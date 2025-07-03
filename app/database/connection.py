"""
Database connection management.
"""

import mysql.connector
from mysql.connector import pooling
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

from ..core.config import settings
from ..core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with connection pooling."""
    
    def __init__(self):
        self._pool: Optional[pooling.MySQLConnectionPool] = None
    
    def _get_pool_config(self) -> Dict[str, Any]:
        """Get connection pool configuration."""
        return {
            "pool_name": "purabali_pool",
            "pool_size": 5,
            "host": settings.MYSQL_HOST,
            "port": settings.MYSQL_PORT,
            "user": settings.MYSQL_USER,
            "password": settings.MYSQL_PASSWORD,
            "database": settings.MYSQL_DATABASE,
            "charset": "utf8mb4",
            "autocommit": True,
            "raise_on_warnings": True,
        }
    
    def initialize_pool(self) -> None:
        """Initialize the connection pool."""
        try:
            if self._pool is None:
                pool_config = self._get_pool_config()
                self._pool = pooling.MySQLConnectionPool(**pool_config)
                logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise DatabaseException(f"Database pool initialization failed: {e}")
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self._pool is None:
            self.initialize_pool()
        
        try:
            return self._pool.get_connection()
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise DatabaseException(f"Failed to get database connection: {e}")
    
    @contextmanager
    def get_cursor(self, dictionary: bool = True):
        """Context manager for database cursor."""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise DatabaseException(f"Database operation failed: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute a SELECT query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    def close_pool(self) -> None:
        """Close the connection pool."""
        if self._pool:
            self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")


# Global database connection instance
_db_connection = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    return _db_connection


def initialize_database() -> None:
    """Initialize the database connection pool."""
    _db_connection.initialize_pool()


def close_database() -> None:
    """Close the database connection pool."""
    _db_connection.close_pool() 
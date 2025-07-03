#!/usr/bin/env python3
"""
Startup script for the improved PuraBali RAG Backend.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

def main():
    """Main startup function."""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found. Using default configuration.")
        print("Create a .env file for custom configuration.")
    
    # Set default environment variables if not set
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    
    # Database defaults
    os.environ.setdefault("MYSQL_HOST", "localhost")
    os.environ.setdefault("MYSQL_PORT", "3306")
    os.environ.setdefault("MYSQL_USER", "root")
    os.environ.setdefault("MYSQL_PASSWORD", "")
    os.environ.setdefault("MYSQL_DATABASE", "purabali")
    
    # Cache defaults
    os.environ.setdefault("CACHE_ENABLED", "true")
    os.environ.setdefault("CACHE_DEFAULT_TTL", "3600")
    os.environ.setdefault("CACHE_LOG_LEVEL", "INFO")
    
    # Model defaults
    os.environ.setdefault("MODEL_CACHE_DIR", "./models")
    os.environ.setdefault("MODEL_NAME", "intfloat/multilingual-e5-large")
    
    # Search defaults
    os.environ.setdefault("SEARCH_DEFAULT_TOP_K", "3")
    os.environ.setdefault("SEARCH_MAX_CANDIDATES", "10")
    
    # CORS defaults
    os.environ.setdefault("CORS_ORIGINS", '["*"]')
    os.environ.setdefault("CORS_CREDENTIALS", "true")
    
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") == "development"
    
    print(f"Starting PuraBali RAG Backend...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    print("-" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main_new:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
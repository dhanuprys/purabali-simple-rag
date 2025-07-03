# PuraBali RAG Backend - Improved Architecture

## Overview

This is a completely rewritten and improved backend for the PuraBali RAG (Retrieval-Augmented Generation) system. The new architecture follows modern Python best practices with better separation of concerns, type safety, error handling, and maintainability.

## Architecture

### Directory Structure

```
app/
├── __init__.py                 # Package initialization
├── main_new.py                # New main application entry point
├── core/                      # Core application modules
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logging.py             # Logging configuration
│   └── exceptions.py          # Custom exception classes
├── api/                       # API layer
│   ├── __init__.py
│   └── v1/                    # API version 1
│       ├── __init__.py
│       └── router.py          # API endpoints
├── database/                  # Database layer
│   ├── __init__.py
│   ├── connection.py          # Database connection management
│   └── models.py              # Data models and repositories
├── schemas/                   # Pydantic schemas
│   ├── __init__.py
│   ├── common.py              # Common response models
│   ├── pura.py                # Pura-related schemas
│   └── chat.py                # Chat-related schemas
├── services/                  # Business logic layer
│   ├── __init__.py
│   └── cache_service.py       # Cache management service
├── utils/                     # Utility functions
├── models/                    # ML model files
├── static/                    # Static files
└── templates/                 # HTML templates
```

## Key Improvements

### 1. Configuration Management
- **Pydantic Settings**: Type-safe configuration using Pydantic v2
- **Environment-based**: Support for different environments (dev/prod)
- **Validation**: Automatic validation of configuration values
- **Hierarchical**: Organized into logical groups (database, cache, etc.)

### 2. Error Handling
- **Custom Exceptions**: Domain-specific exception classes
- **Global Handlers**: Centralized exception handling
- **Structured Logging**: Comprehensive logging with different levels
- **Graceful Degradation**: Proper error responses with appropriate HTTP status codes

### 3. Database Layer
- **Connection Pooling**: Efficient database connection management
- **Repository Pattern**: Clean separation of data access logic
- **Type Safety**: Proper type annotations throughout
- **Error Recovery**: Automatic connection recovery and cleanup

### 4. API Design
- **Versioned APIs**: Support for API versioning
- **Pydantic Schemas**: Request/response validation
- **OpenAPI Documentation**: Automatic API documentation
- **Consistent Responses**: Standardized response formats

### 5. Caching System
- **Thread-safe**: Proper concurrency handling
- **TTL Support**: Configurable time-to-live
- **Pattern Invalidation**: Bulk cache invalidation
- **Statistics**: Cache performance monitoring

### 6. Logging
- **Structured**: JSON-formatted logs for production
- **Configurable**: Different log levels per environment
- **Performance**: Minimal overhead logging
- **Debugging**: Comprehensive debug information

## Features

### Core Features
- ✅ **FastAPI Framework**: Modern, fast web framework
- ✅ **Type Safety**: Full type annotations with mypy support
- ✅ **Async Support**: Non-blocking I/O operations
- ✅ **CORS Support**: Cross-origin resource sharing
- ✅ **Static Files**: Serve static assets
- ✅ **Templates**: Jinja2 template rendering

### Database Features
- ✅ **MySQL Support**: Production-ready database
- ✅ **Connection Pooling**: Efficient connection management
- ✅ **Repository Pattern**: Clean data access layer
- ✅ **Migration Support**: Database schema management

### Caching Features
- ✅ **In-Memory Cache**: Fast response times
- ✅ **TTL Management**: Automatic expiration
- ✅ **Pattern Invalidation**: Bulk cache operations
- ✅ **Statistics**: Performance monitoring

### API Features
- ✅ **RESTful Design**: Standard HTTP methods
- ✅ **Pagination**: Efficient data retrieval
- ✅ **Filtering**: Flexible search capabilities
- ✅ **Validation**: Request/response validation
- ✅ **Documentation**: Auto-generated API docs

## Configuration

### Environment Variables

```bash
# Application
ENVIRONMENT=development
DEBUG=true
APP_NAME="PuraBali RAG Backend"
APP_VERSION="1.0.0"

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["*"]
CORS_CREDENTIALS=true

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=purabali

# Cache
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=3600
CACHE_PURA_DATA_TTL=1800
CACHE_PURA_GAMBAR_TTL=3600
CACHE_PURA_DETAIL_TTL=3600
CACHE_FILTER_TTL=7200
CACHE_LOG_LEVEL=INFO

# Gemini AI
GEMINI_API_KEY=your_api_key_here
GEMINI_API_KEYS=key1,key2,key3
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.2
GEMINI_TOP_P=0.9
GEMINI_MAX_TOKENS=512

# Model
MODEL_CACHE_DIR=./models
MODEL_NAME=intfloat/multilingual-e5-large
MODEL_CACHE_VERSION=1.0

# Search
SEARCH_DEFAULT_TOP_K=3
SEARCH_MAX_CANDIDATES=10
```

## API Endpoints

### Pura Endpoints
- `GET /api/pura` - List all pura with filtering and pagination
- `GET /api/pura/{id_pura}` - Get specific pura details
- `GET /api/kabupaten` - List all kabupaten with pura counts
- `GET /api/jenis_pura` - List all temple types with pura counts

### Chat Endpoints
- `POST /api/prompt` - Process chat prompts with RAG

### Cache Management
- `GET /api/cache/stats` - Get cache statistics
- `POST /api/cache/clear` - Clear all cache entries

### Health Check
- `GET /health` - Application health status

## Development

### Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**:
   ```bash
   # Ensure MySQL is running
   mysql -u root -p < init-mysql.sql
   ```

4. **Run Application**:
   ```bash
   # Development
   uvicorn app.main_new:app --reload --host 0.0.0.0 --port 8000
   
   # Production
   uvicorn app.main_new:app --host 0.0.0.0 --port 8000
   ```

### Testing

```bash
# Run tests (when implemented)
pytest

# Type checking
mypy app/

# Linting
flake8 app/
```

### Docker

```bash
# Build image
docker build -t purabali-backend .

# Run container
docker run -p 8000:8000 purabali-backend
```

## Production Deployment

### Requirements
- Python 3.8+
- MySQL 8.0+
- Sufficient RAM for model caching
- SSL certificate for HTTPS

### Deployment Steps
1. Set up production environment variables
2. Configure reverse proxy (nginx)
3. Set up process manager (systemd/supervisor)
4. Configure monitoring and logging
5. Set up backup strategy

## Monitoring

### Health Checks
- Application health: `GET /health`
- Database connectivity
- Cache performance
- API response times

### Logging
- Application logs: `/var/log/purabali/app.log`
- Access logs: `/var/log/purabali/access.log`
- Error logs: `/var/log/purabali/error.log`

### Metrics
- Request rate
- Response times
- Error rates
- Cache hit rates
- Database connection pool usage

## Security

### Best Practices
- Environment variable management
- Input validation
- SQL injection prevention
- CORS configuration
- Rate limiting (to be implemented)
- Authentication (to be implemented)

### Recommendations
- Use HTTPS in production
- Implement API authentication
- Regular security updates
- Database access controls
- Log monitoring for suspicious activity

## Future Enhancements

### Planned Features
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] API versioning strategy
- [ ] Background task processing
- [ ] WebSocket support for real-time features
- [ ] Advanced caching strategies (Redis)
- [ ] Database migrations
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Performance monitoring
- [ ] Backup and recovery procedures

### Technical Debt
- [ ] Complete RAG implementation
- [ ] Model caching optimization
- [ ] Database query optimization
- [ ] Error handling refinement
- [ ] Documentation completion

## Contributing

1. Follow the established code structure
2. Add type annotations to all functions
3. Write comprehensive docstrings
4. Add tests for new features
5. Update documentation
6. Follow PEP 8 style guidelines

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
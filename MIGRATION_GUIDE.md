# Migration Guide: Old Backend to New Backend

## Overview

This guide helps you migrate from the old backend structure to the new improved architecture. The new backend provides better organization, type safety, error handling, and maintainability.

## Key Changes

### 1. File Structure Changes

| Old Location | New Location | Purpose |
|--------------|--------------|---------|
| `app/main.py` | `app/main_new.py` | Main application entry point |
| `app/api.py` | `app/api/v1/router.py` | API endpoints |
| `app/config.py` | `app/core/config.py` | Configuration management |
| `app/db.py` | `app/database/` | Database layer |
| `app/cache.py` | `app/services/cache_service.py` | Caching service |
| `app/search.py` | `app/services/search_service.py` | Search service |
| `app/gen.py` | `app/services/ai_service.py` | AI generation service |

### 2. Configuration Changes

#### Old Configuration
```python
# app/config.py
class CacheConfig:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
    IS_PRODUCTION = ENVIRONMENT == "production"
    # ... more config
```

#### New Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

### 3. Database Changes

#### Old Database Access
```python
# app/db.py
def get_db_connection():
    return mysql.connector.connect(...)

@cached(ttl=CacheConfig.PURA_DATA_TTL, key_prefix="pura_data")
def fetch_pura_data():
    conn = get_db_connection()
    # ... database operations
```

#### New Database Access
```python
# app/database/connection.py
class DatabaseConnection:
    def __init__(self):
        self._pool = None
        self._config = settings.database
    
    @contextmanager
    def get_cursor(self, dictionary: bool = True):
        # ... connection management

# app/database/models.py
class PuraRepository:
    def __init__(self):
        self.db = get_db_connection()
    
    def get_all_pura(self) -> List[Dict[str, Any]]:
        # ... repository methods
```

### 4. API Changes

#### Old API Structure
```python
# app/api.py
router = APIRouter(prefix="/api")

@router.get("/pura")
def get_all_pura(q: str = Query(None), ...):
    # ... endpoint logic
```

#### New API Structure
```python
# app/api/v1/router.py
api_router = APIRouter()

@api_router.get("/pura", response_model=PuraListResponse)
async def get_all_pura(
    q: str = Query(None, description="Search query"),
    # ... parameters
):
    # ... endpoint logic with proper error handling
```

## Migration Steps

### Step 1: Backup Current Code
```bash
# Create backup of current backend
cp -r app app_backup_old
```

### Step 2: Install New Dependencies
```bash
# Update requirements
pip install -r requirements.txt
```

### Step 3: Update Environment Variables
```bash
# Create new .env file with updated variables
cp .env.example .env
# Edit .env with your configuration
```

### Step 4: Test New Backend
```bash
# Run the new backend
python run_new_backend.py
```

### Step 5: Update Frontend Integration
Update any frontend code that calls the API to use the new response formats.

## Breaking Changes

### 1. API Response Format

#### Old Format
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 100,
    "total_pages": 9,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

#### New Format
```json
{
  "data": [
    {
      "id_pura": "P001",
      "nama_pura": "Pura Tanah Lot",
      "deskripsi_singkat": "...",
      "tahun_berdiri": "16th century",
      "link_lokasi": "...",
      "latitude": -8.6214,
      "longitude": 115.0868,
      "link_gambar": "...",
      "nama_jenis_pura": "Kahyangan Jagat",
      "nama_kabupaten": "Tabanan"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 12,
    "total": 100,
    "total_pages": 9,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

### 2. Error Response Format

#### Old Format
```json
{
  "detail": "Error message"
}
```

#### New Format
```json
{
  "error": "Error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "additional error details"
  }
}
```

### 3. Configuration Variables

| Old Variable | New Variable | Notes |
|--------------|--------------|-------|
| `CACHE_DEFAULT_TTL` | `CACHE_DEFAULT_TTL` | Same |
| `CACHE_PURA_DATA_TTL` | `CACHE_PURA_DATA_TTL` | Same |
| `MYSQL_HOST` | `MYSQL_HOST` | Same |
| `GEMINI_API_KEY` | `GEMINI_API_KEY` | Same |
| `GEMINI_API_KEYS` | `GEMINI_API_KEYS` | Same |

## Testing Migration

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00",
  "environment": "development"
}
```

### 2. API Endpoints
```bash
# Test pura list
curl "http://localhost:8000/api/pura?page=1&limit=5"

# Test pura detail
curl "http://localhost:8000/api/pura/P001"

# Test kabupaten list
curl "http://localhost:8000/api/kabupaten"

# Test jenis pura list
curl "http://localhost:8000/api/jenis_pura"
```

### 3. Cache Management
```bash
# Test cache stats
curl "http://localhost:8000/api/cache/stats"

# Test cache clear
curl -X POST "http://localhost:8000/api/cache/clear"
```

## Rollback Plan

If issues arise during migration:

1. **Stop the new backend**:
   ```bash
   # Stop the new backend process
   ```

2. **Restore old backend**:
   ```bash
   # Restore from backup
   rm -rf app
   cp -r app_backup_old app
   ```

3. **Restart old backend**:
   ```bash
   # Start the old backend
   uvicorn app.main:app --reload
   ```

## Performance Improvements

### 1. Database Connection Pooling
- **Before**: Single connections per request
- **After**: Connection pooling with configurable pool size

### 2. Caching Improvements
- **Before**: Basic in-memory cache
- **After**: Thread-safe cache with TTL and statistics

### 3. Error Handling
- **Before**: Basic error responses
- **After**: Structured error handling with logging

### 4. Type Safety
- **Before**: Limited type annotations
- **After**: Full type safety with Pydantic validation

## Monitoring and Debugging

### 1. Logging
The new backend provides comprehensive logging:
```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Configure via CACHE_LOG_LEVEL environment variable
```

### 2. Health Monitoring
```bash
# Health check endpoint
curl http://localhost:8000/health
```

### 3. Cache Statistics
```bash
# Monitor cache performance
curl http://localhost:8000/api/cache/stats
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **Database Connection Issues**
   - Verify MySQL is running
   - Check database credentials in .env file

3. **Configuration Issues**
   - Ensure .env file exists and is properly formatted
   - Check environment variable names

4. **API Response Issues**
   - Verify frontend is using new response format
   - Check API documentation at /docs

### Getting Help

1. Check the logs for error messages
2. Verify configuration in .env file
3. Test individual components
4. Review the BACKEND_README.md for detailed documentation

## Next Steps

After successful migration:

1. **Implement remaining features**:
   - Complete RAG functionality
   - Add authentication
   - Implement rate limiting

2. **Add monitoring**:
   - Set up application monitoring
   - Configure log aggregation
   - Implement health checks

3. **Performance optimization**:
   - Database query optimization
   - Cache tuning
   - Load testing

4. **Security hardening**:
   - API authentication
   - Input validation
   - Security headers 
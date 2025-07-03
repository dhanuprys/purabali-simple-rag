"""
Main FastAPI application with improved structure and error handling.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

from .core.config import settings
from .core.logging import get_logger
from .core.exceptions import PuraBaliException, NotFoundException
from .database.connection import initialize_database, close_database
from .api.v1.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting PuraBali RAG Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    try:
        # Initialize database
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down PuraBali RAG Backend...")
    try:
        close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Bali Temple Information System with RAG capabilities",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler
    @app.exception_handler(PuraBaliException)
    async def purabali_exception_handler(request: Request, exc: PuraBaliException):
        """Handle custom PuraBali exceptions."""
        logger.error(f"PuraBali exception: {exc.message}", extra={
            "error_code": exc.error_code,
            "details": exc.details
        })
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            }
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        """Handle not found exceptions."""
        logger.warning(f"Resource not found: {exc.message}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": exc.message,
                "error_code": exc.error_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        if settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "details": str(exc) if settings.DEBUG else None
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error"
                }
            )
    
    # Include API router
    app.include_router(api_router, prefix="/api")
    
    # Serve static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Jinja2 templates
    templates = Jinja2Templates(directory="app/templates")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT
        }
    
    # Frontend routes
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Home page."""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/pura", response_class=HTMLResponse)
    async def pura_list(
        request: Request, 
        q: str = "", 
        jenis: str = "", 
        kabupaten: str = "", 
        page: int = 1
    ):
        """Pura list page with filters."""
        try:
            async with httpx.AsyncClient() as client:
                base_url = str(request.base_url).rstrip("/")
                
                # Fetch filter options (FIX: swap endpoints)
                jenis_resp = await client.get(f"{base_url}/api/jenis_pura")
                kabupaten_resp = await client.get(f"{base_url}/api/kabupaten")
                
                jenis_pura_list = jenis_resp.json() if jenis_resp.status_code == 200 else []
                kabupaten_list = kabupaten_resp.json() if kabupaten_resp.status_code == 200 else []
            
            return templates.TemplateResponse("pura_list.html", {
                "request": request,
                "jenis_pura_list": jenis_pura_list,
                "kabupaten_list": kabupaten_list,
                "q": q,
                "jenis": jenis,
                "kabupaten": kabupaten,
                "page": page
            })
        except Exception as e:
            logger.error(f"Error loading pura list page: {e}")
            raise HTTPException(status_code=500, detail="Failed to load page")
    
    @app.get("/pura/{id_pura}", response_class=HTMLResponse)
    async def pura_detail(request: Request, id_pura: str):
        """Pura detail page."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{str(request.base_url).rstrip('/')}/api/pura/{id_pura}"
                resp = await client.get(url)
                
                if resp.status_code != 200:
                    return HTMLResponse("<h2>Pura not found</h2>", status_code=404)
                
                pura = resp.json()
            
            return templates.TemplateResponse("pura_detail.html", {
                "request": request, 
                "pura": pura.get("data", {})
            })
        except Exception as e:
            logger.error(f"Error loading pura detail page: {e}")
            raise HTTPException(status_code=500, detail="Failed to load page")
    
    @app.get("/kabupaten", response_class=HTMLResponse)
    async def kabupaten_list(request: Request):
        """Kabupaten list page."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{str(request.base_url).rstrip('/')}/api/kabupaten"
                resp = await client.get(url)
                kabupaten_list = resp.json() if resp.status_code == 200 else []
            
            return templates.TemplateResponse("kabupaten_list.html", {
                "request": request, 
                "kabupaten_list": kabupaten_list
            })
        except Exception as e:
            logger.error(f"Error loading kabupaten list page: {e}")
            raise HTTPException(status_code=500, detail="Failed to load page")
    
    @app.get("/jenis-pura", response_class=HTMLResponse)
    async def jenis_pura_list(request: Request):
        """Jenis Pura list page."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{str(request.base_url).rstrip('/')}/api/jenis_pura"
                resp = await client.get(url)
                jenis_pura_list = resp.json() if resp.status_code == 200 else []
            
            return templates.TemplateResponse("jenis_pura_list.html", {
                "request": request, 
                "jenis_pura_list": jenis_pura_list
            })
        except Exception as e:
            logger.error(f"Error loading jenis pura list page: {e}")
            raise HTTPException(status_code=500, detail="Failed to load page")
    
    @app.get("/chat", response_class=HTMLResponse)
    async def chat_page(request: Request):
        """Chat page."""
        return templates.TemplateResponse("chat.html", {"request": request})
    
    return app


# Create the application instance
app = create_app()

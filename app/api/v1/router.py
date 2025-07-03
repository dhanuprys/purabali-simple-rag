"""
API v1 router with all endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from ...schemas.pura import PuraResponse, PuraListResponse, PuraDetailResponse
from ...schemas.chat import PromptRequest, PromptResponse, PuraAttachment
from ...schemas.common import PaginationResponse
from ...database.models import PuraRepository, KabupatenRepository, JenisPuraRepository
from ...core.exceptions import NotFoundException
from ...core.logging import get_logger

logger = get_logger(__name__)

# Create router
api_router = APIRouter()

# Initialize repositories
pura_repo = PuraRepository()
kabupaten_repo = KabupatenRepository()
jenis_pura_repo = JenisPuraRepository()


@api_router.get("/pura", response_model=PuraListResponse)
async def get_all_pura(
    q: str = Query(None, description="Search query"),
    jenis: str = Query(None, description="Filter by temple type"),
    kabupaten: str = Query(None, description="Filter by regency"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(12, ge=1, le=100, description="Number of items per page (max 100)")
):
    """Get all pura with optional filtering and pagination."""
    try:
        result = pura_repo.search_pura(
            query=q,
            jenis=jenis,
            kabupaten=kabupaten,
            page=page,
            limit=limit
        )
        
        # Convert to response models
        pura_list = [PuraResponse(**pura) for pura in result["data"]]
        pagination = PaginationResponse(**result["pagination"])
        
        return PuraListResponse(data=pura_list, pagination=pagination)
        
    except Exception as e:
        logger.error(f"Error fetching pura list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pura list"
        )


@api_router.get("/pura/{id_pura}", response_model=PuraDetailResponse)
async def get_pura_by_id(id_pura: str):
    """Get pura details by ID."""
    try:
        pura_data = pura_repo.get_pura_by_id(id_pura)
        if not pura_data:
            raise NotFoundException(f"Pura with ID {id_pura} not found")
        
        pura = PuraResponse(**pura_data)
        return PuraDetailResponse(data=pura)
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pura {id_pura}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pura details"
        )


@api_router.get("/kabupaten")
async def get_all_kabupaten():
    """Get all kabupaten with pura count."""
    try:
        kabupaten_list = kabupaten_repo.get_all_kabupaten()
        return kabupaten_list
        
    except Exception as e:
        logger.error(f"Error fetching kabupaten list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch kabupaten list"
        )


@api_router.get("/jenis_pura")
async def get_all_jenis_pura():
    """Get all jenis pura with pura count."""
    try:
        jenis_pura_list = jenis_pura_repo.get_all_jenis_pura()
        return jenis_pura_list
        
    except Exception as e:
        logger.error(f"Error fetching jenis pura list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch jenis pura list"
        )


@api_router.post("/prompt", response_model=PromptResponse)
async def handle_prompt(payload: PromptRequest):
    """Handle chat prompt with RAG capabilities."""
    try:
        # For now, return a simple response
        # TODO: Implement full RAG functionality
        answer = f"Terima kasih atas pertanyaan Anda: '{payload.message}'. Fitur RAG sedang dalam pengembangan."
        
        return PromptResponse(
            answer=answer,
            attachments=[]
        )
        
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process prompt"
        )


@api_router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        from ...services.cache_service import cache_service
        return cache_service.get_stats()
        
    except Exception as e:
        logger.error(f"Error fetching cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cache statistics"
        )


@api_router.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries."""
    try:
        from ...services.cache_service import cache_service
        cache_service.clear()
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        ) 
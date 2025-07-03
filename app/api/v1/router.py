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
from ...data_loader import load_corpus
from ...search import SemanticSearch
from ...gen import generate_response

logger = get_logger(__name__)

# Create router
api_router = APIRouter()

# Initialize repositories
pura_repo = PuraRepository()
kabupaten_repo = KabupatenRepository()
jenis_pura_repo = JenisPuraRepository()

# Load corpus and initialize search engine (singleton)
try:
    texts, metadata = load_corpus()
    search_engine = SemanticSearch(texts, metadata)
except Exception as e:
    logger.error(f"Error initializing search engine: {e}")
    texts, metadata = [], []
    search_engine = None

def extract_lokasi(meta: dict) -> str:
    if meta.get("type") == "lokasi" and "https://" in meta.get("chunk", ""):
        return meta["chunk"].replace("Lokasi Google Maps: ", "").strip()
    return ""

def get_gambar(pura_id: str) -> str:
    # Use the repository for image lookup
    return pura_repo.get_pura_gambar(pura_id)

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


def is_list_query(query: str) -> bool:
    # Detect if the query is asking for a list
    keywords = ["daftar", "list", "semua", "berikan semua", "tampilkan semua", "sebutkan semua", "apa saja", "semuanya"]
    return any(kw in query.lower() for kw in keywords)

def extract_category(query: str, jenis_list) -> str:
    # Try to extract the category from the query using the dynamic list
    for jenis in jenis_list:
        if jenis and jenis.lower() in query.lower():
            return jenis
    return ""

@api_router.post("/prompt", response_model=PromptResponse)
async def handle_prompt(payload: PromptRequest):
    """Handle chat prompt with RAG capabilities (enhanced for list queries, dynamic category)."""
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    try:
        user_query = payload.message
        # Detect if this is a list/daftar query
        if is_list_query(user_query):
            # Dynamically get all available jenis_pura
            jenis_list = [j.get("nama_jenis_pura") for j in jenis_pura_repo.get_all_jenis_pura()]
            category = extract_category(user_query, jenis_list)
            # Retrieve all matching temples for the category (cap at 30)
            if category:
                # Filter metadata for this category
                indices = [i for i, meta in enumerate(search_engine.metadata) if meta.get("jenis") == category]
                # If none found, fallback to normal search
                if not indices:
                    retrieved = search_engine.search(user_query, top_k=10)
                else:
                    # Build results for all
                    results = []
                    for idx in indices[:30]:
                        results.append({
                            "score": 1.0,  # Not used for list
                            "text": search_engine.texts[idx],
                            "meta": search_engine.metadata[idx]
                        })
                    retrieved = results
            else:
                # No category found, fallback to normal search
                retrieved = search_engine.search(user_query, top_k=10)
            answer = generate_response(user_query, retrieved)
        else:
            # Default: top-3 semantic search
            retrieved = search_engine.search(user_query, top_k=3)
            answer = generate_response(user_query, retrieved)
        if not answer:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        want_attachment = any(kw in user_query.lower() for kw in ["di mana", "lokasi", "maps", "gambar", "foto", "pura", "daftar", "list", "semua"])
        attachments = []
        if want_attachment:
            seen_ids = set()
            for r in retrieved:
                meta = r["meta"]
                pura_id = meta.get("id")
                if pura_id in seen_ids:
                    continue
                seen_ids.add(pura_id)
                attachments.append(PuraAttachment(
                    id_pura=pura_id,
                    nama_pura=meta.get("nama", ""),
                    jenis_pura=meta.get("jenis", ""),
                    kabupaten=meta.get("kabupaten", ""),
                    deskripsi=meta.get("chunk", ""),
                    link_lokasi=extract_lokasi(meta),
                    link_gambar=get_gambar(pura_id)
                ))
        return PromptResponse(answer=answer, attachments=attachments)
    except Exception as e:
        logger.error(f"Error in RAG /prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
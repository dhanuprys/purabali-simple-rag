from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.db import (
    get_db_connection, fetch_pura_data, get_pura_gambar, 
    get_pura_by_id_cached, get_kabupaten_list_cached, 
    get_jenis_pura_list_cached, invalidate_pura_cache, invalidate_filter_cache
)
from app.data_loader import load_corpus
from app.search import SemanticSearch
from app.gen import generate_response
from typing import List, Optional

router = APIRouter(prefix="/api")

# --- Models ---
class PromptRequest(BaseModel):
    message: str

class PuraAttachment(BaseModel):
    id_pura: str
    nama_pura: str
    jenis_pura: str
    kabupaten: str
    deskripsi: str
    link_lokasi: Optional[str] = ""
    link_gambar: Optional[str] = ""

class PromptResponse(BaseModel):
    answer: str
    attachments: List[PuraAttachment] = []

# Load corpus and initialize search engine
try:
    texts, metadata = load_corpus()
    search_engine = SemanticSearch(texts, metadata)
except Exception as e:
    print(f"Error initializing search engine: {e}")
    texts, metadata = [], []
    search_engine = None

@router.post("/prompt", response_model=PromptResponse)
async def handle_prompt(payload: PromptRequest):
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        user_query = payload.message
        retrieved = search_engine.search(user_query, top_k=3)
        answer = generate_response(user_query, retrieved)
        
        if not answer:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        want_attachment = any(kw in user_query.lower() for kw in ["di mana", "lokasi", "maps", "gambar", "foto", "pura"])
        attachments = []
        
        if want_attachment:
            seen_ids = set()
            for r in retrieved:
                meta = r["meta"]
                if meta["id"] in seen_ids:
                    continue
                seen_ids.add(meta["id"])
                attachments.append(PuraAttachment(
                    id_pura=meta["id"],
                    nama_pura=meta["nama"],
                    jenis_pura=meta["jenis"],
                    kabupaten=meta["kabupaten"],
                    deskripsi=meta.get("chunk", ""),
                    link_lokasi=extract_lokasi(meta),
                    link_gambar=get_gambar(meta["id"])
                ))

        return PromptResponse(answer=answer, attachments=attachments)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_lokasi(meta: dict) -> str:
    if meta["type"] == "lokasi" and "https://" in meta["chunk"]:
        return meta["chunk"].replace("Lokasi Google Maps: ", "").strip()
    return ""

def get_gambar(pura_id: str) -> str:
    """Get image link for a pura - uses cached version"""
    return get_pura_gambar(pura_id)

# --- General Data Endpoints ---
@router.get("/pura")
def get_all_pura(
    q: str = Query(None), 
    jenis: str = Query(None), 
    kabupaten: str = Query(None),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(12, ge=1, le=100, description="Number of items per page (max 100)")
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Base query for counting total records
    count_sql = """
        SELECT COUNT(*) as total
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
        WHERE 1=1
    """
    
    # Main query for fetching data
    sql = """
        SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, p.link_lokasi, p.latitude, p.longitude, p.link_gambar, j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
        WHERE 1=1
    """
    
    params = []
    if q:
        sql += " AND (p.nama_pura LIKE %s OR p.deskripsi_singkat LIKE %s)"
        count_sql += " AND (p.nama_pura LIKE %s OR p.deskripsi_singkat LIKE %s)"
        params.extend([f"%{q}%", f"%{q}%"])
    if jenis:
        sql += " AND j.nama_jenis_pura = %s"
        count_sql += " AND j.nama_jenis_pura = %s"
        params.append(jenis)
    if kabupaten:
        sql += " AND k.nama_kabupaten = %s"
        count_sql += " AND k.nama_kabupaten = %s"
        params.append(kabupaten)
    
    # Add ORDER BY and LIMIT to main query
    sql += " ORDER BY p.nama_pura ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    # Execute count query with regular cursor
    count_cursor = conn.cursor()
    count_cursor.execute(count_sql, params[:-2] if len(params) > 2 else [])
    count_result = count_cursor.fetchone()
    total_count = int(count_result[0]) if count_result else 0
    count_cursor.close()
    
    # Execute main query
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Calculate pagination metadata
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "data": rows,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": page + 1 if has_next else None,
            "prev_page": page - 1 if has_prev else None
        }
    }

@router.get("/pura/{id_pura}")
def get_pura_by_id(id_pura: str):
    """Get pura details by ID - uses cached version"""
    row = get_pura_by_id_cached(id_pura)
    if not row:
        raise HTTPException(status_code=404, detail="Pura not found")
    return row

@router.get("/kabupaten")
def get_all_kabupaten():
    """Get kabupaten list with pura count - uses cached version"""
    return get_kabupaten_list_cached()

@router.get("/jenis_pura")
def get_all_jenis_pura():
    """Get jenis_pura list with pura count - uses cached version"""
    return get_jenis_pura_list_cached()

# --- Cache Management Endpoints ---
@router.get("/cache/stats")
def get_cache_stats():
    """Get cache statistics"""
    from app.cache import cache
    return cache.get_stats()

@router.post("/cache/clear")
def clear_cache():
    """Clear all cache entries"""
    from app.cache import cache
    cache.clear()
    return {"message": "Cache cleared successfully"}

@router.post("/cache/invalidate/pura")
def invalidate_pura_cache_endpoint():
    """Invalidate all pura-related cache entries"""
    invalidate_pura_cache()
    return {"message": "Pura cache invalidated successfully"}

@router.post("/cache/invalidate/filters")
def invalidate_filter_cache_endpoint():
    """Invalidate filter-related cache entries"""
    invalidate_filter_cache()
    return {"message": "Filter cache invalidated successfully"} 
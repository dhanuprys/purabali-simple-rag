"""
Database models and repositories for data access.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from .connection import get_db_connection
from ..core.exceptions import NotFoundException, DatabaseException

logger = logging.getLogger(__name__)


@dataclass
class Pura:
    """Pura (temple) data model."""
    id_pura: str
    nama_pura: str
    deskripsi_singkat: Optional[str]
    tahun_berdiri: Optional[str]
    link_lokasi: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    link_gambar: Optional[str]
    nama_jenis_pura: Optional[str]
    nama_kabupaten: Optional[str]


@dataclass
class Kabupaten:
    """Kabupaten (regency) data model."""
    id_kabupaten: str
    nama_kabupaten: str
    pura_count: int


@dataclass
class JenisPura:
    """Jenis Pura (temple type) data model."""
    id_jenis_pura: str
    nama_jenis_pura: str
    pura_count: int


class PuraRepository:
    """Repository for Pura (temple) data operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def get_all_pura(self) -> List[Dict[str, Any]]:
        """Get all pura data with joins."""
        query = """
            SELECT 
                p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri,
                p.link_lokasi, p.latitude, p.longitude, p.link_gambar,
                j.nama_jenis_pura, k.nama_kabupaten
            FROM pura p
            LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
            LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
            ORDER BY p.nama_pura ASC
        """
        return self.db.execute_query(query)
    
    def get_pura_by_id(self, id_pura: str) -> Optional[Dict[str, Any]]:
        """Get pura by ID."""
        query = """
            SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, 
                   p.link_lokasi, p.latitude, p.longitude, p.link_gambar, 
                   j.nama_jenis_pura, k.nama_kabupaten
            FROM pura p
            LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
            LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
            WHERE p.id_pura = %s
        """
        results = self.db.execute_query(query, (id_pura,))
        return results[0] if results else None
    
    def get_pura_gambar(self, id_pura: str) -> str:
        """Get pura image link."""
        query = "SELECT link_gambar FROM pura WHERE id_pura = %s"
        results = self.db.execute_query(query, (id_pura,))
        if results and results[0]:
            return str(results[0].get("link_gambar", ""))
        return ""
    
    def search_pura(
        self,
        query: Optional[str] = None,
        jenis: Optional[str] = None,
        kabupaten: Optional[str] = None,
        page: int = 1,
        limit: int = 12
    ) -> Dict[str, Any]:
        """Search pura with filters and pagination."""
        offset = (page - 1) * limit
        
        # Base query parts
        select_clause = """
            SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, 
                   p.link_lokasi, p.latitude, p.longitude, p.link_gambar, 
                   j.nama_jenis_pura, k.nama_kabupaten
            FROM pura p
            LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
            LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
        """
        
        where_clause = "WHERE 1=1"
        params = []
        
        # Add search filters
        if query:
            where_clause += " AND (p.nama_pura LIKE %s OR p.deskripsi_singkat LIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if jenis:
            where_clause += " AND j.nama_jenis_pura = %s"
            params.append(jenis)
        
        if kabupaten:
            where_clause += " AND k.nama_kabupaten = %s"
            params.append(kabupaten)
        
        # Count query
        count_query = f"""
            SELECT COUNT(*) as total
            FROM pura p
            LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
            LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
            {where_clause}
        """
        
        # Data query
        data_query = f"""
            {select_clause}
            {where_clause}
            ORDER BY p.nama_pura ASC 
            LIMIT %s OFFSET %s
        """
        
        # Execute queries
        count_result = self.db.execute_query(count_query, params)
        total_count = int(count_result[0]["total"]) if count_result else 0
        
        data_params = params + [limit, offset]
        data_results = self.db.execute_query(data_query, data_params)
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "data": data_results,
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


class KabupatenRepository:
    """Repository for Kabupaten (regency) data operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def get_all_kabupaten(self) -> List[Dict[str, Any]]:
        """Get all kabupaten with pura count."""
        query = """
            SELECT k.id_kabupaten, k.nama_kabupaten, COUNT(p.id_pura) as pura_count
            FROM kabupaten k
            LEFT JOIN pura p ON k.id_kabupaten = p.id_kabupaten
            GROUP BY k.id_kabupaten, k.nama_kabupaten
            ORDER BY k.nama_kabupaten
        """
        return self.db.execute_query(query)


class JenisPuraRepository:
    """Repository for Jenis Pura (temple type) data operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def get_all_jenis_pura(self) -> List[Dict[str, Any]]:
        """Get all jenis pura with pura count."""
        query = """
            SELECT j.id_jenis_pura, j.nama_jenis_pura, COUNT(p.id_pura) as pura_count
            FROM jenis_pura j
            LEFT JOIN pura p ON j.id_jenis_pura = p.id_jenis_pura
            GROUP BY j.id_jenis_pura, j.nama_jenis_pura
            ORDER BY j.nama_jenis_pura
        """
        return self.db.execute_query(query) 
import mysql.connector
import os
from dotenv import load_dotenv
from app.cache import cached, cache
from app.config import CacheConfig

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "purabali")
    )

@cached(ttl=CacheConfig.PURA_DATA_TTL, key_prefix="pura_data")
def fetch_pura_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri,
            p.link_lokasi, p.link_gambar,
            j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@cached(ttl=CacheConfig.PURA_GAMBAR_TTL, key_prefix="pura_gambar")
def get_pura_gambar(pura_id: str) -> str:
    """Get image link for a specific pura - cached version"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT link_gambar FROM pura WHERE id_pura = %s", (pura_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return ""
    if isinstance(row, dict):
        return str(row.get("link_gambar", ""))
    return str(row[0]) if row[0] is not None else ""

@cached(ttl=CacheConfig.PURA_DETAIL_TTL, key_prefix="pura_detail")
def get_pura_by_id_cached(id_pura: str):
    """Get pura details by ID - cached version"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, 
               p.link_lokasi, p.latitude, p.longitude, p.link_gambar, 
               j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
        WHERE p.id_pura = %s
    """, (id_pura,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

@cached(ttl=CacheConfig.FILTER_TTL, key_prefix="kabupaten_list")
def get_kabupaten_list_cached():
    """Get kabupaten list with pura count - cached version"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT k.id_kabupaten, k.nama_kabupaten, COUNT(p.id_pura) as pura_count
        FROM kabupaten k
        LEFT JOIN pura p ON k.id_kabupaten = p.id_kabupaten
        GROUP BY k.id_kabupaten, k.nama_kabupaten
        ORDER BY k.nama_kabupaten
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@cached(ttl=CacheConfig.FILTER_TTL, key_prefix="jenis_pura_list")
def get_jenis_pura_list_cached():
    """Get jenis_pura list with pura count - cached version"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT j.id_jenis_pura, j.nama_jenis_pura, COUNT(p.id_pura) as pura_count
        FROM jenis_pura j
        LEFT JOIN pura p ON j.id_jenis_pura = p.id_jenis_pura
        GROUP BY j.id_jenis_pura, j.nama_jenis_pura
        ORDER BY j.nama_jenis_pura
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def invalidate_pura_cache():
    """Invalidate all pura-related cache entries"""
    cache.invalidate_pattern("pura_data")
    cache.invalidate_pattern("pura_gambar")
    cache.invalidate_pattern("pura_detail")

def invalidate_filter_cache():
    """Invalidate filter-related cache entries"""
    cache.invalidate_pattern("kabupaten_list")
    cache.invalidate_pattern("jenis_pura_list")

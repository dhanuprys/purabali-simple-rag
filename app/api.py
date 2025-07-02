from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_db_connection, fetch_pura_data
from app.data_loader import load_corpus
from app.search import SemanticSearch
from app.gen import generate_response

router = APIRouter(prefix="/api")

# --- Prompt Endpoint ---
class PromptRequest(BaseModel):
    message: str

texts, metadata = load_corpus()
search_engine = SemanticSearch(texts, metadata)

@router.post("/prompt")
async def handle_prompt(payload: PromptRequest):
    user_query = payload.message
    retrieved = search_engine.search(user_query, top_k=3)
    answer = generate_response(user_query, retrieved)

    want_attachment = any(kw in user_query.lower() for kw in ["di mana", "lokasi", "maps", "gambar", "foto", "pura"])
    attachments = []
    if want_attachment:
        seen_ids = set()
        for r in retrieved:
            meta = r["meta"]
            if meta["id"] in seen_ids:
                continue
            seen_ids.add(meta["id"])
            attachments.append({
                "nama_pura": meta["nama"],
                "jenis_pura": meta["jenis"],
                "kabupaten": meta["kabupaten"],
                "deskripsi": meta.get("chunk", ""),
                "link_lokasi": extract_lokasi(meta),
                "link_gambar": get_gambar(meta["id"])
            })

    return {
        "answer": answer,
        "attachments": attachments
    }

def extract_lokasi(meta: dict) -> str:
    if meta["type"] == "lokasi" and "https://" in meta["chunk"]:
        return meta["chunk"].replace("Lokasi Google Maps: ", "").strip()
    return ""

def get_gambar(pura_id: str) -> str:
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

# --- General Data Endpoints ---
@router.get("/pura")
def get_all_pura():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, p.link_lokasi, p.latitude, p.longitude, p.link_gambar, j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@router.get("/pura/{id_pura}")
def get_pura_by_id(id_pura: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri, p.link_lokasi, p.latitude, p.longitude, p.link_gambar, j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
        WHERE p.id_pura = %s
    """, (id_pura,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Pura not found")
    return row

@router.get("/kabupaten")
def get_all_kabupaten():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_kabupaten, nama_kabupaten FROM kabupaten")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@router.get("/jenis_pura")
def get_all_jenis_pura():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_jenis_pura, nama_jenis_pura FROM jenis_pura")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows 
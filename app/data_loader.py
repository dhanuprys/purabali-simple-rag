import hashlib
from app.db import fetch_pura_data

def hash_chunk(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode()).hexdigest()

def build_chunks_from_row(row: dict):
    chunks = []
    chunks.append(("intro", f"{row['nama_pura']} adalah pura jenis {row['nama_jenis_pura']} yang berada di Kabupaten {row['nama_kabupaten']}."))
    if row["deskripsi_singkat"]:
        chunks.append(("deskripsi", f"Deskripsi: {row['deskripsi_singkat']}"))
    if row["tahun_berdiri"]:
        chunks.append(("sejarah", f"Pura ini diperkirakan berdiri pada {row['tahun_berdiri']}."))
    if row["link_lokasi"]:
        chunks.append(("lokasi", f"Lokasi Google Maps: {row['link_lokasi']}"))
    return chunks

def load_corpus():
    data = fetch_pura_data()
    seen_hashes = set()
    texts = []
    metadata = []
    for row in data:
        chunks = build_chunks_from_row(row)
        for chunk_type, chunk in chunks:
            h = hash_chunk(chunk)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            texts.append(chunk)
            metadata.append({
                "id": row["id_pura"],
                "nama": row["nama_pura"],
                "jenis": row["nama_jenis_pura"],
                "kabupaten": row["nama_kabupaten"],
                "type": chunk_type,
                "chunk": chunk
            })
    return texts, metadata

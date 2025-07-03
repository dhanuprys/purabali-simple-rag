from sentence_transformers import SentenceTransformer
from .model_cache import get_cached_model

# Get the cached model
model = get_cached_model()

def embed_texts(texts: list[str]):
    return model.encode([f"Dokumen: {t}" for t in texts], convert_to_numpy=True, normalize_embeddings=True)

def embed_query(query: str):
    return model.encode(f"Pertanyaan: {query}", convert_to_numpy=True, normalize_embeddings=True)

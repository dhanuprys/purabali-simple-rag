import faiss
import numpy as np
from app.embed import embed_texts, embed_query, model

class SemanticSearch:
    def __init__(self, texts: list[str], metadata: list[dict]):
        self.texts = texts
        self.metadata = metadata
        self.embeddings = embed_texts(texts)
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def detect_filters(self, query: str):
        kabupaten_list = ['Badung', 'Bangli', 'Buleleng', 'Denpasar', 'Gianyar', 'Jembrana', 'Karangasem', 'Klungkung', 'Tabanan']
        jenis_list = ['Dang Kahyangan', 'Kahyangan Jagat', 'Pura Beji', 'Pura Gunung', 'Pura Melanting', 'Pura Puseh', 'Pura Segara', 'Pura Sejarah', 'Pura Taman', 'Sad Kahyangan']
        filters = {}
        for kab in kabupaten_list:
            if kab.lower() in query.lower():
                filters['kabupaten'] = kab
        for jenis in jenis_list:
            if jenis.lower() in query.lower():
                filters['jenis'] = jenis
        return filters

    def rerank(self, query_vec, candidates, top_k=3):
        reranked = []
        for idx in candidates:
            score = np.dot(self.embeddings[idx], query_vec)
            reranked.append((score, idx))
        reranked.sort(reverse=True)
        return reranked[:top_k]

    def search(self, query: str, top_k: int = 3):
        query_vec = embed_query(query)
        D, I = self.index.search(np.array([query_vec]), 10)
        filters = self.detect_filters(query)
        filtered = []
        for i in I[0]:
            meta = self.metadata[i]
            if ('kabupaten' in filters and filters['kabupaten'] != meta['kabupaten']) or                ('jenis' in filters and filters['jenis'] != meta['jenis']):
                continue
            filtered.append(i)
        candidate_indices = filtered if filtered else list(I[0])
        reranked = self.rerank(query_vec, candidate_indices, top_k=top_k)
        results = []
        for score, idx in reranked:
            results.append({
                "score": float(score),
                "text": self.texts[idx],
                "meta": self.metadata[idx]
            })
        return results

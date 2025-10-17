from pathlib import Path
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGIndex:
    def __init__(self, path: str):
        p = Path(path)
        self.index = faiss.read_index(str(p / "faiss.index"))
        self.chunks = json.loads((p / "chunks.json").read_text())
        self.meta = json.loads((p / "meta.json").read_text())
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def search(self, query: str, k: int = 5):
        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        D, I = self.index.search(q, k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            ch = self.chunks[int(idx)]
            m = self.meta[int(idx)]
            hits.append({"score": float(score), "snippet": ch[:360], "page": m["page"]})
        return hits

def load_index(path: str) -> RAGIndex:
    return RAGIndex(path)

def answer_question(rag: RAGIndex, question: str):
    hits = rag.search(question, k=5)
    if not hits or hits[0]["score"] < 0.2:
        return {"answer": "não encontrado", "sources": hits[:3]}
    best = hits[0]
    return {
        "answer": best["snippet"],
        "sources": hits[:3]
    }
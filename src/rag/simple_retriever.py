#!/usr/bin/env python3
"""Simple retriever for testing without large model downloads"""

from pathlib import Path
import json
import faiss
import numpy as np

class SimpleRAGIndex:
    def __init__(self, path: str):
        p = Path(path)
        self.index = faiss.read_index(str(p / "faiss.index"))
        self.chunks = json.loads((p / "chunks.json").read_text())
        self.meta = json.loads((p / "meta.json").read_text())
        print(f"✅ Loaded index with {len(self.chunks)} chunks")

    def search(self, query: str, k: int = 5):
        """Simple keyword-based search for testing"""
        query_lower = query.lower()
        scores = []
        
        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            words = query_lower.split()
            score = sum(1 for word in words if word in chunk_lower) / len(words)
            scores.append((score, i))
        
        scores.sort(reverse=True)
        
        hits = []
        for score, idx in scores[:k]:
            if score > 0:
                chunk = self.chunks[idx]
                meta = self.meta[idx]
                hits.append({
                    "score": float(score), 
                    "snippet": chunk[:360], 
                    "page": meta.get("page", 1)
                })
        
        return hits

def load_index(path: str) -> SimpleRAGIndex:
    return SimpleRAGIndex(path)

def answer_question(rag: SimpleRAGIndex, question: str):
    hits = rag.search(question, k=5)
    if not hits or hits[0]["score"] < 0.1:
        return {"answer": "No relevant information found", "sources": []}
    
    context = " | ".join([h["snippet"] for h in hits[:3]])
    return {
        "answer": f"Based on the documentation: {context}",
        "sources": hits
    }

if __name__ == "__main__":
    rag = load_index("data/rag/index")
    result = answer_question(rag, "What are the router specifications?")
    print("Test result:", result)
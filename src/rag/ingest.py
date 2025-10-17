from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import argparse

def chunk_text(text: str, max_chars=1200, overlap=200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0: start = 0
        if start >= len(text): break
    return chunks

def read_pdf_chunks(pdf_path: str):
    reader = PdfReader(pdf_path)
    chunks = []
    meta = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for ch in chunk_text(text):
            chunks.append(ch)
            meta.append({"page": i})
    return chunks, meta

def build_index(chunks: List[str], model_name="sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embs = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs.astype(np.float32))
    return index, embs

def save_index(out_dir: str, index, chunks: List[str], meta: List[Dict]):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "faiss.index"))
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", default="data/rag/index")
    args = ap.parse_args()

    chunks, meta = read_pdf_chunks(args.pdf)
    index, _ = build_index(chunks)
    save_index(args.out, index, chunks, meta)

if __name__ == "__main__":
    main()
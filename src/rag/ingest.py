from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
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
        if start < 0:
            start = 0
        if start >= len(text):
            break
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


def build_lightweight_index(chunks: List[str]):
    # Create a dummy index for compatibility
    # The actual search will be keyword-based in retriever
    dim = 1  # Minimal dimension
    index = faiss.IndexFlatL2(dim)
    
    # Add dummy vectors for each chunk
    vectors = np.ones((len(chunks), dim), dtype=np.float32)
    index.add(vectors)
    
    print(f"✅ Built lightweight index with {len(chunks)} chunks")
    return index


def save_index(out_dir: str, index, chunks: List[str], meta: List[Dict]):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(out / "faiss.index"))
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))
    
    print(f"✅ Saved index to {out_dir}")


def main():
    ap = argparse.ArgumentParser(description="Ingest PDF documents for RAG")
    ap.add_argument("--pdf", required=True, help="Path to PDF file")
    ap.add_argument("--out", default="data/rag/index", help="Output directory")
    args = ap.parse_args()

    print(f"📄 Processing PDF: {args.pdf}")
    chunks, meta = read_pdf_chunks(args.pdf)
    
    print(f"📝 Extracted {len(chunks)} text chunks")
    index = build_lightweight_index(chunks)
    
    save_index(args.out, index, chunks, meta)
    print("🎉 Document ingestion complete!")


if __name__ == "__main__":
    main()

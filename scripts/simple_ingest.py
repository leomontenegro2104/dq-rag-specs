#!/usr/bin/env python3
"""Simple ingestion script for testing without large model downloads"""

import json
import numpy as np
import faiss
from pathlib import Path


def create_dummy_index():
    """Create a simple test index with pre-defined embeddings"""
    chunks = [
        "Alpha-X Pro Router Specifications - High-performance enterprise router",
        "Operating frequency: 2.4GHz and 5GHz dual-band wireless",
        "Data transfer rates: Up to 1.9 Gbps combined throughput",
        "Ethernet ports: 4 x Gigabit LAN ports, 1 x Gigabit WAN port",
        "Security features: WPA3 encryption, VPN support, firewall",
        "Physical dimensions: 220x120x45mm, Weight: 950 grams",
        "Power consumption: 12V/2A adapter, Energy Star certified",
        "Management: Web interface, mobile app, SNMP support",
    ]

    meta = [{"page": 1, "chunk_id": i} for i in range(len(chunks))]

    np.random.seed(42)
    embeddings = np.random.randn(len(chunks), 384).astype(np.float32)

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms

    index = faiss.IndexFlatIP(384)
    index.add(embeddings)

    return index, chunks, meta


def save_index(out_dir: str, index, chunks, meta):
    """Save index, chunks, and metadata"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(out / "faiss.index"))

    with open(out / "chunks.json", "w") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    with open(out / "meta.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ Index saved to {out_dir}")
    print(f"   - {len(chunks)} chunks indexed")
    print(f"   - Index size: {index.ntotal} vectors")
    print(f"   - Vector dimension: {index.d}")


if __name__ == "__main__":
    index, chunks, meta = create_dummy_index()
    save_index("data/rag/index", index, chunks, meta)

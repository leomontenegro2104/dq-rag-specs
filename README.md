# DQ-RAG-Specs

Data Quality RAG (Retrieval-Augmented Generation) Specifications Project

## Overview

This project implements a complete ETL pipeline for data quality validation and a RAG system for intelligent document querying using FAISS and Sentence Transformers.

## Requirements

- **Python**: 3.11+
- **System**: Works on CPU (no GPU required)
- **Dependencies**: See `pyproject.toml`

## Setup

```bash
# Install dependencies
make setup

# Generate sample inventory data
make gen-inventory

# Run ETL pipeline
make run-etl

# Ingest PDF into FAISS index
make ingest-specs

# Start RAG API
make run-rag
```

## Make Targets

| Target | Description |
|--------|-------------|
| `setup` | Install all dependencies |
| `gen-inventory` | Generate sample inventory.parquet |
| `run-etl` | Process raw data through ETL pipeline |
| `ingest-specs` | Index PDF into FAISS for RAG |
| `run-rag` | Start FastAPI server on port 8000 |
| `test` | Run pytest suite |
| `lint` | Check code with ruff and black |
| `fmt` | Format code with black |

### ETL Pipeline
```bash
# Process raw data with validation and quarantine
make run-etl

# Output: data/dim_vendor/, data/dim_product/, data/fact_inventory/
# Quarantine: data/silver/_quarantine/
```

### RAG System
```bash
# Index documentation
make ingest-specs

# Start API server
make run-rag

# Query via curl
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the operating temperature?"}'

# Response:
# {
#   "answer": "Operating temperature range: 0°C to 40°C...",
#   "sources": [{"score": 0.85, "snippet": "...", "page": 3}]
# }
```

## Quarantine Policy

### Data Quality Issues Handling

**Products (`raw/products.csv`)**:
- **Missing SKU**: → quarantine (reason: "sku_missing")
- **Invalid weight**: ≤ 0 or non-numeric → quarantine (reason: "invalid_weight")  
- **Incomplete dimensions**: Missing L×W×H → quarantine (reason: "dimensions_incomplete")
- **Invalid MSRP**: < 0 or non-numeric → quarantine (reason: "invalid_msrp")
- **Missing vendor_code**: → quarantine (reason: "vendor_code_missing")

**Inventory (`raw/inventory.parquet`)**:
- **Negative stock**: on_hand < 0 → quarantine (reason: "negative_on_hand")
- **Missing FK**: product_id not in dim_product → quarantine (reason: "fk_product_missing")

**Vendors (`raw/vendors.jsonl`)**:
- **Duplicates**: Same vendor_code → deduplicated (longest name wins)

### Parsing Decisions

**Decimal Numbers**:
- Convert "159,90" → 159.90 (European format support)
- Invalid formats → quarantine

**Dates**:
- Support formats: "YYYY-MM-DD", "YYYY/MM/DD", "YYYY/DD/MM"
- Invalid dates (e.g., "2021-02-29") → NULL (policy: don't impute)
- Malformed strings → quarantine

**Dimensions**:
- Parse "220x120x45" → length=220, width=120, height=45
- Incomplete "90x60x" → quarantine
- Invalid formats → quarantine

## Troubleshooting

### FAISS CPU Issues
If you encounter FAISS/BLAS errors:

```bash
# Install CPU-only FAISS
pip install faiss-cpu --no-cache

# Alternative: Use conda
conda install faiss-cpu -c conda-forge
```

### Memory Issues
- **Embedding model**: Uses all-MiniLM-L6-v2 (80MB, CPU-optimized)
- **Index size**: ~1KB per chunk (minimal memory footprint)
- **CPU-only**: No GPU required, runs on modest hardware

### Common Issues

**Import Errors**:
```bash
make setup  # Ensure all dependencies installed
```

**Missing Index**:
```bash
make ingest-specs  # Build FAISS index first
```

**API Startup**:
- Index must exist in `data/rag/index/`
- Check `docs/specs.pdf` exists

## Project Structure

```
.
├── raw/                         # Raw data with intentional quality issues
├── data/                        # Processed parquet files (partitioned)
├── docs/specs.pdf              # Alpha-X Pro specifications (5 pages)
├── schemas/                     # Pandera contracts (raw + trusted)
├── src/etl/                     # ETL pipeline with quarantine
├── src/rag/                     # FAISS + Sentence Transformers RAG
├── tests/                       # Unit tests + smoke tests
├── eval/                        # Evaluation questions + script
└── scripts/                     # Utility scripts
```

## Architecture

**ETL Flow**:
Raw CSV/JSONL/Parquet → Pandera Validation → Transform → Quarantine → Trusted Parquet

**RAG Flow**:
PDF → Chunk → Embed → FAISS Index → Query → Retrieve → Respond

**No LLM**: Uses deterministic snippet-based responses (zero cost)
# DQ-RAG-Specs

Data Quality RAG (Retrieval-Augmented Generation) Specifications Project

## Overview

This project implements a complete ETL pipeline for data quality validation and a RAG system for intelligent document querying using FAISS and Sentence Transformers.

## Requirements

- **Platform**: Ubuntu 20.04+ or WSL2 with Ubuntu
- **Python**: 3.10+ (system Python recommended)
- **RAM**: 4GB+ recommended for embedding models
- **Dependencies**: See `pyproject.toml`

### Prerequisites
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-dev libffi-dev build-essential
```

## Setup

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-pandas python3-dev libffi-dev
/usr/bin/python3 -m pip install --user pyarrow

# 2. Install project dependencies
make setup

# 3. Generate sample data & run pipeline
make gen-inventory
make run-etl
make ingest-specs
make run-rag
```

### Using Custom Python
If you need to use a specific Python version:
```bash
# Edit Makefile to use specific Python
PY=/usr/bin/python3.10       # Specific system version
# or
PY=python3                    # Default system Python
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

### Python Environment Issues

**Error: "No module named '_ctypes'"**:
```bash
# Install development libraries
sudo apt install -y libffi-dev libbz2-dev libreadline-dev libsqlite3-dev

# If using pyenv, reinstall Python
pyenv install 3.10.6 --force

# Alternative: Use system Python (recommended)
# Edit Makefile: PY=/usr/bin/python3
```

**Error: "ModuleNotFoundError: pandas/pyarrow"**:
```bash
# Install system packages
sudo apt install -y python3-pandas
/usr/bin/python3 -m pip install --user pyarrow

# Or install in project environment
pip install pandas pyarrow
```

### FAISS CPU Issues
```bash
# Install CPU-only FAISS
pip install faiss-cpu --no-cache

# If still issues, use conda
conda install faiss-cpu -c conda-forge
```

### WSL-Specific Issues
```bash
# Update WSL if old version
wsl --update

# Fix file permissions
chmod +x scripts/*.py

# Use Windows paths if needed
# Raw data: /mnt/c/path/to/data
```

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

## Known Limitations

### Environment Compatibility
- **Tested on**: Ubuntu 20.04 LTS (WSL2)
- **Partial support**: macOS, Windows with WSL
- **Untested**: Pure Windows, older Linux distributions

### Python Compatibility
- **Recommended**: System Python 3.10+ or conda environments
- **pyenv**: May require manual compilation with development libraries
- **Virtual environments**: Work but may need dependency troubleshooting

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB+ recommended for larger documents
- **Storage**: ~500MB for dependencies, ~1GB for models and data
- **CPU**: Any modern x64 CPU (no GPU required)

### Performance Notes
- **Cold start**: First embedding takes ~30s (model download)
- **Query time**: ~100-500ms per question
- **Index build**: ~10s per 100 document pages

For production deployment, consider Docker or conda for better environment isolation.

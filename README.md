# DQ-RAG-Specs

Data Quality RAG (Retrieval-Augmented Generation) Specifications Project

## Overview

This project implements a complete pipeline for processing specification documents and building a RAG system for intelligent document querying.

## Project Structure

```
.
├── raw/                         # dados brutos
├── data/                        # dados processados (parquet)
├── docs/                        # specs.pdf
├── schemas/                     # contratos (pandera/pydantic)
├── src/
│   ├── etl/                     # ETL pipeline
│   │   ├── __init__.py
│   │   ├── run.py               # CLI
│   │   ├── transform.py
│   │   ├── validators.py
│   │   └── utils.py
│   └── rag/                     # RAG system
│       ├── __init__.py
│       ├── api.py               # FastAPI /ask
│       ├── ingest.py            # chunk + embed + index
│       └── retriever.py
├── tests/                       # unit tests
├── eval/                        # evaluation metrics
├── Makefile                     # build automation
├── pyproject.toml               # project configuration
├── .pre-commit-config.yaml      # code quality hooks
└── REPORT.md                    # project report
```

## Installation

```bash
# Install the package in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

### ETL Pipeline
```bash
# Run ETL pipeline
make run-etl
# or
python -m src.etl.run
```

### RAG API
```bash
# Start the FastAPI server
make run-api
# or
uvicorn src.rag.api:app --reload
```

### Development
```bash
# Run tests
make test

# Lint code
make lint

# Format code
make format

# Clean cache
make clean
```

## Features

- **ETL Pipeline**: Complete data processing workflow
- **Data Validation**: Schema validation with Pandera/Pydantic
- **RAG System**: Document ingestion, embedding, and retrieval
- **FastAPI Integration**: RESTful API for querying
- **Quality Assurance**: Pre-commit hooks, linting, and testing

## Requirements

- Python 3.9+
- Dependencies defined in `pyproject.toml`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License
PY=python
PIP=python -m pip

setup:
	$(PIP) install -U pip
	$(PIP) install -e .[dev]

lint:
	ruff check .
	black --check .

fmt:
	black .

test:
	pytest -q

run-etl:
	$(PY) -m src.etl.run --raw-dir raw --out-dir data

ingest-specs:
	$(PY) -m src.rag.ingest --pdf docs/specs.pdf --out data/rag/index

run-rag:
	$(PY) -m src.rag.api
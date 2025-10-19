PY=python3.11
PIP=python3.11 -m pip

setup:
	$(PIP) install -U pip
	$(PIP) install -e .[dev]

lint:
	ruff check .
	black --check .

fmt:
	black .

pre-commit:
	pre-commit run --all-files

test:
	PYTHONPATH=. $(PY) -m pytest tests/ -v

gen-inventory:
	$(PY) scripts/gen_inventory.py

run-etl:
	$(PY) -m src.etl.run --raw-dir raw --out-dir data

ingest-specs:
	$(PY) -m src.rag.ingest --pdf raw/example_specs.pdf --out data/rag/index

run-rag:
	$(PY) -m src.rag.api

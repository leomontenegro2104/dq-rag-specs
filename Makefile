PY=/usr/bin/python3
PIP=/usr/bin/python3 -m pip

setup:
	$(PIP) install -U pip
	$(PIP) install -e .[dev]

lint:
	ruff check .
	black --check .

fmt:
	black .

test:
	PYTHONPATH=. $(PY) -m pytest tests/ -v

gen-inventory:
	$(PY) scripts/gen_inventory.py

run-etl:
	$(PY) -m src.etl.run --raw-dir raw --out-dir data

ingest-specs:
	$(PY) scripts/simple_ingest.py

run-rag:
	$(PY) -m src.rag.simple_api
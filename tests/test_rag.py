from fastapi.testclient import TestClient
from src.rag.api import app, _startup


def test_ask_smoke():
    _startup()
    c = TestClient(app)
    r = c.post("/ask", json={"question": "router specifications"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) >= 1

from fastapi.testclient import TestClient
from src.rag.api import app

def test_ask_smoke():
    c = TestClient(app)
    r = c.post("/ask", json={"question":"temperatura operacional"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) >= 1
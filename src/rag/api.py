from fastapi import FastAPI
from pydantic import BaseModel
from .retriever import load_index, answer_question

app = FastAPI(title="Specs RAG API")
_index = None


class Ask(BaseModel):
    question: str


@app.on_event("startup")
def _startup():
    global _index
    print("🚀 Starting RAG API...")
    _index = load_index("data/rag/index")
    print("✅ RAG API ready!")


@app.post("/ask")
def ask(body: Ask):
    result = answer_question(_index, body.question)
    return result


@app.get("/health")
def health():
    return {"status": "ok", "index_loaded": _index is not None}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

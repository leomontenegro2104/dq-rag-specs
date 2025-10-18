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
    _index = load_index("data/rag/index")


@app.post("/ask")
def ask(body: Ask):
    return answer_question(_index, body.question)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.rag.api:app", host="0.0.0.0", port=8000, reload=False)

"""
api.py — Outpatient Care Intelligence API
Exposes the same FAISS + GPT-4o-mini RAG chain as app.py over HTTP,
so an ElevenLabs agent can call it as a webhook tool.

Run:  uvicorn api:app --reload --port 8000
"""

import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

TOOL_TOKEN = os.environ.get("TOOL_TOKEN")
if not TOOL_TOKEN:
    raise RuntimeError("Set TOOL_TOKEN in your .env before starting the API.")

FAISS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_index")

# Voice answers need to be short: the agent reads them aloud (in Creole).
# Same retrieval and model settings as app.py; only the answer style differs.
VOICE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an outpatient care data analyst answering questions about CMS Medicare data across US states.

Use ONLY the retrieved context below. If the context does not contain the answer, say so plainly. Never invent numbers.

Context:
{context}

Question: {question}

Answer in 2-4 short sentences of plain English, suitable for being read aloud.
Name the specific states and numbers. No bullet points, no markdown, no tables.

Answer:""",
)


def build_chain():
    if not os.path.exists(FAISS_DIR):
        raise RuntimeError("FAISS index not found. Run `python ingest.py` first.")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": VOICE_PROMPT},
    )


app = FastAPI(title="Outpatient Care Intelligence API")
chain = build_chain()  # loaded once at startup, like st.cache_resource


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(q: Question, authorization: str = Header(default="")):
    if not secrets.compare_digest(authorization, f"Bearer {TOOL_TOKEN}"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    result = chain.invoke({"query": q.question})
    sources = sorted({
        f"{d.metadata.get('state_name', d.metadata.get('state_code', '?'))} · "
        f"{d.metadata.get('source', '').replace('_', ' ').title()}"
        for d in result.get("source_documents", [])
    })
    return {"answer": result["result"], "sources": sources}

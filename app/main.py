from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title="Semantic RAG Foundation",
    version="0.1.0",
    description="Milestone 1 foundation: FastAPI + PostgreSQL + pgvector",
)

app.include_router(health_router)
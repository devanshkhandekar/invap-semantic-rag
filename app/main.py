from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.ingest_routes import router as ingest_router
from app.api.search_routes import router as search_router

app = FastAPI(
    title="Semantic RAG Foundation",
    version="0.3.0",
    description="FastAPI + PostgreSQL + pgvector + ingestion + retrieval",
)

app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(search_router)
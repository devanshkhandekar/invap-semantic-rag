from app.ingestion.embedding_service import EmbeddingService
from app.core.config import settings

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingService(settings.EMBEDDING_MODEL_NAME)
    return _embedder

def embed_query(query: str) -> list[float]:
    embedder = get_embedder()
    result = embedder.embed_texts([query])
    return result[0]
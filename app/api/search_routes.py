from fastapi import APIRouter, HTTPException
from app.schemas.search import SearchRequest, SearchResponse
from app.retrieval.vector_search_service import search_chunks

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def semantic_search(payload: SearchRequest):
    try:
        results = search_chunks(
            user_id=payload.user_id,
            query=payload.query,
            top_k=payload.top_k,
        )
        return SearchResponse(
            query=payload.query,
            top_k=payload.top_k,
            results=results,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")
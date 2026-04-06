from pydantic import BaseModel, Field
from typing import List


class SearchRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    document_id: int
    document_name: str
    project_id: int
    page_number: int | None
    chunk_index: int
    chunk_text: str
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]
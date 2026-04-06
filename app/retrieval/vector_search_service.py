from sqlalchemy import text
from app.core.database import engine
from app.retrieval.query_embedding_service import embed_query
from app.retrieval.access_control_service import get_allowed_project_ids


def to_pgvector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(v)) for v in values) + "]"


def search_chunks(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    allowed_project_ids = get_allowed_project_ids(user_id)

    if not allowed_project_ids:
        return []

    query_embedding = embed_query(query)
    query_vector = to_pgvector_literal(query_embedding)

    sql = text("""
        SELECT
            d.id AS document_id,
            d.filename AS document_name,
            d.project_id AS project_id,
            c.page_number AS page_number,
            c.chunk_index AS chunk_index,
            c.chunk_text AS chunk_text,
            1 - (c.embedding <=> CAST(:query_vector AS vector)) AS similarity_score
        FROM document_chunks c
        JOIN documents d
          ON d.id = c.document_id
        WHERE d.project_id = ANY(CAST(:allowed_project_ids AS bigint[]))
        ORDER BY c.embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k
    """)

    with engine.begin() as connection:
        rows = connection.execute(
            sql,
            {
                "query_vector": query_vector,
                "allowed_project_ids": allowed_project_ids,
                "top_k": top_k,
            },
        ).fetchall()

    return [
        {
            "document_id": row[0],
            "document_name": row[1],
            "project_id": row[2],
            "page_number": row[3],
            "chunk_index": row[4],
            "chunk_text": row[5],
            "similarity_score": round(float(row[6]), 4),
        }
        for row in rows
    ]
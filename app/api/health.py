from fastapi import APIRouter, HTTPException
from app.core.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "semantic-rag-foundation",
    }


@router.get("/health/db")
def health_db() -> dict:
    db_status = check_database_connection()

    if not db_status.get("database_connected"):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "service": "semantic-rag-foundation",
                "database": db_status,
            },
        )

    return {
        "status": "ok",
        "service": "semantic-rag-foundation",
        "database": db_status,
    }
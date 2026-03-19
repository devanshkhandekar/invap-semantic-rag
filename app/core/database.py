from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

engine = create_engine(
    settings.sqlalchemy_database_uri,
    pool_pre_ping=True,
    future=True,
)


def check_database_connection() -> dict:
    """
    Verifies that PostgreSQL is reachable and pgvector extension exists.
    """
    try:
        with engine.connect() as connection:
            db_name = connection.execute(text("SELECT current_database();")).scalar()
            vector_installed = connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='vector');")
            ).scalar()

        return {
            "database_connected": True,
            "database_name": db_name,
            "pgvector_installed": bool(vector_installed),
        }

    except SQLAlchemyError as exc:
        return {
            "database_connected": False,
            "error": str(exc),
        }
from sqlalchemy import text
from app.core.database import engine


def get_allowed_project_ids(user_id: str) -> list[int]:
    with engine.begin() as connection:
        rows = connection.execute(
            text("""
                SELECT project_id
                FROM user_projects
                WHERE user_id = :user_id
                ORDER BY project_id
            """),
            {"user_id": user_id},
        ).fetchall()

    return [row[0] for row in rows]
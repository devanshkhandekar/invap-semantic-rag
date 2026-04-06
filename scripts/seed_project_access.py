import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("/app/.env")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "rag_db"),
        user=os.getenv("POSTGRES_USER", "rag_user"),
        password=os.getenv("POSTGRES_PASSWORD", "rag_password"),
    )


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (name)
                VALUES (%s), (%s)
                ON CONFLICT (name) DO NOTHING
            """, ("Project A", "Project B"))

            cur.execute("SELECT id, name FROM projects ORDER BY id")
            projects = cur.fetchall()
            project_map = {name: project_id for project_id, name in projects}

            seed_users = [
                ("user_1", "Project A"),
                ("user_2", "Project B"),
                ("user_admin", "Project A"),
                ("user_admin", "Project B"),
            ]

            for user_id, project_name in seed_users:
                cur.execute("""
                    INSERT INTO user_projects (user_id, project_id)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, project_id) DO NOTHING
                """, (user_id, project_map[project_name]))

            cur.execute("""
                SELECT id
                FROM documents
                WHERE project_id IS NULL
                ORDER BY id
            """)
            docs = cur.fetchall()

            for idx, (doc_id,) in enumerate(docs):
                project_name = "Project A" if idx % 2 == 0 else "Project B"
                cur.execute("""
                    UPDATE documents
                    SET project_id = %s
                    WHERE id = %s
                """, (project_map[project_name], doc_id))

        conn.commit()
        print("Project access seed complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
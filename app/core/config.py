import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "rag_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "rag_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "rag_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
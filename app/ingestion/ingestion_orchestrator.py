from pathlib import Path
from psycopg2.extras import execute_values

from app.core.config import settings
from app.core.database import get_db_connection
from app.ingestion.pdf_text_extractor import PDFTextExtractor
from app.ingestion.text_chunking_service import TextChunkingService
from app.ingestion.embedding_service import EmbeddingService


class IngestionOrchestrator:
    def __init__(self):
        self.extractor = PDFTextExtractor()
        self.chunker = TextChunkingService(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.embedder = EmbeddingService(settings.EMBEDDING_MODEL_NAME)

    def ingest_directory(self, directory_path: str) -> dict:
        directory = Path(directory_path)
        pdf_files = sorted(directory.glob("*.pdf"))

        results = []
        total_pages = 0
        total_chunks = 0

        for pdf_file in pdf_files:
            result = self.ingest_pdf(str(pdf_file))
            results.append(result)
            total_pages += result["page_count"]
            total_chunks += result["chunk_count"]

        return {
            "pdfs_processed": len(results),
            "total_pages_extracted": total_pages,
            "total_chunks_created": total_chunks,
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.embedding_dimension,
            "documents": results,
        }

    def ingest_pdf(self, pdf_path: str) -> dict:
        pdf_data = self.extractor.extract(pdf_path)
        chunks = self.chunker.chunk_pages(pdf_data["pages"])

        texts = [chunk["chunk_text"] for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts) if texts else []

        document_id = self._insert_document(pdf_data, ingest_status="processing")
        inserted_chunk_count = self._insert_chunks(document_id, chunks, embeddings)
        self._update_document_status(document_id, "completed")

        return {
            "document_id": document_id,
            "filename": pdf_data["filename"],
            "page_count": pdf_data["page_count"],
            "language": pdf_data["language"],
            "chunk_count": len(chunks),
            "inserted_chunk_count": inserted_chunk_count,
            "embedding_dimension": self.embedder.embedding_dimension,
            "embedding_model": self.embedder.model_name,
        }

    def _insert_document(self, pdf_data: dict, ingest_status: str) -> int:
        query = """
            INSERT INTO documents (filename, source_path, language, page_count, ingest_status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        pdf_data["filename"],
                        pdf_data["source_path"],
                        pdf_data["language"],
                        pdf_data["page_count"],
                        ingest_status,
                    ),
                )
                row = cur.fetchone()
                document_id = row[0] if isinstance(row, tuple) else row["id"]
                conn.commit()
                return document_id
        finally:
            conn.close()

    def _insert_chunks(
        self,
        document_id: int,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            return 0

        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append(
                (
                    document_id,
                    chunk["chunk_index"],
                    chunk["page_number"],
                    chunk["chunk_text"],
                    self._vector_to_pg_string(embedding),
                )
            )

        query = """
            INSERT INTO document_chunks (document_id, chunk_index, page_number, chunk_text, embedding)
            VALUES %s
        """

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    query,
                    rows,
                    template="(%s, %s, %s, %s, %s::vector)",
                )
                conn.commit()
            return len(rows)
        finally:
            conn.close()

    def _update_document_status(self, document_id: int, status: str) -> None:
        query = """
            UPDATE documents
            SET ingest_status = %s
            WHERE id = %s
        """

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (status, document_id))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _vector_to_pg_string(embedding: list[float]) -> str:
        return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"
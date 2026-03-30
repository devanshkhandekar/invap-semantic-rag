
# Semantic RAG Foundation + PDF Ingestion

This repository contains the local foundation and the first end-to-end ingestion workflow for the semantic document search system for INVAP.

This milestone allows you to:

- start the system locally with Docker
- run PostgreSQL with `pgvector`
- run the FastAPI service
- verify health endpoints
- ingest sample PDF files end to end
- store extracted document chunks and embeddings in PostgreSQL
- verify that ingestion worked using SQL checks and API responses

---

## Included in this milestone

### Milestone 1
- Dockerized local environment
- PostgreSQL with `pgvector`
- Basic FastAPI service
- Health check endpoints
- Local startup instructions

### Milestone 2
- PDF ingestion pipeline
- Page text extraction from PDFs
- Text chunking
- Embedding generation
- Storage of documents and chunks in PostgreSQL
- Embedding storage in `pgvector`
- Sample ingestion script
- API endpoint to trigger sample ingestion
- Verification steps to confirm ingestion worked

---

## Requirements

- Ubuntu 22.04 or Windows 11 + Docker Desktop + WSL2
- Docker
- Docker Compose

---

## Repository structure

```text
app/
  api/
  core/
  ingestion/
  main.py

initdb/
  001_init.sql
  002_ingestion_schema.sql

sample_data/
  README.md
  <place your PDF files here>

scripts/
  run_sample_ingestion.py
  download_sample_data.py

Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
````

---

## Environment setup

Copy the example environment file:

```bash
cp .env.example .env
```

For Docker-based testing, make sure the `.env` file contains values similar to:

```env
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

APP_HOST=0.0.0.0
APP_PORT=8000

EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=800
CHUNK_OVERLAP=120
SAMPLE_DATA_DIR=/app/sample_data
```

---

## Add sample PDF files

Place 1 or more PDF files inside the `sample_data/` folder.

Recommended:

* text-based PDFs
* mostly textual content
* minimal tables and images for initial testing

The ingestion flow reads all `.pdf` files from that folder.

---

## Start the system

Build and start the containers:

```bash
docker compose up --build -d
```

---

## Services

* FastAPI API: `http://localhost:8000`
* Swagger Docs: `http://localhost:8000/docs`
* PostgreSQL: `localhost:5432` or your configured mapped port

Health checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
```

Expected:

* API should respond successfully
* database health should show PostgreSQL connectivity
* `pgvector` should be available

---

## Verify the containers are running

```bash
docker ps
```

You should see:

* one API container
* one PostgreSQL container

You can also inspect logs:

```bash
docker compose logs -f db
docker compose logs -f api
```

Expected:

* PostgreSQL starts successfully
* FastAPI starts successfully
* no repeated errors in logs

---

## Verify sample PDFs are visible inside the API container

List the PDFs from inside the running API container:

```bash
docker exec -it semantic_rag_api sh -c "ls /app/sample_data"
```

Expected:

* your PDF filenames should be listed

You can also verify through Python:

```bash
docker exec -it semantic_rag_api python -c "from pathlib import Path; from app.core.config import settings; print([p.name for p in Path(settings.SAMPLE_DATA_DIR).glob('*.pdf')])"
```

Expected:

* a list of PDF filenames

---

## Verify the ingestion schema exists

Check that the required tables exist:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
```

Expected tables:

* `documents`
* `document_chunks`

Check that `pgvector` is enabled:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Expected:

* `vector`

### If the tables are missing

If the database was already initialized earlier, new SQL files in `initdb/` may not run automatically.

Apply the ingestion schema manually:

```bash
docker exec -i semantic_rag_db psql -U rag_user -d rag_db < initdb/002_ingestion_schema.sql
```

Then rerun the verification commands above.

---

## Run sample ingestion from inside the API container

Run the ingestion script:

```bash
docker exec -it semantic_rag_api python scripts/run_sample_ingestion.py
```

Expected output:

* number of PDFs processed
* number of pages extracted
* number of chunks created
* embedding model name
* embedding dimension
* document-level summary for each ingested PDF

A successful run confirms that the following pipeline worked:

1. PDF read from `sample_data/`
2. page text extracted
3. text cleaned
4. text split into chunks
5. embeddings generated
6. rows written to PostgreSQL

---

## Trigger ingestion through the API

You can also trigger the same ingestion flow through the API.

```bash
curl -X POST http://localhost:8000/ingest/sample
```

Or use Swagger Docs at:

```text
http://localhost:8000/docs
```

Expected:

* JSON response with ingestion summary

---

## Verify that the documents were inserted

Check how many documents were stored:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT COUNT(*) AS document_count FROM documents;"
```

List inserted documents:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT id, filename, ingest_status, page_count, language, created_at FROM documents ORDER BY id DESC;"
```

Expected:

* one row per ingested PDF
* `ingest_status` should usually be `completed`

---

## Verify that chunks were inserted

Check total chunk rows:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT COUNT(*) AS chunk_count FROM document_chunks;"
```

Preview stored chunk text:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT document_id, chunk_index, page_number, LEFT(chunk_text, 180) AS preview FROM document_chunks ORDER BY id DESC LIMIT 10;"
```

Expected:

* chunk count greater than document count
* readable text previews from the PDFs

---

## Verify that embeddings were stored

Check how many chunk rows have embeddings:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT COUNT(*) AS embedded_chunks FROM document_chunks WHERE embedding IS NOT NULL;"
```

Check embedding dimension:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT vector_dims(embedding) AS dims FROM document_chunks WHERE embedding IS NOT NULL LIMIT 5;"
```

Preview stored vectors:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT LEFT(embedding::text, 200) AS embedding_preview FROM document_chunks WHERE embedding IS NOT NULL LIMIT 3;"
```

Expected:

* embeddings should not be null
* `vector_dims(embedding)` should return `384`
* vector preview should look like numeric array data

---

## Useful verification query

See chunk counts per document:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT d.id, d.filename, COUNT(c.id) AS chunk_count FROM documents d LEFT JOIN document_chunks c ON d.id = c.document_id GROUP BY d.id, d.filename ORDER BY d.id DESC;"
```

Expected:

* each ingested document should have a non-zero chunk count

---

## What success looks like

The milestone is working correctly if all of the following are true:

* Docker containers start successfully
* health endpoints respond
* sample PDFs are visible inside the API container
* `documents` table exists
* `document_chunks` table exists
* `pgvector` extension exists
* ingestion script runs successfully
* document rows are inserted
* chunk rows are inserted
* embeddings are stored in the `embedding` column
* `vector_dims(embedding)` returns `384`
* `/ingest/sample` responds successfully

---

## Notes

* The current ingestion flow works best with text-based PDFs
* scanned or image-only PDFs may produce little or no extractable text
* repeated ingestion runs will create new rows unless deduplication is added later
* this milestone is intended to validate the complete local ingestion path before adding search and retrieval

---

## Milestone acceptance criteria

* sample PDFs can be placed in `sample_data/`
* system starts locally with Docker
* sample ingestion runs successfully
* documents are stored in PostgreSQL
* chunks are stored in PostgreSQL
* embeddings are stored in `pgvector`
* API endpoint `/ingest/sample` is available
* README provides full replication steps

---

## Stop the system

```bash
docker compose down
```

```
```

# INVAP Semantic RAG

A Dockerized FastAPI + PostgreSQL + pgvector project for PDF ingestion and semantic retrieval with project-based access control.

This milestone includes:

- PDF ingestion into PostgreSQL
- text chunking and embeddings
- pgvector-based semantic search
- project-level document access filtering
- Docker-based setup and testing

---

## Features

### Foundation
- FastAPI application
- PostgreSQL with pgvector
- Docker Compose setup
- health endpoints for API and DB connectivity

### Ingestion
- extract text from PDF files
- chunk extracted text into overlapping segments
- generate embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- store documents and chunks in PostgreSQL

### Retrieval
- embed a user query with the same embedding model
- perform semantic similarity search over stored chunk embeddings
- return:
  - document name
  - page number
  - chunk text
  - similarity score
- enforce project-based filtering so users only see documents from assigned projects

---

## Project Structure

```text
├── app
│   ├── api
│   │   ├── health.py
│   │   ├── ingest_routes.py
│   │   └── search_routes.py
│   ├── core
│   │   ├── config.py
│   │   └── database.py
│   ├── ingestion
│   │   ├── embedding_service.py
│   │   ├── ingestion_orchestrator.py
│   │   ├── pdf_text_extractor.py
│   │   └── text_chunking_service.py
│   ├── retrieval
│   │   ├── access_control_service.py
│   │   ├── query_embedding_service.py
│   │   └── vector_search_service.py
│   └── schemas
│       ├── ingest.py
│       └── search.py
├── initdb
│   ├── 001_init.sql
│   ├── 002_ingestion_schema.sql
│   └── 003_search_schema.sql
├── sample_data
├── scripts
│   ├── run_sample_search_tests.py
│   └── seed_project_access.py
├── docker-compose.yml
├── Dockerfile
└── README.md

```
## How document access works

This milestone uses **project-based access control**.

- each document belongs to exactly one project
- each user can belong to one or more projects
- ingestion assigns a document to a `project_id`
- retrieval uses `user_id` to return only documents from projects that user can access

### Important note

At this stage, ingestion is performed using `project_id`, not directly with `user_id`.

So the workflow is:

1. identify which project(s) a user belongs to
2. ingest the document into one of those projects
3. search using that `user_id`

---

## Check which projects a user can access

To see all project assignments:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT * FROM user_projects ORDER BY user_id, project_id;"

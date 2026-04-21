
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


## UI Testing Guide

### Overview

This final milestone adds a browser-based Streamlit UI on top of the existing FastAPI + PostgreSQL + pgvector backend.

The system now supports:

* PDF ingestion through the UI
* semantic search through the UI
* project-based access control
* API testing via Swagger and `curl`

The recommended test flow is:

1. start Docker services
2. seed projects and users
3. open the UI
4. upload PDF files into a selected project
5. search as a user
6. verify access control

---

## 1. Start the application

From the project root, run:

```bash
docker compose up --build
```

This starts:

* `db` → PostgreSQL + pgvector
* `api` → FastAPI backend
* `ui` → Streamlit frontend

Wait until all containers are healthy/running.

To verify:

```bash
docker compose ps
```

---

## 2. Seed sample projects and user access

If this is a fresh setup, seed the test projects and users:

```bash
docker compose exec api python scripts/seed_project_access.py
```

This creates sample project/user mappings such as:

* `user_1` → Project A
* `user_2` → Project B
* `user_admin` → Project A and Project B

---

## 3. Verify seeded projects

Optional verification:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT * FROM projects ORDER BY id;"
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT * FROM user_projects ORDER BY user_id, project_id;"
```

---

## 4. Open the applications

### FastAPI Swagger UI

Open in browser:

```text
http://localhost:8000/docs
```

You should see routes such as:

* `GET /projects`
* `POST /ingest/sample`
* `POST /ingest/upload`
* `POST /search`

### Streamlit UI

Open in browser:

```text
http://localhost:8501
```

You should see:

* **Ingest PDFs** tab
* **Search** tab

---

## 5. Test PDF ingestion from the Streamlit UI

### Ingest flow

1. Open `http://localhost:8501`
2. Go to **Ingest PDFs**
3. Select a target project from the dropdown
4. Upload one or more PDF files
5. Click **Ingest Uploaded PDFs**

### Expected behavior

* only `.pdf` files should be selectable in the browser uploader
* the backend also validates that only PDF uploads are accepted
* successful uploads should display:

  * document ID
  * project ID
  * page count
  * chunk count

### Important note

Ingestion is currently **project-based**, not directly user-based.

That means:

* you ingest documents into a project
* users assigned to that project can later retrieve those documents

---

## 6. Verify ingested documents in the database

Run:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT id, filename, project_id, ingest_status FROM documents ORDER BY id DESC LIMIT 20;"
```

Expected:

* uploaded documents appear in the `documents` table
* `project_id` matches the selected project
* `ingest_status` should be `completed`

To verify chunks:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT document_id, chunk_index, page_number FROM document_chunks ORDER BY id DESC LIMIT 20;"
```

Expected:

* chunk rows exist for newly ingested documents

---

## 7. Test semantic search from the Streamlit UI

### Search flow

1. Go to the **Search** tab in Streamlit
2. Enter a valid `user_id`
3. Enter a semantic query
4. Select `top_k`
5. Click **Search**

### Example test users

* `user_1`
* `user_2`
* `user_admin`

### Expected search output

Each result should show:

* document name
* page number
* snippet/chunk text
* similarity score
* project ID

---

## 8. Validate access control

This is one of the most important tests.

### Example scenario

* upload a PDF into **Project A**
* search with `user_1` if `user_1` belongs to Project A
* search again with `user_2` if `user_2` does not belong to Project A

### Expected result

* `user_1` should see the document
* `user_2` should **not** see the document
* `user_admin` should see it if assigned to both projects

This confirms project-based filtering works correctly.

---

## 9. Test using Swagger instead of Streamlit

### List projects

In Swagger, call:

```text
GET /projects
```

### Upload a PDF

Use:

```text
POST /ingest/upload
```

Fields:

* `project_id`
* `file`

Upload a `.pdf` file only.

### Run search

Use:

```text
POST /search
```

Example request:

```json
{
  "user_id": "user_1",
  "query": "thermal design requirements",
  "top_k": 5
}
```

---

## 10. Test using curl

### Upload a PDF

Example:

```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "project_id=1" \
  -F "file=@sample_data/your_file.pdf"
```

### Search as a user

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_1\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

### Search as another user

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_2\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

---

## 11. Recommended end-to-end validation flow

Use this sequence for a full test:

### Step A

Start Docker:

```bash
docker compose up --build
```

### Step B

Seed sample access:

```bash
docker compose exec api python scripts/seed_project_access.py
```

### Step C

Open Streamlit:

```text
http://localhost:8501
```

### Step D

Upload a PDF into Project A

### Step E

Search as `user_1`

Expected:

* uploaded document appears if query is relevant

### Step F

Search as `user_2`

Expected:

* uploaded document should not appear if `user_2` is not assigned to Project A

### Step G

Search as `user_admin`

Expected:

* document appears if relevant

---

## 12. Troubleshooting

### UI does not open

Check containers:

```bash
docker compose ps
```

### Upload fails

Make sure:

* file is actually a PDF
* selected project exists
* backend container is running

### Search returns no results

Check:

* document was ingested successfully
* chunks were created
* `project_id` is set correctly
* querying user has access to that project

### Database looks empty

Ensure seed and ingestion steps were run after startup.

---

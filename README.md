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
````

To see project names:

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT * FROM projects ORDER BY id;"
```

### Example seed mappings

* `user_1` → Project A
* `user_2` → Project B
* `user_admin` → Project A and Project B

---

## Ingest documents for a specific user

Because ingestion is project-based, you first identify the project assigned to that user.

### Example: ingest for `user_1`

If `user_1` belongs to `project_id = 1`, then ingest documents into Project A like this:

```bash
curl -X POST http://localhost:8000/ingest/sample \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":1}"
```

### Example: ingest for `user_2`

If `user_2` belongs to `project_id = 2`, then ingest documents into Project B like this:

```bash
curl -X POST http://localhost:8000/ingest/sample \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":2}"
```

### Verify which project the ingested documents were stored under

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT id, filename, project_id, ingest_status FROM documents ORDER BY id DESC LIMIT 20;"
```

### Practical interpretation

If you want to ingest a document "for user_1", that means:

* find the project(s) assigned to `user_1`
* choose one of those projects
* ingest the document into that `project_id`

---

## Retrieve documents for a specific user using Swagger

Swagger UI is available at:

```text
http://localhost:8000/docs
```

### Search using Swagger

1. Open `http://localhost:8000/docs`
2. Expand `POST /search`
3. Click **Try it out**
4. Use a request body like this:

```json
{
  "user_id": "user_1",
  "query": "thermal design requirements",
  "top_k": 5
}
```

5. Click **Execute**

### Expected behavior

* `user_1` will only receive results from documents stored under projects assigned to `user_1`
* `user_2` will only receive results from documents stored under projects assigned to `user_2`
* `user_admin` can receive results from both Project A and Project B

---

## Retrieve documents for a specific user using curl

### Example: search as `user_1`

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_1\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

### Example: search as `user_2`

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_2\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

### Example: search as `user_admin`

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_admin\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

---

## End-to-end example: ingest for a user, then retrieve for that user

### Step 1: check the user's project assignment

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT * FROM user_projects WHERE user_id = 'user_1';"
```

Suppose the output shows:

* `user_1` → `project_id = 1`

### Step 2: ingest sample PDFs into that project

```bash
curl -X POST http://localhost:8000/ingest/sample \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":1}"
```

### Step 3: verify the ingested documents

```bash
docker exec -it semantic_rag_db psql -U rag_user -d rag_db -c "SELECT id, filename, project_id FROM documents ORDER BY id DESC LIMIT 10;"
```

Expected:

* newly ingested documents should have `project_id = 1`

### Step 4: retrieve as that user

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_1\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

Expected:

* results should include only documents from Project A / `project_id = 1`

### Step 5: try another user who should not have access

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"user_2\",\"query\":\"thermal design requirements\",\"top_k\":5}"
```

Expected:

* the Project A documents ingested for `user_1` should not appear

---



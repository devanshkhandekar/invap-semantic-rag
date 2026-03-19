# Semantic RAG Foundation

This repository contains the initial local foundation setup for the semantic document search system for INVAP.

## Included in this milestone

- Dockerized local environment
- PostgreSQL with pgvector
- Basic FastAPI service
- Health check endpoints
- Local startup instructions

## Requirements

- Ubuntu 22.04 or Windows 11 + Docker Desktop + WSL2
- Docker
- Docker Compose

## Environment setup

Copy:

```bash
cp .env.example .env
```


## Start the system

```bash
docker compose up --build -d
```

## Services

- FastAPI API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432` (or your configured mapped port)
- Health Check:
    ```bash
    curl http://localhost:8000/health
    curl http://localhost:8000/health/db
    ```

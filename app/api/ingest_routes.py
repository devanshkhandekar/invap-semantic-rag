from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.ingestion.ingestion_orchestrator import IngestionOrchestrator
from app.schemas.ingest import SampleIngestRequest

router = APIRouter()


@router.get("/projects")
def list_projects():
    with engine.begin() as connection:
        rows = connection.execute(
            text("""
                SELECT id, name
                FROM projects
                ORDER BY id
            """)
        ).fetchall()

    return {
        "projects": [
            {"id": row[0], "name": row[1]}
            for row in rows
        ]
    }


@router.post("/ingest/sample")
def ingest_sample(payload: SampleIngestRequest):
    orchestrator = IngestionOrchestrator()
    result = orchestrator.ingest_directory(
        settings.SAMPLE_DATA_DIR,
        project_id=payload.project_id,
    )
    return {
        "status": "success",
        "message": "Sample ingestion completed successfully",
        "data": result,
    }


@router.post("/ingest/upload")
def ingest_uploaded_pdf(
    project_id: int = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    filename = Path(file.filename).name
    suffix = Path(filename).suffix.lower()

    allowed_content_types = {
        "application/pdf",
        "application/x-pdf",
        "binary/octet-stream",
        "application/octet-stream",
    }

    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    if file.content_type and file.content_type.lower() not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file content type: {file.content_type}. Only PDF files are allowed."
        )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}_{filename}"
    stored_path = upload_dir / stored_name

    try:
        with stored_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        orchestrator = IngestionOrchestrator()
        result = orchestrator.ingest_pdf(
            str(stored_path),
            project_id=project_id,
        )

        return {
            "status": "success",
            "message": "Uploaded PDF ingested successfully",
            "data": result,
        }

    except ValueError as exc:
        if stored_path.exists():
            stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        if stored_path.exists():
            stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Upload ingestion failed: {exc}")

    finally:
        try:
            file.file.close()
        except Exception:
            pass
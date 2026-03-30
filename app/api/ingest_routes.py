from fastapi import APIRouter
from app.core.config import settings
from app.ingestion.ingestion_orchestrator import IngestionOrchestrator

router = APIRouter()


@router.post("/ingest/sample")
def ingest_sample():
    orchestrator = IngestionOrchestrator()
    result = orchestrator.ingest_directory(settings.SAMPLE_DATA_DIR)

    return {
        "status": "success",
        "message": "Sample ingestion completed successfully",
        "data": result,
    }
from fastapi import APIRouter
from app.core.config import settings
from app.ingestion.ingestion_orchestrator import IngestionOrchestrator
from app.schemas.ingest import SampleIngestRequest

router = APIRouter()

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
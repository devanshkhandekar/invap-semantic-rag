import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.ingestion.ingestion_orchestrator import IngestionOrchestrator


def main():
    sample_dir = Path(settings.SAMPLE_DATA_DIR)

    print("===== INGESTION TEST START =====")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Configured SAMPLE_DATA_DIR: {settings.SAMPLE_DATA_DIR}")
    print(f"Resolved sample path: {sample_dir.resolve()}")
    print(f"Sample path exists: {sample_dir.exists()}")

    pdf_files = sorted(sample_dir.glob('*.pdf'))
    print(f"PDFs found: {[pdf.name for pdf in pdf_files]}")

    if not sample_dir.exists():
        raise FileNotFoundError(
            f"Sample data directory does not exist: {sample_dir.resolve()}"
        )

    orchestrator = IngestionOrchestrator()
    result = orchestrator.ingest_directory(str(sample_dir))

    print("\n===== SAMPLE INGESTION SUMMARY =====")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
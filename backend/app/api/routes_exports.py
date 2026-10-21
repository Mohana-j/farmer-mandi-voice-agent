"""Export inspection and download API endpoints."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.models import ExportRecord

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("")
def list_exports(db: Session = Depends(get_db)):
    """List all generated and verified CSV export records."""
    exports = db.query(ExportRecord).order_by(ExportRecord.created_at.desc()).all()
    return [
        {
            "export_id": e.export_id,
            "query_id": e.query_id,
            "filename": e.filename,
            "row_count": e.row_count,
            "sha256_hash": e.verification_hash,
            "is_verified": e.is_verified,
            "created_at": e.created_at.isoformat(),
        }
        for e in exports
    ]


@router.get("/{export_id}/download")
def download_export(export_id: str, db: Session = Depends(get_db)):
    """Download the verified CSV file."""
    export = db.query(ExportRecord).filter(ExportRecord.export_id == export_id).first()
    if not export:
        raise HTTPException(status_code=404, detail=f"Export '{export_id}' not found")

    file_path = Path(export.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Exported file missing from filesystem")

    return FileResponse(
        path=str(file_path),
        filename=export.filename,
        media_type="text/csv",
    )

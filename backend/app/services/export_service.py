"""Service for verified, idempotent CSV exports of market price comparisons."""

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.models import ExportRecord, MarketRecord


class ExportService:
    @staticmethod
    def prepare_export_preview(
        query_id: str,
        records: List[MarketRecord],
    ) -> Dict[str, Any]:
        """Generate metadata and preview of CSV export before human approval."""
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mandi_comparison_{query_id}_{timestamp_str}.csv"
        dest_dir = settings.get_export_path()
        file_path = str(dest_dir / filename)

        columns = [
            "Market Name",
            "Location",
            "Distance (km)",
            "Crop",
            "Grade",
            "Reported Price Min",
            "Reported Price Max",
            "Reported Modal Price",
            "Reported Unit",
            "Normalized Min (INR/kg)",
            "Normalized Max (INR/kg)",
            "Normalized Modal (INR/kg)",
            "Observation Date",
            "Freshness",
            "Source ID",
            "Source URL",
            "Data Mode",
        ]

        sample_rows = []
        for r in records[:5]:
            sample_rows.append({
                "market": r.market_name,
                "location": r.market_location,
                "distance_km": r.distance_km,
                "crop": r.crop,
                "grade": r.grade,
                "normalized_modal": r.normalized_modal_price_per_kg,
                "observation_date": r.observation_date,
                "data_mode": r.data_mode,
            })

        return {
            "query_id": query_id,
            "filename": filename,
            "destination_path": file_path,
            "columns": columns,
            "total_records": len(records),
            "sample_rows": sample_rows,
        }

    @staticmethod
    def execute_and_verify_export(
        db: Session,
        query_id: str,
        export_id: str,
        filename: str,
        records: List[MarketRecord],
    ) -> Dict[str, Any]:
        """Write CSV to disk and perform independent verification.
        
        Verification ensures:
        1. File actually exists on disk.
        2. Size is > 0 bytes.
        3. Row count matches record count + 1 header row.
        4. Hash is generated for tamper audit.
        """
        dest_dir = settings.get_export_path()
        file_path = dest_dir / filename

        headers = [
            "Market Name",
            "Location",
            "Distance (km)",
            "Crop",
            "Grade",
            "Reported Price Min",
            "Reported Price Max",
            "Reported Modal Price",
            "Reported Unit",
            "Normalized Min (INR/kg)",
            "Normalized Max (INR/kg)",
            "Normalized Modal (INR/kg)",
            "Observation Date",
            "Freshness",
            "Source ID",
            "Source URL",
            "Data Mode",
        ]

        # Write CSV safely
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for r in records:
                writer.writerow([
                    r.market_name,
                    r.market_location,
                    r.distance_km if r.distance_km is not None else "N/A",
                    r.crop,
                    r.grade,
                    r.original_price_min if r.original_price_min is not None else "N/A",
                    r.original_price_max if r.original_price_max is not None else "N/A",
                    r.original_modal_price if r.original_modal_price is not None else "N/A",
                    r.original_unit,
                    r.normalized_price_min_per_kg if r.normalized_price_min_per_kg is not None else "N/A",
                    r.normalized_price_max_per_kg if r.normalized_price_max_per_kg is not None else "N/A",
                    r.normalized_modal_price_per_kg if r.normalized_modal_price_per_kg is not None else "N/A",
                    r.observation_date,
                    r.freshness_category,
                    r.source_id,
                    r.source_url,
                    r.data_mode,
                ])

        # Independent post-execution verification
        if not file_path.exists():
            return {
                "verified": False,
                "error": f"Verification failed: exported file {file_path} was not found on filesystem."
            }

        file_size = file_path.stat().st_size
        if file_size == 0:
            return {
                "verified": False,
                "error": "Verification failed: exported CSV is empty (0 bytes)."
            }

        # Check line count
        with open(file_path, mode="r", encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        expected_lines = len(records) + 1  # header + records
        if len(lines) != expected_lines:
            return {
                "verified": False,
                "error": f"Verification failed: expected {expected_lines} lines but found {len(lines)}."
            }

        # Compute SHA-256 hash for integrity
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            hasher.update(f.read())
        file_hash = hasher.hexdigest()

        # Save record
        import json
        export_rec = ExportRecord(
            export_id=export_id,
            query_id=query_id,
            file_path=str(file_path),
            filename=filename,
            row_count=len(records),
            columns=json.dumps(headers),
            verification_hash=file_hash,
            is_verified=True,
        )
        db.add(export_rec)
        db.commit()

        return {
            "verified": True,
            "export_id": export_id,
            "filename": filename,
            "file_path": str(file_path),
            "file_size_bytes": file_size,
            "rows_written": len(records),
            "sha256_hash": file_hash,
            "verification_status": "verified_success",
            "message": f"Successfully exported and independently verified {len(records)} market records.",
        }

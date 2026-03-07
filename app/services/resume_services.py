"""Resume analysis result formatting and retrieval."""
import os
import json
from typing import Optional
from pathlib import Path


def format_result_response(job_id: str) -> Optional[dict]:
    """
    Build result response for a job_id from outputs directory.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Dict with job_id, summary, file_paths or None if not found
    """
    output_dir = Path("outputs")
    job_dir = output_dir / job_id
    if not job_dir.is_dir():
        return None
    
    file_paths = {}
    summary = None
    
    for f in job_dir.iterdir():
        if f.suffix == ".json" and "analysis" in f.name:
            try:
                with open(f, encoding="utf-8") as fp:
                    summary = json.load(fp)
            except Exception:
                pass
        elif f.is_file():
            key = f.stem.replace(" ", "_").lower()
            file_paths[key] = str(f)
    
    if not summary and not file_paths:
        return None
    
    return {
        "job_id": job_id,
        "summary": summary,
        "file_paths": file_paths or None,
    }

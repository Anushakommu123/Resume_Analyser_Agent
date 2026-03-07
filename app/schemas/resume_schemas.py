"""Pydantic models for resume analysis API."""
from pydantic import BaseModel, Field
from typing import List, Optional


class JobResultItem(BaseModel):
    """Single job analysis result in batch."""
    job_id: str = Field(..., description="Unique job identifier")
    jd_filename: Optional[str] = Field(None, description="Job description filename")
    status: str = Field(..., description="e.g. success, error")


class AnalyzeResponse(BaseModel):
    """Response for batch resume analyze."""
    batch_id: Optional[str] = Field(None, description="Batch identifier")
    total_jds: int = Field(..., description="Number of job descriptions processed")
    results: List[JobResultItem] = Field(..., description="Per-job results")
    message: str = Field(..., description="Status message")


class ResultResponse(BaseModel):
    """Response for get result by job_id."""
    job_id: str = Field(..., description="Job identifier")
    summary: Optional[dict] = Field(None, description="Analysis summary")
    file_paths: Optional[dict] = Field(None, description="Paths to generated files")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="healthy or unhealthy")
    mongodb_connected: bool = Field(..., description="Whether MongoDB is connected")

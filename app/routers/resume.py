"""API routes for resume analysis and tuning."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.services.orchestrator import Orchestrator
from app.database import db
from app.schemas.resume_schemas import AnalyzeResponse, ResultResponse, HealthResponse
from app.services.resume_services import format_result_response

router = APIRouter(prefix="/api/v1", tags=["resume"])

orchestrator = Orchestrator()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume file (PDF, DOCX, TXT, or MD)"),
    job_descriptions: List[UploadFile] = File(..., description="Up to 10 job description files")
):
    """
    Analyze resume against multiple job descriptions and generate tuned resumes.
    
    - **resume**: Resume file in PDF, DOCX, TXT, or MD format
    - **job_descriptions**: List of up to 10 job description files
    
    Returns batch processing results with job IDs for each JD.
    """
    # Validate number of JDs
    if len(job_descriptions) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one job description is required"
        )
    
    if len(job_descriptions) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 job descriptions allowed"
        )
    
    try:
        # Process resume and all JDs
        results = await orchestrator.process_resume_and_jds(resume, job_descriptions)
        
        return AnalyzeResponse(
            batch_id=results["batch_id"],
            total_jds=results["total_jds"],
            results=results["results"],
            message="Processing completed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/results/{job_id}", response_model=ResultResponse)
async def get_results(job_id: str):
    """
    Retrieve analysis results for a specific job description.
    
    - **job_id**: Unique identifier for the job analysis
    
    Returns analysis summary and file paths.
    """
    try:
        result = format_result_response(job_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Results not found for job_id: {job_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving results: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and MongoDB connection status.
    """
    try:
        # Check MongoDB connection
        mongodb_connected = (
            db.client is not None 
            and db.database is not None
        )
        if mongodb_connected:
            # Try a simple operation
            db.database.command("ping")
    except Exception:
        mongodb_connected = False
    
    return HealthResponse(
        status="healthy",
        mongodb_connected=mongodb_connected
    )


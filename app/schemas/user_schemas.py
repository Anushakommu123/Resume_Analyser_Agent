"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CodeFile(BaseModel):
    """Model for code file input."""
    path: str = Field(..., description="Path to the code file")
    content: str = Field(..., description="Content of the code file")


class TestGenerationRequest(BaseModel):
    """Request model for test generation."""
    code_files: List[CodeFile] = Field(..., description="List of code files to analyze")
    use_rag: bool = Field(True, description="Whether to use RAG for test generation")
    store_tests: bool = Field(False, description="Whether to store generated tests in vector DB")


class TestGenerationFromPathsRequest(BaseModel):
    """Request model for test generation from file paths."""
    file_paths: List[str] = Field(..., description="List of file paths to analyze")
    use_rag: bool = Field(True, description="Whether to use RAG for test generation")
    store_tests: bool = Field(False, description="Whether to store generated tests in vector DB")


class CodeSummaryResponse(BaseModel):
    """Response model for code summary."""
    files: List[str]
    endpoints: List[Dict[str, Any]]
    models: List[Dict[str, Any]]
    operations: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]


class AnalysisResponse(BaseModel):
    """Response model for analysis."""
    test_scenarios: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]
    error_cases: List[Dict[str, Any]]
    validation_requirements: List[Dict[str, Any]]
    integration_points: List[Dict[str, Any]]
    rag_used: bool
    rag_results_count: int


class TestGenerationMetadata(BaseModel):
    """Metadata for test generation."""
    files_analyzed: int
    rag_used: bool
    test_case_id: Optional[str] = None
    success: bool
    error: Optional[str] = None


class TestGenerationResponse(BaseModel):
    """Response model for test generation."""
    code_summary: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    test_code: Optional[str] = None
    metadata: TestGenerationMetadata


class TestCaseMetadata(BaseModel):
    """Metadata for a test case."""
    files: Optional[List[str]] = None
    endpoints_count: Optional[int] = None
    test_scenarios_count: Optional[int] = None
    created_at: Optional[datetime] = None


class TestCaseCreate(BaseModel):
    """Request model for creating a test case."""
    test_code: str = Field(..., description="The test code to store")
    description: str = Field(..., description="Description of the test case")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TestCaseResponse(BaseModel):
    """Response model for a test case."""
    id: str
    test_code: str
    description: str
    metadata: Dict[str, Any]
    similarity_score: Optional[float] = None


class TestCaseListResponse(BaseModel):
    """Response model for list of test cases."""
    test_cases: List[TestCaseResponse]
    total: int


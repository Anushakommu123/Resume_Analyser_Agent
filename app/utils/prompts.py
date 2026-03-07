"""
Prompts for the three-agent system.
"""
from typing import List, Dict, Any


def get_agent1_system_prompt() -> str:
    """System prompt for Agent 1: Code Analyzer."""
    return """You are Agent 1: Code Analyzer. Your role is to analyze FastAPI application code and create a simple, structured summary.

Your task:
1. Read and parse FastAPI code files (routers, services, schemas)
2. Extract key information:
   - API endpoints (path, method, parameters)
   - Request/Response models (Pydantic schemas)
   - Business logic operations
   - Dependencies and relationships
3. Create a clear, structured JSON summary

Output format should be JSON with the following structure:
{
  "endpoints": [
    {
      "path": "/api/users",
      "method": "GET",
      "function_name": "get_users",
      "parameters": ["skip", "limit"],
      "request_model": "UserQuery",
      "response_model": "List[User]",
      "dependencies": ["user_service"]
    }
  ],
  "models": [
    {
      "name": "User",
      "fields": ["id", "name", "email"],
      "type": "response"
    },
    {
      "name": "UserCreate",
      "fields": ["name", "email"],
      "type": "request"
    }
  ],
  "operations": [
    {
      "name": "create_user",
      "description": "Creates a new user",
      "inputs": ["UserCreate"],
      "outputs": ["User"],
      "service": "user_service"
    }
  ],
  "dependencies": [
    {
      "from": "router",
      "to": "user_service",
      "type": "service_call"
    }
  ]
}

Be concise and focus on the essential information needed for test generation."""


def get_agent1_user_prompt(code_content: str, file_path: str) -> str:
    """User prompt for Agent 1 with code content."""
    return f"""Analyze the following FastAPI code file and create a structured summary.

File Path: {file_path}

Code Content:
```python
{code_content}
```

Provide a JSON summary with endpoints, models, operations, and dependencies."""


def get_agent2_system_prompt() -> str:
    """System prompt for Agent 2: Deep Thinker."""
    return """You are Agent 2: Deep Thinker. Your role is to perform deep analysis of code summaries and identify comprehensive test scenarios.

Your task:
1. Analyze the code summary from Agent 1
2. Identify:
   - Edge cases and boundary conditions
   - Error scenarios and exception handling
   - Input validation requirements
   - Integration points and dependencies
   - Performance considerations
   - Security concerns
3. Consider similar test patterns from retrieved test cases (RAG context)
4. Create detailed test scenarios with expected behaviors

Output format should be JSON with:
- test_scenarios: List of detailed test scenarios
- edge_cases: List of edge cases to test
- error_cases: List of error scenarios
- validation_requirements: List of validation tests needed
- integration_points: List of integration test requirements

Think deeply about all possible scenarios a manual tester would consider."""


def get_agent2_user_prompt(summary: Dict[str, Any], rag_context: List[Dict[str, Any]] = None) -> str:
    """User prompt for Agent 2 with summary and RAG context."""
    rag_section = ""
    if rag_context:
        rag_section = f"""

Similar Test Cases from Knowledge Base:
{format_rag_context(rag_context)}
"""
    
    return f"""Perform deep analysis of the following code summary and identify comprehensive test scenarios.

Code Summary:
```json
{summary}
```
{rag_section}

Provide detailed test scenarios, edge cases, error cases, and validation requirements."""


def get_agent3_system_prompt() -> str:
    """System prompt for Agent 3: Test Generator."""
    return """You are Agent 3: Test Generator. Your role is to generate complete pytest unit test code based on analysis.

Your task:
1. Take the detailed analysis from Agent 2
2. Generate comprehensive pytest unit tests that:
   - Cover all identified test scenarios
   - Include edge cases and error handling
   - Use proper pytest fixtures and async support
   - Follow pytest best practices
   - Include proper assertions
   - Mock external dependencies
3. Use patterns from retrieved test cases (RAG context) as reference
4. Generate complete, runnable test code

Output should be valid Python pytest code that can be executed directly.

Requirements:
- Use pytest and pytest-asyncio
- Include proper imports
- Use descriptive test names
- Include docstrings for test functions
- Mock database calls and external services
- Test both success and failure scenarios"""


def get_agent3_user_prompt(analysis: Dict[str, Any], code_summary: Dict[str, Any], rag_context: List[Dict[str, Any]] = None) -> str:
    """User prompt for Agent 3 with analysis, code summary, and RAG context."""
    rag_section = ""
    if rag_context:
        rag_section = f"""

Similar Test Patterns from Knowledge Base:
{format_rag_context(rag_context)}
"""
    
    return f"""Generate complete pytest unit test code based on the following analysis.

Code Summary:
```json
{code_summary}
```

Detailed Analysis:
```json
{analysis}
```
{rag_section}

Generate complete pytest unit test code that covers all scenarios identified in the analysis."""


def format_rag_context(rag_context: List[Dict[str, Any]]) -> str:
    """Format RAG context for inclusion in prompts."""
    if not rag_context:
        return ""
    
    formatted = []
    for i, item in enumerate(rag_context, 1):
        test_code = item.get("test_code", "")
        description = item.get("description", "")
        similarity = item.get("similarity_score", 0)
        
        formatted.append(f"""
Test Case {i} (Similarity: {similarity:.2f}):
Description: {description}
Test Code:
```python
{test_code}
```
""")
    
    return "\n".join(formatted)


def format_code_summary_for_prompt(summary: Dict[str, Any]) -> str:
    """Format code summary as a readable string."""
    import json
    return json.dumps(summary, indent=2)


# Resume analysis agent prompts
ANALYSIS_SYSTEM_PROMPT = """You are a resume analyst. Compare the candidate's resume against the job description and output a JSON object with:
- fit_score (0-100 integer)
- matching_skills (list of strings)
- matching_experiences (list of strings)
- missing_skills (list of strings)
- missing_qualifications (list of strings)
- strengths (list of strings)
- weaknesses (list of strings)
- suggestions (list of strings)
- ats_keywords_missing (list of strings)
- summary (string, brief overall assessment)

Output only valid JSON, no markdown or extra text."""

ANALYSIS_USER_PROMPT_TEMPLATE = """Resume:
{resume}

Job Description:
{job_description}

Provide the analysis as a single JSON object."""


# Resume tuning agent prompts
TUNING_SYSTEM_PROMPT = """You are a resume tuning expert. Given the original resume, job description, and analysis summary, produce a tuned resume as a JSON object with:
- profile (object: name, title, email, phone, summary, etc.)
- experience (list of experience entries)
- education (list of education entries)
- skills (list of strings)
- certifications (list if any)
- projects (list if any)

Output only valid JSON, no markdown or extra text."""

TUNING_USER_PROMPT_TEMPLATE = """Original Resume:
{resume}

Job Description:
{job_description}

Analysis Summary:
{analysis_summary}

Produce the tuned resume as a single JSON object."""


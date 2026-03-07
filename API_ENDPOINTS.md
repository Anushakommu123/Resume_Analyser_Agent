# API Endpoints Reference

Base URL: `http://localhost:8000`

## Table of Contents
1. [Root Endpoints](#root-endpoints)
2. [Test Generation Endpoints](#test-generation-endpoints)
3. [Test Case Management Endpoints](#test-case-management-endpoints)
4. [MongoDB Management Endpoints](#mongodb-management-endpoints)
5. [Health Check Endpoints](#health-check-endpoints)

---

## Root Endpoints

### GET `/`
**Description:** Root endpoint with API information

**Request Body:** None

**Response:**
```json
{
  "message": "Testing Agents API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Test Generation Endpoints

### POST `/api/v1/generate-tests`
**Description:** Generate unit tests from code files using the three-agent pipeline

**Request Body:**
```json
{
  "code_files": [
    {
      "path": "app/routers/user.py",
      "content": "from fastapi import APIRouter\nrouter = APIRouter()\n..."
    }
  ],
  "use_rag": true,
  "store_tests": false
}
```

**Request Schema:**
- `code_files` (required): Array of objects with:
  - `path` (string, required): Path to the code file
  - `content` (string, required): Content of the code file
- `use_rag` (boolean, optional, default: `true`): Whether to use RAG for test generation
- `store_tests` (boolean, optional, default: `false`): Whether to store generated tests in vector DB

**Response:**
```json
{
  "code_summary": {
    "files": ["app/routers/user.py"],
    "endpoints": [...],
    "models": [...],
    "operations": [...],
    "dependencies": [...]
  },
  "analysis": {
    "test_scenarios": [...],
    "edge_cases": [...],
    "error_cases": [...],
    "validation_requirements": [...],
    "integration_points": [...],
    "rag_used": true,
    "rag_results_count": 3
  },
  "test_code": "import pytest\nfrom fastapi.testclient import TestClient\n...",
  "metadata": {
    "files_analyzed": 1,
    "rag_used": true,
    "test_case_id": null,
    "success": true,
    "error": null
  }
}
```

---

### POST `/api/v1/generate-tests-from-paths`
**Description:** Generate unit tests from file paths (reads files automatically)

**Request Body:**
```json
{
  "file_paths": [
    "app/routers/user.py",
    "app/services/user_services.py"
  ],
  "use_rag": true,
  "store_tests": false
}
```

**Request Schema:**
- `file_paths` (required): Array of file paths (strings)
- `use_rag` (boolean, optional, default: `true`): Whether to use RAG for test generation
- `store_tests` (boolean, optional, default: `false`): Whether to store generated tests in vector DB

**Response:** Same as `/api/v1/generate-tests`

---

## Test Case Management Endpoints

### POST `/api/v1/test-cases`
**Description:** Store a test case in the vector database

**Request Body:**
```json
{
  "test_code": "import pytest\n\ndef test_example():\n    assert True",
  "description": "Simple test case example",
  "metadata": {
    "endpoint": "/api/v1/users",
    "method": "GET",
    "category": "unit_test"
  }
}
```

**Request Schema:**
- `test_code` (string, required): The test code to store
- `description` (string, required): Description of the test case
- `metadata` (object, optional): Additional metadata (key-value pairs)

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "test_code": "import pytest\n\ndef test_example():\n    assert True",
  "description": "Simple test case example",
  "metadata": {
    "endpoint": "/api/v1/users",
    "method": "GET",
    "category": "unit_test"
  }
}
```

---

### GET `/api/v1/test-cases`
**Description:** Retrieve all stored test cases

**Query Parameters:**
- `limit` (integer, optional, default: `100`): Maximum number of test cases to return

**Request Body:** None

**Response:**
```json
{
  "test_cases": [
    {
      "id": "507f1f77bcf86cd799439011",
      "test_code": "import pytest\n...",
      "description": "Test case description",
      "metadata": {...},
      "similarity_score": null
    }
  ],
  "total": 1
}
```

---

### GET `/api/v1/test-cases/{test_case_id}`
**Description:** Retrieve a specific test case by ID

**Path Parameters:**
- `test_case_id` (string, required): MongoDB ObjectId of the test case

**Request Body:** None

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "test_code": "import pytest\n...",
  "description": "Test case description",
  "metadata": {...}
}
```

**Error Response (404):**
```json
{
  "detail": "Test case not found: 507f1f77bcf86cd799439011"
}
```

---

## MongoDB Management Endpoints

### GET `/api/v1/mongodb/status`
**Description:** Get MongoDB connection status

**Request Body:** None

**Response:**
```json
{
  "connected": true,
  "rag_enabled": true,
  "mongodb_uri": "mongodb://localhost:27017",
  "database_name": "testing_agents",
  "collection": "test_cases",
  "message": "MongoDB is connected. RAG features are enabled."
}
```

---

### POST `/api/v1/mongodb/reconnect`
**Description:** Manually reconnect to MongoDB

**Request Body:** None

**Response (Success):**
```json
{
  "status": "success",
  "connected": true,
  "rag_enabled": true,
  "message": "Successfully connected to MongoDB. RAG features are now ENABLED.",
  "mongodb_uri": "mongodb://localhost:27017",
  "database": "testing_agents"
}
```

**Response (Failed):**
```json
{
  "status": "failed",
  "connected": false,
  "rag_enabled": false,
  "message": "Failed to connect to MongoDB. Please check:",
  "checks": [
    "1. Is MongoDB running?",
    "2. Is MONGODB_URI correct in .env file?",
    "3. Current URI: mongodb://localhost:27017",
    "4. Can you reach MongoDB from this machine?"
  ]
}
```

---

## Health Check Endpoints

### GET `/api/v1/health`
**Description:** Health check endpoint with MongoDB and OpenAI status

**Request Body:** None

**Response:**
```json
{
  "status": "healthy",
  "service": "Testing Agents API",
  "mongodb": {
    "status": "connected",
    "uri": "mongodb://localhost:27017",
    "database": "testing_agents"
  },
  "rag_enabled": true,
  "openai_configured": true
}
```

---

## Example cURL Requests

### Generate Tests from Code Files
```bash
curl -X POST "http://localhost:8000/api/v1/generate-tests" \
  -H "Content-Type: application/json" \
  -d '{
    "code_files": [
      {
        "path": "app/routers/user.py",
        "content": "from fastapi import APIRouter\nrouter = APIRouter()"
      }
    ],
    "use_rag": true,
    "store_tests": false
  }'
```

### Generate Tests from File Paths
```bash
curl -X POST "http://localhost:8000/api/v1/generate-tests-from-paths" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["app/routers/user.py"],
    "use_rag": true,
    "store_tests": false
  }'
```

### Store Test Case
```bash
curl -X POST "http://localhost:8000/api/v1/test-cases" \
  -H "Content-Type: application/json" \
  -d '{
    "test_code": "import pytest\ndef test_example():\n    assert True",
    "description": "Example test case",
    "metadata": {"category": "unit_test"}
  }'
```

### Get All Test Cases
```bash
curl -X GET "http://localhost:8000/api/v1/test-cases?limit=10"
```

### Get Test Case by ID
```bash
curl -X GET "http://localhost:8000/api/v1/test-cases/507f1f77bcf86cd799439011"
```

### Check MongoDB Status
```bash
curl -X GET "http://localhost:8000/api/v1/mongodb/status"
```

### Reconnect to MongoDB
```bash
curl -X POST "http://localhost:8000/api/v1/mongodb/reconnect"
```

### Health Check
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly.





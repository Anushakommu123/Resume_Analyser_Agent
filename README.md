## Resume Analyser Agent API

A **FastAPI-based backend** that analyzes resumes against job descriptions and generates tuned resumes. It uses a multi-agent pipeline (analysis, tuning, and output agents) to match candidates to roles and produce tailored resume outputs.

---

## Features

- **Resume analysis**: Compare a resume against one or more job descriptions (up to 10).
- **Three-agent pipeline**: Analysis agent, tuning agent, and output agent for structured processing.
- **Multiple formats**: Accepts PDF, DOCX, TXT, and MD for resume and job descriptions.
- **Output generation**: Produces tuned resumes in Markdown and DOCX, plus analysis summaries in JSON and Markdown.
- **Health endpoints**: Check service health and MongoDB connectivity.
- **Interactive docs**: Swagger UI at `/docs`.

---

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: MongoDB (optional, for health checks)
- **LLM**: OpenAI GPT (via LangChain) for analysis and tuning

---

## Project Structure

- `main.py` – FastAPI app entrypoint.
- `app/config.py` – Configuration and environment.
- `app/database.py` – MongoDB connection.
- `app/routers/resume.py` – Resume analysis API routes.
- `app/services/` – Orchestrator, resume services.
- `app/agents/` – Analysis, tuning, output, and input processor agents.
- `app/schemas/` – Pydantic models for request/response.
- `app/utils/` – Parsers, formatters, prompts.

---

## Getting Started

### 1. Prerequisites

- Python 3.11+
- OpenAI API key
- (Optional) MongoDB for health checks

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

For full file support, also install:

```bash
pip install pypdf python-docx
```

### 3. Configure environment

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-key-here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=resume_analyser
```

### 4. Run the server

```bash
python main.py
```

Or:

```bash
uvicorn main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

---

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| POST | `/api/v1/analyze` | Analyze resume against job descriptions (resume + JDs as file uploads) |
| GET | `/api/v1/results/{job_id}` | Get analysis results for a job |
| GET | `/api/v1/health` | Health check with MongoDB status |

---
Tested Hermes AI Code Review Agent - 03/06/2026 at 03:16
## License

Add your chosen license here.

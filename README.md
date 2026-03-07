## Resume Analyser Agent API

This project is a **FastAPI-based backend** that exposes agentic workflows for analysing source code and managing generated test cases. It uses a multi-agent pipeline (analysis, tuning, and output agents) together with optional RAG (MongoDB + vector search) to **generate, store, and retrieve test code** for your services.

For detailed request/response payloads for each route, see **`API_ENDPOINTS.md`**.

---

## Features

- **Automated test generation**: Generate unit tests from raw code snippets or from file paths.
- **Three-agent pipeline**: Separate analysis, tuning, and output agents for better control over how tests are produced.
- **RAG-backed test management**: Store test cases in MongoDB and query them later for reuse.
- **Health and observability endpoints**: Check service health and MongoDB connectivity.
- **Interactive docs**: Built‑in Swagger UI at `/docs`.

---

## Tech Stack

- **Language**: Python 3.11+ (project currently targets Python 3.12)
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: MongoDB (for RAG + test case storage)
- **Vector / RAG**: Mongo-backed test case store accessed via service layer

See `requirements.txt` for the full list of Python dependencies.

---

## Project Structure

High‑level layout:

- `main.py` – FastAPI app entrypoint and router mounting.
- `app/config.py` – Configuration and environment handling.
- `app/database.py` – MongoDB connection logic.
- `app/routers/` – API route definitions (e.g. `user.py` and other domain routers).
- `app/services/` – Business logic and service layer (e.g. `user_services.py`).
- `app/agents/` – Multi‑agent pipeline components:
  - `analysis_agent.py`
  - `tuning_agent.py`
  - `output_agent.py`
  - `input_processor.py`
- `app/schemas/` – Pydantic models for request/response schemas.
- `app/utils/prompts.py` – Prompt templates used by the agents.
- `API_ENDPOINTS.md` – In‑depth API reference with examples.

---

## Getting Started

### 1. Prerequisites

- Python **3.11+** (recommended: 3.12)
- MongoDB running locally or accessible via URI
- (Optional but typical) An OpenAI or compatible LLM API key for the agents

### 2. Clone and install dependencies

```bash
git clone <this-repo-url>
cd Resume_Analyser_Agent/Resume_Analyser_Agent

python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root (same folder as `main.py`) with values appropriate for your setup, for example:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=testing_agents
MONGODB_COLLECTION=test_cases

# LLM / provider configuration (example)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1
```

Check `app/config.py` for the exact variable names used and adjust accordingly.

### 4. Run the development server

From the project root:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

- **OpenAPI / Swagger UI**: `http://localhost:8000/docs`
- **Redoc** (if enabled): `http://localhost:8000/redoc`

---

## Key Endpoints

The full list of routes and example payloads lives in `API_ENDPOINTS.md`. Some important ones:

- **Generate tests from code files**: `POST /api/v1/generate-tests`
- **Generate tests from file paths**: `POST /api/v1/generate-tests-from-paths`
- **Store a test case**: `POST /api/v1/test-cases`
- **List test cases**: `GET /api/v1/test-cases`
- **MongoDB status**: `GET /api/v1/mongodb/status`
- **API health check**: `GET /api/v1/health`

Refer to `API_ENDPOINTS.md` for request/response schemas and cURL examples.

---

## Development Notes

- **Code style**: Prefer `black` and `isort` (or the tooling already configured in your environment) for consistent formatting.
- **Testing**: Tests can be generated via the API and then integrated into your usual `pytest` or test runner setup.
- **Agents**: The multi‑agent logic is encapsulated under `app/agents/`; you can extend or swap agent implementations without changing the public API contracts.

---

## License

Add your chosen license here (e.g. MIT, Apache‑2.0). If this is private/internal, you can note that instead.


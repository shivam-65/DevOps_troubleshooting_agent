# AI Service — Incident Commander

Python-based AI investigation service using Google Gemini API for automated incident root cause analysis.

## Architecture

```
Backend (Spring Boot)            AI Service (FastAPI)            Gemini API
       │                               │                           │
       │  POST /api/investigate         │                           │
       │ ─────────────────────────────> │                           │
       │                               │                           │
       │  202 Accepted                  │                           │
       │ <───────────────────────────── │                           │
       │                               │  [Background Task]        │
       │  GET /api/adapters/*           │                           │
       │ <───────────────────────────── │                           │
       │  Evidence data                 │                           │
       │ ─────────────────────────────> │                           │
       │                               │  Analyze evidence         │
       │                               │ ─────────────────────────>│
       │                               │  Analysis result          │
       │                               │ <─────────────────────────│
       │  POST callback                │                           │
       │ <───────────────────────────── │                           │
```

## Quick Start

### 1. Install Dependencies
```bash
cd ai-service
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and set your Gemini API key:
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your-key
```

### 3. Run the Service
```bash
python src/main.py
```

Service starts on **http://localhost:8000**

### 4. API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/investigate` | Start AI investigation (returns 202) |
| GET | `/health` | Health check with Gemini + backend status |

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GEMINI_API_KEY | Yes | — | Google Gemini API key |
| GEMINI_MODEL | No | gemini-1.5-flash | Gemini model |
| BACKEND_BASE_URL | No | http://localhost:8080 | Backend API URL |
| LOG_LEVEL | No | INFO | Logging level |
| PORT | No | 8000 | Server port |

## Testing

```bash
python -m pytest tests/ -v -p no:asyncio
```

## Project Structure

```
ai-service/
├── src/
│   ├── main.py                    # FastAPI entry point
│   ├── api/
│   │   ├── routes.py              # API route definitions
│   │   └── dependencies.py        # Dependency injection
│   ├── models/
│   │   ├── requests.py            # Request models
│   │   ├── responses.py           # Response models
│   │   ├── evidence.py            # Evidence data models
│   │   └── investigation.py       # Investigation result models
│   ├── services/
│   │   ├── investigation_service.py  # Main orchestration
│   │   ├── evidence_collector.py     # Parallel evidence fetching
│   │   ├── gemini_service.py         # Gemini API integration
│   │   └── callback_service.py       # Backend callback delivery
│   ├── adapters/
│   │   ├── base_adapter.py        # Base HTTP adapter
│   │   ├── kubernetes_adapter.py  # K8s evidence
│   │   ├── logs_adapter.py        # Log evidence
│   │   ├── metrics_adapter.py     # Metrics evidence
│   │   └── git_adapter.py         # Git evidence
│   ├── prompts/
│   │   ├── system_prompt.py       # System prompt
│   │   ├── investigation_prompt.py # Prompt builder
│   │   └── output_schema.py       # Expected JSON schema
│   ├── config/
│   │   └── settings.py            # Pydantic settings
│   └── utils/
│       ├── logger.py              # Structured logging
│       └── retry.py               # Retry decorator
├── tests/
│   ├── test_api.py
│   ├── test_investigation_service.py
│   ├── test_evidence_collector.py
│   └── test_gemini_service.py
├── requirements.txt
├── .env.example
└── README.md
```

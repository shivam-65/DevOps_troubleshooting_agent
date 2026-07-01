# AI-Powered DevOps Incident Commander — AI Service Specification

> Comprehensive specification for the Python-based AI Service that performs automated incident investigation using a single-agent architecture powered by Google Gemini API.

---

## Table of Contents

1. [Tech Stack & Dependencies](#1-tech-stack--dependencies)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [API Specification](#4-api-specification)
5. [Data Models](#5-data-models)
6. [Investigation Workflow](#6-investigation-workflow)
7. [Evidence Collection](#7-evidence-collection)
8. [Single-Agent Analysis](#8-single-agent-analysis)
9. [Prompt Engineering](#9-prompt-engineering)
10. [Error Handling & Retry Logic](#10-error-handling--retry-logic)
11. [Configuration](#11-configuration)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Tech Stack & Dependencies

| Category | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Runtime |
| **Framework** | FastAPI | REST API framework |
| **LLM** | Google Gemini API (gemini-2.0-flash / gemini-2.0-pro) | AI analysis and reasoning |
| **Validation** | Pydantic v2 | Request/response validation |
| **HTTP Client** | httpx | Async HTTP calls to backend adapters |
| **Async** | asyncio | Asynchronous operations |
| **Logging** | structlog | Structured logging |
| **Environment** | python-dotenv | Environment variable management |
| **Testing** | pytest + pytest-asyncio | Unit and integration tests |
| **API Docs** | FastAPI built-in (Swagger/ReDoc) | Auto-generated API documentation |

### Dependencies (requirements.txt)

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
google-generativeai>=0.4.0
httpx>=0.27.0
structlog>=24.1.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## 2. Architecture Overview

### Single-Agent Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Spring Boot)                          │
│                                                                          │
│  1. POST /api/investigate                                                │
│     (incident details, scope, callbackUrl)                               │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI SERVICE (FastAPI)                           │
│                                                                          │
│  2. Receive request → Validate → Return 202 Accepted                     │
│                                                                          │
│  3. Background task starts:                                              │
│     ┌─────────────────────────────────────────────────────────────────┐ │
│     │                    INVESTIGATION PIPELINE                        │ │
│     │                                                                  │ │
│     │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │ │
│     │  │   COLLECT    │ →  │   ANALYZE    │ →  │   CALLBACK   │       │ │
│     │  │   EVIDENCE   │    │  (Gemini)    │    │  (Backend)   │       │ │
│     │  └──────┬───────┘    └──────────────┘    └──────────────┘       │ │
│     │         │                                                        │ │
│     │         ▼                                                        │ │
│     │  ┌──────────────────────────────────────────────────────┐       │ │
│     │  │  Call Backend Adapters (via HTTP)                    │       │ │
│     │  │  • /api/adapters/kubernetes/pod-events               │       │ │
│     │  │  • /api/adapters/logs/error-logs                     │       │ │
│     │  │  • /api/adapters/metrics/cpu                         │       │ │
│     │  │  • /api/adapters/git/recent-commits                  │       │ │
│     │  └──────────────────────────────────────────────────────┘       │ │
│     └─────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  4. Send results to callbackUrl                                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Spring Boot)                          │
│                                                                          │
│  5. POST /api/internal/investigations/{id}/callback                      │
│     (status, summary, rootCause, confidence, evidence, actions)          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Single agent**: One LLM call with all evidence — simpler, faster, cheaper than multi-agent
- **Background processing**: Investigation runs asynchronously after returning 202
- **Callback pattern**: AI Service pushes results to backend (backend doesn't poll)
- **Adapter calls**: AI Service fetches evidence from backend adapters (not embedded in request)
- **Structured output**: Gemini response parsed into typed Pydantic models

---

## 3. Directory Structure

```
ai-service/
├── src/
│   ├── main.py                           # FastAPI app entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                     # API route definitions
│   │   └── dependencies.py               # Dependency injection
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py                   # Pydantic request models
│   │   ├── responses.py                  # Pydantic response models
│   │   ├── evidence.py                   # Evidence data models
│   │   └── investigation.py              # Investigation result models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── investigation_service.py      # Main investigation orchestration
│   │   ├── evidence_collector.py         # Fetches evidence from adapters
│   │   ├── gemini_service.py             # Gemini API integration
│   │   └── callback_service.py           # Sends results to backend
│   │
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py               # Base HTTP adapter class
│   │   ├── kubernetes_adapter.py         # Kubernetes evidence fetcher
│   │   ├── logs_adapter.py               # Logs evidence fetcher
│   │   ├── metrics_adapter.py            # Metrics evidence fetcher
│   │   └── git_adapter.py                # Git evidence fetcher
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system_prompt.py              # System prompt template
│   │   ├── investigation_prompt.py       # Investigation prompt builder
│   │   └── output_schema.py              # Expected output JSON schema
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                   # Pydantic settings (env vars)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                     # Structured logging setup
│       └── retry.py                      # Retry decorator with backoff
│
├── tests/
│   ├── __init__.py
│   ├── test_investigation_service.py
│   ├── test_evidence_collector.py
│   ├── test_gemini_service.py
│   └── test_api.py
│
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

---

## 4. API Specification

**Base URL:** `http://localhost:8000`

---

### 4.1 Start Investigation

**Endpoint:** `POST /api/investigate`

**Description:** Triggers an AI-powered investigation for an incident. Returns immediately with 202 Accepted. Investigation runs in background and results are sent to callback URL.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| investigationId | string (UUID) | Yes | Unique investigation identifier |
| incidentId | string (UUID) | Yes | Parent incident identifier |
| incident | IncidentContext | Yes | Incident details for context |
| callbackUrl | string (URL) | Yes | Backend URL to receive results |
| scope | string[] | No | Evidence sources to query (default: all) |

**IncidentContext:**

| Field | Type | Description |
|---|---|---|
| title | string | Incident title |
| description | string | Incident description |
| severity | string | CRITICAL / HIGH / MEDIUM / LOW |
| affectedServices | string[] | List of affected service names |
| createdAt | string (ISO 8601) | Incident creation timestamp |

**Request Example:**

```json
{
  "investigationId": "inv-550e8400-e29b-41d4-a716-446655440000",
  "incidentId": "inc-550e8400-e29b-41d4-a716-446655440001",
  "incident": {
    "title": "Payment service latency spike",
    "description": "Payment service experiencing 5x latency increase since 10:30 AM",
    "severity": "HIGH",
    "affectedServices": ["payment-api", "checkout-service"],
    "createdAt": "2025-01-15T10:30:00Z"
  },
  "callbackUrl": "http://localhost:8080/api/internal/investigations/inv-550e8400-e29b-41d4-a716-446655440000/callback",
  "scope": ["kubernetes", "logs", "metrics", "git"]
}
```

**Response:** `202 Accepted`

```json
{
  "status": "ACCEPTED",
  "investigationId": "inv-550e8400-e29b-41d4-a716-446655440000",
  "message": "Investigation started",
  "estimatedDuration": "PT3M"
}
```

**Error Responses:**

| Status | Condition |
|---|---|
| 400 Bad Request | Invalid request body (validation error) |
| 422 Unprocessable Entity | Missing required fields |
| 500 Internal Server Error | Unexpected server error |

---

### 4.2 Health Check

**Endpoint:** `GET /health`

**Description:** Returns service health status including Gemini API connectivity.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:35:00Z",
  "components": {
    "gemini_api": {
      "status": "healthy",
      "model": "gemini-1.5-pro"
    },
    "backend_connection": {
      "status": "healthy",
      "url": "http://localhost:8080"
    }
  }
}
```

**Unhealthy Response:** `503 Service Unavailable`

```json
{
  "status": "unhealthy",
  "timestamp": "2025-01-15T10:35:00Z",
  "components": {
    "gemini_api": {
      "status": "unhealthy",
      "error": "API key invalid or quota exceeded"
    },
    "backend_connection": {
      "status": "healthy",
      "url": "http://localhost:8080"
    }
  }
}
```

---

### 4.3 API Documentation

**Endpoints:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 5. Data Models

### 5.1 Request Models

**InvestigationRequest**
- investigationId: str (UUID)
- incidentId: str (UUID)
- incident: IncidentContext
- callbackUrl: HttpUrl
- scope: list[str] = ["kubernetes", "logs", "metrics", "git"]

**IncidentContext**
- title: str
- description: str
- severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
- affectedServices: list[str]
- createdAt: datetime

### 5.2 Response Models

**InvestigationAcceptedResponse**
- status: Literal["ACCEPTED"]
- investigationId: str
- message: str
- estimatedDuration: str (ISO 8601 duration)

**HealthResponse**
- status: Literal["healthy", "unhealthy"]
- timestamp: datetime
- components: dict[str, ComponentHealth]

**ComponentHealth**
- status: Literal["healthy", "unhealthy"]
- model: str | None
- url: str | None
- error: str | None

### 5.3 Evidence Models

**Evidence**
- source: str ("kubernetes" | "logs" | "metrics" | "git")
- type: str (specific evidence type)
- data: dict[str, Any]
- collectedAt: datetime

**KubernetesEvidence**
- podEvents: list[PodEvent]
- deployments: list[DeploymentStatus]
- nodeStatus: list[NodeCondition] | None

**PodEvent**
- podName: str
- namespace: str
- status: str (Running, Pending, Failed, CrashLoopBackOff, OOMKilled, etc.)
- restarts: int
- age: str
- events: list[str]
- containers: list[ContainerStatus]

**ContainerStatus**
- name: str
- ready: bool
- restartCount: int
- state: str
- lastTerminationReason: str | None

**DeploymentStatus**
- name: str
- namespace: str
- replicas: int
- readyReplicas: int
- updatedReplicas: int
- availableReplicas: int
- conditions: list[str]

**LogsEvidence**
- errorLogs: list[LogEntry]
- applicationLogs: list[LogEntry]

**LogEntry**
- timestamp: datetime
- level: str (ERROR, WARN, INFO, DEBUG)
- service: str
- message: str
- stackTrace: str | None

**MetricsEvidence**
- cpu: list[MetricDataPoint]
- memory: list[MetricDataPoint]
- requestRate: list[MetricDataPoint]
- errorRate: list[MetricDataPoint]
- latency: LatencyMetrics

**MetricDataPoint**
- timestamp: datetime
- value: float
- service: str | None

**LatencyMetrics**
- p50: list[MetricDataPoint]
- p95: list[MetricDataPoint]
- p99: list[MetricDataPoint]

**GitEvidence**
- recentCommits: list[GitCommit]
- recentDeployments: list[GitDeployment]

**GitCommit**
- sha: str
- author: str
- message: str
- timestamp: datetime
- filesChanged: int
- additions: int
- deletions: int

**GitDeployment**
- version: str
- timestamp: datetime
- deployer: str
- environment: str
- commitSha: str

### 5.4 Investigation Result Models

**InvestigationResult**
- investigationId: str
- status: Literal["COMPLETED", "FAILED"]
- summary: str | None
- rootCause: str | None
- confidence: float | None (0.0–1.0)
- aiModelUsed: str
- evidence: list[Evidence]
- recommendedActions: list[RecommendedAction]
- error: str | None (if FAILED)
- startedAt: datetime
- completedAt: datetime

**RecommendedAction**
- type: ActionType
- title: str
- description: str
- command: str | None
- targetService: str | None
- parameters: dict[str, Any] | None
- risk: Literal["LOW", "MEDIUM", "HIGH"]
- estimatedImpact: str

**ActionType** (enum)
- RESTART_SERVICE
- SCALE_UP
- ROLLBACK_DEPLOYMENT
- RUN_SCRIPT
- APPLY_CONFIG_CHANGE
- CLEAR_CACHE
- FAILOVER
- CUSTOM

---

## 6. Investigation Workflow

### 6.1 Workflow Steps

```
1. RECEIVE REQUEST
   │
   ├── Validate request body (Pydantic)
   ├── Log investigation start
   └── Return 202 Accepted immediately
   
2. BACKGROUND TASK STARTS
   │
   ├── Update status: IN_PROGRESS
   └── Record startedAt timestamp
   
3. COLLECT EVIDENCE (parallel)
   │
   ├── Call Kubernetes adapter
   │   └── GET /api/adapters/kubernetes?services={services}&namespace={ns}
   │
   ├── Call Logs adapter
   │   └── GET /api/adapters/logs?services={services}&level=ERROR&since={time}
   │
   ├── Call Metrics adapter
   │   └── GET /api/adapters/metrics?services={services}&from={time}&to={time}
   │
   └── Call Git adapter
       └── GET /api/adapters/git?services={services}&since={time}
   
4. ANALYZE WITH GEMINI
   │
   ├── Build prompt with incident context + all evidence
   ├── Call Gemini API (gemini-2.0-flash)
   ├── Parse structured JSON response
   └── Extract: summary, rootCause, confidence, recommendedActions
   
5. SEND CALLBACK TO BACKEND
   │
   ├── POST {callbackUrl}
   │   Body: InvestigationResult
   ├── Handle callback errors (retry 3x)
   └── Log completion
   
6. COMPLETE
   │
   ├── Record completedAt timestamp
   └── Log final status
```

### 6.2 Timing Expectations

| Step | Expected Duration |
|---|---|
| Evidence collection (parallel) | 5–15 seconds |
| Gemini API call | 10–60 seconds |
| Callback to backend | 1–2 seconds |
| **Total** | **~30 seconds to 2 minutes** |

---

## 7. Evidence Collection

### 7.1 Adapter Interface

Each adapter implements:

**BaseAdapter (abstract)**
- base_url: str (backend URL)
- timeout: float (default 30s)
- async fetch(services: list[str], time_range: TimeRange) → Evidence

### 7.2 Backend Adapter Endpoints

The AI Service calls these backend endpoints to fetch evidence:

| Adapter | Backend Endpoint | Query Params |
|---|---|---|
| Kubernetes | GET /api/adapters/kubernetes | services, namespace, types (pod_events, deployments, nodes) |
| Logs | GET /api/adapters/logs | services, level, since, until, limit |
| Metrics | GET /api/adapters/metrics | services, metrics (cpu, memory, latency, error_rate), from, to, step |
| Git | GET /api/adapters/git | services, since, until, limit |

### 7.3 Evidence Collection Strategy

**Parallel fetching:**
- All 4 adapters called concurrently using `asyncio.gather()`
- Individual adapter failures don't block others
- Failed adapters return empty evidence with error logged

**Time range:**
- Default: 1 hour before incident creation to current time
- Configurable via scope parameters

**Service filtering:**
- Only fetch evidence for `affectedServices` listed in incident
- Reduces noise and API calls

### 7.4 Evidence Aggregation

After collection, evidence is aggregated into a single structure:

```
CollectedEvidence:
  - kubernetes: KubernetesEvidence | None
  - logs: LogsEvidence | None
  - metrics: MetricsEvidence | None
  - git: GitEvidence | None
  - errors: list[str]  # Any collection errors
```

---

## 8. Single-Agent Analysis

### 8.1 Gemini Service

**Model:** `gemini-2.0-flash` (or `gemini-2.0-pro` for higher quality)

**Configuration:**
- Temperature: 0.2 (low for consistent, factual output)
- Max output tokens: 4096
- Response format: JSON (structured output)

### 8.2 Analysis Flow

1. **Build prompt** — Combine system prompt + incident context + evidence
2. **Call Gemini API** — Send prompt, receive response
3. **Parse response** — Extract JSON from response, validate with Pydantic
4. **Handle errors** — Retry on transient errors, fail gracefully on persistent errors

### 8.3 Gemini API Integration

**Using google-generativeai SDK:**

- Configure API key from environment
- Create GenerativeModel instance
- Use `generate_content()` with structured prompt
- Parse response.text as JSON

**Response parsing:**
- Gemini returns text containing JSON
- Extract JSON block from response
- Validate against Pydantic model
- Handle malformed responses with retry or fallback

---

## 9. Prompt Engineering

### 9.1 System Prompt

```
You are an expert DevOps incident investigator AI. Your task is to analyze production incidents by examining evidence from multiple sources (Kubernetes, logs, metrics, Git) and determine the root cause.

You must:
1. Analyze all provided evidence carefully
2. Identify patterns and correlations across different data sources
3. Determine the most likely root cause with a confidence score
4. Recommend specific remediation actions

Your response must be valid JSON matching the exact schema provided.

Guidelines:
- Be specific about the root cause, referencing actual evidence
- Confidence score should reflect how certain you are (0.0 = no idea, 1.0 = certain)
- Recommend actionable remediation steps with specific commands when possible
- Consider the timeline of events when correlating evidence
- Prioritize actions by risk level (prefer LOW risk actions)
```

### 9.2 Investigation Prompt Template

```
## Incident Details

**Title:** {incident.title}
**Description:** {incident.description}
**Severity:** {incident.severity}
**Affected Services:** {incident.affectedServices}
**Created At:** {incident.createdAt}

## Evidence

### Kubernetes Evidence
{kubernetes_evidence_formatted}

### Logs Evidence
{logs_evidence_formatted}

### Metrics Evidence
{metrics_evidence_formatted}

### Git Evidence
{git_evidence_formatted}

## Task

Analyze the above incident and evidence. Provide your analysis in the following JSON format:

{output_schema}
```

### 9.3 Output Schema

```json
{
  "summary": "string - Brief summary of the investigation findings (2-3 sentences)",
  "rootCause": "string - Detailed explanation of the root cause with evidence references",
  "confidence": "number - Confidence score between 0.0 and 1.0",
  "reasoning": "string - Step-by-step reasoning that led to the conclusion",
  "recommendedActions": [
    {
      "type": "string - One of: RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, RUN_SCRIPT, APPLY_CONFIG_CHANGE, CLEAR_CACHE, FAILOVER, CUSTOM",
      "title": "string - Short action title",
      "description": "string - Detailed description of what this action does",
      "command": "string or null - Specific command to execute (if applicable)",
      "targetService": "string or null - Service this action targets",
      "parameters": "object or null - Additional parameters for the action",
      "risk": "string - One of: LOW, MEDIUM, HIGH",
      "estimatedImpact": "string - Expected outcome of this action"
    }
  ]
}
```

### 9.4 Evidence Formatting

**Kubernetes formatting:**
```
Pod Status:
- payment-api-7d8f9-pod1: CrashLoopBackOff (5 restarts, last terminated: OOMKilled)
- payment-api-7d8f9-pod2: Running (0 restarts)
- checkout-service-abc12: Running (0 restarts)

Deployment Status:
- payment-api: 2/3 replicas ready, 1 unavailable
- checkout-service: 3/3 replicas ready
```

**Logs formatting:**
```
Error Logs (last 1 hour):
[10:32:15] ERROR payment-api - OutOfMemoryError: Java heap space
  at com.payment.PaymentProcessor.processPayment(PaymentProcessor.java:142)
  at com.payment.PaymentController.handlePayment(PaymentController.java:58)
  
[10:32:18] ERROR payment-api - Connection pool exhausted
  at com.zaxxer.hikari.HikariPool.getConnection(HikariPool.java:155)
```

**Metrics formatting:**
```
CPU Usage (last 1 hour):
- payment-api: avg 45%, max 92% at 10:31
- checkout-service: avg 30%, max 35%

Memory Usage (last 1 hour):
- payment-api: avg 78%, max 98% at 10:31 (near OOM)
- checkout-service: avg 55%, max 60%

Error Rate:
- payment-api: 0.1% → 15% spike at 10:30
- checkout-service: 0.5% → 8% spike at 10:32
```

**Git formatting:**
```
Recent Commits (last 24 hours):
- abc1234 (10:15 AM) by john.doe: "Increase batch size for payment processing"
  Files: PaymentProcessor.java (+15, -3)
  
- def5678 (yesterday) by jane.doe: "Add new payment provider integration"
  Files: PaymentProvider.java (+200, -10), config.yml (+5, -0)

Recent Deployments:
- v2.3.1 deployed at 10:20 AM by CI/CD (commit: abc1234)
```

---

## 10. Error Handling & Retry Logic

### 10.1 Retry Strategy

**Adapter calls:**
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Retry on: Connection errors, 5xx responses, timeouts
- No retry on: 4xx responses (client errors)

**Gemini API calls:**
- Max retries: 3
- Backoff: Exponential (2s, 4s, 8s)
- Retry on: Rate limits (429), server errors (5xx), transient failures
- No retry on: Invalid API key, quota exceeded (after initial failure)

**Callback to backend:**
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Retry on: Connection errors, 5xx responses
- No retry on: 4xx responses

### 10.2 Error Scenarios

| Scenario | Handling |
|---|---|
| Adapter timeout | Log warning, continue with partial evidence |
| Adapter 5xx | Retry 3x, then continue with partial evidence |
| Adapter 4xx | Log error, continue with empty evidence for that source |
| All adapters fail | Mark investigation FAILED, callback with error |
| Gemini rate limit | Retry with backoff |
| Gemini invalid response | Retry once, then mark FAILED |
| Gemini API key invalid | Mark FAILED immediately, log critical error |
| Callback fails | Retry 3x, then log critical error (investigation results lost) |

### 10.3 Investigation Failure

When investigation fails, callback payload:

```json
{
  "investigationId": "inv-uuid",
  "status": "FAILED",
  "summary": null,
  "rootCause": null,
  "confidence": null,
  "aiModelUsed": "gemini-1.5-pro",
  "evidence": [],
  "recommendedActions": [],
  "error": "Gemini API error: Invalid API key",
  "startedAt": "2025-01-15T10:35:00Z",
  "completedAt": "2025-01-15T10:35:05Z"
}
```

### 10.4 Logging

**Structured logging with structlog:**

| Event | Level | Fields |
|---|---|---|
| Investigation started | INFO | investigationId, incidentId |
| Evidence collection started | INFO | investigationId, scope |
| Adapter call success | DEBUG | adapter, duration, recordCount |
| Adapter call failed | WARNING | adapter, error, attempt |
| Gemini call started | INFO | investigationId, model |
| Gemini call success | INFO | investigationId, duration, tokensUsed |
| Gemini call failed | ERROR | investigationId, error, attempt |
| Investigation completed | INFO | investigationId, status, duration, confidence |
| Callback sent | INFO | investigationId, callbackUrl, status |
| Callback failed | ERROR | investigationId, callbackUrl, error |

---

## 11. Configuration

### 11.1 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| GEMINI_API_KEY | Yes | — | Google Gemini API key |
| GEMINI_MODEL | No | gemini-2.0-flash | Gemini model to use |
| BACKEND_BASE_URL | No | http://localhost:8080 | Backend API base URL |
| LOG_LEVEL | No | INFO | Logging level |
| ADAPTER_TIMEOUT | No | 30 | Adapter HTTP timeout (seconds) |
| GEMINI_TIMEOUT | No | 120 | Gemini API timeout (seconds) |
| MAX_RETRIES | No | 3 | Max retry attempts |
| PORT | No | 8000 | Server port |

### 11.2 Settings Class (Pydantic Settings)

```
Settings:
  gemini_api_key: str
  gemini_model: str = "gemini-2.0-flash"
  gemini_temperature: float = 0.2
  gemini_max_tokens: int = 4096
  gemini_timeout: int = 120
  
  backend_base_url: str = "http://localhost:8080"
  adapter_timeout: int = 30
  max_retries: int = 3
  retry_backoff_base: float = 1.0
  
  log_level: str = "INFO"
  port: int = 8000
```

### 11.3 Example .env File

```
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro
BACKEND_BASE_URL=http://localhost:8080
LOG_LEVEL=DEBUG
PORT=8000
```

---

## 12. Testing Strategy

### 12.1 Test Categories

**Unit Tests:**
- Prompt building (correct formatting of evidence)
- Response parsing (JSON extraction, Pydantic validation)
- Retry logic (correct backoff, max attempts)
- Evidence aggregation

**Integration Tests:**
- Full investigation flow with mocked adapters and Gemini
- Callback delivery
- Error handling scenarios

**API Tests:**
- Request validation (valid/invalid payloads)
- Response format verification
- Health check endpoint

### 12.2 Mocking Strategy

**Adapters:**
- Mock HTTP responses for each adapter
- Test partial failures (some adapters succeed, some fail)

**Gemini API:**
- Mock successful responses with sample JSON
- Mock error responses (rate limit, invalid key, malformed output)

**Backend callback:**
- Mock callback endpoint
- Verify correct payload sent

### 12.3 Test Data

- Sample incidents with various severities
- Sample evidence for each source type
- Sample Gemini responses (valid and invalid)
- Edge cases: empty evidence, all adapters fail, Gemini timeout

### 12.4 Running Tests

```bash
cd ai-service
pytest tests/ -v --asyncio-mode=auto
```

---

## Appendix: Integration with Backend

### Backend Adapter Endpoints (to be implemented)

The backend needs to expose these endpoints for the AI Service to fetch evidence:

| Endpoint | Method | Description |
|---|---|---|
| /api/adapters/kubernetes | GET | Fetch Kubernetes evidence |
| /api/adapters/logs | GET | Fetch log evidence |
| /api/adapters/metrics | GET | Fetch metrics evidence |
| /api/adapters/git | GET | Fetch Git evidence |

These endpoints call the appropriate adapter (simulator or real) based on backend configuration.

### Callback Endpoint (already in backend spec)

```
POST /api/internal/investigations/{investigationId}/callback
```

Receives `InvestigationResult` payload from AI Service.

---

## Appendix: Sequence Diagram

```
Backend                    AI Service                 Gemini API
   │                           │                          │
   │  POST /api/investigate    │                          │
   │ ─────────────────────────>│                          │
   │                           │                          │
   │  202 Accepted             │                          │
   │ <─────────────────────────│                          │
   │                           │                          │
   │                           │ [Background Task]        │
   │                           │                          │
   │  GET /api/adapters/*      │                          │
   │ <─────────────────────────│                          │
   │                           │                          │
   │  Evidence data            │                          │
   │ ─────────────────────────>│                          │
   │                           │                          │
   │                           │  Generate content        │
   │                           │ ────────────────────────>│
   │                           │                          │
   │                           │  Analysis result         │
   │                           │ <────────────────────────│
   │                           │                          │
   │  POST /callback           │                          │
   │ <─────────────────────────│                          │
   │                           │                          │
   │  200 OK                   │                          │
   │ ─────────────────────────>│                          │
   │                           │                          │
```

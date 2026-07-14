# AI-Powered DevOps Incident Commander — MCP Server Specification

> Comprehensive specification for the MCP (Model Context Protocol) server that exposes all project tools to AI assistants (Cascade/Windsurf) via the standard MCP protocol.

---

## Table of Contents

1. [Overview & Purpose](#1-overview--purpose)
2. [Architecture](#2-architecture)
3. [Tech Stack & Dependencies](#3-tech-stack--dependencies)
4. [Directory Structure](#4-directory-structure)
5. [Configuration](#5-configuration)
6. [Windsurf/Cascade Integration](#6-windsurfcascade-integration)
7. [MCP Tool Catalog](#7-mcp-tool-catalog)
8. [Tool Specifications](#8-tool-specifications)
9. [HTTP Client Layer](#9-http-client-layer)
10. [Error Handling](#10-error-handling)
11. [Testing Strategy](#11-testing-strategy)

---

## 1. Overview & Purpose

### What is MCP?

MCP (Model Context Protocol) is a standard protocol that connects AI assistants with external tools and data sources. It enables AI assistants like Cascade/Windsurf to call tools exposed by an MCP server.

### Why MCP for This Project?

- **AI-powered incident management** — Cascade can directly create incidents, trigger investigations, view evidence, and execute remediation actions through natural conversation
- **Simulator control** — Activate/deactivate failure scenarios to test AI workflows
- **Single integration point** — One MCP server wraps all REST APIs (Backend + Simulator) into standardized tools
- **Mode switching** — Same tools work against simulator (dev/testing) or real adapters (production)

### How It Works

```
User types: "Create a high severity incident for payment-api latency"
                    ↓
Cascade (AI Assistant) detects intent → selects create_incident tool
                    ↓
MCP Protocol (stdio transport)
                    ↓
MCP Server receives tool call → makes HTTP request
                    ↓
Backend API (POST /api/incidents) → processes request
                    ↓
Response flows back: MCP Server → Cascade → User sees formatted result
```

---

## 2. Architecture

### System Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    WINDSURF / CASCADE IDE                         │
│                                                                  │
│  User: "Create incident for payment-api high CPU"                │
│  AI: Calls create_incident tool via MCP                          │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ MCP Protocol (stdio transport)
                         │ JSON-RPC over stdin/stdout
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MCP SERVER (Python)                           │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Tool        │  │ HTTP Client  │  │ Configuration          │  │
│  │ Registry    │  │ (httpx)      │  │ (env vars / .env)      │  │
│  │ 24 tools    │  │              │  │ BACKEND_URL            │  │
│  │             │  │ GET/POST/    │  │ SIMULATOR_URL          │  │
│  │ list_tools  │  │ PUT/DELETE   │  │ ADAPTER_MODE           │  │
│  │ call_tool   │  │              │  │                        │  │
│  └──────┬──────┘  └──────┬───────┘  └────────────────────────┘  │
│         │                │                                       │
│         │  Tool handler  │  HTTP requests                        │
│         │  routes call   │  to backend/simulator                 │
│         └────────────────┘                                       │
│                          │                                       │
└──────────────────────────┼──────────────────────────────────────┘
                           │
              ┌────────────┼─────────────────┐
              │            │                 │
              ▼            ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Backend API     │ │  Simulator   │ │  AI Service      │
│  :8080           │ │  :8001       │ │  :8002           │
│                  │ │              │ │                  │
│  /api/incidents  │ │  /api/       │ │  /api/investigate│
│  /api/actions    │ │  scenarios   │ │  /health         │
│  /api/adapters   │ │  /api/       │ │                  │
│  /api/reports    │ │  adapters    │ │                  │
│  /api/internal   │ │  /api/       │ │                  │
│                  │ │  services    │ │                  │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

### Transport

- **Protocol**: MCP over stdio (stdin/stdout)
- **Encoding**: JSON-RPC 2.0 messages
- **Lifecycle**: Cascade starts the MCP server as a subprocess; communication flows over stdin/stdout; server exits when Cascade terminates the process

---

## 3. Tech Stack & Dependencies

| Category | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Runtime |
| **MCP SDK** | `mcp[cli]` | MCP server framework, stdio transport |
| **HTTP Client** | `httpx` | Async HTTP calls to Backend & Simulator |
| **Config** | `pydantic-settings` | Type-safe settings from environment |
| **Env** | `python-dotenv` | Load `.env` files |

### Dependencies (requirements.txt)

```
mcp[cli]>=1.0.0
httpx>=0.27.0
pydantic>=2.6.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.0
```

---

## 4. Directory Structure

```
mcp-server/
├── src/
│   ├── main.py                  # MCP server entry point, tool routing
│   ├── config.py                # Pydantic settings (env vars)
│   ├── client.py                # Shared async HTTP client
│   └── tools/
│       ├── __init__.py
│       ├── incidents.py         # 5 tools — Incident CRUD
│       ├── investigations.py    # 4 tools — Investigation management
│       ├── evidence.py          # 4 tools — Evidence fetching
│       ├── actions.py           # 6 tools — Remediation actions
│       ├── reports.py           # 3 tools — Report generation
│       └── scenarios.py         # 7 tools — Simulator control
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. Configuration

### 5.1 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BACKEND_URL` | No | `http://localhost:8080` | Spring Boot backend base URL |
| `SIMULATOR_URL` | No | `http://localhost:8001` | Simulator base URL |
| `ADAPTER_MODE` | No | `simulator` | `simulator` or `real` — controls which evidence source is used |
| `HTTP_TIMEOUT` | No | `30` | HTTP request timeout in seconds |

### 5.2 Settings Class

```python
class Settings(BaseSettings):
    backend_url: str = "http://localhost:8080"
    simulator_url: str = "http://localhost:8001"
    adapter_mode: str = "simulator"    # "simulator" or "real"
    http_timeout: int = 30

    class Config:
        env_file = ".env"
```

### 5.3 .env.example

```env
BACKEND_URL=http://localhost:8080
SIMULATOR_URL=http://localhost:8001
ADAPTER_MODE=simulator
HTTP_TIMEOUT=30
```

---

## 6. Windsurf/Cascade Integration

### 6.1 MCP Configuration File Location

Windsurf/Cascade reads MCP server definitions from a JSON file. The location depends on scope:

| Scope | File Path |
|---|---|
| **Global (all projects)** | `~/.codeium/windsurf/mcp_config.json` |
| **Workspace (this project only)** | `<project-root>/.windsurf/mcp.json` |

> **Recommendation**: Use **workspace-level** config so the MCP server is tied to this project.

### 6.2 Workspace Configuration

Create file `.windsurf/mcp.json` in the project root:

```json
{
  "mcpServers": {
    "devops-incident-commander": {
      "command": "python",
      "args": [
        "mcp-server/src/main.py"
      ],
      "cwd": "c:\\Users\\Shivam_Padaliya\\CascadeProjects\\Ai Devops",
      "env": {
        "BACKEND_URL": "http://localhost:8080",
        "SIMULATOR_URL": "http://localhost:8001",
        "ADAPTER_MODE": "simulator"
      }
    }
  }
}
```

### 6.3 Activation Steps

1. **Install dependencies**: `cd mcp-server && pip install -r requirements.txt`
2. **Create `.windsurf/mcp.json`** as shown above
3. **Start backend services** (backend on :8080, simulator on :8001)
4. **Restart Windsurf/Cascade** (or reload MCP servers from settings)
5. **Verify**: Open Cascade chat → MCP tools icon should show 24 tools from `devops-incident-commander`

### 6.4 How Cascade Uses the Tools

Once configured, Cascade **automatically discovers** all 24 tools and their input schemas. When a user makes a request, Cascade:

1. Interprets the user's intent
2. Selects the appropriate MCP tool
3. Fills in the tool's input parameters from the conversation context
4. Calls the tool via MCP protocol
5. Receives the response and presents it to the user

**Example interactions:**

```
User: "Create a critical incident — payment service is down"
Cascade → calls create_incident(title="Payment service is down", severity="CRITICAL", affectedServices=["payment-api"])

User: "Investigate this incident"
Cascade → calls trigger_investigation(incidentId="<id from previous response>")

User: "What does the Kubernetes evidence show?"
Cascade → calls get_kubernetes_evidence(services="payment-api")

User: "Approve the restart action"
Cascade → calls approve_action(id="<action-id>", approvedBy="user")
```

---

## 7. MCP Tool Catalog

### Summary — 29 Total Tools

| Category | Count | Tools |
|---|---|---|
| **Incident Management** | 5 | create_incident, list_incidents, get_incident, update_incident, delete_incident |
| **Investigation** | 4 | trigger_investigation, list_investigations, get_investigation, get_investigation_evidence |
| **Evidence Adapters** | 4 | get_kubernetes_evidence, get_logs_evidence, get_metrics_evidence, get_git_evidence |
| **Action Management** | 6 | create_action, list_actions, get_action, approve_action, reject_action, execute_action |
| **Reports** | 3 | generate_report, list_reports, get_report |
| **Simulator Scenarios** | 5 | list_scenarios, get_scenario, activate_scenario, deactivate_scenario, create_custom_scenario |
| **Simulator Services** | 2 | list_services, add_service |

---

## 8. Tool Specifications

### 8.1 Incident Management Tools

---

#### Tool: `create_incident`

| Field | Value |
|---|---|
| **Description** | Create a new production incident |
| **Backend Endpoint** | `POST /api/incidents` |
| **Returns** | Created incident with ID, status=OPEN |

**Input Schema:**

| Param | Type | Required | Constraints | Description |
|---|---|---|---|---|
| title | string | Yes | max 255 chars | Short incident title |
| description | string | Yes | max 5000 chars | Detailed description |
| severity | string | Yes | CRITICAL, HIGH, MEDIUM, LOW | Severity level |
| affectedServices | string[] | No | — | Affected service names |
| assignee | string | No | max 100 chars | Assigned operator |
| tags | string[] | No | — | Categorization tags |

**Response format:**
```
Incident created:
  ID: <uuid>
  Title: <title>
  Severity: <severity>
  Status: OPEN
  Affected Services: <services>
  Created: <timestamp>
```

---

#### Tool: `list_incidents`

| Field | Value |
|---|---|
| **Description** | List incidents with optional filters |
| **Backend Endpoint** | `GET /api/incidents` |
| **Returns** | Paginated list of incidents |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| status | string | No | — | OPEN, INVESTIGATING, RESOLVED, CLOSED |
| severity | string | No | — | CRITICAL, HIGH, MEDIUM, LOW |
| search | string | No | — | Search in title/description |
| page | integer | No | 0 | Page number (0-indexed) |
| size | integer | No | 20 | Page size (1–100) |
| sortBy | string | No | createdAt | Sort field: createdAt, updatedAt, severity |
| sortDir | string | No | desc | asc or desc |

---

#### Tool: `get_incident`

| Field | Value |
|---|---|
| **Description** | Get full details of a single incident |
| **Backend Endpoint** | `GET /api/incidents/{id}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Incident UUID |

---

#### Tool: `update_incident`

| Field | Value |
|---|---|
| **Description** | Update an existing incident (partial update) |
| **Backend Endpoint** | `PUT /api/incidents/{id}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Incident UUID |
| title | string | No | New title |
| description | string | No | New description |
| severity | string | No | CRITICAL, HIGH, MEDIUM, LOW |
| status | string | No | OPEN, INVESTIGATING, RESOLVED, CLOSED |
| affectedServices | string[] | No | Updated services list |
| assignee | string | No | New assignee |
| tags | string[] | No | Updated tags |

**Status transition rules enforced by backend:**
- OPEN → INVESTIGATING, CLOSED
- INVESTIGATING → RESOLVED, OPEN
- RESOLVED → CLOSED, INVESTIGATING
- CLOSED → (terminal, no transitions)

---

#### Tool: `delete_incident`

| Field | Value |
|---|---|
| **Description** | Delete an incident and all related data (investigations, evidence, actions, reports) |
| **Backend Endpoint** | `DELETE /api/incidents/{id}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Incident UUID |

---

### 8.2 Investigation Tools

---

#### Tool: `trigger_investigation`

| Field | Value |
|---|---|
| **Description** | Start an AI-powered investigation for an incident |
| **Backend Endpoint** | `POST /api/incidents/{incidentId}/investigations` |
| **Returns** | Investigation record with status=PENDING; investigation runs asynchronously |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| incidentId | string | Yes | Incident UUID |
| priority | string | No | Investigation priority |
| scope | string[] | No | Evidence sources: kubernetes, logs, metrics, git |

**Behaviour:**
1. Creates Investigation record (status=PENDING)
2. Moves incident status to INVESTIGATING
3. Asynchronously calls AI Service → collects evidence → runs Gemini analysis → sends callback
4. Investigation record updated with summary, rootCause, confidence, actions

---

#### Tool: `list_investigations`

| Field | Value |
|---|---|
| **Description** | List all investigations for a specific incident |
| **Backend Endpoint** | `GET /api/incidents/{incidentId}/investigations` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| incidentId | string | Yes | Incident UUID |

---

#### Tool: `get_investigation`

| Field | Value |
|---|---|
| **Description** | Get detailed investigation results including summary, root cause, confidence, evidence, and recommended actions |
| **Backend Endpoint** | `GET /api/incidents/{incidentId}/investigations/{investigationId}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| incidentId | string | Yes | Incident UUID |
| investigationId | string | Yes | Investigation UUID |

**Response includes:** id, status, summary, rootCause, confidence, aiModelUsed, evidence[], actions[], timestamps

---

#### Tool: `get_investigation_evidence`

| Field | Value |
|---|---|
| **Description** | Get all collected evidence for a specific investigation |
| **Backend Endpoint** | `GET /api/incidents/{incidentId}/investigations/{investigationId}/evidence` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| incidentId | string | Yes | Incident UUID |
| investigationId | string | Yes | Investigation UUID |

**Response:** Array of evidence objects with source (kubernetes/logs/metrics/git), type, data, collectedAt

---

### 8.3 Evidence Adapter Tools

These tools call the backend adapter endpoints which route to simulator or real tools.

---

#### Tool: `get_kubernetes_evidence`

| Field | Value |
|---|---|
| **Description** | Fetch Kubernetes evidence: pod events, deployment status, node conditions |
| **Backend Endpoint** | `GET /api/adapters/kubernetes` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| namespace | string | No | default | Kubernetes namespace |
| types | string | No | all | pod_events, deployments, nodes |
| since | string | No | 1h ago | Start time (ISO 8601) |
| until | string | No | now | End time (ISO 8601) |

**Response:** podEvents[], deployments[], nodeStatus[]

---

#### Tool: `get_logs_evidence`

| Field | Value |
|---|---|
| **Description** | Fetch log evidence: error logs, application logs, access logs |
| **Backend Endpoint** | `GET /api/adapters/logs` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| level | string | No | all | ERROR, WARN, INFO, DEBUG |
| type | string | No | all | error, application, access |
| since | string | No | 1h ago | Start time (ISO 8601) |
| until | string | No | now | End time (ISO 8601) |
| limit | integer | No | 100 | Max entries |

**Response:** errorLogs[], applicationLogs[], accessLogs[]

---

#### Tool: `get_metrics_evidence`

| Field | Value |
|---|---|
| **Description** | Fetch metrics time-series: CPU, memory, request rate, error rate, latency percentiles |
| **Backend Endpoint** | `GET /api/adapters/metrics` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| metrics | string | No | all | cpu, memory, request_rate, error_rate, latency |
| from | string | No | 1h ago | Start time (ISO 8601) |
| to | string | No | now | End time (ISO 8601) |
| step | string | No | 1m | Data point interval: 1m, 5m, 15m |

**Response:** cpu[], memory[], requestRate[], errorRate[], latency{p50[], p95[], p99[]}

---

#### Tool: `get_git_evidence`

| Field | Value |
|---|---|
| **Description** | Fetch Git evidence: recent commits, deployments, rollbacks |
| **Backend Endpoint** | `GET /api/adapters/git` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| since | string | No | 24h ago | Start time (ISO 8601) |
| until | string | No | now | End time (ISO 8601) |
| limit | integer | No | 20 | Max entries |

**Response:** recentCommits[], recentDeployments[], rollbacks[]

---

### 8.4 Action Management Tools

---

#### Tool: `create_action`

| Field | Value |
|---|---|
| **Description** | Create a remediation action |
| **Backend Endpoint** | `POST /api/actions` |
| **Returns** | Action with status=PROPOSED |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| investigationId | string | Yes | Investigation UUID |
| incidentId | string | Yes | Incident UUID |
| type | string | Yes | RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, RUN_SCRIPT, APPLY_CONFIG_CHANGE, CLEAR_CACHE, FAILOVER, CUSTOM |
| title | string | Yes | Action title (max 255) |
| description | string | No | Detailed description (max 5000) |
| command | string | No | Command/script to execute (max 2000) |
| targetService | string | No | Target service name (max 100) |
| parameters | object | No | Additional parameters |
| risk | string | No | LOW, MEDIUM, HIGH |
| estimatedImpact | string | No | Expected outcome (max 500) |

---

#### Tool: `list_actions`

| Field | Value |
|---|---|
| **Description** | List actions with optional filters |
| **Backend Endpoint** | `GET /api/actions` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| incidentId | string | No | — | Filter by incident |
| investigationId | string | No | — | Filter by investigation |
| status | string | No | — | PROPOSED, APPROVED, EXECUTING, COMPLETED, FAILED, REJECTED |
| page | integer | No | 0 | Page number |
| size | integer | No | 20 | Page size |

---

#### Tool: `get_action`

| Field | Value |
|---|---|
| **Description** | Get full action details |
| **Backend Endpoint** | `GET /api/actions/{id}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Action UUID |

---

#### Tool: `approve_action`

| Field | Value |
|---|---|
| **Description** | Approve a proposed action for execution |
| **Backend Endpoint** | `POST /api/actions/{id}/approve` |
| **Precondition** | Action status must be PROPOSED |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Action UUID |
| approvedBy | string | Yes | Person approving |

---

#### Tool: `reject_action`

| Field | Value |
|---|---|
| **Description** | Reject a proposed or approved action |
| **Backend Endpoint** | `POST /api/actions/{id}/reject` |
| **Precondition** | Action status must be PROPOSED or APPROVED |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Action UUID |
| reason | string | No | Rejection reason |

---

#### Tool: `execute_action`

| Field | Value |
|---|---|
| **Description** | Execute an approved action |
| **Backend Endpoint** | `POST /api/actions/{id}/execute` |
| **Precondition** | Action status must be APPROVED |
| **Behaviour** | Sets status=EXECUTING, runs asynchronously, ends with COMPLETED or FAILED |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Action UUID |

---

### 8.5 Report Tools

---

#### Tool: `generate_report`

| Field | Value |
|---|---|
| **Description** | Generate an incident report aggregating all data |
| **Backend Endpoint** | `POST /api/reports` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| incidentId | string | Yes | Incident UUID |
| title | string | No | Report title (max 255) |
| format | string | No | JSON or PDF (default: JSON) |

---

#### Tool: `list_reports`

| Field | Value |
|---|---|
| **Description** | List reports with optional incident filter |
| **Backend Endpoint** | `GET /api/reports` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| incidentId | string | No | — | Filter by incident |
| page | integer | No | 0 | Page number |
| size | integer | No | 20 | Page size |

---

#### Tool: `get_report`

| Field | Value |
|---|---|
| **Description** | Get full report content |
| **Backend Endpoint** | `GET /api/reports/{id}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | Report UUID |

---

### 8.6 Simulator Control Tools

These tools call the Simulator API directly at SIMULATOR_URL.

---

#### Tool: `list_scenarios`

| Field | Value |
|---|---|
| **Description** | List all available failure scenarios and their status |
| **Simulator Endpoint** | `GET /api/scenarios` |

**Input Schema:** No required parameters

**Available scenario IDs:**
- `pod-crash` — Pod enters CrashLoopBackOff
- `oom-kill` — Memory exhaustion → OOMKilled
- `latency-spike` — Latency multiplied 3–10x
- `error-rate` — Error rate surges to 10–30%
- `deployment-failure` — Failed deployment, ImagePullBackOff

---

#### Tool: `get_scenario`

| Field | Value |
|---|---|
| **Description** | Get details of a specific scenario including affected evidence types |
| **Simulator Endpoint** | `GET /api/scenarios/{scenarioId}` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| scenarioId | string | Yes | Scenario ID (e.g., pod-crash, oom-kill) |

---

#### Tool: `activate_scenario`

| Field | Value |
|---|---|
| **Description** | Activate a failure scenario to simulate production issues |
| **Simulator Endpoint** | `POST /api/scenarios/{scenarioId}/activate` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| scenarioId | string | Yes | Scenario ID |
| targetServices | string[] | No | Services to affect (default: []) |
| parameters | object | No | Scenario-specific parameters |

---

#### Tool: `deactivate_scenario`

| Field | Value |
|---|---|
| **Description** | Deactivate an active failure scenario |
| **Simulator Endpoint** | `POST /api/scenarios/{scenarioId}/deactivate` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| scenarioId | string | Yes | Scenario ID |

---

#### Tool: `create_custom_scenario`

| Field | Value |
|---|---|
| **Description** | Create a custom failure scenario with specific effects |
| **Simulator Endpoint** | `POST /api/scenarios/custom` |

**Input Schema:**

| Param | Type | Required | Description |
|---|---|---|---|
| name | string | Yes | Scenario name |
| description | string | Yes | Scenario description |
| targetServices | string[] | No | Services to affect |
| effects | object | No | Custom effects per evidence type |
| duration | string | No | Duration (ISO 8601, e.g., PT30M) |

---

#### Tool: `list_services`

| Field | Value |
|---|---|
| **Description** | List all simulated services |
| **Simulator Endpoint** | `GET /api/services` |

**Input Schema:** No required parameters

---

#### Tool: `add_service`

| Field | Value |
|---|---|
| **Description** | Add a new service to the simulated environment |
| **Simulator Endpoint** | `POST /api/services` |

**Input Schema:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| name | string | Yes | — | Service name |
| namespace | string | No | production | Kubernetes namespace |
| replicas | integer | No | 2 | Number of replicas |
| version | string | No | v1.0.0 | Service version |
| dependencies | string[] | No | [] | Dependent services |

---

## 9. HTTP Client Layer

### 9.1 Client Design

Single shared `APIClient` class used by all tool handlers.

**Responsibilities:**
- Async HTTP calls via httpx
- Route requests to correct base URL (backend vs simulator)
- Handle timeouts, retries, error responses
- Parse JSON responses

### 9.2 Routing Rules

| Tool Category | Target | Base URL |
|---|---|---|
| Incidents, Investigations, Actions, Reports, Evidence Adapters | Backend | `BACKEND_URL` (:8080) |
| Scenarios, Simulator Services | Simulator | `SIMULATOR_URL` (:8001) |

### 9.3 Client Methods

```
GET  (endpoint, params?, base_url?) → dict
POST (endpoint, data?, base_url?)   → dict
PUT  (endpoint, data?)              → dict  (always backend)
DELETE (endpoint)                   → None  (always backend)
```

### 9.4 Error Mapping

| HTTP Status | MCP Response |
|---|---|
| 200, 201, 202 | Tool result text with formatted data |
| 400 | Error: Validation failed — {details} |
| 404 | Error: Resource not found — {id} |
| 409 | Error: Conflict — {details} |
| 422 | Error: Unprocessable — {details} |
| 500 | Error: Server error — {details} |
| Connection error | Error: Cannot connect to {service} at {url} |
| Timeout | Error: Request timed out after {timeout}s |

---

## 10. Error Handling

### 10.1 Tool-Level Error Handling

Every tool handler wraps execution in try/except and returns a descriptive error message instead of raising exceptions. MCP tools should **never crash** — they always return text content.

```python
async def some_tool(arguments: dict) -> list[TextContent]:
    try:
        result = await client.get(...)
        return [TextContent(type="text", text=format_result(result))]
    except httpx.ConnectError:
        return [TextContent(type="text", text="Error: Cannot connect to backend at http://localhost:8080. Is it running?")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error: {e.response.status_code} — {e.response.text}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### 10.2 Service Availability

If the backend or simulator is not running, tool calls return a clear message telling the user which service needs to be started. The MCP server itself should not crash.

---

## 11. Testing Strategy

### 11.1 Manual Testing

1. Start backend + simulator
2. Run MCP server: `python mcp-server/src/main.py`
3. In Cascade, use tools via natural language

### 11.2 Test Workflow

Complete end-to-end test sequence:

```
1. list_services                           → See simulated services
2. activate_scenario(oom-kill, [payment-api]) → Simulate OOM failure
3. get_kubernetes_evidence(payment-api)     → See CrashLoopBackOff pods
4. get_logs_evidence(payment-api, ERROR)    → See OOM error logs
5. get_metrics_evidence(payment-api)        → See memory spike
6. create_incident(title, description, HIGH) → Create incident
7. trigger_investigation(incidentId)         → Start AI investigation
8. get_investigation(incidentId, invId)      → See root cause analysis
9. list_actions(incidentId=...)              → See recommended actions
10. approve_action(actionId, "admin")        → Approve remediation
11. execute_action(actionId)                 → Execute remediation
12. generate_report(incidentId)              → Generate incident report
13. deactivate_scenario(oom-kill)            → Clean up
```

---

## Appendix: Quick Reference — All 29 Tools

| # | Tool Name | Method | Endpoint | Target |
|---|---|---|---|---|
| 1 | create_incident | POST | /api/incidents | Backend |
| 2 | list_incidents | GET | /api/incidents | Backend |
| 3 | get_incident | GET | /api/incidents/{id} | Backend |
| 4 | update_incident | PUT | /api/incidents/{id} | Backend |
| 5 | delete_incident | DELETE | /api/incidents/{id} | Backend |
| 6 | trigger_investigation | POST | /api/incidents/{id}/investigations | Backend |
| 7 | list_investigations | GET | /api/incidents/{id}/investigations | Backend |
| 8 | get_investigation | GET | /api/incidents/{id}/investigations/{invId} | Backend |
| 9 | get_investigation_evidence | GET | /api/incidents/{id}/investigations/{invId}/evidence | Backend |
| 10 | get_kubernetes_evidence | GET | /api/adapters/kubernetes | Backend |
| 11 | get_logs_evidence | GET | /api/adapters/logs | Backend |
| 12 | get_metrics_evidence | GET | /api/adapters/metrics | Backend |
| 13 | get_git_evidence | GET | /api/adapters/git | Backend |
| 14 | create_action | POST | /api/actions | Backend |
| 15 | list_actions | GET | /api/actions | Backend |
| 16 | get_action | GET | /api/actions/{id} | Backend |
| 17 | approve_action | POST | /api/actions/{id}/approve | Backend |
| 18 | reject_action | POST | /api/actions/{id}/reject | Backend |
| 19 | execute_action | POST | /api/actions/{id}/execute | Backend |
| 20 | generate_report | POST | /api/reports | Backend |
| 21 | list_reports | GET | /api/reports | Backend |
| 22 | get_report | GET | /api/reports/{id} | Backend |
| 23 | list_scenarios | GET | /api/scenarios | Simulator |
| 24 | get_scenario | GET | /api/scenarios/{id} | Simulator |
| 25 | activate_scenario | POST | /api/scenarios/{id}/activate | Simulator |
| 26 | deactivate_scenario | POST | /api/scenarios/{id}/deactivate | Simulator |
| 27 | create_custom_scenario | POST | /api/scenarios/custom | Simulator |
| 28 | list_services | GET | /api/services | Simulator |
| 29 | add_service | POST | /api/services | Simulator |

# AI-Powered DevOps Incident Commander — Simulator Specification

> Comprehensive specification for the Python-based Simulator service that generates realistic production failure scenarios and evidence for testing the AI-powered incident investigation system.

---

## Table of Contents

1. [Tech Stack & Dependencies](#1-tech-stack--dependencies)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [API Specification](#4-api-specification)
5. [Data Models](#5-data-models)
6. [Evidence Generators](#6-evidence-generators)
7. [Failure Scenarios](#7-failure-scenarios)
8. [Scenario Management](#8-scenario-management)
9. [In-Memory State Management](#9-in-memory-state-management)
10. [Configuration](#10-configuration)
11. [Testing Strategy](#11-testing-strategy)

---

## 1. Tech Stack & Dependencies

| Category | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Runtime |
| **Framework** | FastAPI | REST API framework |
| **Validation** | Pydantic v2 | Request/response validation |
| **Async** | asyncio | Asynchronous operations |
| **Scheduling** | APScheduler | Scenario scheduling |
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
apscheduler>=3.10.0
structlog>=24.1.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## 2. Architecture Overview

### Simulator Role in System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Spring Boot)                          │
│                                                                          │
│  Adapter Layer (mode: simulator)                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │ Kubernetes  │ │    Logs     │ │   Metrics   │ │     Git     │        │
│  │  Adapter    │ │   Adapter   │ │   Adapter   │ │   Adapter   │        │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘        │
└─────────┼───────────────┼───────────────┼───────────────┼───────────────┘
          │               │               │               │
          │    HTTP       │    HTTP       │    HTTP       │    HTTP
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SIMULATOR (FastAPI)                              │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      API ROUTES                                  │    │
│  │  /api/adapters/kubernetes  /api/adapters/logs                   │    │
│  │  /api/adapters/metrics     /api/adapters/git                    │    │
│  │  /api/scenarios/*                                                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SCENARIO SERVICE                              │    │
│  │  • Active scenario lookup                                        │    │
│  │  • Scenario scheduling                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    EVIDENCE GENERATORS                           │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │Kubernetes│ │   Logs   │ │ Metrics  │ │   Git    │            │    │
│  │  │Generator │ │Generator │ │Generator │ │Generator │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    IN-MEMORY STATE                               │    │
│  │  • Active scenarios                                              │    │
│  │  • Service registry                                              │    │
│  │  • Generated evidence cache                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Stateless evidence generation**: Evidence generated on-demand based on active scenarios
- **Scenario-driven**: Active scenarios modify the baseline "healthy" state
- **Configurable services**: Define which services exist in the simulated environment
- **Time-aware**: Evidence respects time ranges in queries
- **Realistic patterns**: Data follows realistic production patterns (not random noise)

---

## 3. Directory Structure

```
simulator/
├── src/
│   ├── main.py                           # FastAPI app entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                     # All API route definitions
│   │   ├── adapter_routes.py             # Adapter endpoints (kubernetes, logs, metrics, git)
│   │   ├── scenario_routes.py            # Scenario management endpoints
│   │   └── dependencies.py               # Dependency injection
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py                   # Pydantic request models
│   │   ├── responses.py                  # Pydantic response models
│   │   ├── kubernetes.py                 # Kubernetes data models
│   │   ├── logs.py                       # Logs data models
│   │   ├── metrics.py                    # Metrics data models
│   │   ├── git.py                        # Git data models
│   │   └── scenario.py                   # Scenario data models
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base_generator.py             # Base generator interface
│   │   ├── kubernetes_generator.py       # Kubernetes evidence generator
│   │   ├── logs_generator.py             # Logs evidence generator
│   │   ├── metrics_generator.py          # Metrics evidence generator
│   │   └── git_generator.py              # Git evidence generator
│   │
│   ├── scenarios/
│   │   ├── __init__.py
│   │   ├── base_scenario.py              # Base scenario class
│   │   ├── pod_crash_scenario.py         # Pod crash failure scenario
│   │   ├── oom_kill_scenario.py          # OOM kill scenario
│   │   ├── latency_spike_scenario.py     # Latency spike scenario
│   │   ├── error_rate_scenario.py        # Error rate surge scenario
│   │   ├── deployment_failure_scenario.py # Deployment failure scenario
│   │   └── scenario_registry.py          # Registry of all scenarios
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scenario_service.py           # Scenario lifecycle management
│   │   ├── state_service.py              # In-memory state management
│   │   └── scheduler_service.py          # Scenario scheduling
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   ├── memory_store.py               # In-memory data store
│   │   └── service_registry.py           # Simulated services registry
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                   # Pydantic settings (env vars)
│   │   └── defaults.py                   # Default services, namespaces, etc.
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                     # Structured logging setup
│       ├── time_utils.py                 # Time range helpers
│       └── random_utils.py               # Controlled randomization
│
├── tests/
│   ├── __init__.py
│   ├── test_kubernetes_generator.py
│   ├── test_logs_generator.py
│   ├── test_metrics_generator.py
│   ├── test_git_generator.py
│   ├── test_scenarios.py
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

**Base URL:** `http://localhost:8001`

---

### 4.1 Adapter Endpoints

These endpoints are called by the backend adapters to fetch simulated evidence.

---

#### GET /api/adapters/kubernetes

**Description:** Fetch simulated Kubernetes evidence (pods, deployments, nodes).

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| namespace | string | No | default | Kubernetes namespace |
| types | string | No | all | Evidence types: pod_events, deployments, nodes |
| since | string (ISO 8601) | No | 1h ago | Start time |
| until | string (ISO 8601) | No | now | End time |

**Response:** `200 OK`

```json
{
  "podEvents": [
    {
      "podName": "payment-api-7d8f9-abc12",
      "namespace": "production",
      "service": "payment-api",
      "status": "CrashLoopBackOff",
      "restarts": 5,
      "age": "PT2H30M",
      "reason": "OOMKilled",
      "message": "Container exceeded memory limit",
      "containers": [
        {
          "name": "payment-api",
          "ready": false,
          "restartCount": 5,
          "state": "waiting",
          "lastTerminationReason": "OOMKilled",
          "lastTerminationExitCode": 137
        }
      ],
      "events": [
        "Back-off restarting failed container",
        "Container payment-api exceeded memory limit"
      ],
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "deployments": [
    {
      "name": "payment-api",
      "namespace": "production",
      "replicas": 3,
      "readyReplicas": 2,
      "updatedReplicas": 3,
      "availableReplicas": 2,
      "unavailableReplicas": 1,
      "conditions": [
        "Available: True",
        "Progressing: True"
      ],
      "lastUpdateTime": "2025-01-15T10:20:00Z"
    }
  ],
  "nodeStatus": [
    {
      "name": "node-1",
      "status": "Ready",
      "conditions": [
        "Ready: True",
        "MemoryPressure: False",
        "DiskPressure: False"
      ],
      "allocatableCpu": "4",
      "allocatableMemory": "16Gi",
      "usedCpu": "2.5",
      "usedMemory": "12Gi"
    }
  ]
}
```

---

#### GET /api/adapters/logs

**Description:** Fetch simulated log entries.

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| level | string | No | all | Log levels: ERROR, WARN, INFO, DEBUG |
| type | string | No | all | Log types: error, application, access |
| since | string (ISO 8601) | No | 1h ago | Start time |
| until | string (ISO 8601) | No | now | End time |
| limit | int | No | 100 | Max entries to return |

**Response:** `200 OK`

```json
{
  "errorLogs": [
    {
      "timestamp": "2025-01-15T10:32:15Z",
      "level": "ERROR",
      "service": "payment-api",
      "logger": "com.payment.PaymentProcessor",
      "message": "OutOfMemoryError: Java heap space",
      "stackTrace": "java.lang.OutOfMemoryError: Java heap space\n\tat com.payment.PaymentProcessor.processPayment(PaymentProcessor.java:142)\n\tat com.payment.PaymentController.handlePayment(PaymentController.java:58)",
      "threadName": "http-nio-8080-exec-5",
      "traceId": "abc123def456"
    }
  ],
  "applicationLogs": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "level": "INFO",
      "service": "payment-api",
      "logger": "com.payment.PaymentService",
      "message": "Processing payment for order 12345",
      "threadName": "http-nio-8080-exec-3",
      "traceId": "xyz789"
    }
  ],
  "accessLogs": [
    {
      "timestamp": "2025-01-15T10:32:10Z",
      "service": "payment-api",
      "method": "POST",
      "path": "/api/payments",
      "statusCode": 500,
      "latencyMs": 5230,
      "clientIp": "10.0.0.15",
      "userAgent": "checkout-service/1.0"
    }
  ]
}
```

---

#### GET /api/adapters/metrics

**Description:** Fetch simulated metrics time-series data.

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| metrics | string | No | all | Metric types: cpu, memory, request_rate, error_rate, latency |
| from | string (ISO 8601) | No | 1h ago | Start time |
| to | string (ISO 8601) | No | now | End time |
| step | string | No | 1m | Data point interval (1m, 5m, 15m) |

**Response:** `200 OK`

```json
{
  "cpu": [
    {
      "service": "payment-api",
      "unit": "percent",
      "dataPoints": [
        { "timestamp": "2025-01-15T10:00:00Z", "value": 45.2 },
        { "timestamp": "2025-01-15T10:01:00Z", "value": 48.5 },
        { "timestamp": "2025-01-15T10:02:00Z", "value": 92.1 }
      ]
    }
  ],
  "memory": [
    {
      "service": "payment-api",
      "unit": "percent",
      "dataPoints": [
        { "timestamp": "2025-01-15T10:00:00Z", "value": 65.0 },
        { "timestamp": "2025-01-15T10:01:00Z", "value": 78.5 },
        { "timestamp": "2025-01-15T10:02:00Z", "value": 98.2 }
      ]
    }
  ],
  "requestRate": [
    {
      "service": "payment-api",
      "unit": "requests_per_second",
      "dataPoints": [
        { "timestamp": "2025-01-15T10:00:00Z", "value": 150.0 },
        { "timestamp": "2025-01-15T10:01:00Z", "value": 155.0 },
        { "timestamp": "2025-01-15T10:02:00Z", "value": 45.0 }
      ]
    }
  ],
  "errorRate": [
    {
      "service": "payment-api",
      "unit": "percent",
      "dataPoints": [
        { "timestamp": "2025-01-15T10:00:00Z", "value": 0.1 },
        { "timestamp": "2025-01-15T10:01:00Z", "value": 0.2 },
        { "timestamp": "2025-01-15T10:02:00Z", "value": 15.5 }
      ]
    }
  ],
  "latency": {
    "p50": [
      {
        "service": "payment-api",
        "unit": "milliseconds",
        "dataPoints": [
          { "timestamp": "2025-01-15T10:00:00Z", "value": 45.0 },
          { "timestamp": "2025-01-15T10:01:00Z", "value": 48.0 },
          { "timestamp": "2025-01-15T10:02:00Z", "value": 250.0 }
        ]
      }
    ],
    "p95": [
      {
        "service": "payment-api",
        "unit": "milliseconds",
        "dataPoints": [
          { "timestamp": "2025-01-15T10:00:00Z", "value": 120.0 },
          { "timestamp": "2025-01-15T10:01:00Z", "value": 125.0 },
          { "timestamp": "2025-01-15T10:02:00Z", "value": 850.0 }
        ]
      }
    ],
    "p99": [
      {
        "service": "payment-api",
        "unit": "milliseconds",
        "dataPoints": [
          { "timestamp": "2025-01-15T10:00:00Z", "value": 200.0 },
          { "timestamp": "2025-01-15T10:01:00Z", "value": 210.0 },
          { "timestamp": "2025-01-15T10:02:00Z", "value": 2500.0 }
        ]
      }
    ]
  }
}
```

---

#### GET /api/adapters/git

**Description:** Fetch simulated Git history (commits, deployments).

**Query Parameters:**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| services | string | No | all | Comma-separated service names |
| since | string (ISO 8601) | No | 24h ago | Start time |
| until | string (ISO 8601) | No | now | End time |
| limit | int | No | 20 | Max entries to return |

**Response:** `200 OK`

```json
{
  "recentCommits": [
    {
      "sha": "abc1234567890",
      "shortSha": "abc1234",
      "author": "john.doe",
      "authorEmail": "john.doe@company.com",
      "message": "Increase batch size for payment processing",
      "timestamp": "2025-01-15T10:15:00Z",
      "service": "payment-api",
      "filesChanged": [
        {
          "path": "src/main/java/com/payment/PaymentProcessor.java",
          "additions": 15,
          "deletions": 3,
          "changeType": "modified"
        }
      ],
      "totalAdditions": 15,
      "totalDeletions": 3
    }
  ],
  "recentDeployments": [
    {
      "id": "deploy-12345",
      "version": "v2.3.1",
      "service": "payment-api",
      "environment": "production",
      "timestamp": "2025-01-15T10:20:00Z",
      "deployer": "ci-bot",
      "commitSha": "abc1234567890",
      "status": "success",
      "duration": "PT2M30S"
    }
  ],
  "rollbacks": []
}
```

---

### 4.2 Scenario Management Endpoints

---

#### GET /api/scenarios

**Description:** List all available scenarios and their status.

**Response:** `200 OK`

```json
{
  "scenarios": [
    {
      "id": "pod-crash",
      "name": "Pod Crash Scenario",
      "description": "Simulates a pod entering CrashLoopBackOff state",
      "status": "inactive",
      "targetServices": [],
      "parameters": {}
    },
    {
      "id": "oom-kill",
      "name": "OOM Kill Scenario",
      "description": "Simulates memory exhaustion leading to OOMKilled",
      "status": "active",
      "targetServices": ["payment-api"],
      "parameters": {
        "memoryGrowthRate": "fast",
        "triggerTime": "2025-01-15T10:30:00Z"
      },
      "activatedAt": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/scenarios/{scenarioId}

**Description:** Get details of a specific scenario.

**Response:** `200 OK`

```json
{
  "id": "oom-kill",
  "name": "OOM Kill Scenario",
  "description": "Simulates memory exhaustion leading to OOMKilled",
  "status": "active",
  "targetServices": ["payment-api"],
  "parameters": {
    "memoryGrowthRate": "fast",
    "triggerTime": "2025-01-15T10:30:00Z"
  },
  "activatedAt": "2025-01-15T10:00:00Z",
  "affectedEvidence": {
    "kubernetes": ["pod_events", "deployments"],
    "logs": ["error_logs"],
    "metrics": ["memory", "error_rate"],
    "git": []
  }
}
```

---

#### POST /api/scenarios/{scenarioId}/activate

**Description:** Activate a scenario.

**Request Body:**

```json
{
  "targetServices": ["payment-api", "checkout-service"],
  "parameters": {
    "memoryGrowthRate": "fast",
    "triggerTime": "2025-01-15T10:30:00Z"
  }
}
```

**Response:** `200 OK`

```json
{
  "id": "oom-kill",
  "status": "active",
  "targetServices": ["payment-api", "checkout-service"],
  "activatedAt": "2025-01-15T10:00:00Z",
  "message": "Scenario activated successfully"
}
```

---

#### POST /api/scenarios/{scenarioId}/deactivate

**Description:** Deactivate a scenario.

**Response:** `200 OK`

```json
{
  "id": "oom-kill",
  "status": "inactive",
  "deactivatedAt": "2025-01-15T11:00:00Z",
  "message": "Scenario deactivated successfully"
}
```

---

#### POST /api/scenarios/custom

**Description:** Create a custom scenario.

**Request Body:**

```json
{
  "name": "Custom Database Connection Failure",
  "description": "Simulates database connection pool exhaustion",
  "targetServices": ["payment-api"],
  "effects": {
    "kubernetes": {
      "podStatus": "Running",
      "restarts": 0
    },
    "logs": {
      "errorPatterns": [
        "Connection pool exhausted",
        "Unable to acquire connection from pool",
        "HikariPool-1 - Connection is not available"
      ],
      "errorRate": 0.3
    },
    "metrics": {
      "errorRateSpike": 25.0,
      "latencyMultiplier": 3.0
    }
  },
  "duration": "PT30M"
}
```

**Response:** `201 Created`

```json
{
  "id": "custom-db-connection-failure",
  "name": "Custom Database Connection Failure",
  "status": "inactive",
  "message": "Custom scenario created successfully"
}
```

---

#### DELETE /api/scenarios/custom/{scenarioId}

**Description:** Delete a custom scenario.

**Response:** `204 No Content`

---

### 4.3 Service Registry Endpoints

---

#### GET /api/services

**Description:** List all simulated services.

**Response:** `200 OK`

```json
{
  "services": [
    {
      "name": "payment-api",
      "namespace": "production",
      "replicas": 3,
      "healthyReplicas": 3,
      "version": "v2.3.1",
      "dependencies": ["database", "redis", "checkout-service"]
    },
    {
      "name": "checkout-service",
      "namespace": "production",
      "replicas": 2,
      "healthyReplicas": 2,
      "version": "v1.8.0",
      "dependencies": ["payment-api", "inventory-service"]
    }
  ]
}
```

---

#### POST /api/services

**Description:** Add a new simulated service.

**Request Body:**

```json
{
  "name": "inventory-service",
  "namespace": "production",
  "replicas": 2,
  "version": "v1.0.0",
  "dependencies": ["database"]
}
```

**Response:** `201 Created`

---

#### DELETE /api/services/{serviceName}

**Description:** Remove a simulated service.

**Response:** `204 No Content`

---

### 4.4 Health Check

#### GET /health

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:35:00Z",
  "activeScenarios": 1,
  "registeredServices": 5
}
```

---

## 5. Data Models

### 5.1 Kubernetes Models

**PodEvent**
- podName: str
- namespace: str
- service: str
- status: PodStatus (enum)
- restarts: int
- age: str (ISO 8601 duration)
- reason: str | None
- message: str | None
- containers: list[ContainerStatus]
- events: list[str]
- timestamp: datetime

**PodStatus** (enum)
- Running
- Pending
- Failed
- Succeeded
- Unknown
- CrashLoopBackOff
- ImagePullBackOff
- ErrImagePull
- CreateContainerConfigError
- OOMKilled

**ContainerStatus**
- name: str
- ready: bool
- restartCount: int
- state: Literal["running", "waiting", "terminated"]
- lastTerminationReason: str | None
- lastTerminationExitCode: int | None

**DeploymentStatus**
- name: str
- namespace: str
- replicas: int
- readyReplicas: int
- updatedReplicas: int
- availableReplicas: int
- unavailableReplicas: int
- conditions: list[str]
- lastUpdateTime: datetime

**NodeStatus**
- name: str
- status: Literal["Ready", "NotReady", "Unknown"]
- conditions: list[str]
- allocatableCpu: str
- allocatableMemory: str
- usedCpu: str
- usedMemory: str

### 5.2 Logs Models

**LogEntry**
- timestamp: datetime
- level: Literal["ERROR", "WARN", "INFO", "DEBUG"]
- service: str
- logger: str
- message: str
- stackTrace: str | None
- threadName: str | None
- traceId: str | None

**AccessLogEntry**
- timestamp: datetime
- service: str
- method: str
- path: str
- statusCode: int
- latencyMs: float
- clientIp: str
- userAgent: str

### 5.3 Metrics Models

**MetricSeries**
- service: str
- unit: str
- dataPoints: list[MetricDataPoint]

**MetricDataPoint**
- timestamp: datetime
- value: float

**LatencyMetrics**
- p50: list[MetricSeries]
- p95: list[MetricSeries]
- p99: list[MetricSeries]

### 5.4 Git Models

**GitCommit**
- sha: str
- shortSha: str
- author: str
- authorEmail: str
- message: str
- timestamp: datetime
- service: str
- filesChanged: list[FileChange]
- totalAdditions: int
- totalDeletions: int

**FileChange**
- path: str
- additions: int
- deletions: int
- changeType: Literal["added", "modified", "deleted", "renamed"]

**GitDeployment**
- id: str
- version: str
- service: str
- environment: str
- timestamp: datetime
- deployer: str
- commitSha: str
- status: Literal["success", "failed", "in_progress"]
- duration: str (ISO 8601 duration)

**GitRollback**
- id: str
- fromVersion: str
- toVersion: str
- service: str
- timestamp: datetime
- initiator: str
- reason: str

### 5.5 Scenario Models

**Scenario**
- id: str
- name: str
- description: str
- status: Literal["active", "inactive"]
- targetServices: list[str]
- parameters: dict[str, Any]
- activatedAt: datetime | None
- deactivatedAt: datetime | None
- affectedEvidence: AffectedEvidence

**AffectedEvidence**
- kubernetes: list[str]
- logs: list[str]
- metrics: list[str]
- git: list[str]

**ScenarioEffect**
- kubernetes: KubernetesEffect | None
- logs: LogsEffect | None
- metrics: MetricsEffect | None
- git: GitEffect | None

---

## 6. Evidence Generators

### 6.1 Base Generator Interface

All generators implement:

**BaseGenerator (abstract)**
- generate(services: list[str], time_range: TimeRange, active_scenarios: list[Scenario]) → Evidence

### 6.2 Kubernetes Generator

**Responsibilities:**
- Generate pod events based on active scenarios
- Generate deployment status
- Generate node conditions
- Apply scenario effects (CrashLoopBackOff, OOMKilled, etc.)

**Baseline (healthy) state:**
- All pods Running with 0 restarts
- All deployments fully available
- All nodes Ready

**Scenario effects:**

| Scenario | Pod Effect | Deployment Effect |
|---|---|---|
| Pod Crash | CrashLoopBackOff, restarts++ | unavailableReplicas++ |
| OOM Kill | OOMKilled, restarts++ | unavailableReplicas++ |
| Deployment Failure | ImagePullBackOff | Progressing: False |

### 6.3 Logs Generator

**Responsibilities:**
- Generate application logs (INFO, WARN)
- Generate error logs with stack traces
- Generate access logs with status codes and latency
- Apply scenario effects (error patterns, increased error rate)

**Baseline (healthy) state:**
- Mostly INFO logs
- Occasional WARN logs
- Very few ERROR logs (< 0.1%)
- Access logs with 200/201 status codes, low latency

**Scenario effects:**

| Scenario | Log Effect |
|---|---|
| Pod Crash | ERROR logs with restart messages |
| OOM Kill | OutOfMemoryError stack traces |
| Latency Spike | Timeout errors, slow request warnings |
| Error Rate Surge | Increased ERROR logs, 5xx access logs |
| DB Connection | Connection pool exhausted errors |

**Error patterns library:**
- OutOfMemoryError (Java)
- NullPointerException (Java)
- ConnectionTimeoutException
- HikariPool connection exhausted
- Redis connection refused
- HTTP 503 Service Unavailable
- gRPC UNAVAILABLE errors

### 6.4 Metrics Generator

**Responsibilities:**
- Generate CPU time-series data
- Generate memory time-series data
- Generate request rate data
- Generate error rate data
- Generate latency percentiles (P50, P95, P99)
- Apply scenario effects (spikes, gradual increases)

**Baseline (healthy) state:**
- CPU: 30-50% with minor fluctuations
- Memory: 50-70% stable
- Request rate: Consistent with daily patterns
- Error rate: < 0.5%
- Latency: P50=50ms, P95=150ms, P99=300ms

**Scenario effects:**

| Scenario | Metric Effect |
|---|---|
| Pod Crash | Request rate drops, error rate spikes |
| OOM Kill | Memory gradual increase to 98%+, then drop |
| Latency Spike | P50/P95/P99 multiply by 3-10x |
| Error Rate Surge | Error rate jumps to 10-30% |
| CPU Saturation | CPU spikes to 90%+ |

**Time-series generation:**
- Generate data points at specified intervals (1m, 5m, 15m)
- Apply realistic noise (±5% variation)
- Apply scenario effects at trigger time
- Support gradual transitions (not instant jumps)

### 6.5 Git Generator

**Responsibilities:**
- Generate recent commits with realistic metadata
- Generate deployment history
- Generate rollback events
- Correlate commits with incident timing

**Baseline state:**
- Regular commits during business hours
- Deployments 1-2 times per day
- No rollbacks

**Scenario effects:**

| Scenario | Git Effect |
|---|---|
| Any failure | Recent commit that could be the cause |
| Deployment Failure | Failed deployment record |
| Rollback | Rollback event with reason |

**Commit message patterns:**
- "Fix bug in {component}"
- "Increase {resource} for {service}"
- "Add new feature: {feature}"
- "Refactor {component}"
- "Update dependencies"
- "Performance optimization for {operation}"

---

## 7. Failure Scenarios

### 7.1 Pre-defined Scenarios

#### Pod Crash Scenario (`pod-crash`)

**Description:** Simulates a pod entering CrashLoopBackOff state due to application crash.

**Parameters:**
- targetServices: list[str] — Services to affect
- crashReason: str — Reason for crash (default: "Error")
- restartCount: int — Number of restarts (default: 5)

**Effects:**
- **Kubernetes:** Pod status = CrashLoopBackOff, restarts = {restartCount}
- **Logs:** ERROR logs with crash messages, stack traces
- **Metrics:** Request rate drops, error rate spikes
- **Git:** No direct effect

---

#### OOM Kill Scenario (`oom-kill`)

**Description:** Simulates memory exhaustion leading to OOMKilled container.

**Parameters:**
- targetServices: list[str] — Services to affect
- memoryGrowthRate: Literal["slow", "medium", "fast"] — How quickly memory grows
- triggerTime: datetime — When OOM occurs

**Effects:**
- **Kubernetes:** Pod status = OOMKilled, container terminated with exit code 137
- **Logs:** OutOfMemoryError stack traces
- **Metrics:** Memory gradual increase to 98%, then sudden drop; error rate spike
- **Git:** Recent commit with memory-related change (e.g., "Increase batch size")

---

#### Latency Spike Scenario (`latency-spike`)

**Description:** Simulates significant latency increase in service responses.

**Parameters:**
- targetServices: list[str] — Services to affect
- latencyMultiplier: float — How much latency increases (default: 5.0)
- affectedEndpoints: list[str] — Specific endpoints (default: all)

**Effects:**
- **Kubernetes:** Pods remain Running (no crash)
- **Logs:** Timeout warnings, slow query logs
- **Metrics:** P50/P95/P99 latency multiply by {latencyMultiplier}
- **Git:** Recent commit with potential cause (e.g., "Add new database query")

---

#### Error Rate Surge Scenario (`error-rate-surge`)

**Description:** Simulates sudden increase in error responses.

**Parameters:**
- targetServices: list[str] — Services to affect
- errorRate: float — Target error rate percentage (default: 15.0)
- errorType: str — Type of error (default: "500 Internal Server Error")

**Effects:**
- **Kubernetes:** Pods remain Running
- **Logs:** Increased ERROR logs, 5xx access logs
- **Metrics:** Error rate jumps to {errorRate}%
- **Git:** Recent deployment or commit

---

#### Deployment Failure Scenario (`deployment-failure`)

**Description:** Simulates a failed deployment with pods unable to start.

**Parameters:**
- targetServices: list[str] — Services to affect
- failureReason: str — Reason for failure (default: "ImagePullBackOff")
- newVersion: str — Version being deployed

**Effects:**
- **Kubernetes:** New pods in ImagePullBackOff/Pending, deployment stuck
- **Logs:** Image pull errors, deployment timeout logs
- **Metrics:** Request rate unchanged (old pods still running) or drops (if old pods terminated)
- **Git:** Deployment record with status = "failed"

---

### 7.2 Scenario Composition

Scenarios can be combined for complex failure patterns:

**Example: Cascading Failure**
1. Activate `oom-kill` on `payment-api`
2. This causes `error-rate-surge` on `checkout-service` (dependency)
3. Results in realistic cascading failure evidence

---

## 8. Scenario Management

### 8.1 Scenario Lifecycle

```
INACTIVE ──► ACTIVE ──► INACTIVE
    │           │
    │           └── Effects applied to evidence generation
    │
    └── No effects, baseline healthy state
```

### 8.2 Scenario Service

**Responsibilities:**
- Maintain list of active scenarios
- Validate scenario activation (check target services exist)
- Apply scenario effects to generators
- Handle scenario scheduling

### 8.3 Scenario Scheduling

Using APScheduler for time-based scenario activation:

- **Immediate activation:** Scenario starts now
- **Scheduled activation:** Scenario starts at specified time
- **Duration-based:** Scenario auto-deactivates after duration
- **Recurring:** Scenario activates on schedule (for testing)

---

## 9. In-Memory State Management

### 9.1 State Store

**MemoryStore** maintains:
- Active scenarios: dict[str, Scenario]
- Service registry: dict[str, ServiceDefinition]
- Custom scenarios: dict[str, CustomScenario]
- Evidence cache: dict[str, CachedEvidence] (optional, for performance)

### 9.2 Service Registry

**Default services (pre-configured):**

| Service | Namespace | Replicas | Dependencies |
|---|---|---|---|
| payment-api | production | 3 | database, redis, checkout-service |
| checkout-service | production | 2 | payment-api, inventory-service |
| inventory-service | production | 2 | database |
| user-service | production | 2 | database, redis |
| api-gateway | production | 3 | all services |

### 9.3 State Persistence

- **No persistence** — state resets on restart
- **Optional:** Save/load state to JSON file for development convenience

---

## 10. Configuration

### 10.1 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| PORT | No | 8001 | Server port |
| LOG_LEVEL | No | INFO | Logging level |
| DEFAULT_NAMESPACE | No | production | Default Kubernetes namespace |
| EVIDENCE_TIME_RANGE | No | 1h | Default time range for evidence queries |
| METRICS_STEP | No | 1m | Default metrics data point interval |

### 10.2 Settings Class

```
Settings:
  port: int = 8001
  log_level: str = "INFO"
  default_namespace: str = "production"
  evidence_time_range: str = "1h"
  metrics_step: str = "1m"
  enable_scheduling: bool = True
```

### 10.3 Default Configuration (defaults.py)

**Default services, namespaces, error patterns, commit authors, etc.**

---

## 11. Testing Strategy

### 11.1 Test Categories

**Unit Tests:**
- Each generator produces valid output
- Scenario effects are applied correctly
- Time range filtering works
- Service filtering works

**Integration Tests:**
- Full API endpoint tests
- Scenario activation/deactivation flow
- Multiple scenarios active simultaneously

**Scenario Tests:**
- Each pre-defined scenario produces expected evidence
- Custom scenarios work correctly

### 11.2 Test Data

- Fixed seed for reproducible random generation
- Sample time ranges
- Sample service configurations

### 11.3 Running Tests

```bash
cd simulator
pytest tests/ -v
```

---

## Appendix: Integration with Backend

### Backend Adapter Configuration

When backend is in simulator mode:

```yaml
# backend/application.yml
adapters:
  mode: simulator
  simulator:
    base-url: http://localhost:8001
```

Backend adapters call:
- `GET http://localhost:8001/api/adapters/kubernetes?services={services}`
- `GET http://localhost:8001/api/adapters/logs?services={services}&level=ERROR`
- `GET http://localhost:8001/api/adapters/metrics?services={services}&from={from}&to={to}`
- `GET http://localhost:8001/api/adapters/git?services={services}`

### Testing Workflow

1. Start Simulator: `uvicorn src.main:app --port 8001`
2. Activate a scenario: `POST /api/scenarios/oom-kill/activate`
3. Start Backend (simulator mode)
4. Create incident in Frontend
5. Trigger investigation
6. AI Service fetches evidence from Backend → Backend fetches from Simulator
7. AI analyzes simulated evidence and returns recommendations

---

## Appendix: Example Scenario Activation Flow

```
1. User activates OOM Kill scenario for payment-api
   POST /api/scenarios/oom-kill/activate
   { "targetServices": ["payment-api"], "parameters": { "memoryGrowthRate": "fast" } }

2. Scenario becomes active in memory store

3. Backend requests Kubernetes evidence
   GET /api/adapters/kubernetes?services=payment-api

4. Kubernetes generator checks active scenarios
   - Finds oom-kill scenario targeting payment-api
   - Applies OOMKilled effect to pod events

5. Returns modified evidence:
   {
     "podEvents": [{
       "podName": "payment-api-xyz",
       "status": "OOMKilled",
       "restarts": 3,
       "reason": "OOMKilled",
       ...
     }]
   }

6. Similar flow for logs, metrics, git adapters
```

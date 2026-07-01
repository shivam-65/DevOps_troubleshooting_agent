# AI-Powered DevOps Incident Commander — Backend Specification

> Comprehensive backend specification for the Spring Boot service powering incident management, AI-driven investigation, automated remediation, and real-time event streaming.

---

## Table of Contents

1. [Tech Stack & Dependencies](#1-tech-stack--dependencies)
2. [Architecture Overview](#2-architecture-overview)
3. [Package Structure](#3-package-structure)
4. [Data Models & Enums](#4-data-models--enums)
5. [Database Schema](#5-database-schema)
6. [REST API Specification](#6-rest-api-specification)
7. [WebSocket Events](#7-websocket-events)
8. [Integration Contracts](#8-integration-contracts)
9. [Error Handling](#9-error-handling)
10. [Configuration](#10-configuration)
11. [Testing Strategy](#11-testing-strategy)
12. [Non-Functional Requirements](#12-non-functional-requirements)

---

## 1. Tech Stack & Dependencies

| Category | Technology | Version | Purpose |
|---|---|---|---|
| **Core Framework** | Spring Boot | 3.x | Application framework |
| **Language** | Java | 17+ | Primary language |
| **Database (MVP)** | H2 | Latest | In-memory relational DB (no installation required) |
| **Database (Prod)** | PostgreSQL | 16+ | Relational database (production) |
| **Data Access** | Spring JDBC Template | — | SQL query execution |
| **Web** | Spring Web (REST) | — | REST API endpoints |
| **HTTP Client** | WebClient (Spring WebFlux) | — | Non-blocking external HTTP calls |
| **WebSocket** | Spring WebSocket + STOMP | — | Real-time event streaming |
| **JSON** | Jackson | — | JSON serialization/deserialization |
| **Validation** | Spring Validation (jakarta.validation) | — | Request input validation |
| **Boilerplate** | Lombok | Latest | Reduce getter/setter/builder boilerplate |
| **Logging** | SLF4J + Logback | — | Structured logging |
| **API Docs** | Springdoc OpenAPI (Swagger UI) | 2.x | Auto-generated API documentation |
| **Testing** | JUnit 5, Mockito, Spring Boot Test | — | Unit + integration tests |
| **Build** | Maven | 3.9+ | Build & dependency management |

### Maven Key Dependencies (pom.xml)

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</parent>

<dependencies>
    <!-- Core -->
    <dependency>spring-boot-starter-web</dependency>
    <dependency>spring-boot-starter-websocket</dependency>
    <dependency>spring-boot-starter-validation</dependency>
    <dependency>spring-boot-starter-jdbc</dependency>
    <dependency>spring-boot-starter-webflux</dependency>  <!-- WebClient -->

    <!-- Database -->
    <dependency>com.h2database:h2 (runtime)</dependency>

    <!-- Utilities -->
    <dependency>org.projectlombok:lombok (compileOnly)</dependency>
    <dependency>org.springdoc:springdoc-openapi-starter-webmvc-ui:2.5.0</dependency>

    <!-- Testing -->
    <dependency>spring-boot-starter-test (test)</dependency>
</dependencies>
```

### Future Migration Path

- **H2 → PostgreSQL**: Replace H2 dependency with `org.postgresql:postgresql`, update `application.yml` datasource URL, driver class, and credentials. Schema DDL is written in standard SQL to ease migration.

---

## 2. Architecture Overview

### Layered Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT (React / cURL)                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP / WebSocket
┌────────────────────────────▼─────────────────────────────────────┐
│                     CONTROLLER LAYER                              │
│  IncidentController · InvestigationController · ActionController  │
│  ReportController · WebSocketEventController                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      SERVICE LAYER                                │
│  IncidentService · InvestigationService · ActionService           │
│  ReportService · EventPublisherService                            │
└──────────┬─────────────────┬─────────────────┬───────────────────┘
           │                 │                 │
┌──────────▼──────┐ ┌───────▼────────┐ ┌──────▼──────────────────┐
│ REPOSITORY LAYER│ │ INTEGRATION    │ │ ADAPTER LAYER           │
│ (Spring JDBC)   │ │ (AI Service)   │ │ (Simulator/Real Tools)  │
│                 │ │ via WebClient  │ │ KubernetesAdapter       │
│ IncidentRepo    │ │                │ │ LogsAdapter             │
│ InvestigationRep│ │ AIServiceClient│ │ MetricsAdapter          │
│ ActionRepo      │ │                │ │ GitAdapter              │
│ ReportRepo      │ │                │ │                         │
│ EvidenceRepo    │ │                │ │ ↕ ToolAdapterFactory    │
└────────┬────────┘ └───────┬────────┘ └──────────┬──────────────┘
         │                  │                      │
┌────────▼──────────────────▼──────────────────────▼──────────────┐
│                      H2 DATABASE (MVP)                           │
│              (PostgreSQL in production)                           │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Layered separation**: Controllers handle HTTP concerns only; services contain business logic; repositories handle data access.
- **Adapter pattern**: All external tool integrations (Kubernetes, Logs, Metrics, Git) implement a common `ToolAdapter` interface. A `ToolAdapterFactory` selects the correct implementation (simulator vs. real) based on configuration.
- **Event-driven updates**: Services publish domain events via `EventPublisherService`, which broadcasts over WebSocket/STOMP topics.
- **Non-blocking external calls**: `WebClient` is used for all outbound HTTP calls to the AI Service and external tool adapters.

---

## 3. Package Structure

```
com.devops.incident/
├── IncidentCommanderApplication.java        # @SpringBootApplication entry point
│
├── controller/
│   ├── IncidentController.java
│   ├── InvestigationController.java
│   ├── ActionController.java
│   └── ReportController.java
│
├── service/
│   ├── IncidentService.java
│   ├── InvestigationService.java
│   ├── ActionService.java
│   ├── ReportService.java
│   └── EventPublisherService.java
│
├── repository/
│   ├── IncidentRepository.java
│   ├── InvestigationRepository.java
│   ├── ActionRepository.java
│   ├── ReportRepository.java
│   └── EvidenceRepository.java
│
├── model/
│   ├── Incident.java
│   ├── Investigation.java
│   ├── InvestigationEvidence.java
│   ├── Action.java
│   ├── Report.java
│   ├── enums/
│   │   ├── IncidentSeverity.java
│   │   ├── IncidentStatus.java
│   │   ├── InvestigationStatus.java
│   │   ├── ActionStatus.java
│   │   ├── ActionType.java
│   │   └── ReportFormat.java
│   └── dto/
│       ├── request/
│       │   ├── CreateIncidentRequest.java
│       │   ├── UpdateIncidentRequest.java
│       │   ├── CreateActionRequest.java
│       │   └── GenerateReportRequest.java
│       └── response/
│           ├── IncidentResponse.java
│           ├── InvestigationResponse.java
│           ├── ActionResponse.java
│           ├── ReportResponse.java
│           ├── PagedResponse.java
│           └── ErrorResponse.java
│
├── adapter/
│   ├── ToolAdapter.java                     # Interface
│   ├── ToolAdapterFactory.java
│   ├── kubernetes/
│   │   ├── KubernetesAdapter.java           # Interface
│   │   ├── SimulatedKubernetesAdapter.java
│   │   └── RealKubernetesAdapter.java
│   ├── logs/
│   │   ├── LogsAdapter.java
│   │   ├── SimulatedLogsAdapter.java
│   │   └── RealLogsAdapter.java
│   ├── metrics/
│   │   ├── MetricsAdapter.java
│   │   ├── SimulatedMetricsAdapter.java
│   │   └── RealMetricsAdapter.java
│   └── git/
│       ├── GitAdapter.java
│       ├── SimulatedGitAdapter.java
│       └── RealGitAdapter.java
│
├── integration/
│   ├── AIServiceClient.java
│   ├── dto/
│   │   ├── AIInvestigationRequest.java
│   │   ├── AIInvestigationResponse.java
│   │   ├── AIEvidencePayload.java
│   │   └── AIAnalysisResult.java
│   └── SimulatorClient.java
│
├── config/
│   ├── WebSocketConfig.java
│   ├── WebClientConfig.java
│   ├── CorsConfig.java
│   ├── OpenApiConfig.java
│   └── DatabaseConfig.java
│
├── websocket/
│   └── WebSocketEventHandler.java
│
└── exception/
    ├── GlobalExceptionHandler.java
    ├── ResourceNotFoundException.java
    ├── InvalidStateTransitionException.java
    ├── AIServiceException.java
    └── AdapterException.java
```

---

## 4. Data Models & Enums

### 4.1 Enums

#### IncidentSeverity
```
CRITICAL, HIGH, MEDIUM, LOW
```

#### IncidentStatus
```
OPEN → INVESTIGATING → RESOLVED → CLOSED
```

Valid transitions:
| From | Allowed To |
|---|---|
| OPEN | INVESTIGATING, CLOSED |
| INVESTIGATING | RESOLVED, OPEN |
| RESOLVED | CLOSED, INVESTIGATING |
| CLOSED | *(terminal — no transitions)* |

#### InvestigationStatus
```
PENDING, IN_PROGRESS, COMPLETED, FAILED
```

#### ActionStatus
```
PROPOSED → APPROVED → EXECUTING → COMPLETED
                   → REJECTED
              EXECUTING → FAILED
```

#### ActionType
```
RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, RUN_SCRIPT,
APPLY_CONFIG_CHANGE, CLEAR_CACHE, FAILOVER, CUSTOM
```

#### ReportFormat
```
JSON, PDF
```

---

### 4.2 Entity Definitions

#### Incident

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | String (UUID) | PK, auto-generated | Unique identifier |
| title | String | Not blank, max 255 | Short incident title |
| description | String | Not blank, max 5000 | Detailed description |
| severity | IncidentSeverity | Not null | CRITICAL / HIGH / MEDIUM / LOW |
| status | IncidentStatus | Not null, default OPEN | Current lifecycle state |
| affectedServices | List\<String\> | — | JSON-serialized list of service names |
| assignee | String | Nullable, max 100 | Assigned operator/user |
| tags | List\<String\> | — | JSON-serialized labels/tags |
| createdAt | Instant | Auto-set | Creation timestamp (UTC) |
| updatedAt | Instant | Auto-set on modify | Last update timestamp (UTC) |
| resolvedAt | Instant | Nullable | When status moved to RESOLVED |
| closedAt | Instant | Nullable | When status moved to CLOSED |

#### Investigation

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | String (UUID) | PK, auto-generated | Unique identifier |
| incidentId | String (UUID) | FK → Incident.id, not null | Parent incident |
| status | InvestigationStatus | Not null, default PENDING | Current status |
| summary | String | Nullable, max 5000 | AI-generated summary |
| rootCause | String | Nullable, max 5000 | Identified root cause |
| confidence | Double | Nullable, 0.0–1.0 | AI confidence score |
| aiModelUsed | String | Nullable, max 100 | Model identifier |
| startedAt | Instant | Nullable | When investigation started |
| completedAt | Instant | Nullable | When investigation finished |
| createdAt | Instant | Auto-set | Creation timestamp |
| updatedAt | Instant | Auto-set on modify | Last update timestamp |

#### InvestigationEvidence

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | String (UUID) | PK, auto-generated | Unique identifier |
| investigationId | String (UUID) | FK → Investigation.id, not null | Parent investigation |
| source | String | Not blank, max 100 | Source system (e.g., "kubernetes", "logs") |
| type | String | Not blank, max 100 | Evidence type (e.g., "pod_events", "error_log") |
| data | String (TEXT) | Not null | JSON-serialized evidence payload |
| collectedAt | Instant | Auto-set | Collection timestamp |

#### Action

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | String (UUID) | PK, auto-generated | Unique identifier |
| investigationId | String (UUID) | FK → Investigation.id, not null | Parent investigation |
| incidentId | String (UUID) | FK → Incident.id, not null | Associated incident |
| type | ActionType | Not null | Remediation action type |
| status | ActionStatus | Not null, default PROPOSED | Current action status |
| title | String | Not blank, max 255 | Action title |
| description | String | Nullable, max 5000 | Detailed description |
| command | String | Nullable, max 2000 | Command/script to execute |
| targetService | String | Nullable, max 100 | Service this action targets |
| parameters | String (TEXT) | Nullable | JSON-serialized parameters |
| risk | String | Nullable, max 50 | Risk level: LOW / MEDIUM / HIGH |
| estimatedImpact | String | Nullable, max 500 | Expected outcome description |
| executionResult | String (TEXT) | Nullable | JSON-serialized execution output |
| approvedBy | String | Nullable, max 100 | Who approved |
| approvedAt | Instant | Nullable | Approval timestamp |
| executedAt | Instant | Nullable | Execution timestamp |
| completedAt | Instant | Nullable | Completion timestamp |
| createdAt | Instant | Auto-set | Creation timestamp |
| updatedAt | Instant | Auto-set on modify | Last update timestamp |

#### Report

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | String (UUID) | PK, auto-generated | Unique identifier |
| incidentId | String (UUID) | FK → Incident.id, not null | Associated incident |
| title | String | Not blank, max 255 | Report title |
| content | String (TEXT) | Not null | Full report content (Markdown/HTML) |
| format | ReportFormat | Not null, default JSON | Export format |
| metadata | String (TEXT) | Nullable | JSON-serialized metadata (duration, severity, services, etc.) |
| generatedAt | Instant | Auto-set | Generation timestamp |
| createdAt | Instant | Auto-set | Creation timestamp |

---

## 5. Database Schema

All timestamps stored as `TIMESTAMP` (ISO 8601 UTC). JSON arrays/objects stored as `CLOB`/`TEXT`.

```sql
-- ============================================================
-- INCIDENTS
-- ============================================================
CREATE TABLE incidents (
    id                VARCHAR(36)   PRIMARY KEY,
    title             VARCHAR(255)  NOT NULL,
    description       VARCHAR(5000) NOT NULL,
    severity          VARCHAR(20)   NOT NULL,       -- CRITICAL, HIGH, MEDIUM, LOW
    status            VARCHAR(20)   NOT NULL DEFAULT 'OPEN',
    affected_services CLOB,                          -- JSON array
    assignee          VARCHAR(100),
    tags              CLOB,                          -- JSON array
    created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at       TIMESTAMP,
    closed_at         TIMESTAMP
);

CREATE INDEX idx_incidents_status   ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_created  ON incidents(created_at);

-- ============================================================
-- INVESTIGATIONS
-- ============================================================
CREATE TABLE investigations (
    id              VARCHAR(36)   PRIMARY KEY,
    incident_id     VARCHAR(36)   NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    summary         VARCHAR(5000),
    root_cause      VARCHAR(5000),
    confidence      DOUBLE,
    ai_model_used   VARCHAR(100),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);

CREATE INDEX idx_investigations_incident ON investigations(incident_id);
CREATE INDEX idx_investigations_status   ON investigations(status);

-- ============================================================
-- INVESTIGATION EVIDENCE
-- ============================================================
CREATE TABLE investigation_evidence (
    id                VARCHAR(36)   PRIMARY KEY,
    investigation_id  VARCHAR(36)   NOT NULL,
    source            VARCHAR(100)  NOT NULL,
    type              VARCHAR(100)  NOT NULL,
    data              CLOB          NOT NULL,
    collected_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
);

CREATE INDEX idx_evidence_investigation ON investigation_evidence(investigation_id);

-- ============================================================
-- ACTIONS
-- ============================================================
CREATE TABLE actions (
    id                VARCHAR(36)   PRIMARY KEY,
    investigation_id  VARCHAR(36)   NOT NULL,
    incident_id       VARCHAR(36)   NOT NULL,
    type              VARCHAR(30)   NOT NULL,
    status            VARCHAR(20)   NOT NULL DEFAULT 'PROPOSED',
    title             VARCHAR(255)  NOT NULL,
    description       VARCHAR(5000),
    command           VARCHAR(2000),
    target_service    VARCHAR(100),
    parameters        CLOB,
    risk              VARCHAR(50),
    estimated_impact  VARCHAR(500),
    execution_result  CLOB,
    approved_by       VARCHAR(100),
    approved_at       TIMESTAMP,
    executed_at       TIMESTAMP,
    completed_at      TIMESTAMP,
    created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
    FOREIGN KEY (incident_id)      REFERENCES incidents(id)      ON DELETE CASCADE
);

CREATE INDEX idx_actions_investigation ON actions(investigation_id);
CREATE INDEX idx_actions_incident      ON actions(incident_id);
CREATE INDEX idx_actions_status        ON actions(status);

-- ============================================================
-- REPORTS
-- ============================================================
CREATE TABLE reports (
    id            VARCHAR(36)   PRIMARY KEY,
    incident_id   VARCHAR(36)   NOT NULL,
    title         VARCHAR(255)  NOT NULL,
    content       CLOB          NOT NULL,
    format        VARCHAR(10)   NOT NULL DEFAULT 'JSON',
    metadata      CLOB,
    generated_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_incident ON reports(incident_id);
```

### Relationships

```
Incident (1) ──── (N) Investigation
Investigation (1) ──── (N) InvestigationEvidence
Investigation (1) ──── (N) Action
Incident (1) ──── (N) Action       (denormalized for quick lookup)
Incident (1) ──── (N) Report
```

### PostgreSQL Migration Notes

| H2 Feature | PostgreSQL Equivalent |
|---|---|
| `CLOB` | `TEXT` |
| `VARCHAR(36)` for UUID | `UUID` native type |
| `DOUBLE` | `DOUBLE PRECISION` |
| `CURRENT_TIMESTAMP` default | Same syntax |
| Auto-init via `schema.sql` | Flyway / Liquibase migrations |

---

## 6. REST API Specification

**Base URL:** `http://localhost:8080/api`
**Content-Type:** `application/json`

---

### 6.1 Incidents — `/api/incidents`

#### `POST /api/incidents` — Create Incident

**Request Body:**
```json
{
  "title": "Payment service latency spike",
  "description": "Payment service experiencing 5x latency increase",
  "severity": "HIGH",
  "affectedServices": ["payment-api", "checkout-service"],
  "assignee": "john.doe",
  "tags": ["payment", "latency"]
}
```

**Validation:**
- `title` — required, max 255 chars
- `description` — required, max 5000 chars
- `severity` — required, one of: CRITICAL, HIGH, MEDIUM, LOW
- `affectedServices` — optional, list of strings
- `assignee` — optional, max 100 chars
- `tags` — optional, list of strings

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Payment service latency spike",
  "description": "Payment service experiencing 5x latency increase",
  "severity": "HIGH",
  "status": "OPEN",
  "affectedServices": ["payment-api", "checkout-service"],
  "assignee": "john.doe",
  "tags": ["payment", "latency"],
  "createdAt": "2025-01-15T10:30:00Z",
  "updatedAt": "2025-01-15T10:30:00Z",
  "resolvedAt": null,
  "closedAt": null
}
```

**WebSocket Event:** Publishes `INCIDENT_CREATED` to `/topic/incidents`.

---

#### `GET /api/incidents` — List Incidents

**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| page | int | 0 | Page number (0-indexed) |
| size | int | 20 | Page size (max 100) |
| status | String | — | Filter by status |
| severity | String | — | Filter by severity |
| search | String | — | Search in title/description |
| sortBy | String | createdAt | Sort field: createdAt, updatedAt, severity |
| sortDir | String | desc | Sort direction: asc, desc |

**Response:** `200 OK`
```json
{
  "content": [ { /* IncidentResponse */ } ],
  "page": 0,
  "size": 20,
  "totalElements": 42,
  "totalPages": 3
}
```

---

#### `GET /api/incidents/{id}` — Get Incident

**Response:** `200 OK` — Single `IncidentResponse` object.
**Error:** `404 Not Found` if ID does not exist.

---

#### `PUT /api/incidents/{id}` — Update Incident

**Request Body (partial update supported):**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "severity": "CRITICAL",
  "status": "INVESTIGATING",
  "affectedServices": ["payment-api"],
  "assignee": "jane.doe",
  "tags": ["payment", "critical"]
}
```

**Status Transition Rules:**
- Validates allowed transitions (see Section 4.1).
- Setting status to `RESOLVED` auto-sets `resolvedAt`.
- Setting status to `CLOSED` auto-sets `closedAt`.
- Invalid transitions return `400 Bad Request` with descriptive error.

**Response:** `200 OK` — Updated `IncidentResponse`.
**WebSocket Event:** Publishes `INCIDENT_UPDATED` to `/topic/incidents`.

---

#### `DELETE /api/incidents/{id}` — Delete Incident

**Response:** `204 No Content`
**Cascade:** Deletes all related investigations, evidence, actions, and reports.
**WebSocket Event:** Publishes `INCIDENT_DELETED` to `/topic/incidents`.

---

### 6.2 Investigations — `/api/incidents/{incidentId}/investigations`

#### `POST /api/incidents/{incidentId}/investigations` — Trigger Investigation

Starts an AI-powered investigation for the given incident.

**Request Body:** *(optional overrides)*
```json
{
  "priority": "HIGH",
  "scope": ["logs", "metrics", "kubernetes"]
}
```

**Behavior:**
1. Creates an `Investigation` record with status `PENDING`.
2. Transitions incident status to `INVESTIGATING` (if currently `OPEN`).
3. Asynchronously calls the AI Service via `AIServiceClient`.
4. AI Service response updates investigation status, summary, root cause, confidence.
5. Evidence collected during investigation is stored in `investigation_evidence`.

**Response:** `202 Accepted`
```json
{
  "id": "investigation-uuid",
  "incidentId": "incident-uuid",
  "status": "PENDING",
  "summary": null,
  "rootCause": null,
  "confidence": null,
  "aiModelUsed": null,
  "startedAt": null,
  "completedAt": null,
  "createdAt": "2025-01-15T10:35:00Z",
  "updatedAt": "2025-01-15T10:35:00Z"
}
```

**WebSocket Event:** Publishes `INVESTIGATION_STARTED` to `/topic/incidents/{incidentId}/investigations`.

---

#### `GET /api/incidents/{incidentId}/investigations` — List Investigations

**Response:** `200 OK` — Array of `InvestigationResponse` for the incident.

---

#### `GET /api/incidents/{incidentId}/investigations/{investigationId}` — Get Investigation

**Response:** `200 OK`
```json
{
  "id": "investigation-uuid",
  "incidentId": "incident-uuid",
  "status": "COMPLETED",
  "summary": "Investigation found memory leak in payment service...",
  "rootCause": "Memory leak caused by unclosed database connections in PaymentProcessor.java",
  "confidence": 0.87,
  "aiModelUsed": "gpt-4",
  "evidence": [
    {
      "id": "evidence-uuid",
      "source": "kubernetes",
      "type": "pod_events",
      "data": { /* ... */ },
      "collectedAt": "2025-01-15T10:36:00Z"
    }
  ],
  "actions": [
    { /* ActionResponse */ }
  ],
  "startedAt": "2025-01-15T10:35:05Z",
  "completedAt": "2025-01-15T10:38:00Z",
  "createdAt": "2025-01-15T10:35:00Z",
  "updatedAt": "2025-01-15T10:38:00Z"
}
```

---

#### `GET /api/incidents/{incidentId}/investigations/{investigationId}/evidence` — Get Evidence

**Response:** `200 OK` — Array of `InvestigationEvidence` objects.

---

### 6.3 Actions — `/api/actions`

#### `POST /api/actions` — Create Action

**Request Body:**
```json
{
  "investigationId": "investigation-uuid",
  "incidentId": "incident-uuid",
  "type": "RESTART_SERVICE",
  "title": "Restart payment-api pods",
  "description": "Rolling restart of payment-api deployment to clear leaked connections",
  "command": "kubectl rollout restart deployment/payment-api -n production",
  "targetService": "payment-api",
  "parameters": { "namespace": "production", "deployment": "payment-api" },
  "risk": "MEDIUM",
  "estimatedImpact": "Brief service interruption (~30s) during rolling restart"
}
```

**Validation:**
- `investigationId` — required, must exist
- `incidentId` — required, must exist
- `type` — required, valid ActionType
- `title` — required, max 255 chars

**Response:** `201 Created` — `ActionResponse` with status `PROPOSED`.

---

#### `GET /api/actions` — List Actions

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| incidentId | String | Filter by incident |
| investigationId | String | Filter by investigation |
| status | String | Filter by action status |
| page | int | Page number (default 0) |
| size | int | Page size (default 20) |

**Response:** `200 OK` — `PagedResponse<ActionResponse>`.

---

#### `GET /api/actions/{id}` — Get Action

**Response:** `200 OK` — Single `ActionResponse`.

---

#### `POST /api/actions/{id}/approve` — Approve Action

**Request Body:**
```json
{
  "approvedBy": "john.doe"
}
```

**Precondition:** Action status must be `PROPOSED`.
**Response:** `200 OK` — Action with status `APPROVED`, `approvedBy` and `approvedAt` set.
**WebSocket Event:** Publishes `ACTION_APPROVED` to `/topic/actions`.

---

#### `POST /api/actions/{id}/reject` — Reject Action

**Request Body:**
```json
{
  "reason": "Too risky during peak hours"
}
```

**Precondition:** Action status must be `PROPOSED` or `APPROVED`.
**Response:** `200 OK` — Action with status `REJECTED`.
**WebSocket Event:** Publishes `ACTION_REJECTED` to `/topic/actions`.

---

#### `POST /api/actions/{id}/execute` — Execute Action

**Precondition:** Action status must be `APPROVED`.

**Behavior:**
1. Transitions status to `EXECUTING`.
2. Asynchronously executes the action via the appropriate `ToolAdapter`.
3. On success: status → `COMPLETED`, `executionResult` populated.
4. On failure: status → `FAILED`, `executionResult` contains error details.

**Response:** `202 Accepted` — Action with status `EXECUTING`.
**WebSocket Events:**
- `ACTION_EXECUTING` on start
- `ACTION_COMPLETED` or `ACTION_FAILED` on finish

---

### 6.4 Reports — `/api/reports`

#### `POST /api/reports` — Generate Report

**Request Body:**
```json
{
  "incidentId": "incident-uuid",
  "title": "Post-Incident Report: Payment Latency Spike",
  "format": "JSON"
}
```

**Behavior:**
1. Aggregates incident data, investigation results, evidence, and actions.
2. Generates structured report content.
3. Stores the report record.

**Response:** `201 Created`
```json
{
  "id": "report-uuid",
  "incidentId": "incident-uuid",
  "title": "Post-Incident Report: Payment Latency Spike",
  "format": "JSON",
  "content": "...",
  "metadata": {
    "incidentDuration": "PT2H30M",
    "severity": "HIGH",
    "affectedServices": ["payment-api", "checkout-service"],
    "rootCause": "Memory leak...",
    "actionsExecuted": 2,
    "actionsProposed": 3
  },
  "generatedAt": "2025-01-15T13:00:00Z",
  "createdAt": "2025-01-15T13:00:00Z"
}
```

---

#### `GET /api/reports` — List Reports

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| incidentId | String | Filter by incident |
| page | int | Page number (default 0) |
| size | int | Page size (default 20) |

**Response:** `200 OK` — `PagedResponse<ReportResponse>`.

---

#### `GET /api/reports/{id}` — Get Report

**Response:** `200 OK` — Full `ReportResponse` including content.

---

#### `GET /api/reports/{id}/export` — Export Report

**Query Parameters:**
| Param | Type | Description |
|---|---|---|
| format | String | `JSON` or `PDF` |

**Behavior:**
- **JSON**: Returns `application/json` with the full report as structured JSON.
- **PDF**: Returns `application/pdf` with a generated PDF document.

**Response:** `200 OK` with appropriate `Content-Type` and `Content-Disposition` headers.

---

### 6.5 Adapter Endpoints (Called by AI Service)

These endpoints are called by the AI Service to fetch evidence during investigation. The backend routes requests to the appropriate adapter (simulator or real tools) based on configuration.

#### `GET /api/adapters/kubernetes` — Fetch Kubernetes Evidence

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
      "events": ["Back-off restarting failed container"],
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
      "conditions": ["Available: True", "Progressing: True"],
      "lastUpdateTime": "2025-01-15T10:20:00Z"
    }
  ],
  "nodeStatus": [
    {
      "name": "node-1",
      "status": "Ready",
      "conditions": ["Ready: True", "MemoryPressure: False"],
      "allocatableCpu": "4",
      "allocatableMemory": "16Gi",
      "usedCpu": "2.5",
      "usedMemory": "12Gi"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` — Invalid query parameters
- `503 Service Unavailable` — Kubernetes adapter unavailable

---

#### `GET /api/adapters/logs` — Fetch Log Evidence

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
      "stackTrace": "java.lang.OutOfMemoryError: Java heap space\n\tat com.payment.PaymentProcessor.processPayment(PaymentProcessor.java:142)",
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

#### `GET /api/adapters/metrics` — Fetch Metrics Evidence

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
    "p95": [],
    "p99": []
  }
}
```

---

#### `GET /api/adapters/git` — Fetch Git Evidence

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

### 6.6 Health & Info

#### `GET /actuator/health` — Health Check

**Response:** `200 OK`
```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "aiService": { "status": "UP" },
    "simulator": { "status": "UP" }
  }
}
```

#### `GET /swagger-ui.html` — Swagger UI

Auto-generated API documentation via Springdoc OpenAPI.

---

## 7. WebSocket Events

### Connection

- **Endpoint:** `ws://localhost:8080/ws`
- **Protocol:** STOMP over WebSocket
- **SockJS fallback:** Enabled at `/ws` with `withSockJS()`

### STOMP Topics

| Topic | Event Types | Payload |
|---|---|---|
| `/topic/incidents` | INCIDENT_CREATED, INCIDENT_UPDATED, INCIDENT_DELETED | `WebSocketEvent<IncidentResponse>` |
| `/topic/incidents/{incidentId}/investigations` | INVESTIGATION_STARTED, INVESTIGATION_PROGRESS, INVESTIGATION_COMPLETED, INVESTIGATION_FAILED | `WebSocketEvent<InvestigationResponse>` |
| `/topic/actions` | ACTION_APPROVED, ACTION_REJECTED, ACTION_EXECUTING, ACTION_COMPLETED, ACTION_FAILED | `WebSocketEvent<ActionResponse>` |
| `/topic/system` | SYSTEM_HEALTH, SYSTEM_ERROR | `WebSocketEvent<SystemStatus>` |

### Event Envelope

```json
{
  "eventType": "INVESTIGATION_PROGRESS",
  "entityId": "investigation-uuid",
  "timestamp": "2025-01-15T10:36:30Z",
  "data": {
    /* entity-specific payload */
  }
}
```

### WebSocket Configuration

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }
}
```

---

## 8. Integration Contracts

### 8.1 AI Service Client

**Target:** `http://localhost:8000` (Python FastAPI)
**Transport:** HTTP via Spring `WebClient` (non-blocking)

#### Start Investigation

```
POST http://localhost:8000/api/investigate
```

**Request:**
```json
{
  "investigationId": "investigation-uuid",
  "incidentId": "incident-uuid",
  "incident": {
    "title": "Payment service latency spike",
    "description": "...",
    "severity": "HIGH",
    "affectedServices": ["payment-api", "checkout-service"]
  },
  "callbackUrl": "http://localhost:8080/api/internal/investigations/{investigationId}/callback",
  "scope": ["logs", "metrics", "kubernetes"]
}
```

**Response:** `202 Accepted`
```json
{
  "status": "ACCEPTED",
  "estimatedDuration": "PT5M"
}
```

#### Investigation Callback (AI → Backend)

```
POST /api/internal/investigations/{investigationId}/callback
```

**Payload from AI Service:**
```json
{
  "investigationId": "investigation-uuid",
  "status": "COMPLETED",
  "summary": "Investigation found memory leak...",
  "rootCause": "Unclosed DB connections in PaymentProcessor.java",
  "confidence": 0.87,
  "aiModelUsed": "gpt-4",
  "evidence": [
    {
      "source": "logs",
      "type": "error_log",
      "data": { "entries": [...] }
    }
  ],
  "recommendedActions": [
    {
      "type": "RESTART_SERVICE",
      "title": "Restart payment-api pods",
      "description": "...",
      "command": "kubectl rollout restart deployment/payment-api",
      "targetService": "payment-api",
      "risk": "MEDIUM",
      "estimatedImpact": "Brief interruption (~30s)"
    }
  ]
}
```

#### Error Handling

| Scenario | Backend Behavior |
|---|---|
| AI service unreachable | Retry 3x with exponential backoff (1s, 2s, 4s). Mark investigation `FAILED`. |
| AI service returns 5xx | Retry once. Log error. Mark investigation `FAILED`. |
| AI service timeout (>5min) | Mark investigation `FAILED` with timeout message. |
| Invalid AI response | Log malformed response. Mark investigation `FAILED`. |

---

### 8.2 Tool Adapters

#### Common Interface

```java
public interface ToolAdapter {
    String getType();  // "kubernetes", "logs", "metrics", "git"
    CompletableFuture<Map<String, Object>> fetchData(ToolQuery query);
    CompletableFuture<Map<String, Object>> executeAction(ToolAction action);
    boolean isAvailable();
}
```

#### ToolQuery

```java
@Data @Builder
public class ToolQuery {
    private String type;          // e.g., "pod_events", "error_logs"
    private String service;       // Target service name
    private String namespace;     // Kubernetes namespace
    private Instant from;         // Time range start
    private Instant to;           // Time range end
    private Map<String, String> filters;  // Additional filters
}
```

#### ToolAction

```java
@Data @Builder
public class ToolAction {
    private String type;          // e.g., "restart_pods", "scale_deployment"
    private String service;
    private String namespace;
    private Map<String, Object> parameters;
}
```

#### Adapter Implementations

##### KubernetesAdapter

| Method | Data Returned |
|---|---|
| `fetchData("pod_events")` | Pod status, restarts, events, OOMKills |
| `fetchData("deployments")` | Deployment status, replicas, rollout history |
| `fetchData("node_status")` | Node conditions, resource usage |
| `executeAction("restart_pods")` | Rolling restart result |
| `executeAction("scale_deployment")` | Scale operation result |

##### LogsAdapter

| Method | Data Returned |
|---|---|
| `fetchData("error_logs")` | Error log entries with timestamps, stack traces |
| `fetchData("application_logs")` | Application log entries |
| `fetchData("access_logs")` | HTTP access logs with status codes, latencies |

##### MetricsAdapter

| Method | Data Returned |
|---|---|
| `fetchData("cpu")` | CPU usage time series per service |
| `fetchData("memory")` | Memory usage time series per service |
| `fetchData("request_rate")` | Request rate time series |
| `fetchData("error_rate")` | Error rate time series |
| `fetchData("latency")` | P50/P95/P99 latency time series |

##### GitAdapter

| Method | Data Returned |
|---|---|
| `fetchData("recent_commits")` | Recent commits with author, message, diff stats |
| `fetchData("recent_deployments")` | Deployment history with timestamps, versions |
| `fetchData("changed_files")` | Files changed in recent commits |

#### Adapter Selection (Configuration-Driven)

```yaml
adapters:
  mode: simulator    # "simulator" or "real"
  simulator:
    base-url: http://localhost:8001
  real:
    kubernetes:
      kubeconfig: ~/.kube/config
    logs:
      elasticsearch-url: http://localhost:9200
    metrics:
      prometheus-url: http://localhost:9090
    git:
      provider: github
      token: ${GIT_TOKEN}
```

`ToolAdapterFactory` reads `adapters.mode` and wires the corresponding beans:

```java
@Component
public class ToolAdapterFactory {

    private final Map<String, ToolAdapter> adapters;

    public ToolAdapter getAdapter(String type) {
        return adapters.get(type);  // "kubernetes", "logs", "metrics", "git"
    }
}
```

---

## 9. Error Handling

### Global Exception Handler

`@RestControllerAdvice` class `GlobalExceptionHandler` catches all exceptions and returns a uniform error response.

### Standard Error Response

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Invalid state transition: cannot move from CLOSED to INVESTIGATING",
  "path": "/api/incidents/550e8400-e29b-41d4-a716-446655440000",
  "details": {
    "field": "status",
    "currentValue": "CLOSED",
    "requestedValue": "INVESTIGATING",
    "allowedValues": []
  }
}
```

### Exception Mapping

| Exception | HTTP Status | Description |
|---|---|---|
| `ResourceNotFoundException` | 404 | Entity not found by ID |
| `InvalidStateTransitionException` | 400 | Invalid status change |
| `MethodArgumentNotValidException` | 400 | Request validation failure |
| `AIServiceException` | 502 | AI service call failed |
| `AdapterException` | 502 | Tool adapter call failed |
| `HttpMessageNotReadableException` | 400 | Malformed JSON |
| `ConstraintViolationException` | 400 | Path/query param validation |
| `Exception` (catch-all) | 500 | Unexpected server error |

### Validation Error Response (multiple fields)

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "status": 400,
  "error": "Validation Failed",
  "message": "Request validation failed",
  "path": "/api/incidents",
  "fieldErrors": [
    { "field": "title", "message": "must not be blank" },
    { "field": "severity", "message": "must be one of: CRITICAL, HIGH, MEDIUM, LOW" }
  ]
}
```

---

## 10. Configuration

### application.yml

```yaml
server:
  port: 8080

spring:
  application:
    name: incident-commander-backend

  datasource:
    url: jdbc:h2:mem:incidentdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password:

  h2:
    console:
      enabled: true
      path: /h2-console

  sql:
    init:
      mode: always
      schema-locations: classpath:schema.sql
      data-locations: classpath:data.sql    # optional seed data

  jackson:
    serialization:
      write-dates-as-timestamps: false
    default-property-inclusion: non_null
    date-format: com.fasterxml.jackson.databind.util.StdDateFormat

logging:
  level:
    root: INFO
    com.devops.incident: DEBUG
    org.springframework.web: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"

# --- External Services ---
ai-service:
  base-url: http://localhost:8000
  timeout:
    connect: 5s
    read: 300s            # AI investigation can take minutes
  retry:
    max-attempts: 3
    backoff: 1s

# --- Adapter Configuration ---
adapters:
  mode: simulator         # simulator | real
  simulator:
    base-url: http://localhost:8001
  real:
    kubernetes:
      kubeconfig: ${KUBECONFIG:~/.kube/config}
    logs:
      elasticsearch-url: ${ELASTICSEARCH_URL:http://localhost:9200}
    metrics:
      prometheus-url: ${PROMETHEUS_URL:http://localhost:9090}
    git:
      provider: github
      token: ${GIT_TOKEN:}

# --- API Documentation ---
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    tags-sorter: alpha
    operations-sorter: method

# --- Pagination Defaults ---
pagination:
  default-page-size: 20
  max-page-size: 100

# --- CORS ---
cors:
  allowed-origins: http://localhost:3000
  allowed-methods: GET,POST,PUT,DELETE,OPTIONS
  allowed-headers: "*"
  allow-credentials: true
```

### Local Development Notes

**H2 In-Memory Database:**
- No installation required
- Data persists only while backend is running
- H2 Console available at http://localhost:8080/h2-console
- Connection string: `jdbc:h2:mem:incidentdb`
- Username: `sa`, Password: (empty)

**Production Migration:**
- For production, switch to PostgreSQL
- Change datasource URL, driver, credentials
- Schema is compatible with PostgreSQL
- See DATABASE_SETUP.md for PostgreSQL setup

**Redis (Optional):**
```yaml
spring:
  redis:
    host: localhost
    port: 6379
    timeout: 2000ms
```

---

## 11. Testing Strategy

### 11.1 Unit Tests (JUnit 5 + Mockito)

**Scope:** Service layer business logic, state transitions, validation.

| Test Class | Coverage |
|---|---|
| `IncidentServiceTest` | Create, update, status transitions, validation |
| `InvestigationServiceTest` | Trigger, callback processing, status updates |
| `ActionServiceTest` | Approve, reject, execute flow, precondition checks |
| `ReportServiceTest` | Report generation, content aggregation |
| `EventPublisherServiceTest` | Event publishing to correct topics |

**Example:**
```java
@ExtendWith(MockitoExtension.class)
class IncidentServiceTest {

    @Mock private IncidentRepository incidentRepository;
    @Mock private EventPublisherService eventPublisher;
    @InjectMocks private IncidentService incidentService;

    @Test
    void shouldRejectInvalidStatusTransition() {
        Incident incident = Incident.builder()
            .id("uuid").status(IncidentStatus.CLOSED).build();
        when(incidentRepository.findById("uuid")).thenReturn(Optional.of(incident));

        assertThrows(InvalidStateTransitionException.class, () ->
            incidentService.updateStatus("uuid", IncidentStatus.INVESTIGATING));
    }
}
```

### 11.2 Integration Tests (Spring Boot Test + H2)

**Scope:** Full request lifecycle, database operations, API contracts.

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureTestDatabase
class IncidentControllerIntegrationTest {

    @Autowired private TestRestTemplate restTemplate;

    @Test
    void shouldCreateAndRetrieveIncident() {
        // POST to create, GET to verify, PUT to update status, etc.
    }
}
```

### 11.3 WebSocket Tests

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class WebSocketIntegrationTest {
    // Connect via STOMP client, subscribe to /topic/incidents,
    // create an incident, assert event received.
}
```

### 11.4 Test Data

- `src/test/resources/data.sql` — seed test data
- Builder patterns via Lombok `@Builder` for test entity construction

---

## 12. Non-Functional Requirements

### Pagination

All list endpoints support `page` (0-indexed) and `size` parameters. Max page size: 100. Response wrapped in `PagedResponse<T>`:

```json
{
  "content": [],
  "page": 0,
  "size": 20,
  "totalElements": 42,
  "totalPages": 3
}
```

### Filtering

- String filters: exact match (case-insensitive)
- `search` parameter: partial match on title + description via SQL `LIKE`

### Sorting

- `sortBy` + `sortDir` query params
- Default: `createdAt DESC`
- Allowed sort fields vary by endpoint (documented per endpoint)

### Logging Standards

- **Controller layer**: Log request method, path, response status
- **Service layer**: Log business operations (created, updated, deleted), state transitions
- **Integration layer**: Log external call URL, response status, duration
- **Error**: Log full stack trace at ERROR level
- **Format**: `timestamp [thread] level logger - message`

### Health Checks

- Spring Boot Actuator enabled at `/actuator/health`
- Custom health indicators for AI Service and Simulator connectivity
- Liveness: `/actuator/health/liveness`
- Readiness: `/actuator/health/readiness`

### Request/Response Conventions

- All timestamps in **ISO 8601 UTC** format
- All IDs are **UUID v4** strings
- Null fields excluded from JSON responses (`NON_NULL` inclusion)
- Request validation returns all field errors at once (not fail-fast)

### API Versioning

- No versioning for MVP (all endpoints under `/api/`)
- Future: prefix with `/api/v1/` when breaking changes are introduced

---

## Appendix: Quick Reference — All Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/incidents` | Create incident |
| `GET` | `/api/incidents` | List incidents (paginated, filtered) |
| `GET` | `/api/incidents/{id}` | Get incident by ID |
| `PUT` | `/api/incidents/{id}` | Update incident |
| `DELETE` | `/api/incidents/{id}` | Delete incident |
| `POST` | `/api/incidents/{incidentId}/investigations` | Trigger investigation |
| `GET` | `/api/incidents/{incidentId}/investigations` | List investigations for incident |
| `GET` | `/api/incidents/{incidentId}/investigations/{investigationId}` | Get investigation |
| `GET` | `/api/incidents/{incidentId}/investigations/{investigationId}/evidence` | Get evidence |
| `POST` | `/api/internal/investigations/{investigationId}/callback` | AI callback (internal) |
| `POST` | `/api/actions` | Create action |
| `GET` | `/api/actions` | List actions (paginated, filtered) |
| `GET` | `/api/actions/{id}` | Get action |
| `POST` | `/api/actions/{id}/approve` | Approve action |
| `POST` | `/api/actions/{id}/reject` | Reject action |
| `POST` | `/api/actions/{id}/execute` | Execute action |
| `POST` | `/api/reports` | Generate report |
| `GET` | `/api/reports` | List reports |
| `GET` | `/api/reports/{id}` | Get report |
| `GET` | `/api/reports/{id}/export` | Export report (JSON/PDF) |
| `GET` | `/actuator/health` | Health check |
| `GET` | `/swagger-ui.html` | API documentation |
| `WS` | `/ws` | WebSocket STOMP endpoint |

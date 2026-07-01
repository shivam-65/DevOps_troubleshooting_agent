# AI-Powered DevOps Incident Commander — Frontend Specification

> Comprehensive frontend specification for the React dashboard powering incident management, real-time investigation tracking, evidence visualization, and automated remediation workflows.

---

## Table of Contents

1. [Tech Stack & Dependencies](#1-tech-stack--dependencies)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [Routing Table](#4-routing-table)
5. [Page Definitions](#5-page-definitions)
6. [Component Catalog](#6-component-catalog)
7. [State Management](#7-state-management)
8. [TypeScript Types & Interfaces](#8-typescript-types--interfaces)
9. [API Service Layer](#9-api-service-layer)
10. [WebSocket Integration](#10-websocket-integration)
11. [UI/UX Conventions](#11-uiux-conventions)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Tech Stack & Dependencies

| Category | Technology | Purpose |
|---|---|---|
| **Framework** | React 18 | UI framework |
| **Language** | TypeScript | Type safety |
| **Build Tool** | Vite | Fast dev server and build |
| **Routing** | React Router v6 | Client-side routing |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Components** | shadcn/ui | Pre-built accessible components (Button, Dialog, Table, Card, Tabs, Badge, Sheet, DropdownMenu, Select, Input, Textarea, Toast, Skeleton, etc.) |
| **Icons** | Lucide React | Consistent icon set |
| **Charts** | Recharts | Metrics and time-series visualization |
| **HTTP Client** | Axios | REST API calls with interceptors |
| **WebSocket** | @stomp/stompjs + sockjs-client | STOMP over WebSocket for real-time events |
| **Date/Time** | date-fns | Date formatting and manipulation |
| **State** | React Context + useReducer + custom hooks | Application state management |
| **Testing** | Vitest + React Testing Library | Unit and component tests |
| **Linting** | ESLint + Prettier | Code quality |

### Package Manager

npm

---

## 2. Architecture Overview

### Data Flow

```
User Interaction
      │
      ▼
┌─────────────┐    dispatch()    ┌──────────────────┐
│   Pages     │ ───────────────► │  Context + Hooks  │
│  (Routes)   │ ◄─────────────── │  (State Mgmt)     │
└──────┬──────┘    state          └────────┬──────────┘
       │                                   │
       │ renders                           │ calls
       ▼                                   ▼
┌─────────────┐                  ┌──────────────────┐
│ Components  │                  │  API Services     │
│ (shadcn/ui) │                  │  (Axios)          │
└─────────────┘                  └────────┬──────────┘
                                          │
                                          │ HTTP / WebSocket
                                          ▼
                                 ┌──────────────────┐
                                 │  Backend          │
                                 │  (Spring Boot)    │
                                 └──────────────────┘
```

### Provider Hierarchy

```
<BrowserRouter>
  <WebSocketProvider>
    <IncidentProvider>
      <InvestigationProvider>
        <ActionProvider>
          <ReportProvider>
            <ToastProvider>
              <AppLayout>
                <Outlet />    ← Page routes render here
              </AppLayout>
            </ToastProvider>
          </ReportProvider>
        </ActionProvider>
      </InvestigationProvider>
    </IncidentProvider>
  </WebSocketProvider>
</BrowserRouter>
```

---

## 3. Directory Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.tsx                          # Entry point
│   ├── App.tsx                           # Root component with router
│   │
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── IncidentsListPage.tsx
│   │   ├── IncidentDetailPage.tsx
│   │   ├── InvestigationDetailPage.tsx
│   │   ├── ActionsPage.tsx
│   │   ├── ReportsPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx             # Sidebar + header + main content
│   │   │   ├── Sidebar.tsx               # Navigation sidebar
│   │   │   ├── Header.tsx                # Top header bar
│   │   │   └── PageHeader.tsx            # Page title + breadcrumb + actions
│   │   │
│   │   ├── incidents/
│   │   │   ├── IncidentCard.tsx          # Summary card in list/dashboard
│   │   │   ├── IncidentForm.tsx          # Create/edit incident form
│   │   │   ├── IncidentTimeline.tsx      # Status change timeline
│   │   │   ├── IncidentStatusTransition.tsx  # Status action buttons
│   │   │   └── IncidentFilters.tsx       # Filter bar (status, severity, search)
│   │   │
│   │   ├── investigations/
│   │   │   ├── InvestigationCard.tsx     # Investigation summary card
│   │   │   ├── InvestigationProgress.tsx # Progress indicator with steps
│   │   │   ├── EvidenceViewer.tsx        # Tabbed evidence display
│   │   │   ├── EvidencePanel.tsx         # Single evidence source panel
│   │   │   ├── RootCauseDisplay.tsx      # Root cause + confidence display
│   │   │   └── AgentWorkflow.tsx         # Multi-agent step visualization
│   │   │
│   │   ├── actions/
│   │   │   ├── ActionCard.tsx            # Single action with approve/reject/execute
│   │   │   ├── ActionList.tsx            # List of actions
│   │   │   ├── ActionForm.tsx            # Create manual action form
│   │   │   └── ExecutionResult.tsx       # Action execution output
│   │   │
│   │   ├── reports/
│   │   │   ├── ReportCard.tsx            # Report summary card
│   │   │   ├── ReportViewer.tsx          # Full report content display
│   │   │   └── GenerateReportForm.tsx    # Report generation form
│   │   │
│   │   ├── charts/
│   │   │   ├── MetricsChart.tsx          # Time-series line/area chart
│   │   │   ├── SeverityDistribution.tsx  # Pie/donut chart for severity breakdown
│   │   │   ├── StatusOverview.tsx        # Bar chart for status distribution
│   │   │   └── IncidentTrend.tsx         # Incidents over time line chart
│   │   │
│   │   └── shared/
│   │       ├── StatusBadge.tsx           # Color-coded status badge
│   │       ├── SeverityBadge.tsx         # Color-coded severity badge
│   │       ├── ConfidenceScore.tsx       # Confidence score display (progress ring)
│   │       ├── PagedTable.tsx            # Paginated table wrapper
│   │       ├── EmptyState.tsx            # Empty state placeholder
│   │       ├── LoadingState.tsx          # Loading skeleton/spinner
│   │       ├── ErrorState.tsx            # Error display with retry
│   │       ├── ConfirmDialog.tsx         # Confirmation modal
│   │       ├── ConnectionStatus.tsx      # WebSocket connection indicator
│   │       └── TimeAgo.tsx              # Relative time display
│   │
│   ├── contexts/
│   │   ├── IncidentContext.tsx
│   │   ├── InvestigationContext.tsx
│   │   ├── ActionContext.tsx
│   │   ├── ReportContext.tsx
│   │   └── WebSocketContext.tsx
│   │
│   ├── hooks/
│   │   ├── useIncidents.ts
│   │   ├── useInvestigations.ts
│   │   ├── useActions.ts
│   │   ├── useReports.ts
│   │   ├── useWebSocket.ts
│   │   └── usePagination.ts
│   │
│   ├── services/
│   │   ├── api.ts                        # Axios instance + interceptors
│   │   ├── incidentService.ts
│   │   ├── investigationService.ts
│   │   ├── actionService.ts
│   │   └── reportService.ts
│   │
│   ├── types/
│   │   ├── incident.ts
│   │   ├── investigation.ts
│   │   ├── action.ts
│   │   ├── report.ts
│   │   ├── evidence.ts
│   │   ├── websocket.ts
│   │   └── common.ts
│   │
│   ├── lib/
│   │   └── utils.ts                      # shadcn/ui utility (cn function)
│   │
│   └── config/
│       └── index.ts                      # API base URL, WS URL, defaults
│
├── index.html
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
├── package.json
├── components.json                       # shadcn/ui config
└── .env
```

---

## 4. Routing Table

| Path | Page | Description |
|---|---|---|
| `/` | DashboardPage | Overview with stats, active incidents, recent investigations |
| `/incidents` | IncidentsListPage | Paginated incident list with filters |
| `/incidents/:id` | IncidentDetailPage | Single incident detail with timeline, investigations, actions |
| `/incidents/:id/investigations/:investigationId` | InvestigationDetailPage | Investigation detail with evidence, root cause, actions |
| `/actions` | ActionsPage | All actions across incidents with filters |
| `/reports` | ReportsPage | Report list + generation |
| `/settings` | SettingsPage | Configuration (adapter mode, API endpoints, preferences) |

---

## 5. Page Definitions

### 5.1 Dashboard Page (`/`)

**Purpose:** High-level overview of system state. First thing the user sees.

**Sections:**

- **Stats Row** — 4 stat cards:
  - Total incidents (count)
  - Open incidents (count, colored red if > 0)
  - Active investigations (count)
  - Pending actions (count)

- **Severity Distribution** — Donut chart showing incidents by severity (CRITICAL/HIGH/MEDIUM/LOW)

- **Status Overview** — Bar chart showing incidents by status (OPEN/INVESTIGATING/RESOLVED/CLOSED)

- **Incident Trend** — Line chart showing incidents created over time (last 7/14/30 days)

- **Active Incidents Table** — Table of OPEN + INVESTIGATING incidents, sorted by severity then createdAt. Columns: title, severity badge, status badge, affected services, created time (relative). Click row → navigate to incident detail.

- **Recent Investigations** — Card list of last 5 investigations. Each card: incident title, investigation status, confidence (if completed), time started. Click → navigate to investigation detail.

- **Recent Actions** — Card list of last 5 PROPOSED/APPROVED actions needing attention. Each card: action title, type, risk, status. Quick approve/reject buttons inline.

**Real-time:** WebSocket updates auto-refresh stats, tables, and cards without page reload.

---

### 5.2 Incidents List Page (`/incidents`)

**Purpose:** Browse, search, filter all incidents.

**Sections:**

- **Page Header** — Title "Incidents" + "Create Incident" button (opens dialog/modal)

- **Filter Bar** — Row of filter controls:
  - Status dropdown (All, OPEN, INVESTIGATING, RESOLVED, CLOSED)
  - Severity dropdown (All, CRITICAL, HIGH, MEDIUM, LOW)
  - Search input (searches title + description)
  - Sort dropdown (Created date, Updated date, Severity)
  - Sort direction toggle (asc/desc)

- **Incidents Table** — Paginated table with columns:
  - Title (clickable → detail)
  - Severity (badge)
  - Status (badge)
  - Affected Services (comma-separated, max 3 shown + "+N more")
  - Assignee
  - Created (relative time)
  - Updated (relative time)

- **Pagination Controls** — Page number, page size selector (10/20/50), total count display

- **Create Incident Dialog** — Modal form with fields:
  - Title (text input, required)
  - Description (textarea, required)
  - Severity (dropdown, required)
  - Affected Services (multi-input, comma-separated or tag-style)
  - Assignee (text input, optional)
  - Tags (multi-input, optional)

**Real-time:** New incidents from WebSocket appear at top of table. Status changes update badges in-place.

---

### 5.3 Incident Detail Page (`/incidents/:id`)

**Purpose:** Full incident view with lifecycle management, linked investigations, and actions.

**Sections:**

- **Page Header** — Incident title + severity badge + status badge + "Delete" button (with confirm dialog)

- **Info Panel** — Card displaying:
  - Description (full text)
  - Affected Services (tag list)
  - Assignee
  - Tags
  - Created at / Updated at / Resolved at / Closed at (formatted timestamps)

- **Status Transition Bar** — Row of action buttons based on current status:
  - OPEN → "Start Investigation" button (triggers investigation AND transitions to INVESTIGATING), "Close" button
  - INVESTIGATING → "Mark Resolved" button, "Reopen" button
  - RESOLVED → "Close" button, "Reopen Investigation" button
  - CLOSED → *(no buttons — terminal state)*

- **Timeline** — Vertical timeline showing:
  - Incident created
  - Status changes (with timestamps)
  - Investigations started/completed
  - Actions approved/executed
  - Each entry: icon + title + timestamp + optional detail text

- **Investigations Section** — List of investigations for this incident:
  - Each as a card: status badge, summary preview (truncated), confidence, timestamps
  - "Start New Investigation" button
  - Click card → navigate to Investigation Detail

- **Actions Section** — List of actions linked to this incident:
  - Each as ActionCard with approve/reject/execute buttons
  - Filter tabs: All / Proposed / Approved / Completed / Failed

- **Reports Section** — List of reports for this incident:
  - Each as a small card: title, format, generated date
  - "Generate Report" button (opens form dialog)
  - Click card → view report content

**Real-time:** WebSocket updates status badges, timeline entries, investigation/action cards live.

---

### 5.4 Investigation Detail Page (`/incidents/:id/investigations/:investigationId`)

**Purpose:** Deep dive into AI investigation results, evidence, and recommended actions.

**Sections:**

- **Page Header** — Breadcrumb (Incidents > {title} > Investigation) + investigation status badge

- **Status & Progress** — Prominent status display:
  - PENDING: "Waiting to start..." with subtle animation
  - IN_PROGRESS: Step-by-step progress indicator showing AI agent stages (Planning → Collecting → Analyzing → Root Cause → Recommendations)
  - COMPLETED: Green checkmark with completion time
  - FAILED: Red error with failure reason

- **Investigation Progress** — Shows investigation workflow stages:
  - Collecting Evidence (fetching from Kubernetes, Logs, Metrics, Git adapters)
  - Analyzing Evidence (Gemini LLM analysis)
  - Generating Recommendations (creating remediation actions)
  - Each stage: icon + name + status (waiting/running/done/error) + duration

- **Root Cause & Summary Panel** (visible when COMPLETED):
  - **Summary** — AI-generated investigation summary (full text, formatted)
  - **Root Cause** — Root cause text highlighted in a callout/alert card
  - **Confidence Score** — Circular progress ring showing confidence (0-100%) with color coding (green >80%, yellow 50-80%, red <50%)
  - **AI Model Used** — Small label showing which model was used

- **Evidence Section** — Tabbed interface with one tab per evidence source:
  - **Kubernetes** tab:
    - Pod status table (pod name, status, restarts, age, events)
    - Deployment status (name, replicas desired/ready, rollout status)
    - Node conditions (if relevant)
    - Highlighted rows for unhealthy pods (CrashLoopBackOff, OOMKilled, etc.)
  - **Logs** tab:
    - Error log entries in a log viewer (timestamp + level + message)
    - Syntax-highlighted stack traces
    - Filter by log level (ERROR, WARN, INFO)
  - **Metrics** tab:
    - Recharts line/area charts for:
      - CPU usage over time
      - Memory usage over time
      - Request rate over time
      - Error rate over time
      - Latency percentiles (P50/P95/P99) over time
    - Time range selector (last 1h, 6h, 24h)
  - **Git** tab:
    - Recent commits table (hash, author, message, date, files changed)
    - Recent deployments (version, timestamp, deployer)
    - Highlight commits that correlate with incident timing

- **Recommended Actions** — List of AI-generated ActionCards:
  - Each card: type badge, title, description, command, target service, risk level, estimated impact
  - "Approve" and "Reject" buttons per card
  - "Approve All" bulk action button

**Real-time:** WebSocket updates progress steps, evidence tabs populate as data arrives, status transitions animate.

---

### 5.5 Actions Page (`/actions`)

**Purpose:** Cross-incident view of all remediation actions.

**Sections:**

- **Page Header** — Title "Actions"

- **Filter Bar:**
  - Status filter (All, PROPOSED, APPROVED, EXECUTING, COMPLETED, FAILED, REJECTED)
  - Type filter (RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, etc.)
  - Incident filter (dropdown of incident titles)
  - Search (title/description)

- **Actions Table** — Paginated table with columns:
  - Title (clickable → linked investigation)
  - Type (badge)
  - Status (badge)
  - Risk (color-coded)
  - Target Service
  - Incident (link)
  - Created (relative time)
  - Actions column (Approve / Reject / Execute buttons based on status)

- **Action Detail Drawer** — Side panel that opens when an action row is clicked:
  - Full description
  - Command to execute (code block style)
  - Parameters (key-value display)
  - Estimated impact
  - Execution result (if executed — formatted output)
  - Approval info (who approved, when)
  - Timeline of status changes

**Real-time:** Action status updates via WebSocket, buttons enable/disable based on real-time status.

---

### 5.6 Reports Page (`/reports`)

**Purpose:** Generate, browse, and export incident reports.

**Sections:**

- **Page Header** — Title "Reports" + "Generate Report" button

- **Generate Report Dialog:**
  - Incident selector (dropdown of incidents)
  - Report title (auto-filled: "Post-Incident Report: {incident title}")
  - Format selector (JSON / PDF)
  - "Generate" button

- **Reports Table** — Paginated table with columns:
  - Title
  - Incident (link)
  - Format (badge)
  - Generated at (formatted date)
  - Actions: View / Export JSON / Export PDF buttons

- **Report Viewer** — When a report is clicked, display content in a readable format:
  - Incident summary section
  - Investigation findings section
  - Evidence summary section
  - Actions taken section
  - Timeline section
  - Metadata (duration, severity, services affected)

---

### 5.7 Settings Page (`/settings`)

**Purpose:** Configure application preferences and integration settings.

**Sections:**

- **Adapter Configuration:**
  - Mode toggle: Simulator / Real Tools (display only — controlled by backend, shown for visibility)
  - Simulator URL display
  - Real tools connection status (Kubernetes, Elasticsearch, Prometheus, Git — green/red indicators)

- **API Configuration:**
  - Backend API URL
  - AI Service URL
  - Connection status indicators

- **Preferences:**
  - Default page size (10/20/50)
  - Default incident sort order
  - Auto-refresh interval
  - Theme (light/dark) — if implemented

- **System Health:**
  - Backend health status (from `/actuator/health`)
  - AI Service status
  - Simulator status
  - WebSocket connection status

---

## 6. Component Catalog

### Layout Components

| Component | Description |
|---|---|
| **AppLayout** | Main layout with collapsible sidebar, header, and scrollable content area |
| **Sidebar** | Vertical navigation with links: Dashboard, Incidents, Actions, Reports, Settings. Active route highlighted. Collapsible to icon-only mode. |
| **Header** | Top bar with page title, breadcrumb, WebSocket connection indicator, and optional action buttons |
| **PageHeader** | Reusable page header with title, description, breadcrumb trail, and right-aligned action buttons |

### Incident Components

| Component | Props | Description |
|---|---|---|
| **IncidentCard** | incident: Incident, onClick | Compact card showing title, severity badge, status badge, affected services, time |
| **IncidentForm** | onSubmit, initialValues? | Create/edit form with validation for all incident fields |
| **IncidentTimeline** | events: TimelineEvent[] | Vertical timeline rendering chronological events with icons and descriptions |
| **IncidentStatusTransition** | incident: Incident, onTransition | Renders allowed status transition buttons based on current status |
| **IncidentFilters** | filters, onFilterChange | Row of filter controls (status, severity, search, sort) |

### Investigation Components

| Component | Props | Description |
|---|---|---|
| **InvestigationCard** | investigation: Investigation, onClick | Summary card with status, confidence, timestamps |
| **InvestigationProgress** | status, steps: AgentStep[] | Step indicator showing current AI agent progress |
| **EvidenceViewer** | evidence: Evidence[] | Tabbed container rendering EvidencePanel per source type |
| **EvidencePanel** | evidence: Evidence, type: string | Renders evidence data formatted for its type (table for k8s, log viewer for logs, charts for metrics, table for git) |
| **RootCauseDisplay** | rootCause, confidence, summary | Highlighted callout card with root cause, summary text, and confidence ring |
| **AgentWorkflow** | steps: AgentStep[] | Horizontal stepper showing 5 AI agent stages with status indicators |

### Action Components

| Component | Props | Description |
|---|---|---|
| **ActionCard** | action: Action, onApprove, onReject, onExecute | Card with action details and contextual action buttons |
| **ActionList** | actions: Action[], filters | Filterable list rendering ActionCards |
| **ActionForm** | onSubmit, investigationId, incidentId | Form for creating manual remediation actions |
| **ExecutionResult** | result: string (JSON) | Formatted display of action execution output |

### Report Components

| Component | Props | Description |
|---|---|---|
| **ReportCard** | report: Report, onView, onExport | Summary card with title, format, date, action buttons |
| **ReportViewer** | report: Report | Full report content renderer with sections |
| **GenerateReportForm** | incidents: Incident[], onSubmit | Form with incident selector, title input, format selector |

### Chart Components

| Component | Props | Description |
|---|---|---|
| **MetricsChart** | data: TimeSeriesData[], title, yAxisLabel | Recharts line/area chart for time-series metrics |
| **SeverityDistribution** | data: { severity: string, count: number }[] | Recharts pie/donut chart for severity breakdown |
| **StatusOverview** | data: { status: string, count: number }[] | Recharts bar chart for status distribution |
| **IncidentTrend** | data: { date: string, count: number }[] | Recharts line chart for incidents over time |

### Shared Components

| Component | Props | Description |
|---|---|---|
| **StatusBadge** | status: IncidentStatus \| InvestigationStatus \| ActionStatus | Color-coded badge using shadcn Badge |
| **SeverityBadge** | severity: IncidentSeverity | Color-coded severity badge (red=CRITICAL, orange=HIGH, yellow=MEDIUM, blue=LOW) |
| **ConfidenceScore** | value: number (0-1) | Circular progress ring with percentage. Green >0.8, yellow 0.5-0.8, red <0.5 |
| **PagedTable** | columns, data, pagination, onPageChange | Reusable table with pagination controls wrapping shadcn Table |
| **EmptyState** | icon, title, description, action? | Placeholder for empty lists/tables |
| **LoadingState** | — | Skeleton loader using shadcn Skeleton |
| **ErrorState** | error, onRetry | Error display with retry button |
| **ConfirmDialog** | title, description, onConfirm, onCancel | shadcn AlertDialog for destructive actions (delete, execute) |
| **ConnectionStatus** | connected: boolean | Small dot indicator (green = connected, red = disconnected) |
| **TimeAgo** | date: string | Renders relative time ("2 minutes ago") with tooltip showing absolute time |

---

## 7. State Management

### Context Structure

Each context follows the same pattern: state + dispatch + provider + custom hook.

#### IncidentContext

**State:**
- `incidents: Incident[]` — current page of incidents
- `currentIncident: Incident | null` — selected incident detail
- `pagination: PaginationState` — page, size, totalElements, totalPages
- `filters: IncidentFilters` — status, severity, search, sortBy, sortDir
- `loading: boolean`
- `error: string | null`

**Actions (via useReducer):**
- SET_INCIDENTS — replace incident list
- SET_CURRENT_INCIDENT — set detail view
- ADD_INCIDENT — prepend new incident (from create or WebSocket)
- UPDATE_INCIDENT — merge updates (from edit or WebSocket)
- REMOVE_INCIDENT — remove from list (from delete or WebSocket)
- SET_PAGINATION
- SET_FILTERS
- SET_LOADING
- SET_ERROR

#### InvestigationContext

**State:**
- `investigations: Investigation[]` — investigations for current incident
- `currentInvestigation: Investigation | null` — selected investigation detail
- `evidence: Evidence[]` — evidence for current investigation
- `loading: boolean`
- `error: string | null`

**Actions:**
- SET_INVESTIGATIONS
- SET_CURRENT_INVESTIGATION
- UPDATE_INVESTIGATION — merge WebSocket progress updates
- SET_EVIDENCE
- ADD_EVIDENCE — append new evidence as it arrives via WebSocket
- SET_LOADING
- SET_ERROR

#### ActionContext

**State:**
- `actions: Action[]` — current page of actions
- `pagination: PaginationState`
- `filters: ActionFilters` — status, type, incidentId, search
- `loading: boolean`
- `error: string | null`

**Actions:**
- SET_ACTIONS
- ADD_ACTION
- UPDATE_ACTION — status transitions from approve/reject/execute/WebSocket
- SET_PAGINATION
- SET_FILTERS
- SET_LOADING
- SET_ERROR

#### ReportContext

**State:**
- `reports: Report[]`
- `currentReport: Report | null`
- `pagination: PaginationState`
- `loading: boolean`
- `error: string | null`

**Actions:**
- SET_REPORTS
- SET_CURRENT_REPORT
- ADD_REPORT
- SET_PAGINATION
- SET_LOADING
- SET_ERROR

#### WebSocketContext

**State:**
- `connected: boolean`
- `client: StompClient | null`
- `reconnectAttempts: number`

**Responsibilities:**
- Establish STOMP connection on mount
- Subscribe to all relevant topics (see WebSocket Topics below)
- Dispatch events to other contexts (IncidentContext, InvestigationContext, ActionContext)
- Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- Expose connection status for UI indicators

**WebSocket Topics (STOMP):**
- `/topic/incidents` — New incidents created
- `/topic/incidents/{incidentId}` — Updates to specific incident (status, assignee, tags)
- `/topic/investigations/{investigationId}` — Investigation progress updates (status, evidence collected, results)
- `/topic/actions/{actionId}` — Action status changes (PROPOSED → APPROVED → EXECUTING → COMPLETED)
- `/topic/actions` — New actions created
- `/user/queue/errors` — Error notifications (personal queue)

---

## 8. TypeScript Types & Interfaces

### Enums

```
IncidentSeverity: CRITICAL | HIGH | MEDIUM | LOW
IncidentStatus: OPEN | INVESTIGATING | RESOLVED | CLOSED
InvestigationStatus: PENDING | IN_PROGRESS | COMPLETED | FAILED
ActionStatus: PROPOSED | APPROVED | EXECUTING | COMPLETED | FAILED | REJECTED
ActionType: RESTART_SERVICE | SCALE_UP | ROLLBACK_DEPLOYMENT | RUN_SCRIPT | APPLY_CONFIG_CHANGE | CLEAR_CACHE | FAILOVER | CUSTOM
ReportFormat: JSON | PDF
```

### Entity Types

**Incident**
- id: string
- title: string
- description: string
- severity: IncidentSeverity
- status: IncidentStatus
- affectedServices: string[]
- assignee: string | null
- tags: string[]
- createdAt: string (ISO 8601)
- updatedAt: string
- resolvedAt: string | null
- closedAt: string | null

**Investigation**
- id: string
- incidentId: string
- status: InvestigationStatus
- summary: string | null
- rootCause: string | null
- confidence: number | null (0.0–1.0)
- aiModelUsed: string | null
- evidence: Evidence[] (included in detail response)
- actions: Action[] (included in detail response)
- startedAt: string | null
- completedAt: string | null
- createdAt: string
- updatedAt: string

**Evidence**
- id: string
- investigationId: string
- source: string ("kubernetes" | "logs" | "metrics" | "git")
- type: string ("pod_events" | "error_log" | "cpu" | "recent_commits" | etc.)
- data: any (parsed JSON — structure varies by source)
- collectedAt: string

**Action**
- id: string
- investigationId: string
- incidentId: string
- type: ActionType
- status: ActionStatus
- title: string
- description: string | null
- command: string | null
- targetService: string | null
- parameters: Record<string, any> | null
- risk: string | null
- estimatedImpact: string | null
- executionResult: any | null
- approvedBy: string | null
- approvedAt: string | null
- executedAt: string | null
- completedAt: string | null
- createdAt: string
- updatedAt: string

**Report**
- id: string
- incidentId: string
- title: string
- content: string
- format: ReportFormat
- metadata: ReportMetadata | null
- generatedAt: string
- createdAt: string

**ReportMetadata**
- incidentDuration: string
- severity: string
- affectedServices: string[]
- rootCause: string
- actionsExecuted: number
- actionsProposed: number

### Request Types

**CreateIncidentRequest**
- title: string
- description: string
- severity: IncidentSeverity
- affectedServices?: string[]
- assignee?: string
- tags?: string[]

**UpdateIncidentRequest**
- title?: string
- description?: string
- severity?: IncidentSeverity
- status?: IncidentStatus
- affectedServices?: string[]
- assignee?: string
- tags?: string[]

**CreateActionRequest**
- investigationId: string
- incidentId: string
- type: ActionType
- title: string
- description?: string
- command?: string
- targetService?: string
- parameters?: Record<string, any>
- risk?: string
- estimatedImpact?: string

**GenerateReportRequest**
- incidentId: string
- title: string
- format: ReportFormat

### Common Types

**PagedResponse\<T\>**
- content: T[]
- page: number
- size: number
- totalElements: number
- totalPages: number

**WebSocketEvent\<T\>**
- eventType: string
- entityId: string
- timestamp: string
- data: T

**PaginationState**
- page: number
- size: number
- totalElements: number
- totalPages: number

**TimelineEvent**
- id: string
- type: string (CREATED | STATUS_CHANGE | INVESTIGATION_STARTED | etc.)
- title: string
- description: string | null
- timestamp: string
- icon: string

**AgentStep**
- name: string (Planner | Collector | Analyst | RootCause | Remediator)
- status: "waiting" | "running" | "done" | "error"
- duration: number | null (milliseconds)

---

## 9. API Service Layer

### Axios Instance Configuration

**Base setup (services/api.ts):**
- Base URL: read from config (`http://localhost:8080/api`)
- Default headers: `Content-Type: application/json`
- Request interceptor: attach any needed headers
- Response interceptor: extract `data` from Axios response, handle errors uniformly
- Error interceptor: transform backend error responses into consistent format, trigger toast notifications for 4xx/5xx errors

### Service Methods

#### incidentService.ts

| Method | HTTP | Path | Returns |
|---|---|---|---|
| getAll(params) | GET | /incidents | PagedResponse\<Incident\> |
| getById(id) | GET | /incidents/{id} | Incident |
| create(data) | POST | /incidents | Incident |
| update(id, data) | PUT | /incidents/{id} | Incident |
| delete(id) | DELETE | /incidents/{id} | void |

#### investigationService.ts

| Method | HTTP | Path | Returns |
|---|---|---|---|
| getByIncident(incidentId) | GET | /incidents/{incidentId}/investigations | Investigation[] |
| getById(incidentId, invId) | GET | /incidents/{incidentId}/investigations/{invId} | Investigation (with evidence + actions) |
| trigger(incidentId, options?) | POST | /incidents/{incidentId}/investigations | Investigation |
| getEvidence(incidentId, invId) | GET | /incidents/{incidentId}/investigations/{invId}/evidence | Evidence[] |

#### actionService.ts

| Method | HTTP | Path | Returns |
|---|---|---|---|
| getAll(params) | GET | /actions | PagedResponse\<Action\> |
| getById(id) | GET | /actions/{id} | Action |
| create(data) | POST | /actions | Action |
| approve(id, approvedBy) | POST | /actions/{id}/approve | Action |
| reject(id, reason) | POST | /actions/{id}/reject | Action |
| execute(id) | POST | /actions/{id}/execute | Action |

#### reportService.ts

| Method | HTTP | Path | Returns |
|---|---|---|---|
| getAll(params) | GET | /reports | PagedResponse\<Report\> |
| getById(id) | GET | /reports/{id} | Report |
| generate(data) | POST | /reports | Report |
| export(id, format) | GET | /reports/{id}/export?format={format} | Blob (file download) |

---

## 10. WebSocket Integration

### Connection Setup

**WebSocketContext** manages the STOMP connection lifecycle:

- **Connect** on app mount to `ws://localhost:8080/ws` via SockJS
- **Subscribe** to all topics after connection established
- **Reconnect** on disconnect with exponential backoff (1s → 2s → 4s → 8s → max 30s)
- **Expose** connection status (`connected: boolean`) for ConnectionStatus component

### Topic Subscriptions

| Topic | Handler |
|---|---|
| `/topic/incidents` | Dispatch to IncidentContext: ADD_INCIDENT (created), UPDATE_INCIDENT (updated), REMOVE_INCIDENT (deleted) |
| `/topic/incidents/{incidentId}/investigations` | Dispatch to InvestigationContext: UPDATE_INVESTIGATION (progress/completed/failed). Dynamic subscription — subscribe when viewing incident detail, unsubscribe on leave. |
| `/topic/actions` | Dispatch to ActionContext: UPDATE_ACTION (approved/rejected/executing/completed/failed) |
| `/topic/system` | Update system health display in Header/Settings |

### Event Handling Flow

1. WebSocket receives STOMP message
2. Parse JSON body into `WebSocketEvent<T>`
3. Based on `eventType`, determine target context
4. Dispatch appropriate action to context reducer
5. UI re-renders automatically via React reactivity

### Dynamic Subscriptions

- `/topic/incidents/{incidentId}/investigations` — subscribe when user navigates to IncidentDetailPage or InvestigationDetailPage, unsubscribe on navigate away
- Managed via `useEffect` cleanup in the page components

---

## 11. UI/UX Conventions

### Color Coding

**Severity Colors:**
| Severity | Color | Tailwind Class |
|---|---|---|
| CRITICAL | Red | `bg-red-500/10 text-red-500 border-red-500` |
| HIGH | Orange | `bg-orange-500/10 text-orange-500 border-orange-500` |
| MEDIUM | Yellow | `bg-yellow-500/10 text-yellow-500 border-yellow-500` |
| LOW | Blue | `bg-blue-500/10 text-blue-500 border-blue-500` |

**Status Colors:**
| Status | Color | Tailwind Class |
|---|---|---|
| OPEN | Blue | `bg-blue-500/10 text-blue-500` |
| INVESTIGATING / IN_PROGRESS / EXECUTING | Amber | `bg-amber-500/10 text-amber-500` |
| PENDING / PROPOSED | Gray | `bg-gray-500/10 text-gray-500` |
| RESOLVED / COMPLETED / APPROVED | Green | `bg-green-500/10 text-green-500` |
| CLOSED | Slate | `bg-slate-500/10 text-slate-500` |
| FAILED / REJECTED | Red | `bg-red-500/10 text-red-500` |

**Risk Colors:**
| Risk | Color |
|---|---|
| HIGH | Red |
| MEDIUM | Yellow |
| LOW | Green |

### Loading States

- **Page load**: Full-page skeleton using shadcn Skeleton components matching page layout
- **Table load**: Table skeleton rows
- **Card load**: Card skeleton
- **Action in progress**: Button shows spinner + "Loading..." text, disabled state
- **Investigation in progress**: Animated progress stepper

### Error States

- **API error**: ErrorState component with error message + "Retry" button
- **Empty list**: EmptyState component with relevant icon, message, and optional CTA ("Create your first incident")
- **WebSocket disconnected**: Red dot in header + toast notification
- **Form validation**: Inline field errors below inputs (red text)

### Toast Notifications

Using shadcn Toast/Sonner:
- **Success**: Green — "Incident created successfully", "Action approved"
- **Error**: Red — "Failed to create incident", "AI service unavailable"
- **Info**: Blue — "Investigation started", "New evidence collected"
- **Warning**: Yellow — "WebSocket disconnected, attempting reconnect..."

### Responsive Design

- **Desktop** (≥1024px): Full sidebar + content area
- **Tablet** (768–1023px): Collapsed sidebar (icon-only) + full content
- **Mobile** (<768px): Hidden sidebar with hamburger menu, stacked layouts

### Animations

- Page transitions: Subtle fade-in
- Status changes: Badge color transition (CSS transition)
- New items: Slide-in animation for new table rows/cards
- Investigation progress: Step-by-step animation as agents complete
- Loading: Skeleton pulse animation (built into shadcn)

---

## 12. Testing Strategy

### Tools

- **Vitest** — Test runner (Vite-native, fast)
- **React Testing Library** — Component testing
- **MSW (Mock Service Worker)** — API mocking for integration tests

### Test Scope

**Component Tests:**
- All shared components render correctly with different props
- StatusBadge/SeverityBadge show correct colors for each value
- IncidentForm validates required fields
- ActionCard shows correct buttons based on action status
- PagedTable renders data and handles pagination clicks

**Page Tests:**
- DashboardPage fetches and displays stats, tables, cards
- IncidentsListPage applies filters, pagination, navigates to detail
- IncidentDetailPage shows all sections, handles status transitions
- InvestigationDetailPage renders evidence tabs, root cause, actions

**Hook Tests:**
- useIncidents fetches and manages incident state correctly
- usePagination handles page changes
- useWebSocket connects and dispatches events

**Service Tests:**
- API service methods call correct endpoints with correct parameters
- Error handling transforms backend errors correctly

### Test File Convention

- Test files co-located next to source: `ComponentName.test.tsx`
- Or in `__tests__/` directories within each feature folder

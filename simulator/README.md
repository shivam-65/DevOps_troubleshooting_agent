# AI DevOps Incident Commander — Simulator

Generates realistic production failure scenarios and evidence for testing the AI-powered incident investigation system.

## Quick Start

```bash
cd simulator
pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Endpoints

### Adapter Endpoints (called by backend)
- `GET /api/adapters/kubernetes` — Kubernetes evidence (pods, deployments, nodes)
- `GET /api/adapters/logs` — Log entries (error, application, access)
- `GET /api/adapters/metrics` — Metrics time-series (CPU, memory, latency, error rate)
- `GET /api/adapters/git` — Git history (commits, deployments, rollbacks)

### Scenario Management
- `GET /api/scenarios` — List all scenarios
- `GET /api/scenarios/{id}` — Get scenario details
- `POST /api/scenarios/{id}/activate` — Activate a scenario
- `POST /api/scenarios/{id}/deactivate` — Deactivate a scenario
- `POST /api/scenarios/custom` — Create custom scenario
- `DELETE /api/scenarios/custom/{id}` — Delete custom scenario

### Service Registry
- `GET /api/services` — List simulated services
- `POST /api/services` — Add a service
- `DELETE /api/services/{name}` — Remove a service

### Health
- `GET /health` — Health check

## Predefined Scenarios

| ID | Name | Description |
|---|---|---|
| `pod-crash` | Pod Crash | Pod enters CrashLoopBackOff |
| `oom-kill` | OOM Kill | Memory exhaustion → OOMKilled |
| `latency-spike` | Latency Spike | P50/P95/P99 latency multiplied |
| `error-rate-surge` | Error Rate Surge | Error rate jumps to 10-30% |
| `deployment-failure` | Deployment Failure | ImagePullBackOff, failed deploy |

## Testing

```bash
cd simulator
python -m pytest tests/ -v
```

## Usage Example

```bash
# Activate OOM scenario
curl -X POST http://localhost:8001/api/scenarios/oom-kill/activate \
  -H "Content-Type: application/json" \
  -d '{"targetServices": ["payment-api"], "parameters": {"memoryGrowthRate": "fast"}}'

# Fetch Kubernetes evidence (shows OOMKilled pods)
curl http://localhost:8001/api/adapters/kubernetes?services=payment-api

# Deactivate
curl -X POST http://localhost:8001/api/scenarios/oom-kill/deactivate
```

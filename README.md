# AI-Powered DevOps Incident Commander

An AI-powered incident management system that automates production incident investigation through multi-agent AI analysis, providing unified dashboard for monitoring, real-time investigation tracking, and automated remediation recommendations.

## Architecture

```
┌─────────────────┐     HTTP/WebSocket    ┌─────────────────┐
│   Frontend      │◄────────────────────►│   Backend       │
│   (React)       │                        │   (Spring Boot) │
└─────────────────┘                        └────────┬────────┘
                                                   │
                                                   │ REST/gRPC
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                              ▼                    ▼                    ▼
                     ┌─────────────────┐  ┌──────────────┐   ┌──────────────┐
                     │   AI Service    │  │  Simulator   │   │  Real Tools  │
                     │   (Python)      │  │              │   │  (Adapters)  │
                     └─────────────────┘  └──────────────┘   └──────────────┘
```

## Components

### 1. Backend (Spring Boot)
- Incident management (CRUD operations, status tracking)
- Investigation management
- Action management (approve, reject, execute remediation)
- Report management
- WebSocket events (real-time updates)
- Calls AI service for analysis
- Calls simulator/real tools through adapters

**Port:** 8080

### 2. Frontend (React)
- Dashboard (incident overview, statistics, active investigations)
- Incident page (incident details, timeline, actions)
- Investigation page (AI agent progress visualization, evidence display)
- Timeline (incident chronology, investigation steps)
- Agent execution visualization (multi-agent workflow UI)
- Reports (incident reports, analytics)
- Settings (configuration, integrations)

**Port:** 3000

### 3. AI Service (Python)
- Single-agent investigation orchestration
- Evidence collection (fetch from backend adapters)
- Analysis (analyze evidence, identify patterns, determine root cause)
- Recommendations (suggest remediation actions)
- Callback delivery (send results back to backend)

**Single-Agent Architecture:**
- Single Gemini Agent - Analyzes all evidence and generates investigation results in one LLM call
  - Collects evidence from Kubernetes, Logs, Metrics, and Git adapters
  - Analyzes patterns and correlations across all evidence sources
  - Determines root cause with confidence score
  - Generates remediation recommendations

**Port:** 8000

### 4. Simulator
- Simulate production services
- Generate failures (service crashes, latency spikes, errors)
- Generate metrics (CPU, memory, request rates, error rates)
- Generate logs (application logs, error logs, access logs)
- Generate Kubernetes events (pod failures, deployments, scaling)
- Generate Git changes (commits, deployments, rollbacks)

**Port:** 8001

### 5. Local Development
- Manual service startup (no containerization)
- H2 in-memory database (embedded, no installation)
- Local Redis cache (optional)
- Development configuration files

## Technology Stack

### Backend
- Spring Boot 3.x

### Frontend
- React
- Tailwind CSS or Material-UI

### AI Service
- Python 3.11+
- FastAPI
- LangChain or LangGraph
- OpenAI API or Anthropic API
- Pydantic
- Asyncio
- gRPC server

### Simulator
- Python 3.11+ or Node.js
- FastAPI or Express
- In-memory data storage

## Directory Structure

```
ai-devops-incident-commander/
├── backend/                 # Spring Boot
│   ├── src/main/java/
│   │   └── com/devops/incident/
│   │       ├── controller/
│   │       ├── service/
│   │       ├── repository/
│   │       ├── model/
│   │       ├── adapter/
│   │       ├── config/
│   │       └── websocket/
│   ├── src/main/resources/
│   │   └── application.yml
│   └── pom.xml
├── frontend/                # React
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── ai-service/              # Python
│   ├── src/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── models/
│   │   ├── api/
│   │   └── main.py
│   ├── requirements.txt
│   └── pyproject.toml
├── simulator/               # Python/Node.js
│   ├── src/
│   │   ├── generators/
│   │   ├── scenarios/
│   │   ├── api/
│   │   └── main.py
│   ├── requirements.txt
│   └── pyproject.toml
├── deployment/              # Infrastructure
│   ├── docker/
│   ├── docker-compose.yml
│   ├── kubernetes/
│   ├── helm/
│   └── scripts/
└── README.md
```

## Quick Start

### Prerequisites
- Java 17+ (for backend development)
- Maven 3.9+ (for building backend)
- Node.js 18+ (for frontend development)
- Python 3.11+ (for AI service and simulator development)
- Redis (optional, for caching)

### Local Development Setup

**Step 1: Clone the repository**
```bash
git clone <repository-url>
cd ai-devops-incident-commander
```

**Step 2: No Database Setup Required**
- H2 in-memory database is embedded in Spring Boot
- No installation or configuration needed
- Database is created automatically on startup

**Step 3: Start services (open 4 terminal windows)**

**Terminal 1 - Backend (Spring Boot)**
```bash
cd backend
mvn spring-boot:run
```

**Terminal 2 - Frontend (React)**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 3 - AI Service (Python)**
```bash
cd ai-service
pip install -r requirements.txt
python src/main.py
```

**Terminal 4 - Simulator (Python, optional)**
```bash
cd simulator
pip install -r requirements.txt
python src/main.py
```

**Step 4: Access the application**
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8080
- AI Service: http://localhost:8000
- Simulator: http://localhost:8001 (optional)

## Usage

### 1. Create an Incident
```bash
curl -X POST http://localhost:8080/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Payment service latency spike",
    "description": "Payment service experiencing 5x latency",
    "severity": "high",
    "affectedServices": ["payment-api", "checkout-service"]
  }'
```

### 2. Start AI Investigation
```bash
curl -X POST http://localhost:8080/api/incidents/{id}/investigate
```

### 3. Monitor Investigation Progress
The frontend dashboard shows real-time investigation progress via WebSocket.

### 4. Review Recommendations
Once investigation completes, review AI-generated remediation recommendations.

### 5. Execute Actions
Approve and execute recommended actions through the UI or API.

## API Documentation

### Backend API
- Swagger/OpenAPI: http://localhost:8080/swagger-ui.html
- API endpoints documented in specification

### AI Service API
- FastAPI docs: http://localhost:8000/docs
- gRPC service definition in protobuf files

### Simulator API
- Simulator docs: http://localhost:8001/docs

## Configuration

### Backend Configuration
Edit `backend/src/main/resources/application.yml`:
- Database connection
- AI service endpoint
- JWT secret
- WebSocket configuration

### Frontend Configuration
Edit `frontend/src/config.ts`:
- API endpoints
- WebSocket URL
- Authentication settings

### AI Service Configuration
Edit `ai-service/src/config.py`:
- LLM API keys
- Agent configuration
- Tool settings

## Testing

### Run Tests

Backend:
```bash
cd backend
./mvnw test
```

Frontend:
```bash
cd frontend
npm test
```

AI Service:
```bash
cd ai-service
pytest
```

Simulator:
```bash
cd simulator
pytest
```

### Integration Testing
Use the simulator to generate failure scenarios and test the complete investigation workflow.

## Development Workflow

1. **Setup:** Follow Quick Start section above to install dependencies and start services
2. **Database:** H2 embedded database (no setup required, auto-created on startup)
3. **Services:** Start all 3 services in separate terminal windows (Backend, Frontend, AI Service)
4. **Frontend:** Access dashboard at `http://localhost:3000`
5. **Backend:** API available at `http://localhost:8080`
6. **H2 Console:** Database console available at `http://localhost:8080/h2-console`
7. **AI Service:** Available at `http://localhost:8000`
8. **Simulator:** Create failure scenarios via simulator API at `http://localhost:8001` (optional)
8. **Testing:** Use simulator to generate incidents and test AI analysis workflow

For detailed setup instructions, see **LOCAL_DEVELOPMENT_SETUP.md**

## Security

- JWT-based authentication
- Role-based access control
- Secure communication between services (TLS)
- API rate limiting
- Input validation and sanitization

## Monitoring

- Application logs via ELK stack
- Metrics via Prometheus
- Distributed tracing via Jaeger
- Health checks for all services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions, please open an issue on GitHub.

## Roadmap

- [ ] Support for additional monitoring tools (Datadog, New Relic)
- [ ] Multi-cloud support (AWS, GCP, Azure)
- [ ] Advanced AI models for root cause analysis
- [ ] Mobile application
- [ ] Integration with incident management tools (PagerDuty, Opsgenie)
- [ ] Automated rollback capabilities
- [ ] Predictive incident prevention

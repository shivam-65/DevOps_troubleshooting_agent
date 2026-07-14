# MCP Server for AI-Powered DevOps Incident Commander

This MCP server exposes 29 tools for incident management, investigation, and remediation to AI assistants like Cascade/Windsurf.

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Backend service running on `http://localhost:8080`
- Simulator service running on `http://localhost:8001`

### 2. Installation
```bash
cd mcp-server
pip install -r requirements.txt
cp .env.example .env
```

### 3. Start Services
```bash
# Terminal 1 - Backend
cd backend
mvn spring-boot:run

# Terminal 2 - Simulator
cd simulator
python -m src.main

# Terminal 3 - MCP Server (for testing)
cd mcp-server
python -m src.main
```

### 4. Configure Cascade/Windsurf
The configuration is already set in `.windsurf/mcp.json`. 
Restart Cascade/Windsurf to load the MCP server.

## Available Tools (29 total)

### Incident Management (5 tools)
- `create_incident` - Create new incident
- `list_incidents` - List with filters
- `get_incident` - Get incident details
- `update_incident` - Update incident
- `delete_incident` - Delete incident

### Investigation (4 tools)
- `trigger_investigation` - Start AI investigation
- `list_investigations` - List investigations
- `get_investigation` - Get investigation results
- `get_investigation_evidence` - Get collected evidence

### Evidence Collection (4 tools)
- `get_kubernetes_evidence` - Fetch pod events, deployments
- `get_logs_evidence` - Fetch error and application logs
- `get_metrics_evidence` - Fetch CPU, memory, latency metrics
- `get_git_evidence` - Fetch commits and deployments

### Action Management (6 tools)
- `create_action` - Create remediation action
- `list_actions` - List actions with filters
- `get_action` - Get action details
- `approve_action` - Approve action for execution
- `reject_action` - Reject action
- `execute_action` - Execute approved action

### Reports (3 tools)
- `generate_report` - Generate incident report
- `list_reports` - List reports
- `get_report` - Get report content

### Simulator Control (7 tools)
- `list_scenarios` - List failure scenarios
- `get_scenario` - Get scenario details
- `activate_scenario` - Activate failure scenario
- `deactivate_scenario` - Deactivate scenario
- `create_custom_scenario` - Create custom scenario
- `list_services` - List simulated services
- `add_service` - Add new service

## Testing in Cascade

Once configured, you can use natural language to interact with the tools:

```
"Create a critical incident for payment service outage"
"List all open incidents"
"Trigger an investigation for incident <id>"
"Show me the Kubernetes evidence for payment-api"
"Activate the oom-kill scenario for payment-api"
"Approve the restart action"
```

## Configuration

Edit `.env` file to change:
- `BACKEND_URL` - Backend API URL (default: http://localhost:8080)
- `SIMULATOR_URL` - Simulator URL (default: http://localhost:8001)
- `ADAPTER_MODE` - simulator or real (default: simulator)
- `HTTP_TIMEOUT` - Request timeout in seconds (default: 30)

## Troubleshooting

### MCP server not loading in Cascade
1. Check `.windsurf/mcp.json` exists
2. Restart Cascade/Windsurf
3. Check MCP settings in IDE

### Connection errors
1. Verify backend is running on port 8080
2. Verify simulator is running on port 8001
3. Check `.env` configuration

### Tool execution failures
1. Check backend/simulator logs
2. Verify API endpoints are accessible
3. Check MCP server logs

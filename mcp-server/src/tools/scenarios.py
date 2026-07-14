from typing import List
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
LIST_SCENARIOS_TOOL = Tool(
    name="list_scenarios",
    description="List all available failure scenarios and their status",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

GET_SCENARIO_TOOL = Tool(
    name="get_scenario",
    description="Get details of a specific scenario including affected evidence types",
    inputSchema={
        "type": "object",
        "properties": {
            "scenarioId": {"type": "string", "description": "Scenario ID (e.g., pod-crash, oom-kill)"}
        },
        "required": ["scenarioId"]
    }
)

ACTIVATE_SCENARIO_TOOL = Tool(
    name="activate_scenario",
    description="Activate a failure scenario to simulate production issues",
    inputSchema={
        "type": "object",
        "properties": {
            "scenarioId": {"type": "string", "description": "Scenario ID"},
            "targetServices": {"type": "array", "items": {"type": "string"}, "description": "Services to affect (default: [])"},
            "parameters": {"type": "object", "description": "Scenario-specific parameters"}
        },
        "required": ["scenarioId"]
    }
)

DEACTIVATE_SCENARIO_TOOL = Tool(
    name="deactivate_scenario",
    description="Deactivate an active failure scenario",
    inputSchema={
        "type": "object",
        "properties": {
            "scenarioId": {"type": "string", "description": "Scenario ID"}
        },
        "required": ["scenarioId"]
    }
)

CREATE_CUSTOM_SCENARIO_TOOL = Tool(
    name="create_custom_scenario",
    description="Create a custom failure scenario with specific effects",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Scenario name"},
            "description": {"type": "string", "description": "Scenario description"},
            "targetServices": {"type": "array", "items": {"type": "string"}, "description": "Services to affect"},
            "effects": {"type": "object", "description": "Custom effects per evidence type"},
            "duration": {"type": "string", "description": "Duration (ISO 8601, e.g., PT30M)"}
        },
        "required": ["name", "description"]
    }
)

LIST_SERVICES_TOOL = Tool(
    name="list_services",
    description="List all simulated services",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

ADD_SERVICE_TOOL = Tool(
    name="add_service",
    description="Add a new service to the simulated environment",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Service name"},
            "namespace": {"type": "string", "default": "production", "description": "Kubernetes namespace"},
            "replicas": {"type": "integer", "default": 2, "description": "Number of replicas"},
            "version": {"type": "string", "default": "v1.0.0", "description": "Service version"},
            "dependencies": {"type": "array", "items": {"type": "string"}, "description": "Dependent services"}
        },
        "required": ["name"]
    }
)


# Tool implementations
async def list_scenarios(arguments: dict) -> List[TextContent]:
    """List available scenarios"""
    try:
        result = await client.get("/api/scenarios", base_url=client.simulator_url)
        scenarios = result.get("scenarios", [])
        
        if not scenarios:
            return [TextContent(type="text", text="No scenarios available in the simulator")]
        
        output = "Available Failure Scenarios:\n\n"
        
        # Group by status
        active_scenarios = [s for s in scenarios if s.get("status") == "active"]
        inactive_scenarios = [s for s in scenarios if s.get("status") != "active"]
        
        if active_scenarios:
            output += "🔴 ACTIVE SCENARIOS:\n"
            for scenario in active_scenarios:
                output += format_scenario(scenario) + "\n"
            output += "\n"
        
        if inactive_scenarios:
            output += "⚪ AVAILABLE SCENARIOS:\n"
            for scenario in inactive_scenarios:
                output += format_scenario(scenario) + "\n"
        
        # Add common scenario IDs for reference
        output += "\n📌 Common scenario IDs:\n"
        output += "  • pod-crash - Pod enters CrashLoopBackOff\n"
        output += "  • oom-kill - Memory exhaustion → OOMKilled\n"
        output += "  • latency-spike - Latency multiplied 3-10x\n"
        output += "  • error-rate - Error rate surges to 10-30%\n"
        output += "  • deployment-failure - Failed deployment, ImagePullBackOff\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing scenarios: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_scenario(arguments: dict) -> List[TextContent]:
    """Get specific scenario details"""
    try:
        scenario_id = arguments["scenarioId"]
        result = await client.get(f"/api/scenarios/{scenario_id}", base_url=client.simulator_url)
        
        output = format_scenario(result)
        
        # Add affected evidence details if present
        if result.get("affectedEvidence"):
            evidence = result["affectedEvidence"]
            output += "\n\n📊 Affected Evidence Types:"
            if evidence.get("kubernetes"):
                output += "\n  • Kubernetes: " + ", ".join(evidence["kubernetes"])
            if evidence.get("logs"):
                output += "\n  • Logs: " + ", ".join(evidence["logs"])
            if evidence.get("metrics"):
                output += "\n  • Metrics: " + ", ".join(evidence["metrics"])
            if evidence.get("git"):
                output += "\n  • Git: " + ", ".join(evidence["git"])
        
        return [TextContent(
            type="text",
            text=f"Scenario Details:\n{output}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting scenario: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def activate_scenario(arguments: dict) -> List[TextContent]:
    """Activate a failure scenario"""
    try:
        scenario_id = arguments["scenarioId"]
        data = {
            "targetServices": arguments.get("targetServices", []),
            "parameters": arguments.get("parameters", {})
        }
        result = await client.post(f"/api/scenarios/{scenario_id}/activate", data=data, base_url=client.simulator_url)
        
        output = f"✅ Scenario activated successfully:\n{format_scenario(result)}"
        
        if result.get("targetServices"):
            output += f"\n\n🎯 Affecting services: {', '.join(result['targetServices'])}"
        
        output += "\n\n⚠️ Note: Simulated failures are now active. Evidence collection will show failure patterns."
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error activating scenario: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def deactivate_scenario(arguments: dict) -> List[TextContent]:
    """Deactivate a failure scenario"""
    try:
        scenario_id = arguments["scenarioId"]
        result = await client.post(f"/api/scenarios/{scenario_id}/deactivate", base_url=client.simulator_url)
        
        output = f"✅ Scenario deactivated successfully:\n{format_scenario(result)}"
        output += "\n\n✔️ Note: Simulated failures have been cleared. Services returning to normal."
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error deactivating scenario: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def create_custom_scenario(arguments: dict) -> List[TextContent]:
    """Create a custom failure scenario"""
    try:
        result = await client.post("/api/scenarios/custom", data=arguments, base_url=client.simulator_url)
        
        return [TextContent(
            type="text",
            text=f"Custom scenario created successfully:\n{format_scenario(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error creating custom scenario: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def list_services(arguments: dict) -> List[TextContent]:
    """List simulated services"""
    try:
        result = await client.get("/api/services", base_url=client.simulator_url)
        services = result.get("services", [])
        
        if not services:
            return [TextContent(type="text", text="No services registered in the simulator")]
        
        output = f"Simulated Services ({len(services)} total):\n\n"
        for service in services:
            output += format_service(service) + "\n" + "─" * 30 + "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing services: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def add_service(arguments: dict) -> List[TextContent]:
    """Add a new service to the simulator"""
    try:
        # Set defaults if not provided
        if "namespace" not in arguments:
            arguments["namespace"] = "production"
        if "replicas" not in arguments:
            arguments["replicas"] = 2
        if "version" not in arguments:
            arguments["version"] = "v1.0.0"
        if "dependencies" not in arguments:
            arguments["dependencies"] = []
        
        result = await client.post("/api/services", data=arguments, base_url=client.simulator_url)
        
        return [TextContent(
            type="text",
            text=f"Service added successfully:\n{format_service(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error adding service: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_scenario(scenario: dict) -> str:
    """Format scenario data for display"""
    status_emoji = "🔴" if scenario.get("status") == "active" else "⚪"
    
    output = f"""• ID: {scenario.get('id')}
• Name: {scenario.get('name')}
• Description: {scenario.get('description')}
• Status: {status_emoji} {scenario.get('status')}"""
    
    if scenario.get("targetServices"):
        output += f"\n• Target Services: {', '.join(scenario['targetServices'])}"
    
    if scenario.get("activatedAt"):
        output += f"\n• Activated At: {scenario['activatedAt']}"
    
    if scenario.get("deactivatedAt"):
        output += f"\n• Deactivated At: {scenario['deactivatedAt']}"
    
    if scenario.get("parameters"):
        output += f"\n• Parameters: {scenario['parameters']}"
    
    return output


def format_service(service: dict) -> str:
    """Format service data for display"""
    health_status = "✅" if service.get("healthyReplicas") == service.get("replicas") else "⚠️"
    
    output = f"""• Name: {service.get('name')}
• Namespace: {service.get('namespace')}
• Version: {service.get('version')}
• Replicas: {health_status} {service.get('healthyReplicas', 0)}/{service.get('replicas')} healthy"""
    
    if service.get("dependencies"):
        output += f"\n• Dependencies: {', '.join(service['dependencies'])}"
    else:
        output += "\n• Dependencies: None"
    
    if service.get("createdAt"):
        output += f"\n• Created: {service['createdAt']}"
    
    return output


# Tool registry
SCENARIO_TOOLS = [
    LIST_SCENARIOS_TOOL,
    GET_SCENARIO_TOOL,
    ACTIVATE_SCENARIO_TOOL,
    DEACTIVATE_SCENARIO_TOOL,
    CREATE_CUSTOM_SCENARIO_TOOL,
    LIST_SERVICES_TOOL,
    ADD_SERVICE_TOOL
]

SCENARIO_HANDLERS = {
    "list_scenarios": list_scenarios,
    "get_scenario": get_scenario,
    "activate_scenario": activate_scenario,
    "deactivate_scenario": deactivate_scenario,
    "create_custom_scenario": create_custom_scenario,
    "list_services": list_services,
    "add_service": add_service
}

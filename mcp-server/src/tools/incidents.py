from typing import List, Optional
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
CREATE_INCIDENT_TOOL = Tool(
    name="create_incident",
    description="Create a new production incident",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Short incident title (max 255 chars)"},
            "description": {"type": "string", "description": "Detailed description (max 5000 chars)"},
            "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"], "description": "Severity level"},
            "affectedServices": {"type": "array", "items": {"type": "string"}, "description": "Affected service names"},
            "assignee": {"type": "string", "description": "Assigned operator (max 100 chars)"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Categorization tags"}
        },
        "required": ["title", "description", "severity"]
    }
)

LIST_INCIDENTS_TOOL = Tool(
    name="list_incidents",
    description="List incidents with optional filters",
    inputSchema={
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"], "description": "Filter by status"},
            "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"], "description": "Filter by severity"},
            "search": {"type": "string", "description": "Search in title/description"},
            "page": {"type": "integer", "default": 0, "description": "Page number (0-indexed)"},
            "size": {"type": "integer", "default": 20, "description": "Page size (1-100)"},
            "sortBy": {"type": "string", "default": "createdAt", "description": "Sort field: createdAt, updatedAt, severity"},
            "sortDir": {"type": "string", "default": "desc", "enum": ["asc", "desc"], "description": "Sort direction"}
        }
    }
)

GET_INCIDENT_TOOL = Tool(
    name="get_incident",
    description="Get full details of a single incident",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Incident UUID"}
        },
        "required": ["id"]
    }
)

UPDATE_INCIDENT_TOOL = Tool(
    name="update_incident",
    description="Update an existing incident (partial update)",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Incident UUID"},
            "title": {"type": "string", "description": "New title"},
            "description": {"type": "string", "description": "New description"},
            "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"], "description": "New severity"},
            "status": {"type": "string", "enum": ["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"], "description": "New status"},
            "affectedServices": {"type": "array", "items": {"type": "string"}, "description": "Updated services list"},
            "assignee": {"type": "string", "description": "New assignee"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Updated tags"}
        },
        "required": ["id"]
    }
)

DELETE_INCIDENT_TOOL = Tool(
    name="delete_incident",
    description="Delete an incident and all related data (investigations, evidence, actions, reports)",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Incident UUID"}
        },
        "required": ["id"]
    }
)


# Tool implementations
async def create_incident(arguments: dict) -> List[TextContent]:
    """Create a new incident"""
    try:
        result = await client.post("/api/incidents", data=arguments)
        return [TextContent(
            type="text",
            text=f"Incident created successfully:\n{format_incident(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error creating incident: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def list_incidents(arguments: dict) -> List[TextContent]:
    """List incidents with filtering"""
    try:
        # Remove None values from params
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/incidents", params=params)
        
        incidents = result.get("content", [])
        total = result.get("totalElements", 0)
        pages = result.get("totalPages", 0)
        current_page = result.get("page", params.get("page", 0))
        
        if not incidents:
            return [TextContent(type="text", text="No incidents found matching the criteria.")]
        
        output = f"Found {total} incidents (page {current_page + 1}/{pages}):\n\n"
        for incident in incidents:
            output += format_incident(incident) + "\n" + "─" * 50 + "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing incidents: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_incident(arguments: dict) -> List[TextContent]:
    """Get specific incident details"""
    try:
        incident_id = arguments["id"]
        result = await client.get(f"/api/incidents/{incident_id}")
        return [TextContent(
            type="text",
            text=f"Incident Details:\n{format_incident(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting incident: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def update_incident(arguments: dict) -> List[TextContent]:
    """Update an incident"""
    try:
        incident_id = arguments.pop("id")
        # Only send non-None values for update
        update_data = {k: v for k, v in arguments.items() if v is not None}
        result = await client.put(f"/api/incidents/{incident_id}", data=update_data)
        return [TextContent(
            type="text",
            text=f"Incident updated successfully:\n{format_incident(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error updating incident: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def delete_incident(arguments: dict) -> List[TextContent]:
    """Delete an incident"""
    try:
        incident_id = arguments["id"]
        await client.delete(f"/api/incidents/{incident_id}")
        return [TextContent(
            type="text",
            text=f"Incident {incident_id} deleted successfully along with all related data."
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error deleting incident: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_incident(incident: dict) -> str:
    """Format incident data for display"""
    return f"""• ID: {incident.get('id')}
• Title: {incident.get('title')}
• Description: {incident.get('description')}
• Severity: {incident.get('severity')}
• Status: {incident.get('status')}
• Affected Services: {', '.join(incident.get('affectedServices', [])) or 'None'}
• Assignee: {incident.get('assignee') or 'Unassigned'}
• Tags: {', '.join(incident.get('tags', [])) or 'None'}
• Created: {incident.get('createdAt')}
• Updated: {incident.get('updatedAt')}
• Resolved: {incident.get('resolvedAt') or 'Not resolved'}
• Closed: {incident.get('closedAt') or 'Not closed'}"""


# Tool registry
INCIDENT_TOOLS = [
    CREATE_INCIDENT_TOOL,
    LIST_INCIDENTS_TOOL,
    GET_INCIDENT_TOOL,
    UPDATE_INCIDENT_TOOL,
    DELETE_INCIDENT_TOOL
]

INCIDENT_HANDLERS = {
    "create_incident": create_incident,
    "list_incidents": list_incidents,
    "get_incident": get_incident,
    "update_incident": update_incident,
    "delete_incident": delete_incident
}

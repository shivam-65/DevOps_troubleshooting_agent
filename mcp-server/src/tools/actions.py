from typing import List
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
CREATE_ACTION_TOOL = Tool(
    name="create_action",
    description="Create a remediation action",
    inputSchema={
        "type": "object",
        "properties": {
            "investigationId": {"type": "string", "description": "Investigation UUID"},
            "incidentId": {"type": "string", "description": "Incident UUID"},
            "type": {"type": "string", "enum": ["RESTART_SERVICE", "SCALE_UP", "ROLLBACK_DEPLOYMENT", "RUN_SCRIPT", "APPLY_CONFIG_CHANGE", "CLEAR_CACHE", "FAILOVER", "CUSTOM"], "description": "Action type"},
            "title": {"type": "string", "description": "Action title (max 255)"},
            "description": {"type": "string", "description": "Detailed description (max 5000)"},
            "command": {"type": "string", "description": "Command/script to execute (max 2000)"},
            "targetService": {"type": "string", "description": "Target service name (max 100)"},
            "parameters": {"type": "object", "description": "Additional parameters"},
            "risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"], "description": "Risk level"},
            "estimatedImpact": {"type": "string", "description": "Expected outcome (max 500)"}
        },
        "required": ["investigationId", "incidentId", "type", "title"]
    }
)

LIST_ACTIONS_TOOL = Tool(
    name="list_actions",
    description="List actions with optional filters",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Filter by incident"},
            "investigationId": {"type": "string", "description": "Filter by investigation"},
            "status": {"type": "string", "enum": ["PROPOSED", "APPROVED", "EXECUTING", "COMPLETED", "FAILED", "REJECTED"], "description": "Filter by status"},
            "page": {"type": "integer", "default": 0, "description": "Page number"},
            "size": {"type": "integer", "default": 20, "description": "Page size"}
        }
    }
)

GET_ACTION_TOOL = Tool(
    name="get_action",
    description="Get full action details",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Action UUID"}
        },
        "required": ["id"]
    }
)

APPROVE_ACTION_TOOL = Tool(
    name="approve_action",
    description="Approve a proposed action for execution",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Action UUID"},
            "approvedBy": {"type": "string", "description": "Person approving"}
        },
        "required": ["id", "approvedBy"]
    }
)

REJECT_ACTION_TOOL = Tool(
    name="reject_action",
    description="Reject a proposed or approved action",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Action UUID"},
            "reason": {"type": "string", "description": "Rejection reason"}
        },
        "required": ["id"]
    }
)

EXECUTE_ACTION_TOOL = Tool(
    name="execute_action",
    description="Execute an approved action",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Action UUID"}
        },
        "required": ["id"]
    }
)


# Tool implementations
async def create_action(arguments: dict) -> List[TextContent]:
    """Create a remediation action"""
    try:
        result = await client.post("/api/actions", data=arguments)
        return [TextContent(
            type="text",
            text=f"Action created successfully:\n{format_action(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error creating action: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def list_actions(arguments: dict) -> List[TextContent]:
    """List actions with filtering"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/actions", params=params)
        
        actions = result.get("content", [])
        total = result.get("totalElements", 0)
        
        if not actions:
            filter_desc = ""
            if params.get("incidentId"):
                filter_desc = f" for incident {params['incidentId']}"
            elif params.get("investigationId"):
                filter_desc = f" for investigation {params['investigationId']}"
            return [TextContent(type="text", text=f"No actions found{filter_desc}")]
        
        output = f"Found {total} actions:\n\n"
        for action in actions:
            output += format_action(action) + "\n" + "─" * 50 + "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing actions: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_action(arguments: dict) -> List[TextContent]:
    """Get specific action details"""
    try:
        action_id = arguments["id"]
        result = await client.get(f"/api/actions/{action_id}")
        return [TextContent(
            type="text",
            text=f"Action Details:\n{format_action(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting action: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def approve_action(arguments: dict) -> List[TextContent]:
    """Approve an action"""
    try:
        action_id = arguments["id"]
        approved_by = arguments["approvedBy"]
        result = await client.post(f"/api/actions/{action_id}/approve", data={"approvedBy": approved_by})
        return [TextContent(
            type="text",
            text=f"✅ Action approved successfully:\n{format_action(result)}\n\n"
                 f"Note: Action is now ready for execution. Use execute_action to run it."
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error approving action: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def reject_action(arguments: dict) -> List[TextContent]:
    """Reject an action"""
    try:
        action_id = arguments["id"]
        reason = arguments.get("reason")
        data = {"reason": reason} if reason else None
        result = await client.post(f"/api/actions/{action_id}/reject", data=data)
        return [TextContent(
            type="text",
            text=f"❌ Action rejected:\n{format_action(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error rejecting action: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def execute_action(arguments: dict) -> List[TextContent]:
    """Execute an action"""
    try:
        action_id = arguments["id"]
        result = await client.post(f"/api/actions/{action_id}/execute")
        return [TextContent(
            type="text",
            text=f"🚀 Action execution started:\n{format_action(result)}\n\n"
                 f"Note: Action is executing asynchronously. Check status for completion."
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error executing action: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_action(action: dict) -> str:
    """Format action data for display"""
    status_emoji = {
        "PROPOSED": "💡",
        "APPROVED": "✅",
        "EXECUTING": "🔄",
        "COMPLETED": "✔️",
        "FAILED": "❌",
        "REJECTED": "🚫"
    }.get(action.get("status"), "❓")
    
    risk_emoji = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🔴"
    }.get(action.get("risk"), "⚪")
    
    output = f"""• ID: {action.get('id')}
• Investigation ID: {action.get('investigationId')}
• Incident ID: {action.get('incidentId')}
• Type: {action.get('type')}
• Status: {status_emoji} {action.get('status')}
• Title: {action.get('title')}
• Description: {action.get('description') or 'N/A'}
• Target Service: {action.get('targetService') or 'N/A'}
• Risk: {risk_emoji} {action.get('risk') or 'N/A'}
• Estimated Impact: {action.get('estimatedImpact') or 'N/A'}"""
    
    if action.get("command"):
        output += f"\n• Command: {action['command'][:100]}..." if len(action['command']) > 100 else f"\n• Command: {action['command']}"
    
    if action.get("parameters"):
        output += f"\n• Parameters: {action['parameters']}"
    
    if action.get("approvedBy"):
        output += f"\n• Approved By: {action['approvedBy']} at {action.get('approvedAt')}"
    
    if action.get("executedAt"):
        output += f"\n• Executed At: {action['executedAt']}"
    
    if action.get("completedAt"):
        output += f"\n• Completed At: {action['completedAt']}"
    
    if action.get("executionResult"):
        output += f"\n• Execution Result: {action['executionResult']}"
    
    output += f"\n• Created: {action.get('createdAt')}"
    
    return output


# Tool registry
ACTION_TOOLS = [
    CREATE_ACTION_TOOL,
    LIST_ACTIONS_TOOL,
    GET_ACTION_TOOL,
    APPROVE_ACTION_TOOL,
    REJECT_ACTION_TOOL,
    EXECUTE_ACTION_TOOL
]

ACTION_HANDLERS = {
    "create_action": create_action,
    "list_actions": list_actions,
    "get_action": get_action,
    "approve_action": approve_action,
    "reject_action": reject_action,
    "execute_action": execute_action
}

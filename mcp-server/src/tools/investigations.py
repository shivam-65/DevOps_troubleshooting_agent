from typing import List
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
TRIGGER_INVESTIGATION_TOOL = Tool(
    name="trigger_investigation",
    description="Start an AI-powered investigation for an incident",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Incident UUID"},
            "priority": {"type": "string", "description": "Investigation priority"},
            "scope": {"type": "array", "items": {"type": "string"}, "description": "Evidence sources: kubernetes, logs, metrics, git"}
        },
        "required": ["incidentId"]
    }
)

LIST_INVESTIGATIONS_TOOL = Tool(
    name="list_investigations",
    description="List all investigations for a specific incident",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Incident UUID"}
        },
        "required": ["incidentId"]
    }
)

GET_INVESTIGATION_TOOL = Tool(
    name="get_investigation",
    description="Get detailed investigation results including summary, root cause, confidence, evidence, and recommended actions",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Incident UUID"},
            "investigationId": {"type": "string", "description": "Investigation UUID"}
        },
        "required": ["incidentId", "investigationId"]
    }
)

GET_INVESTIGATION_EVIDENCE_TOOL = Tool(
    name="get_investigation_evidence",
    description="Get all collected evidence for a specific investigation",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Incident UUID"},
            "investigationId": {"type": "string", "description": "Investigation UUID"}
        },
        "required": ["incidentId", "investigationId"]
    }
)


# Tool implementations
async def trigger_investigation(arguments: dict) -> List[TextContent]:
    """Trigger AI investigation for an incident"""
    try:
        incident_id = arguments["incidentId"]
        # Build request body with optional fields
        request_data = {}
        if "priority" in arguments:
            request_data["priority"] = arguments["priority"]
        if "scope" in arguments:
            request_data["scope"] = arguments["scope"]
        
        result = await client.post(
            f"/api/incidents/{incident_id}/investigations", 
            data=request_data if request_data else None
        )
        
        return [TextContent(
            type="text",
            text=f"Investigation triggered successfully:\n{format_investigation(result)}\n\n"
                 f"Note: Investigation runs asynchronously. Use get_investigation to check progress."
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error triggering investigation: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def list_investigations(arguments: dict) -> List[TextContent]:
    """List investigations for an incident"""
    try:
        incident_id = arguments["incidentId"]
        result = await client.get(f"/api/incidents/{incident_id}/investigations")
        
        if not result:
            return [TextContent(type="text", text=f"No investigations found for incident {incident_id}")]
        
        output = f"Investigations for incident {incident_id}:\n\n"
        for investigation in result:
            output += format_investigation(investigation) + "\n" + "─" * 50 + "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing investigations: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_investigation(arguments: dict) -> List[TextContent]:
    """Get detailed investigation results"""
    try:
        incident_id = arguments["incidentId"]
        investigation_id = arguments["investigationId"]
        result = await client.get(f"/api/incidents/{incident_id}/investigations/{investigation_id}")
        
        # Format the detailed investigation
        output = format_investigation(result)
        
        # Add evidence summary if present
        if result.get("evidence"):
            output += f"\n\n📊 Evidence Collected ({len(result['evidence'])} sources):"
            for evidence in result["evidence"][:3]:  # Show first 3
                output += f"\n  • {evidence.get('source')} - {evidence.get('type')}"
            if len(result["evidence"]) > 3:
                output += f"\n  ... and {len(result['evidence']) - 3} more"
        
        # Add actions summary if present
        if result.get("actions"):
            output += f"\n\n🔧 Recommended Actions ({len(result['actions'])}):"
            for action in result["actions"][:3]:  # Show first 3
                output += f"\n  • [{action.get('status')}] {action.get('title')} ({action.get('type')})"
            if len(result["actions"]) > 3:
                output += f"\n  ... and {len(result['actions']) - 3} more"
        
        return [TextContent(type="text", text=f"Investigation Details:\n{output}")]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting investigation: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_investigation_evidence(arguments: dict) -> List[TextContent]:
    """Get evidence for an investigation"""
    try:
        incident_id = arguments["incidentId"]
        investigation_id = arguments["investigationId"]
        result = await client.get(f"/api/incidents/{incident_id}/investigations/{investigation_id}/evidence")
        
        if not result:
            return [TextContent(type="text", text=f"No evidence found for investigation {investigation_id}")]
        
        output = f"Evidence for investigation {investigation_id}:\n\n"
        
        # Group evidence by source
        evidence_by_source = {}
        for evidence in result:
            source = evidence.get("source", "Unknown")
            if source not in evidence_by_source:
                evidence_by_source[source] = []
            evidence_by_source[source].append(evidence)
        
        # Format grouped evidence
        for source, items in evidence_by_source.items():
            output += f"📁 {source.upper()} ({len(items)} items):\n"
            for evidence in items:
                output += format_evidence(evidence) + "\n"
            output += "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting evidence: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_investigation(investigation: dict) -> str:
    """Format investigation data for display"""
    status_emoji = {
        "PENDING": "⏳",
        "IN_PROGRESS": "🔄",
        "COMPLETED": "✅",
        "FAILED": "❌"
    }.get(investigation.get("status"), "❓")
    
    return f"""• ID: {investigation.get('id')}
• Incident ID: {investigation.get('incidentId')}
• Status: {status_emoji} {investigation.get('status')}
• Summary: {investigation.get('summary') or 'Pending...'}
• Root Cause: {investigation.get('rootCause') or 'Not determined yet'}
• Confidence: {investigation.get('confidence') or 'N/A'}
• AI Model: {investigation.get('aiModelUsed') or 'N/A'}
• Started: {investigation.get('startedAt') or 'Not started'}
• Completed: {investigation.get('completedAt') or 'In progress'}
• Created: {investigation.get('createdAt')}"""


def format_evidence(evidence: dict) -> str:
    """Format evidence data for display"""
    # Try to extract key info from data field
    data_summary = ""
    if evidence.get("data"):
        data = evidence["data"]
        if isinstance(data, dict):
            # Show first few keys
            keys = list(data.keys())[:3]
            data_summary = f" (keys: {', '.join(keys)})"
        elif isinstance(data, list):
            data_summary = f" ({len(data)} items)"
    
    return f"""  • ID: {evidence.get('id')}
    Type: {evidence.get('type')}
    Collected: {evidence.get('collectedAt')}
    Data: {data_summary}"""


# Tool registry
INVESTIGATION_TOOLS = [
    TRIGGER_INVESTIGATION_TOOL,
    LIST_INVESTIGATIONS_TOOL,
    GET_INVESTIGATION_TOOL,
    GET_INVESTIGATION_EVIDENCE_TOOL
]

INVESTIGATION_HANDLERS = {
    "trigger_investigation": trigger_investigation,
    "list_investigations": list_investigations,
    "get_investigation": get_investigation,
    "get_investigation_evidence": get_investigation_evidence
}

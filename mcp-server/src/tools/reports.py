from typing import List
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
GENERATE_REPORT_TOOL = Tool(
    name="generate_report",
    description="Generate an incident report aggregating all data",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Incident UUID"},
            "title": {"type": "string", "description": "Report title (max 255)"},
            "format": {"type": "string", "enum": ["JSON", "PDF"], "description": "Report format (default: JSON)"}
        },
        "required": ["incidentId"]
    }
)

LIST_REPORTS_TOOL = Tool(
    name="list_reports",
    description="List reports with optional incident filter",
    inputSchema={
        "type": "object",
        "properties": {
            "incidentId": {"type": "string", "description": "Filter by incident"},
            "page": {"type": "integer", "default": 0, "description": "Page number"},
            "size": {"type": "integer", "default": 20, "description": "Page size"}
        }
    }
)

GET_REPORT_TOOL = Tool(
    name="get_report",
    description="Get full report content",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Report UUID"}
        },
        "required": ["id"]
    }
)


# Tool implementations
async def generate_report(arguments: dict) -> List[TextContent]:
    """Generate an incident report"""
    try:
        result = await client.post("/api/reports", data=arguments)
        return [TextContent(
            type="text",
            text=f"Report generated successfully:\n{format_report(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error generating report: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def list_reports(arguments: dict) -> List[TextContent]:
    """List reports with filtering"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/reports", params=params)
        
        reports = result.get("content", [])
        total = result.get("totalElements", 0)
        
        if not reports:
            filter_desc = ""
            if params.get("incidentId"):
                filter_desc = f" for incident {params['incidentId']}"
            return [TextContent(type="text", text=f"No reports found{filter_desc}")]
        
        output = f"Found {total} reports:\n\n"
        for report in reports:
            output += format_report(report) + "\n" + "─" * 50 + "\n"
        
        return [TextContent(type="text", text=output)]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error listing reports: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_report(arguments: dict) -> List[TextContent]:
    """Get specific report details"""
    try:
        report_id = arguments["id"]
        result = await client.get(f"/api/reports/{report_id}")
        
        # Format the report with content preview
        output = format_report(result)
        
        # Add content preview
        if result.get("content"):
            content = result["content"]
            if isinstance(content, str):
                # Show first part of content
                preview_length = 500
                if len(content) > preview_length:
                    output += f"\n\n📄 Content Preview:\n{content[:preview_length]}...\n\n(Total length: {len(content)} characters)"
                else:
                    output += f"\n\n📄 Content:\n{content}"
        
        return [TextContent(
            type="text",
            text=f"Report Details:\n{output}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error getting report: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_report(report: dict) -> str:
    """Format report data for display"""
    format_emoji = {
        "JSON": "📋",
        "PDF": "📑"
    }.get(report.get("format"), "📄")
    
    output = f"""• ID: {report.get('id')}
• Incident ID: {report.get('incidentId')}
• Title: {report.get('title')}
• Format: {format_emoji} {report.get('format')}
• Generated At: {report.get('generatedAt')}
• Created At: {report.get('createdAt')}"""
    
    if report.get("metadata"):
        output += f"\n• Metadata: {report['metadata']}"
    
    return output


# Tool registry
REPORT_TOOLS = [
    GENERATE_REPORT_TOOL,
    LIST_REPORTS_TOOL,
    GET_REPORT_TOOL
]

REPORT_HANDLERS = {
    "generate_report": generate_report,
    "list_reports": list_reports,
    "get_report": get_report
}

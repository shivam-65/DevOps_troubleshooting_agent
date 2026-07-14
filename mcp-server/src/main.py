#!/usr/bin/env python3
"""
MCP Server for AI-Powered DevOps Incident Commander
Exposes incident management, investigation, and remediation tools via MCP protocol
"""

import sys
import logging
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response

# Import tool modules
from src.tools.incidents import INCIDENT_TOOLS, INCIDENT_HANDLERS
from src.tools.investigations import INVESTIGATION_TOOLS, INVESTIGATION_HANDLERS
from src.tools.evidence import EVIDENCE_TOOLS, EVIDENCE_HANDLERS
from src.tools.actions import ACTION_TOOLS, ACTION_HANDLERS
from src.tools.reports import REPORT_TOOLS, REPORT_HANDLERS
from src.tools.scenarios import SCENARIO_TOOLS, SCENARIO_HANDLERS
from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("devops-incident-commander")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    all_tools = (
        INCIDENT_TOOLS +
        INVESTIGATION_TOOLS +
        EVIDENCE_TOOLS +
        ACTION_TOOLS +
        REPORT_TOOLS +
        SCENARIO_TOOLS
    )
    
    logger.info(f"Listing {len(all_tools)} tools")
    return all_tools


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    # Route to appropriate handler
    all_handlers = {
        **INCIDENT_HANDLERS,
        **INVESTIGATION_HANDLERS,
        **EVIDENCE_HANDLERS,
        **ACTION_HANDLERS,
        **REPORT_HANDLERS,
        **SCENARIO_HANDLERS
    }
    
    handler = all_handlers.get(name)
    if not handler:
        error_msg = f"Unknown tool '{name}'. Available tools: {', '.join(all_handlers.keys())}"
        logger.error(error_msg)
        return [TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]
    
    try:
        result = await handler(arguments)
        logger.info(f"Tool {name} executed successfully")
        return result
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(
            type="text",
            text=error_msg
        )]


def main():
    """Main entry point for MCP server"""
    settings = get_settings()
    port = 8000

    logger.info("=" * 60)
    logger.info("Starting MCP Server for DevOps Incident Commander")
    logger.info(f"Backend URL: {settings.backend_url}")
    logger.info(f"Simulator URL: {settings.simulator_url}")
    logger.info(f"Adapter Mode: {settings.adapter_mode}")
    logger.info(f"HTTP Timeout: {settings.http_timeout}s")
    logger.info("=" * 60)

    # Count tools
    total_tools = len(INCIDENT_TOOLS + INVESTIGATION_TOOLS + EVIDENCE_TOOLS +
                     ACTION_TOOLS + REPORT_TOOLS + SCENARIO_TOOLS)
    logger.info(f"Registered {total_tools} tools:")
    logger.info(f"  • Incident Management: {len(INCIDENT_TOOLS)} tools")
    logger.info(f"  • Investigation: {len(INVESTIGATION_TOOLS)} tools")
    logger.info(f"  • Evidence Adapters: {len(EVIDENCE_TOOLS)} tools")
    logger.info(f"  • Action Management: {len(ACTION_TOOLS)} tools")
    logger.info(f"  • Reports: {len(REPORT_TOOLS)} tools")
    logger.info(f"  • Simulator Control: {len(SCENARIO_TOOLS)} tools")

    # Run SSE/HTTP server on port 8000
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/mcp", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    logger.info(f"Starting HTTP/SSE server on port {port}...")
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

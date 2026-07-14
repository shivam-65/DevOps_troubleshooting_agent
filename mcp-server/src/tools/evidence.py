from typing import List
from mcp.types import Tool, TextContent
from src.client import client
import httpx


# Tool definitions
GET_KUBERNETES_EVIDENCE_TOOL = Tool(
    name="get_kubernetes_evidence",
    description="Fetch Kubernetes evidence: pod events, deployment status, node conditions",
    inputSchema={
        "type": "object",
        "properties": {
            "services": {"type": "string", "description": "Comma-separated service names"},
            "namespace": {"type": "string", "default": "default", "description": "Kubernetes namespace"},
            "types": {"type": "string", "description": "Evidence types: pod_events, deployments, nodes"},
            "since": {"type": "string", "description": "Start time (ISO 8601)"},
            "until": {"type": "string", "description": "End time (ISO 8601)"}
        }
    }
)

GET_LOGS_EVIDENCE_TOOL = Tool(
    name="get_logs_evidence",
    description="Fetch log evidence: error logs, application logs, access logs",
    inputSchema={
        "type": "object",
        "properties": {
            "services": {"type": "string", "description": "Comma-separated service names"},
            "level": {"type": "string", "enum": ["ERROR", "WARN", "INFO", "DEBUG"], "description": "Log level filter"},
            "type": {"type": "string", "description": "Log type: error, application, access"},
            "since": {"type": "string", "description": "Start time (ISO 8601)"},
            "until": {"type": "string", "description": "End time (ISO 8601)"},
            "limit": {"type": "integer", "default": 100, "description": "Max entries"}
        }
    }
)

GET_METRICS_EVIDENCE_TOOL = Tool(
    name="get_metrics_evidence",
    description="Fetch metrics time-series: CPU, memory, request rate, error rate, latency percentiles",
    inputSchema={
        "type": "object",
        "properties": {
            "services": {"type": "string", "description": "Comma-separated service names"},
            "metrics": {"type": "string", "description": "Metric types: cpu, memory, request_rate, error_rate, latency"},
            "from": {"type": "string", "description": "Start time (ISO 8601)"},
            "to": {"type": "string", "description": "End time (ISO 8601)"},
            "step": {"type": "string", "default": "1m", "description": "Data point interval: 1m, 5m, 15m"}
        }
    }
)

GET_GIT_EVIDENCE_TOOL = Tool(
    name="get_git_evidence",
    description="Fetch Git evidence: recent commits, deployments, rollbacks",
    inputSchema={
        "type": "object",
        "properties": {
            "services": {"type": "string", "description": "Comma-separated service names"},
            "since": {"type": "string", "description": "Start time (ISO 8601)"},
            "until": {"type": "string", "description": "End time (ISO 8601)"},
            "limit": {"type": "integer", "default": 20, "description": "Max entries"}
        }
    }
)


# Tool implementations
async def get_kubernetes_evidence(arguments: dict) -> List[TextContent]:
    """Fetch Kubernetes evidence"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/adapters/kubernetes", params=params)
        return [TextContent(
            type="text",
            text=f"Kubernetes Evidence:\n{format_kubernetes_evidence(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error fetching Kubernetes evidence: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_logs_evidence(arguments: dict) -> List[TextContent]:
    """Fetch logs evidence"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/adapters/logs", params=params)
        return [TextContent(
            type="text",
            text=f"Logs Evidence:\n{format_logs_evidence(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error fetching logs evidence: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_metrics_evidence(arguments: dict) -> List[TextContent]:
    """Fetch metrics evidence"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/adapters/metrics", params=params)
        return [TextContent(
            type="text",
            text=f"Metrics Evidence:\n{format_metrics_evidence(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error fetching metrics evidence: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def get_git_evidence(arguments: dict) -> List[TextContent]:
    """Fetch Git evidence"""
    try:
        params = {k: v for k, v in arguments.items() if v is not None}
        result = await client.get("/api/adapters/git", params=params)
        return [TextContent(
            type="text",
            text=f"Git Evidence:\n{format_git_evidence(result)}"
        )]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except TimeoutError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"Error fetching Git evidence: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


def format_kubernetes_evidence(data: dict) -> str:
    """Format Kubernetes evidence for display"""
    output = "\n"
    
    if "podEvents" in data and data["podEvents"]:
        output += "🔸 Pod Events:\n"
        for pod in data["podEvents"][:5]:  # Show first 5
            status_emoji = "❌" if pod.get("status") in ["CrashLoopBackOff", "Error", "OOMKilled"] else "✅"
            output += f"  {status_emoji} {pod.get('podName')}: {pod.get('status')} (restarts: {pod.get('restarts', 0)})\n"
            if pod.get("message"):
                output += f"      Message: {pod.get('message')}\n"
        if len(data["podEvents"]) > 5:
            output += f"  ... and {len(data['podEvents']) - 5} more pods\n"
    
    if "deployments" in data and data["deployments"]:
        output += "\n🔸 Deployments:\n"
        for dep in data["deployments"]:
            ready = dep.get("readyReplicas", 0)
            total = dep.get("replicas", 0)
            status_emoji = "✅" if ready == total else "⚠️"
            output += f"  {status_emoji} {dep.get('name')}: {ready}/{total} ready\n"
            if dep.get("conditions"):
                for cond in dep["conditions"]:
                    if cond.get("type") == "Progressing" and cond.get("status") == "False":
                        output += f"      ⚠️ {cond.get('message')}\n"
    
    if "nodeStatus" in data and data["nodeStatus"]:
        output += "\n🔸 Node Status:\n"
        for node in data["nodeStatus"]:
            status_emoji = "✅" if node.get("status") == "Ready" else "❌"
            output += f"  {status_emoji} {node.get('name')}: {node.get('status')}\n"
            if node.get("conditions"):
                for cond in node["conditions"]:
                    if cond.get("status") != "False":
                        output += f"      {cond.get('type')}: {cond.get('message', 'OK')}\n"
    
    return output if output.strip() else "\nNo Kubernetes evidence available"


def format_logs_evidence(data: dict) -> str:
    """Format logs evidence for display"""
    output = "\n"
    
    if "errorLogs" in data and data["errorLogs"]:
        output += f"🔴 Error Logs ({len(data['errorLogs'])} entries):\n"
        for log in data["errorLogs"][:5]:  # Show first 5
            output += f"  [{log.get('timestamp')}] {log.get('service')}:\n"
            output += f"    {log.get('message')}\n"
            if log.get("stackTrace"):
                output += f"    Stack: {log['stackTrace'][:200]}...\n"
        if len(data["errorLogs"]) > 5:
            output += f"  ... and {len(data['errorLogs']) - 5} more errors\n"
    
    if "applicationLogs" in data and data["applicationLogs"]:
        output += f"\n📝 Application Logs ({len(data['applicationLogs'])} entries):\n"
        for log in data["applicationLogs"][:3]:
            level_emoji = {"ERROR": "🔴", "WARN": "🟡", "INFO": "🔵", "DEBUG": "⚪"}.get(log.get("level"), "⚫")
            output += f"  {level_emoji} [{log.get('timestamp')}] {log.get('service')}: {log.get('message')}\n"
        if len(data["applicationLogs"]) > 3:
            output += f"  ... and {len(data['applicationLogs']) - 3} more logs\n"
    
    if "accessLogs" in data and data["accessLogs"]:
        output += f"\n🌐 Access Logs ({len(data['accessLogs'])} entries):\n"
        for log in data["accessLogs"][:3]:
            status = log.get("statusCode", 0)
            status_emoji = "✅" if 200 <= status < 300 else "❌" if status >= 400 else "⚠️"
            output += f"  {status_emoji} {log.get('method')} {log.get('path')} - {status} ({log.get('responseTime')}ms)\n"
    
    return output if output.strip() else "\nNo logs evidence available"


def format_metrics_evidence(data: dict) -> str:
    """Format metrics evidence for display"""
    output = "\n"
    
    if "cpu" in data and data["cpu"]:
        output += "💻 CPU Metrics:\n"
        for metric in data["cpu"]:
            service = metric.get("service")
            values = metric.get("values", [])
            if values:
                latest = values[-1]
                avg = sum(v.get("value", 0) for v in values) / len(values)
                output += f"  • {service}: Current={latest.get('value', 0):.1f}%, Avg={avg:.1f}%\n"
    
    if "memory" in data and data["memory"]:
        output += "\n💾 Memory Metrics:\n"
        for metric in data["memory"]:
            service = metric.get("service")
            values = metric.get("values", [])
            if values:
                latest = values[-1]
                avg = sum(v.get("value", 0) for v in values) / len(values)
                output += f"  • {service}: Current={latest.get('value', 0):.0f}MB, Avg={avg:.0f}MB\n"
    
    if "errorRate" in data and data["errorRate"]:
        output += "\n❌ Error Rate:\n"
        for metric in data["errorRate"]:
            service = metric.get("service")
            values = metric.get("values", [])
            if values:
                latest = values[-1]
                avg = sum(v.get("value", 0) for v in values) / len(values)
                status_emoji = "🔴" if latest.get("value", 0) > 5 else "🟡" if latest.get("value", 0) > 1 else "🟢"
                output += f"  {status_emoji} {service}: Current={latest.get('value', 0):.1f}%, Avg={avg:.1f}%\n"
    
    if "latency" in data and data["latency"]:
        output += "\n⏱️ Latency Metrics:\n"
        for service, percentiles in data["latency"].items():
            if isinstance(percentiles, dict):
                p50 = percentiles.get("p50", [])
                p95 = percentiles.get("p95", [])
                p99 = percentiles.get("p99", [])
                
                if p50 and p50[0].get("values"):
                    latest_p50 = p50[0]["values"][-1].get("value", 0)
                    output += f"  • {service}: P50={latest_p50:.0f}ms"
                    
                    if p95 and p95[0].get("values"):
                        latest_p95 = p95[0]["values"][-1].get("value", 0)
                        output += f", P95={latest_p95:.0f}ms"
                    
                    if p99 and p99[0].get("values"):
                        latest_p99 = p99[0]["values"][-1].get("value", 0)
                        output += f", P99={latest_p99:.0f}ms"
                    
                    output += "\n"
    
    return output if output.strip() else "\nNo metrics evidence available"


def format_git_evidence(data: dict) -> str:
    """Format Git evidence for display"""
    output = "\n"
    
    if "recentCommits" in data and data["recentCommits"]:
        output += f"📝 Recent Commits ({len(data['recentCommits'])}):\n"
        for commit in data["recentCommits"][:5]:
            output += f"  • {commit.get('shortSha', 'unknown')}: {commit.get('message', 'No message')}\n"
            output += f"    Author: {commit.get('author')}, Service: {commit.get('service')}\n"
            output += f"    Time: {commit.get('timestamp')}\n"
        if len(data["recentCommits"]) > 5:
            output += f"  ... and {len(data['recentCommits']) - 5} more commits\n"
    
    if "recentDeployments" in data and data["recentDeployments"]:
        output += f"\n🚀 Recent Deployments ({len(data['recentDeployments'])}):\n"
        for deploy in data["recentDeployments"]:
            status_emoji = "✅" if deploy.get("status") == "success" else "❌"
            output += f"  {status_emoji} {deploy.get('service')} v{deploy.get('version')} to {deploy.get('environment')}\n"
            output += f"    Deployed: {deploy.get('timestamp')}\n"
            if deploy.get("commitSha"):
                output += f"    Commit: {deploy.get('commitSha')}\n"
    
    if "rollbacks" in data and data["rollbacks"]:
        output += f"\n↩️ Rollbacks ({len(data['rollbacks'])}):\n"
        for rollback in data["rollbacks"]:
            output += f"  • {rollback.get('service')}: {rollback.get('fromVersion')} → {rollback.get('toVersion')}\n"
            output += f"    Reason: {rollback.get('reason', 'Unknown')}\n"
            output += f"    Time: {rollback.get('timestamp')}\n"
    
    return output if output.strip() else "\nNo Git evidence available"


# Tool registry
EVIDENCE_TOOLS = [
    GET_KUBERNETES_EVIDENCE_TOOL,
    GET_LOGS_EVIDENCE_TOOL,
    GET_METRICS_EVIDENCE_TOOL,
    GET_GIT_EVIDENCE_TOOL
]

EVIDENCE_HANDLERS = {
    "get_kubernetes_evidence": get_kubernetes_evidence,
    "get_logs_evidence": get_logs_evidence,
    "get_metrics_evidence": get_metrics_evidence,
    "get_git_evidence": get_git_evidence
}

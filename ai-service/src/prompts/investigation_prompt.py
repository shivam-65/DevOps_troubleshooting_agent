import json
from typing import Any

from src.models.evidence import CollectedEvidence
from src.models.requests import IncidentContext
from src.prompts.output_schema import OUTPUT_SCHEMA


def _format_kubernetes(data: dict[str, Any] | None) -> str:
    if not data:
        return "No Kubernetes evidence available."
    lines: list[str] = []

    pod_events = data.get("podEvents", [])
    if pod_events:
        lines.append("Pod Status:")
        for pod in pod_events:
            name = pod.get("podName", "unknown")
            status = pod.get("status", "unknown")
            restarts = pod.get("restarts", 0)
            reason = pod.get("reason", "")
            reason_str = f", reason: {reason}" if reason else ""
            lines.append(f"- {name}: {status} ({restarts} restarts{reason_str})")
            containers = pod.get("containers", [])
            for c in containers:
                term = c.get("lastTerminationReason", "")
                term_str = f", last terminated: {term}" if term else ""
                lines.append(f"  Container {c.get('name','?')}: ready={c.get('ready', False)}, restarts={c.get('restartCount', 0)}{term_str}")
            events = pod.get("events", [])
            for ev in events:
                lines.append(f"  Event: {ev}")

    deployments = data.get("deployments", [])
    if deployments:
        lines.append("\nDeployment Status:")
        for dep in deployments:
            name = dep.get("name", "unknown")
            ready = dep.get("readyReplicas", 0)
            total = dep.get("replicas", 0)
            unavail = dep.get("unavailableReplicas", 0)
            lines.append(f"- {name}: {ready}/{total} replicas ready, {unavail} unavailable")

    return "\n".join(lines) if lines else "No relevant Kubernetes evidence."


def _format_logs(data: dict[str, Any] | None) -> str:
    if not data:
        return "No log evidence available."
    lines: list[str] = []

    for key in ("errorLogs", "applicationLogs"):
        entries = data.get(key, [])
        if entries:
            lines.append(f"{key}:")
            for entry in entries[:20]:
                ts = entry.get("timestamp", "")
                level = entry.get("level", "")
                svc = entry.get("service", "")
                msg = entry.get("message", "")
                lines.append(f"[{ts}] {level} {svc} - {msg}")
                stack = entry.get("stackTrace")
                if stack:
                    for st_line in str(stack).split("\n")[:5]:
                        lines.append(f"  {st_line}")

    return "\n".join(lines) if lines else "No relevant log evidence."


def _format_metrics(data: dict[str, Any] | None) -> str:
    if not data:
        return "No metrics evidence available."
    lines: list[str] = []

    for metric_key in ("cpu", "memory", "requestRate", "errorRate"):
        series_list = data.get(metric_key, [])
        if series_list:
            lines.append(f"\n{metric_key}:")
            for series in series_list:
                svc = series.get("service", "unknown")
                unit = series.get("unit", "")
                points = series.get("dataPoints", [])
                if points:
                    values = [p.get("value", 0) for p in points]
                    avg_val = sum(values) / len(values) if values else 0
                    max_val = max(values) if values else 0
                    max_ts = ""
                    for p in points:
                        if p.get("value") == max_val:
                            max_ts = p.get("timestamp", "")
                            break
                    lines.append(f"- {svc}: avg {avg_val:.1f}{unit}, max {max_val:.1f}{unit} at {max_ts}")

    latency = data.get("latency", {})
    if latency:
        lines.append("\nLatency:")
        for pctl in ("p50", "p95", "p99"):
            series_list = latency.get(pctl, [])
            for series in series_list:
                svc = series.get("service", "unknown")
                points = series.get("dataPoints", [])
                if points:
                    values = [p.get("value", 0) for p in points]
                    avg_val = sum(values) / len(values) if values else 0
                    max_val = max(values) if values else 0
                    lines.append(f"- {svc} {pctl}: avg {avg_val:.0f}ms, max {max_val:.0f}ms")

    return "\n".join(lines) if lines else "No relevant metrics evidence."


def _format_git(data: dict[str, Any] | None) -> str:
    if not data:
        return "No Git evidence available."
    lines: list[str] = []

    commits = data.get("recentCommits", [])
    if commits:
        lines.append("Recent Commits:")
        for c in commits[:10]:
            sha = c.get("shortSha", c.get("sha", "?")[:7])
            author = c.get("author", "unknown")
            msg = c.get("message", "")
            ts = c.get("timestamp", "")
            adds = c.get("totalAdditions", 0)
            dels = c.get("totalDeletions", 0)
            lines.append(f"- {sha} ({ts}) by {author}: \"{msg}\" (+{adds}, -{dels})")

    deployments = data.get("recentDeployments", [])
    if deployments:
        lines.append("\nRecent Deployments:")
        for d in deployments:
            ver = d.get("version", "?")
            ts = d.get("timestamp", "")
            deployer = d.get("deployer", "?")
            status = d.get("status", "?")
            lines.append(f"- {ver} deployed at {ts} by {deployer} (status: {status})")

    return "\n".join(lines) if lines else "No relevant Git evidence."


def build_investigation_prompt(
    incident: IncidentContext,
    evidence: CollectedEvidence,
) -> str:
    created = incident.createdAt.isoformat() if incident.createdAt else "unknown"

    prompt = f"""## Incident Details

**Title:** {incident.title}
**Description:** {incident.description}
**Severity:** {incident.severity}
**Affected Services:** {', '.join(incident.affectedServices)}
**Created At:** {created}

## Evidence

### Kubernetes Evidence
{_format_kubernetes(evidence.kubernetes)}

### Logs Evidence
{_format_logs(evidence.logs)}

### Metrics Evidence
{_format_metrics(evidence.metrics)}

### Git Evidence
{_format_git(evidence.git)}

## Task

Analyze the above incident and evidence. Provide your analysis in the following JSON format:

{OUTPUT_SCHEMA}

IMPORTANT: Return ONLY valid JSON. Do not include any markdown formatting, code fences, or extra text."""

    return prompt

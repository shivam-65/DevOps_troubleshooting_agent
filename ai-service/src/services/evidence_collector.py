import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from src.adapters.kubernetes_adapter import KubernetesAdapter
from src.adapters.logs_adapter import LogsAdapter
from src.adapters.metrics_adapter import MetricsAdapter
from src.adapters.git_adapter import GitAdapter
from src.models.evidence import CollectedEvidence
from src.utils.logger import get_logger

logger = get_logger(__name__)

ADAPTER_MAP = {
    "kubernetes": KubernetesAdapter,
    "logs": LogsAdapter,
    "metrics": MetricsAdapter,
    "git": GitAdapter,
}


async def _safe_fetch(
    adapter_name: str,
    adapter_cls: type,
    services: list[str],
    since: str,
    until: str,
) -> tuple[str, dict[str, Any] | None, str | None]:
    try:
        adapter = adapter_cls()
        data = await adapter.fetch(services, since=since, until=until)
        logger.info("evidence_collected", adapter=adapter_name, keys=list(data.keys()) if data else [])
        return adapter_name, data, None
    except Exception as e:
        error_msg = f"{adapter_name} adapter failed: {e}"
        logger.warning("evidence_collection_failed", adapter=adapter_name, error=str(e))
        return adapter_name, None, error_msg


async def collect_evidence(
    services: list[str],
    scope: list[str],
    incident_created: datetime | None = None,
) -> CollectedEvidence:
    now = datetime.now(timezone.utc)
    since_dt = (incident_created - timedelta(hours=1)) if incident_created else (now - timedelta(hours=1))
    since_str = since_dt.isoformat()
    until_str = now.isoformat()

    logger.info("evidence_collection_start", scope=scope, services=services)

    tasks = []
    for name in scope:
        cls = ADAPTER_MAP.get(name)
        if cls:
            tasks.append(_safe_fetch(name, cls, services, since_str, until_str))
        else:
            logger.warning("unknown_adapter", adapter=name)

    results = await asyncio.gather(*tasks)

    evidence = CollectedEvidence()
    for adapter_name, data, error in results:
        if error:
            evidence.errors.append(error)
        if data:
            setattr(evidence, adapter_name, data)

    logger.info(
        "evidence_collection_complete",
        collected=[n for n, d, _ in results if d],
        errors=evidence.errors,
    )
    return evidence

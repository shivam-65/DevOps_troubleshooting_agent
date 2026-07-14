from typing import Optional

from fastapi import APIRouter, Query, Request

from src.generators.base_generator import TimeRange
from src.generators.kubernetes_generator import KubernetesGenerator
from src.generators.logs_generator import LogsGenerator
from src.generators.metrics_generator import MetricsGenerator
from src.generators.git_generator import GitGenerator
from src.state.memory_store import memory_store
from src.utils.time_utils import default_since, default_until

router = APIRouter(prefix="/api/adapters", tags=["Adapters"])

kubernetes_gen = KubernetesGenerator()
logs_gen = LogsGenerator()
metrics_gen = MetricsGenerator()
git_gen = GitGenerator()


@router.get("/kubernetes")
async def get_kubernetes_evidence(
    services: Optional[str] = Query(None, description="Comma-separated service names"),
    namespace: Optional[str] = Query("production", description="Kubernetes namespace"),
    types: Optional[str] = Query(None, description="Evidence types: pod_events, deployments, nodes"),
    since: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    until: Optional[str] = Query(None, description="End time (ISO 8601)"),
):
    svc_list = [s.strip() for s in services.split(",")] if services else []
    time_range = TimeRange(since=default_since(since), until=default_until(until))
    active = memory_store.get_active_scenarios()
    return kubernetes_gen.generate(svc_list, time_range, active, namespace=namespace or "production")


@router.get("/logs")
async def get_logs_evidence(
    services: Optional[str] = Query(None, description="Comma-separated service names"),
    level: Optional[str] = Query(None, description="Log level filter"),
    type: Optional[str] = Query(None, description="Log type: error, application, access"),
    since: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    until: Optional[str] = Query(None, description="End time (ISO 8601)"),
    limit: Optional[int] = Query(100, description="Max entries"),
):
    svc_list = [s.strip() for s in services.split(",")] if services else []
    time_range = TimeRange(since=default_since(since), until=default_until(until))
    active = memory_store.get_active_scenarios()
    return logs_gen.generate(
        svc_list, time_range, active,
        level=level, type=type, limit=limit,
    )


@router.get("/metrics")
async def get_metrics_evidence(
    request: Request,
    services: Optional[str] = Query(None, description="Comma-separated service names"),
    metrics: Optional[str] = Query(None, description="Metric types: cpu, memory, request_rate, error_rate, latency"),
    since: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    until: Optional[str] = Query(None, description="End time (ISO 8601)"),
    step: Optional[str] = Query("1m", description="Data point interval"),
):
    # Accept both 'from'/'to' (spec) and 'since'/'until' (backend adapter sends these)
    start = since or request.query_params.get("from")
    end = until or request.query_params.get("to")
    svc_list = [s.strip() for s in services.split(",")] if services else []
    time_range = TimeRange(since=default_since(start), until=default_until(end))
    active = memory_store.get_active_scenarios()
    return metrics_gen.generate(
        svc_list, time_range, active,
        step=step, metrics=metrics,
    )


@router.get("/git")
async def get_git_evidence(
    services: Optional[str] = Query(None, description="Comma-separated service names"),
    since: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    until: Optional[str] = Query(None, description="End time (ISO 8601)"),
    limit: Optional[int] = Query(20, description="Max entries"),
):
    svc_list = [s.strip() for s in services.split(",")] if services else []
    time_range = TimeRange(since=default_since(since, default_hours=24), until=default_until(until))
    active = memory_store.get_active_scenarios()
    return git_gen.generate(svc_list, time_range, active, limit=limit)

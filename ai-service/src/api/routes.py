from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.config.settings import get_settings
from src.models.requests import InvestigationRequest
from src.models.responses import (
    InvestigationAcceptedResponse,
    HealthResponse,
    ComponentHealth,
)
from src.services.investigation_service import run_investigation
from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/investigate", response_model=InvestigationAcceptedResponse, status_code=202)
async def start_investigation(request: InvestigationRequest, background_tasks: BackgroundTasks):
    logger.info(
        "investigation_request_received",
        investigationId=request.investigationId,
        incidentId=request.incidentId,
    )
    background_tasks.add_task(run_investigation, request)
    return InvestigationAcceptedResponse(
        investigationId=request.investigationId,
        message="Investigation started",
        estimatedDuration="PT3M",
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    now = datetime.now(timezone.utc)

    # Check Gemini
    gemini_svc = GeminiService()
    gemini_healthy, gemini_error = await gemini_svc.check_health()

    # Check backend connection (200 or 503 both mean backend is reachable)
    backend_healthy = False
    backend_error = None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.backend_base_url}/actuator/health")
            backend_healthy = resp.status_code in (200, 503)
            if not backend_healthy:
                backend_error = f"Unexpected status {resp.status_code}"
    except Exception as e:
        backend_error = str(e)

    overall = "healthy" if (gemini_healthy and backend_healthy) else "unhealthy"
    status_code = 200 if overall == "healthy" else 503

    response = HealthResponse(
        status=overall,
        timestamp=now,
        components={
            "gemini_api": ComponentHealth(
                status="healthy" if gemini_healthy else "unhealthy",
                model=settings.gemini_model,
                error=gemini_error,
            ),
            "backend_connection": ComponentHealth(
                status="healthy" if backend_healthy else "unhealthy",
                url=settings.backend_base_url,
                error=backend_error,
            ),
        },
    )

    if status_code == 503:
        raise HTTPException(status_code=503, detail=response.model_dump(mode="json"))

    return response

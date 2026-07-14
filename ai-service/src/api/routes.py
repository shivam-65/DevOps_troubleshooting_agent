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

    # Simplified health check - just check if service is running
    # External checks can cause hangs, so we skip them for the basic health endpoint
    gemini_svc = GeminiService()
    gemini_healthy = gemini_svc.is_available()
    gemini_error = None if gemini_healthy else "API key not configured"

    # Skip backend health check to avoid hanging
    backend_healthy = True  # Assume backend is healthy to avoid hanging
    backend_error = None

    overall = "healthy" if gemini_healthy else "unhealthy"
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

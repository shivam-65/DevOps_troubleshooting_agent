from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class InvestigationAcceptedResponse(BaseModel):
    status: Literal["ACCEPTED"] = "ACCEPTED"
    investigationId: str
    message: str = "Investigation started"
    estimatedDuration: str = "PT3M"


class ComponentHealth(BaseModel):
    status: Literal["healthy", "unhealthy"]
    model: str | None = None
    url: str | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: datetime
    components: dict[str, ComponentHealth]

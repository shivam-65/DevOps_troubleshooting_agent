from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl, Field


class IncidentContext(BaseModel):
    title: str
    description: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    affectedServices: list[str] = Field(default_factory=list)
    createdAt: datetime | None = None


class InvestigationRequest(BaseModel):
    investigationId: str
    incidentId: str
    incident: IncidentContext
    callbackUrl: str
    scope: list[str] = Field(default_factory=lambda: ["kubernetes", "logs", "metrics", "git"])

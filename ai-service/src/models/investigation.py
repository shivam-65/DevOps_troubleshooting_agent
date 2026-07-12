from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    RESTART_SERVICE = "RESTART_SERVICE"
    SCALE_UP = "SCALE_UP"
    ROLLBACK_DEPLOYMENT = "ROLLBACK_DEPLOYMENT"
    RUN_SCRIPT = "RUN_SCRIPT"
    APPLY_CONFIG_CHANGE = "APPLY_CONFIG_CHANGE"
    CLEAR_CACHE = "CLEAR_CACHE"
    FAILOVER = "FAILOVER"
    CUSTOM = "CUSTOM"


class RecommendedAction(BaseModel):
    type: str
    title: str
    description: str
    command: str | None = None
    targetService: str | None = None
    parameters: dict[str, Any] | None = None
    risk: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    estimatedImpact: str = ""


class EvidencePayload(BaseModel):
    source: str
    type: str
    data: dict[str, Any] | None = None


class InvestigationResult(BaseModel):
    investigationId: str
    status: Literal["COMPLETED", "FAILED"]
    summary: str | None = None
    rootCause: str | None = None
    confidence: float | None = None
    aiModelUsed: str | None = None
    evidence: list[EvidencePayload] = Field(default_factory=list)
    recommendedActions: list[RecommendedAction] = Field(default_factory=list)
    error: str | None = None
    startedAt: datetime | None = None
    completedAt: datetime | None = None

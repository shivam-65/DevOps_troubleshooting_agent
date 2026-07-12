from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Evidence(BaseModel):
    source: str
    type: str
    data: dict[str, Any]
    collectedAt: datetime | None = None


class CollectedEvidence(BaseModel):
    kubernetes: dict[str, Any] | None = None
    logs: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    git: dict[str, Any] | None = None
    errors: list[str] = []

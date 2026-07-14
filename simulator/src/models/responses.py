from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.models.scenario import AffectedEvidence


class ScenarioListResponse(BaseModel):
    scenarios: List[Dict[str, Any]] = []


class ScenarioDetailResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    targetServices: List[str] = []
    parameters: Dict[str, Any] = {}
    activatedAt: Optional[datetime] = None
    deactivatedAt: Optional[datetime] = None
    affectedEvidence: Optional[AffectedEvidence] = None


class ScenarioActivateResponse(BaseModel):
    id: str
    status: str
    targetServices: List[str] = []
    activatedAt: Optional[datetime] = None
    message: str = ""


class ScenarioDeactivateResponse(BaseModel):
    id: str
    status: str
    deactivatedAt: Optional[datetime] = None
    message: str = ""


class CustomScenarioCreateResponse(BaseModel):
    id: str
    name: str
    status: str = "inactive"
    message: str = ""


class ServiceResponse(BaseModel):
    name: str
    namespace: str
    replicas: int
    healthyReplicas: int
    version: str
    dependencies: List[str] = []


class ServiceListResponse(BaseModel):
    services: List[ServiceResponse] = []


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    activeScenarios: int = 0
    registeredServices: int = 0

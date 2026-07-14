from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ActivateScenarioRequest(BaseModel):
    targetServices: List[str] = []
    parameters: Dict[str, Any] = {}


class CreateCustomScenarioRequest(BaseModel):
    name: str
    description: str
    targetServices: List[str] = []
    effects: Dict[str, Any] = {}
    duration: Optional[str] = None  # ISO 8601 duration


class CreateServiceRequest(BaseModel):
    name: str
    namespace: str = "production"
    replicas: int = 2
    version: str = "v1.0.0"
    dependencies: List[str] = []

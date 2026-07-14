from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AffectedEvidence(BaseModel):
    kubernetes: List[str] = []
    logs: List[str] = []
    metrics: List[str] = []
    git: List[str] = []


class ScenarioModel(BaseModel):
    id: str
    name: str
    description: str
    status: str = "inactive"  # active | inactive
    targetServices: List[str] = []
    parameters: Dict[str, Any] = {}
    activatedAt: Optional[datetime] = None
    deactivatedAt: Optional[datetime] = None
    affectedEvidence: AffectedEvidence = AffectedEvidence()


class KubernetesEffect(BaseModel):
    podStatus: Optional[str] = None
    restarts: Optional[int] = None
    reason: Optional[str] = None
    message: Optional[str] = None
    exitCode: Optional[int] = None


class LogsEffect(BaseModel):
    errorPatterns: List[str] = []
    errorRate: float = 0.0


class MetricsEffect(BaseModel):
    cpuSpike: Optional[float] = None
    memorySpike: Optional[float] = None
    errorRateSpike: Optional[float] = None
    latencyMultiplier: Optional[float] = None
    requestRateDrop: Optional[float] = None
    memoryGrowth: bool = False


class GitEffect(BaseModel):
    commitMessage: Optional[str] = None
    deploymentStatus: Optional[str] = None
    rollbackReason: Optional[str] = None
    newVersion: Optional[str] = None


class ScenarioEffect(BaseModel):
    kubernetes: Optional[KubernetesEffect] = None
    logs: Optional[LogsEffect] = None
    metrics: Optional[MetricsEffect] = None
    git: Optional[GitEffect] = None

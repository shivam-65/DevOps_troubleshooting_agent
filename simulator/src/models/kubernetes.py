from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PodStatus(str, Enum):
    Running = "Running"
    Pending = "Pending"
    Failed = "Failed"
    Succeeded = "Succeeded"
    Unknown = "Unknown"
    CrashLoopBackOff = "CrashLoopBackOff"
    ImagePullBackOff = "ImagePullBackOff"
    ErrImagePull = "ErrImagePull"
    CreateContainerConfigError = "CreateContainerConfigError"
    OOMKilled = "OOMKilled"


class ContainerStatus(BaseModel):
    name: str
    ready: bool
    restartCount: int = 0
    state: str = "running"  # running, waiting, terminated
    lastTerminationReason: Optional[str] = None
    lastTerminationExitCode: Optional[int] = None


class PodEvent(BaseModel):
    podName: str
    namespace: str
    service: str
    status: str
    restarts: int = 0
    age: str = "PT1H"
    reason: Optional[str] = None
    message: Optional[str] = None
    containers: List[ContainerStatus] = []
    events: List[str] = []
    timestamp: datetime


class DeploymentStatus(BaseModel):
    name: str
    namespace: str
    replicas: int
    readyReplicas: int
    updatedReplicas: int
    availableReplicas: int
    unavailableReplicas: int = 0
    conditions: List[str] = []
    lastUpdateTime: datetime


class NodeStatus(BaseModel):
    name: str
    status: str = "Ready"
    conditions: List[str] = []
    allocatableCpu: str = "4"
    allocatableMemory: str = "16Gi"
    usedCpu: str = "2.5"
    usedMemory: str = "10Gi"


class KubernetesResponse(BaseModel):
    podEvents: List[PodEvent] = []
    deployments: List[DeploymentStatus] = []
    nodeStatus: List[NodeStatus] = []

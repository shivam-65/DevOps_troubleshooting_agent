from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: datetime
    level: str = "INFO"
    service: str
    logger: str = ""
    message: str
    stackTrace: Optional[str] = None
    threadName: Optional[str] = None
    traceId: Optional[str] = None


class AccessLogEntry(BaseModel):
    timestamp: datetime
    service: str
    method: str = "GET"
    path: str = "/"
    statusCode: int = 200
    latencyMs: float = 50.0
    clientIp: str = "10.0.0.1"
    userAgent: str = "service-client/1.0"


class LogsResponse(BaseModel):
    errorLogs: List[LogEntry] = []
    applicationLogs: List[LogEntry] = []
    accessLogs: List[AccessLogEntry] = []

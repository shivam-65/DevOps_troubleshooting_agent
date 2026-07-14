from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricSeries(BaseModel):
    service: str
    unit: str
    dataPoints: List[MetricDataPoint] = []


class LatencyMetrics(BaseModel):
    p50: List[MetricSeries] = []
    p95: List[MetricSeries] = []
    p99: List[MetricSeries] = []


class MetricsResponse(BaseModel):
    cpu: List[MetricSeries] = []
    memory: List[MetricSeries] = []
    requestRate: List[MetricSeries] = []
    errorRate: List[MetricSeries] = []
    latency: LatencyMetrics = LatencyMetrics()

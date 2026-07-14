from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from src.models.scenario import ScenarioModel


class TimeRange:
    def __init__(self, since: datetime, until: datetime):
        self.since = since
        self.until = until


class BaseGenerator(ABC):
    """Base interface for all evidence generators."""

    @abstractmethod
    def generate(
        self,
        services: List[str],
        time_range: TimeRange,
        active_scenarios: List[ScenarioModel],
        namespace: str = "production",
        **kwargs,
    ) -> Dict[str, Any]:
        ...

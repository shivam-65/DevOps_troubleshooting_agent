from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.models.scenario import AffectedEvidence, ScenarioEffect, ScenarioModel


class BaseScenario(ABC):
    """Base class for all predefined failure scenarios."""

    @property
    @abstractmethod
    def id(self) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    def get_affected_evidence(self) -> AffectedEvidence:
        ...

    @abstractmethod
    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        ...

    def to_model(self, target_services: List[str] = None,
                  parameters: Dict[str, Any] = None) -> ScenarioModel:
        return ScenarioModel(
            id=self.id,
            name=self.name,
            description=self.description,
            status="inactive",
            targetServices=target_services or [],
            parameters=parameters or {},
            affectedEvidence=self.get_affected_evidence(),
        )

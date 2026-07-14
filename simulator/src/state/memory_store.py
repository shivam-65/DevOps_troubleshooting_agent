from typing import Any, Dict, List, Optional

from src.models.scenario import ScenarioModel
from src.state.service_registry import ServiceRegistry


class MemoryStore:
    """Singleton in-memory state store for the simulator."""

    def __init__(self):
        self.active_scenarios: Dict[str, ScenarioModel] = {}
        self.custom_scenarios: Dict[str, ScenarioModel] = {}
        self.service_registry = ServiceRegistry()

    def get_active_scenarios(self) -> List[ScenarioModel]:
        return list(self.active_scenarios.values())

    def get_active_scenario(self, scenario_id: str) -> Optional[ScenarioModel]:
        return self.active_scenarios.get(scenario_id)

    def activate_scenario(self, scenario: ScenarioModel):
        self.active_scenarios[scenario.id] = scenario

    def deactivate_scenario(self, scenario_id: str) -> Optional[ScenarioModel]:
        return self.active_scenarios.pop(scenario_id, None)

    def is_scenario_active(self, scenario_id: str) -> bool:
        return scenario_id in self.active_scenarios

    def get_active_scenarios_for_service(self, service_name: str) -> List[ScenarioModel]:
        return [
            s for s in self.active_scenarios.values()
            if service_name in s.targetServices
        ]

    def add_custom_scenario(self, scenario: ScenarioModel):
        self.custom_scenarios[scenario.id] = scenario

    def get_custom_scenario(self, scenario_id: str) -> Optional[ScenarioModel]:
        return self.custom_scenarios.get(scenario_id)

    def remove_custom_scenario(self, scenario_id: str) -> bool:
        if scenario_id in self.custom_scenarios:
            self.deactivate_scenario(scenario_id)
            del self.custom_scenarios[scenario_id]
            return True
        return False

    def active_scenario_count(self) -> int:
        return len(self.active_scenarios)


# Module-level singleton
memory_store = MemoryStore()

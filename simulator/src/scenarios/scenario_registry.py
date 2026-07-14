from typing import Dict, List, Optional

from src.scenarios.base_scenario import BaseScenario
from src.scenarios.pod_crash_scenario import PodCrashScenario
from src.scenarios.oom_kill_scenario import OomKillScenario
from src.scenarios.latency_spike_scenario import LatencySpikeScenario
from src.scenarios.error_rate_scenario import ErrorRateScenario
from src.scenarios.deployment_failure_scenario import DeploymentFailureScenario


class ScenarioRegistry:
    """Registry of all predefined failure scenarios."""

    def __init__(self):
        self._scenarios: Dict[str, BaseScenario] = {}
        self._register_defaults()

    def _register_defaults(self):
        for scenario in [
            PodCrashScenario(),
            OomKillScenario(),
            LatencySpikeScenario(),
            ErrorRateScenario(),
            DeploymentFailureScenario(),
        ]:
            self._scenarios[scenario.id] = scenario

    def get(self, scenario_id: str) -> Optional[BaseScenario]:
        return self._scenarios.get(scenario_id)

    def get_all(self) -> List[BaseScenario]:
        return list(self._scenarios.values())

    def has(self, scenario_id: str) -> bool:
        return scenario_id in self._scenarios

    def ids(self) -> List[str]:
        return list(self._scenarios.keys())


# Module-level singleton
scenario_registry = ScenarioRegistry()

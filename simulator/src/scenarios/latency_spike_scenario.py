from typing import Any, Dict

from src.models.scenario import (
    AffectedEvidence, GitEffect, KubernetesEffect, LogsEffect,
    MetricsEffect, ScenarioEffect,
)
from src.scenarios.base_scenario import BaseScenario


class LatencySpikeScenario(BaseScenario):
    @property
    def id(self) -> str:
        return "latency-spike"

    @property
    def name(self) -> str:
        return "Latency Spike Scenario"

    @property
    def description(self) -> str:
        return "Simulates significant latency increase in service responses"

    def get_affected_evidence(self) -> AffectedEvidence:
        return AffectedEvidence(
            kubernetes=[],
            logs=["error_logs", "application_logs"],
            metrics=["latency", "error_rate"],
            git=["recent_commits"],
        )

    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        latency_multiplier = parameters.get("latencyMultiplier", 5.0)

        return ScenarioEffect(
            kubernetes=None,
            logs=LogsEffect(
                errorPatterns=[
                    "java.net.SocketTimeoutException: Read timed out",
                    "Request timeout after 5000ms",
                    "Slow query detected: SELECT * FROM orders took 8500ms",
                    "Connection timed out after 30000ms",
                ],
                errorRate=0.15,
            ),
            metrics=MetricsEffect(
                latencyMultiplier=latency_multiplier,
                errorRateSpike=8.0,
            ),
            git=GitEffect(
                commitMessage="Add new database query for order processing",
            ),
        )

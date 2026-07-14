from typing import Any, Dict

from src.models.scenario import (
    AffectedEvidence, GitEffect, KubernetesEffect, LogsEffect,
    MetricsEffect, ScenarioEffect,
)
from src.scenarios.base_scenario import BaseScenario


class OomKillScenario(BaseScenario):
    @property
    def id(self) -> str:
        return "oom-kill"

    @property
    def name(self) -> str:
        return "OOM Kill Scenario"

    @property
    def description(self) -> str:
        return "Simulates memory exhaustion leading to OOMKilled container"

    def get_affected_evidence(self) -> AffectedEvidence:
        return AffectedEvidence(
            kubernetes=["pod_events", "deployments"],
            logs=["error_logs"],
            metrics=["memory", "error_rate"],
            git=["recent_commits"],
        )

    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        growth_rate = parameters.get("memoryGrowthRate", "fast")
        restart_count = 3 if growth_rate == "fast" else (2 if growth_rate == "medium" else 1)

        return ScenarioEffect(
            kubernetes=KubernetesEffect(
                podStatus="OOMKilled",
                restarts=restart_count,
                reason="OOMKilled",
                message="Container exceeded memory limit",
                exitCode=137,
            ),
            logs=LogsEffect(
                errorPatterns=[
                    "java.lang.OutOfMemoryError: Java heap space",
                    "java.lang.OutOfMemoryError: GC overhead limit exceeded",
                    "Container exceeded memory limit",
                ],
                errorRate=0.3,
            ),
            metrics=MetricsEffect(
                memorySpike=98.0,
                errorRateSpike=15.0,
                memoryGrowth=True,
            ),
            git=GitEffect(
                commitMessage="Increase batch size for payment processing",
            ),
        )

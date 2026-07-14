from typing import Any, Dict

from src.models.scenario import (
    AffectedEvidence, GitEffect, KubernetesEffect, LogsEffect,
    MetricsEffect, ScenarioEffect,
)
from src.scenarios.base_scenario import BaseScenario


class PodCrashScenario(BaseScenario):
    @property
    def id(self) -> str:
        return "pod-crash"

    @property
    def name(self) -> str:
        return "Pod Crash Scenario"

    @property
    def description(self) -> str:
        return "Simulates a pod entering CrashLoopBackOff state due to application crash"

    def get_affected_evidence(self) -> AffectedEvidence:
        return AffectedEvidence(
            kubernetes=["pod_events", "deployments"],
            logs=["error_logs"],
            metrics=["request_rate", "error_rate"],
            git=[],
        )

    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        crash_reason = parameters.get("crashReason", "Error")
        restart_count = parameters.get("restartCount", 5)

        return ScenarioEffect(
            kubernetes=KubernetesEffect(
                podStatus="CrashLoopBackOff",
                restarts=restart_count,
                reason=crash_reason,
                message=f"Back-off restarting failed container",
                exitCode=1,
            ),
            logs=LogsEffect(
                errorPatterns=[
                    "Application failed to start",
                    "Error creating bean with name",
                    f"Container crashed with exit code 1: {crash_reason}",
                    "Back-off restarting failed container",
                ],
                errorRate=0.4,
            ),
            metrics=MetricsEffect(
                errorRateSpike=20.0,
                requestRateDrop=0.5,
            ),
            git=None,
        )

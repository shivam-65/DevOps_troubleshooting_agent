from typing import Any, Dict

from src.models.scenario import (
    AffectedEvidence, GitEffect, KubernetesEffect, LogsEffect,
    MetricsEffect, ScenarioEffect,
)
from src.scenarios.base_scenario import BaseScenario


class ErrorRateScenario(BaseScenario):
    @property
    def id(self) -> str:
        return "error-rate-surge"

    @property
    def name(self) -> str:
        return "Error Rate Surge Scenario"

    @property
    def description(self) -> str:
        return "Simulates sudden increase in error responses"

    def get_affected_evidence(self) -> AffectedEvidence:
        return AffectedEvidence(
            kubernetes=[],
            logs=["error_logs", "access_logs"],
            metrics=["error_rate"],
            git=["recent_deployments"],
        )

    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        error_rate = parameters.get("errorRate", 15.0)
        error_type = parameters.get("errorType", "500 Internal Server Error")

        return ScenarioEffect(
            kubernetes=None,
            logs=LogsEffect(
                errorPatterns=[
                    f"HTTP {error_type}",
                    "NullPointerException at com.payment.PaymentProcessor.process",
                    "Failed to process request: internal error",
                    "Unhandled exception in request pipeline",
                ],
                errorRate=error_rate / 100.0,
            ),
            metrics=MetricsEffect(
                errorRateSpike=error_rate,
            ),
            git=GitEffect(
                commitMessage="Update payment processing logic",
                deploymentStatus="success",
            ),
        )

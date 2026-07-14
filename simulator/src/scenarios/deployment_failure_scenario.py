from typing import Any, Dict

from src.models.scenario import (
    AffectedEvidence, GitEffect, KubernetesEffect, LogsEffect,
    MetricsEffect, ScenarioEffect,
)
from src.scenarios.base_scenario import BaseScenario


class DeploymentFailureScenario(BaseScenario):
    @property
    def id(self) -> str:
        return "deployment-failure"

    @property
    def name(self) -> str:
        return "Deployment Failure Scenario"

    @property
    def description(self) -> str:
        return "Simulates a failed deployment with pods unable to start"

    def get_affected_evidence(self) -> AffectedEvidence:
        return AffectedEvidence(
            kubernetes=["pod_events", "deployments"],
            logs=["error_logs"],
            metrics=["request_rate"],
            git=["recent_deployments"],
        )

    def get_effects(self, parameters: Dict[str, Any]) -> ScenarioEffect:
        failure_reason = parameters.get("failureReason", "ImagePullBackOff")
        new_version = parameters.get("newVersion", "v2.4.0")

        return ScenarioEffect(
            kubernetes=KubernetesEffect(
                podStatus="ImagePullBackOff",
                restarts=0,
                reason=failure_reason,
                message=f"Failed to pull image: registry.company.com/service:{new_version}",
            ),
            logs=LogsEffect(
                errorPatterns=[
                    f"Failed to pull image: registry.company.com/service:{new_version}",
                    "ImagePullBackOff: Back-off pulling image",
                    "ErrImagePull: rpc error: code = Unknown",
                    "Deployment timeout: new pods not ready after 300s",
                ],
                errorRate=0.1,
            ),
            metrics=MetricsEffect(
                requestRateDrop=0.3,
            ),
            git=GitEffect(
                commitMessage=f"Release version {new_version}",
                deploymentStatus="failed",
                newVersion=new_version,
            ),
        )

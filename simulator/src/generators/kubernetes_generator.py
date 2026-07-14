import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from src.config.defaults import DEFAULT_NODES
from src.generators.base_generator import BaseGenerator, TimeRange
from src.models.scenario import ScenarioModel
from src.scenarios.scenario_registry import scenario_registry
from src.state.memory_store import memory_store
from src.utils.random_utils import random_pod_suffix
from src.utils.time_utils import format_duration, now_utc


class KubernetesGenerator(BaseGenerator):

    def generate(
        self,
        services: List[str],
        time_range: TimeRange,
        active_scenarios: List[ScenarioModel],
        namespace: str = "production",
        **kwargs,
    ) -> Dict[str, Any]:
        pod_events = []
        deployments = []

        target_services = services if services else memory_store.service_registry.get_service_names()

        for svc_name in target_services:
            svc = memory_store.service_registry.get_service(svc_name)
            if not svc:
                continue

            svc_scenarios = [s for s in active_scenarios if svc_name in s.targetServices]
            k8s_effect = None
            for sc in svc_scenarios:
                scenario_def = scenario_registry.get(sc.id)
                if scenario_def:
                    effect = scenario_def.get_effects(sc.parameters)
                    if effect.kubernetes:
                        k8s_effect = effect.kubernetes
                        break

            for i in range(svc.replicas):
                pod_suffix = random_pod_suffix()
                pod_name = f"{svc_name}-{pod_suffix}"
                ts = time_range.since + timedelta(
                    seconds=random.randint(0, max(1, int((time_range.until - time_range.since).total_seconds())))
                )

                if k8s_effect and i == 0:
                    pod_events.append({
                        "podName": pod_name,
                        "namespace": namespace,
                        "service": svc_name,
                        "status": k8s_effect.podStatus or "CrashLoopBackOff",
                        "restarts": k8s_effect.restarts or 0,
                        "age": format_duration(now_utc() - ts),
                        "reason": k8s_effect.reason,
                        "message": k8s_effect.message,
                        "containers": [{
                            "name": svc_name,
                            "ready": False,
                            "restartCount": k8s_effect.restarts or 0,
                            "state": "waiting" if k8s_effect.podStatus in ("CrashLoopBackOff", "ImagePullBackOff") else "terminated",
                            "lastTerminationReason": k8s_effect.reason,
                            "lastTerminationExitCode": k8s_effect.exitCode,
                        }],
                        "events": [
                            k8s_effect.message or "Container failed",
                            f"Back-off restarting failed container",
                        ],
                        "timestamp": ts.isoformat(),
                    })
                else:
                    pod_events.append({
                        "podName": pod_name,
                        "namespace": namespace,
                        "service": svc_name,
                        "status": "Running",
                        "restarts": 0,
                        "age": format_duration(now_utc() - ts),
                        "reason": None,
                        "message": None,
                        "containers": [{
                            "name": svc_name,
                            "ready": True,
                            "restartCount": 0,
                            "state": "running",
                            "lastTerminationReason": None,
                            "lastTerminationExitCode": None,
                        }],
                        "events": [],
                        "timestamp": ts.isoformat(),
                    })

            ready = svc.replicas - (1 if k8s_effect else 0)
            unavailable = 1 if k8s_effect else 0
            conditions = ["Available: True", "Progressing: True"]
            if k8s_effect and k8s_effect.podStatus == "ImagePullBackOff":
                conditions = ["Available: True", "Progressing: False"]

            deployments.append({
                "name": svc_name,
                "namespace": namespace,
                "replicas": svc.replicas,
                "readyReplicas": ready,
                "updatedReplicas": svc.replicas,
                "availableReplicas": ready,
                "unavailableReplicas": unavailable,
                "conditions": conditions,
                "lastUpdateTime": time_range.until.isoformat(),
            })

        node_status = [dict(n) for n in DEFAULT_NODES]

        return {
            "podEvents": pod_events,
            "deployments": deployments,
            "nodeStatus": node_status,
        }

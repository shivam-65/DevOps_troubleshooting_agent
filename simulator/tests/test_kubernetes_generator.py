"""Unit tests for the Kubernetes evidence generator."""
import pytest
from datetime import datetime, timedelta, timezone

from src.generators.base_generator import TimeRange
from src.generators.kubernetes_generator import KubernetesGenerator
from src.state.memory_store import memory_store
from src.services.scenario_service import scenario_service


@pytest.fixture(autouse=True)
def _reset():
    memory_store.active_scenarios.clear()
    memory_store.custom_scenarios.clear()
    memory_store.service_registry._services.clear()
    memory_store.service_registry._load_defaults()
    yield


@pytest.fixture
def gen():
    return KubernetesGenerator()


@pytest.fixture
def time_range():
    now = datetime.now(timezone.utc)
    return TimeRange(since=now - timedelta(hours=1), until=now)


class TestKubernetesGeneratorHealthy:
    def test_all_pods_running(self, gen, time_range):
        result = gen.generate([], time_range, [])
        for pod in result["podEvents"]:
            assert pod["status"] == "Running"
            assert pod["restarts"] == 0

    def test_deployments_fully_available(self, gen, time_range):
        result = gen.generate([], time_range, [])
        for dep in result["deployments"]:
            assert dep["readyReplicas"] == dep["replicas"]
            assert dep["unavailableReplicas"] == 0

    def test_nodes_returned(self, gen, time_range):
        result = gen.generate([], time_range, [])
        assert len(result["nodeStatus"]) == 3


class TestKubernetesGeneratorWithScenario:
    def test_pod_crash_effect(self, gen, time_range):
        scenario_service.activate_scenario(
            "pod-crash", ["payment-api"], {"crashReason": "Error", "restartCount": 5}
        )
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)

        crash_pods = [p for p in result["podEvents"] if p["status"] == "CrashLoopBackOff"]
        assert len(crash_pods) >= 1
        assert crash_pods[0]["restarts"] == 5

    def test_oom_kill_effect(self, gen, time_range):
        scenario_service.activate_scenario(
            "oom-kill", ["payment-api"], {"memoryGrowthRate": "fast"}
        )
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)

        oom_pods = [p for p in result["podEvents"] if p["status"] == "OOMKilled"]
        assert len(oom_pods) >= 1
        assert oom_pods[0]["containers"][0]["lastTerminationExitCode"] == 137

    def test_unaffected_service_stays_healthy(self, gen, time_range):
        scenario_service.activate_scenario(
            "pod-crash", ["payment-api"], {}
        )
        active = memory_store.get_active_scenarios()
        result = gen.generate(["checkout-service"], time_range, active)

        for pod in result["podEvents"]:
            assert pod["status"] == "Running"

    def test_service_filter(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert all(d["name"] == "payment-api" for d in result["deployments"])

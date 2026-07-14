"""Unit tests for scenario logic."""
import pytest

from src.scenarios.pod_crash_scenario import PodCrashScenario
from src.scenarios.oom_kill_scenario import OomKillScenario
from src.scenarios.latency_spike_scenario import LatencySpikeScenario
from src.scenarios.error_rate_scenario import ErrorRateScenario
from src.scenarios.deployment_failure_scenario import DeploymentFailureScenario
from src.scenarios.scenario_registry import scenario_registry
from src.services.scenario_service import scenario_service
from src.state.memory_store import memory_store


@pytest.fixture(autouse=True)
def _reset():
    memory_store.active_scenarios.clear()
    memory_store.custom_scenarios.clear()
    memory_store.service_registry._services.clear()
    memory_store.service_registry._load_defaults()
    yield


class TestScenarioRegistry:
    def test_all_predefined_scenarios_registered(self):
        ids = scenario_registry.ids()
        assert "pod-crash" in ids
        assert "oom-kill" in ids
        assert "latency-spike" in ids
        assert "error-rate-surge" in ids
        assert "deployment-failure" in ids

    def test_get_scenario(self):
        s = scenario_registry.get("oom-kill")
        assert s is not None
        assert s.id == "oom-kill"

    def test_get_nonexistent(self):
        assert scenario_registry.get("nonexistent") is None


class TestPodCrashScenario:
    def test_effects(self):
        s = PodCrashScenario()
        effects = s.get_effects({"crashReason": "Segfault", "restartCount": 7})
        assert effects.kubernetes is not None
        assert effects.kubernetes.podStatus == "CrashLoopBackOff"
        assert effects.kubernetes.restarts == 7
        assert effects.logs is not None
        assert effects.metrics is not None
        assert effects.metrics.errorRateSpike == 20.0

    def test_affected_evidence(self):
        s = PodCrashScenario()
        ae = s.get_affected_evidence()
        assert "pod_events" in ae.kubernetes
        assert "error_logs" in ae.logs


class TestOomKillScenario:
    def test_effects_fast(self):
        s = OomKillScenario()
        effects = s.get_effects({"memoryGrowthRate": "fast"})
        assert effects.kubernetes.podStatus == "OOMKilled"
        assert effects.kubernetes.exitCode == 137
        assert effects.kubernetes.restarts == 3
        assert effects.metrics.memoryGrowth is True

    def test_effects_slow(self):
        s = OomKillScenario()
        effects = s.get_effects({"memoryGrowthRate": "slow"})
        assert effects.kubernetes.restarts == 1

    def test_git_effect(self):
        s = OomKillScenario()
        effects = s.get_effects({})
        assert effects.git is not None
        assert effects.git.commitMessage is not None


class TestLatencySpikeScenario:
    def test_effects(self):
        s = LatencySpikeScenario()
        effects = s.get_effects({"latencyMultiplier": 10.0})
        assert effects.kubernetes is None
        assert effects.metrics.latencyMultiplier == 10.0
        assert effects.logs is not None
        assert len(effects.logs.errorPatterns) > 0


class TestErrorRateScenario:
    def test_effects(self):
        s = ErrorRateScenario()
        effects = s.get_effects({"errorRate": 25.0})
        assert effects.metrics.errorRateSpike == 25.0
        assert effects.kubernetes is None

    def test_default_effects(self):
        s = ErrorRateScenario()
        effects = s.get_effects({})
        assert effects.metrics.errorRateSpike == 15.0


class TestDeploymentFailureScenario:
    def test_effects(self):
        s = DeploymentFailureScenario()
        effects = s.get_effects({"newVersion": "v3.0.0"})
        assert effects.kubernetes.podStatus == "ImagePullBackOff"
        assert effects.git.deploymentStatus == "failed"
        assert effects.git.newVersion == "v3.0.0"


class TestScenarioService:
    def test_activate_and_deactivate(self):
        model = scenario_service.activate_scenario(
            "pod-crash", ["payment-api"], {"restartCount": 3}
        )
        assert model is not None
        assert model.status == "active"
        assert memory_store.is_scenario_active("pod-crash")

        deactivated = scenario_service.deactivate_scenario("pod-crash")
        assert deactivated.status == "inactive"
        assert not memory_store.is_scenario_active("pod-crash")

    def test_activate_invalid_service(self):
        with pytest.raises(ValueError):
            scenario_service.activate_scenario(
                "pod-crash", ["nonexistent"], {}
            )

    def test_activate_nonexistent_scenario(self):
        result = scenario_service.activate_scenario(
            "nonexistent", ["payment-api"], {}
        )
        assert result is None

    def test_list_shows_active_status(self):
        scenario_service.activate_scenario(
            "oom-kill", ["payment-api"], {}
        )
        all_scenarios = scenario_service.list_all_scenarios()
        oom = next(s for s in all_scenarios if s["id"] == "oom-kill")
        assert oom["status"] == "active"

    def test_multiple_scenarios_active(self):
        scenario_service.activate_scenario("pod-crash", ["payment-api"], {})
        scenario_service.activate_scenario("latency-spike", ["checkout-service"], {})
        assert memory_store.active_scenario_count() == 2

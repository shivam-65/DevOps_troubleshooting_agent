"""Unit tests for the Git evidence generator."""
import pytest
from datetime import datetime, timedelta, timezone

from src.generators.base_generator import TimeRange
from src.generators.git_generator import GitGenerator
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
    return GitGenerator()


@pytest.fixture
def time_range():
    now = datetime.now(timezone.utc)
    return TimeRange(since=now - timedelta(hours=24), until=now)


class TestGitGeneratorHealthy:
    def test_generates_commits(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert len(result["recentCommits"]) > 0

    def test_generates_deployments(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert len(result["recentDeployments"]) > 0

    def test_no_rollbacks_healthy(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert len(result["rollbacks"]) == 0

    def test_commit_fields(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        commit = result["recentCommits"][0]
        assert "sha" in commit
        assert "shortSha" in commit
        assert "author" in commit
        assert "authorEmail" in commit
        assert "message" in commit
        assert "service" in commit
        assert "filesChanged" in commit
        assert "totalAdditions" in commit

    def test_deployment_fields(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        deploy = result["recentDeployments"][0]
        assert "id" in deploy
        assert "version" in deploy
        assert "service" in deploy
        assert "status" in deploy
        assert deploy["status"] == "success"


class TestGitGeneratorWithScenario:
    def test_oom_has_related_commit(self, gen, time_range):
        scenario_service.activate_scenario("oom-kill", ["payment-api"], {})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        # Should have a commit about batch size
        messages = [c["message"] for c in result["recentCommits"]]
        assert any("batch size" in m.lower() or "increase" in m.lower() for m in messages)

    def test_deployment_failure_status(self, gen, time_range):
        scenario_service.activate_scenario(
            "deployment-failure", ["payment-api"],
            {"newVersion": "v2.4.0"}
        )
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        failed = [d for d in result["recentDeployments"] if d["status"] == "failed"]
        assert len(failed) > 0

    def test_limit_parameter(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [], limit=3)
        assert len(result["recentCommits"]) <= 3

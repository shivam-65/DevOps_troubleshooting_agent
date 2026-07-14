"""Unit tests for the Logs evidence generator."""
import pytest
from datetime import datetime, timedelta, timezone

from src.generators.base_generator import TimeRange
from src.generators.logs_generator import LogsGenerator
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
    return LogsGenerator()


@pytest.fixture
def time_range():
    now = datetime.now(timezone.utc)
    return TimeRange(since=now - timedelta(hours=1), until=now)


class TestLogsGeneratorHealthy:
    def test_generates_application_logs(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert len(result["applicationLogs"]) > 0

    def test_healthy_logs_mostly_info(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        info_count = sum(1 for l in result["applicationLogs"] if l["level"] == "INFO")
        assert info_count > 0

    def test_healthy_has_no_error_logs(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        # Healthy state should have no/empty error logs
        assert len(result["errorLogs"]) == 0

    def test_access_logs_generated(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert len(result["accessLogs"]) > 0
        assert all(log["service"] == "payment-api" for log in result["accessLogs"])


class TestLogsGeneratorWithScenario:
    def test_oom_generates_error_logs(self, gen, time_range):
        scenario_service.activate_scenario("oom-kill", ["payment-api"], {"memoryGrowthRate": "fast"})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        assert len(result["errorLogs"]) > 0

    def test_error_logs_have_stack_traces(self, gen, time_range):
        scenario_service.activate_scenario("oom-kill", ["payment-api"], {})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        stack_traces = [l for l in result["errorLogs"] if l.get("stackTrace")]
        assert len(stack_traces) > 0

    def test_latency_spike_timeout_errors(self, gen, time_range):
        scenario_service.activate_scenario("latency-spike", ["payment-api"], {})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        assert len(result["errorLogs"]) > 0

    def test_error_rate_surge_access_logs(self, gen, time_range):
        scenario_service.activate_scenario("error-rate-surge", ["payment-api"], {"errorRate": 50.0})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active)
        error_access = [l for l in result["accessLogs"] if l["statusCode"] >= 500]
        # With 50% error rate, we should have some 5xx
        assert len(error_access) > 0

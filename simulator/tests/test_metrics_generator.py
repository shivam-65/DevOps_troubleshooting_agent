"""Unit tests for the Metrics evidence generator."""
import pytest
from datetime import datetime, timedelta, timezone

from src.generators.base_generator import TimeRange
from src.generators.metrics_generator import MetricsGenerator
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
    return MetricsGenerator()


@pytest.fixture
def time_range():
    now = datetime.now(timezone.utc)
    return TimeRange(since=now - timedelta(hours=1), until=now)


class TestMetricsGeneratorHealthy:
    def test_all_metric_types_present(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        assert "cpu" in result
        assert "memory" in result
        assert "requestRate" in result
        assert "errorRate" in result
        assert "latency" in result

    def test_data_points_generated(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [], step="5m")
        cpu_series = result["cpu"][0]
        assert cpu_series["service"] == "payment-api"
        assert len(cpu_series["dataPoints"]) > 0

    def test_healthy_cpu_range(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        for dp in result["cpu"][0]["dataPoints"]:
            assert 0 < dp["value"] < 100

    def test_healthy_error_rate_low(self, gen, time_range):
        result = gen.generate(["payment-api"], time_range, [])
        for dp in result["errorRate"][0]["dataPoints"]:
            assert dp["value"] < 5.0


class TestMetricsGeneratorWithScenario:
    def test_oom_memory_growth(self, gen, time_range):
        scenario_service.activate_scenario("oom-kill", ["payment-api"], {"memoryGrowthRate": "fast"})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active, step="5m")
        mem_points = result["memory"][0]["dataPoints"]
        # Last data point should be higher than first (memory growth)
        if len(mem_points) > 2:
            assert mem_points[-1]["value"] > mem_points[0]["value"]

    def test_latency_spike_multiplier(self, gen, time_range):
        scenario_service.activate_scenario("latency-spike", ["payment-api"], {"latencyMultiplier": 5.0})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active, step="5m")
        p99_points = result["latency"]["p99"][0]["dataPoints"]
        if len(p99_points) > 2:
            assert p99_points[-1]["value"] > p99_points[0]["value"]

    def test_error_rate_spike(self, gen, time_range):
        scenario_service.activate_scenario("error-rate-surge", ["payment-api"], {"errorRate": 25.0})
        active = memory_store.get_active_scenarios()
        result = gen.generate(["payment-api"], time_range, active, step="5m")
        er_points = result["errorRate"][0]["dataPoints"]
        if len(er_points) > 2:
            assert er_points[-1]["value"] > er_points[0]["value"]

    def test_multiple_services(self, gen, time_range):
        result = gen.generate(["payment-api", "checkout-service"], time_range, [])
        assert len(result["cpu"]) == 2

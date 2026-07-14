"""API endpoint integration tests."""
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.state.memory_store import memory_store


@pytest.fixture(autouse=True)
def _reset():
    memory_store.active_scenarios.clear()
    memory_store.custom_scenarios.clear()
    memory_store.service_registry._services.clear()
    memory_store.service_registry._load_defaults()
    yield


@pytest.fixture
def client():
    """Synchronous wrapper using httpx + ASGITransport for compatibility."""
    import asyncio

    class SyncTestClient:
        def __init__(self):
            self._transport = ASGITransport(app=app)

        def _run(self, coro):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
            return asyncio.run(coro)

        def get(self, url, **kwargs):
            async def _req():
                async with AsyncClient(transport=self._transport, base_url="http://test") as ac:
                    return await ac.get(url, **kwargs)
            return self._run(_req())

        def post(self, url, json=None, **kwargs):
            async def _req():
                async with AsyncClient(transport=self._transport, base_url="http://test") as ac:
                    return await ac.post(url, json=json, **kwargs)
            return self._run(_req())

        def put(self, url, json=None, **kwargs):
            async def _req():
                async with AsyncClient(transport=self._transport, base_url="http://test") as ac:
                    return await ac.put(url, json=json, **kwargs)
            return self._run(_req())

        def delete(self, url, **kwargs):
            async def _req():
                async with AsyncClient(transport=self._transport, base_url="http://test") as ac:
                    return await ac.delete(url, **kwargs)
            return self._run(_req())

    return SyncTestClient()


# ─── Health ──────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["registeredServices"] == 5
        assert data["activeScenarios"] == 0


# ─── Kubernetes Adapter ─────────────────────────────────────────────────────

class TestKubernetesAdapter:
    def test_get_kubernetes_all_services(self, client):
        resp = client.get("/api/adapters/kubernetes")
        assert resp.status_code == 200
        data = resp.json()
        assert "podEvents" in data
        assert "deployments" in data
        assert "nodeStatus" in data
        assert len(data["deployments"]) == 5

    def test_get_kubernetes_single_service(self, client):
        resp = client.get("/api/adapters/kubernetes?services=payment-api")
        assert resp.status_code == 200
        data = resp.json()
        assert all(d["name"] == "payment-api" for d in data["deployments"])

    def test_kubernetes_with_active_scenario(self, client):
        # Activate pod-crash scenario
        client.post("/api/scenarios/pod-crash/activate", json={
            "targetServices": ["payment-api"],
            "parameters": {"crashReason": "Error", "restartCount": 5}
        })
        resp = client.get("/api/adapters/kubernetes?services=payment-api")
        data = resp.json()
        # At least one pod should be in CrashLoopBackOff
        statuses = [p["status"] for p in data["podEvents"]]
        assert "CrashLoopBackOff" in statuses
        # Deployment should have unavailable replicas
        deploy = data["deployments"][0]
        assert deploy["unavailableReplicas"] >= 1


# ─── Logs Adapter ───────────────────────────────────────────────────────────

class TestLogsAdapter:
    def test_get_logs_all_services(self, client):
        resp = client.get("/api/adapters/logs")
        assert resp.status_code == 200
        data = resp.json()
        assert "errorLogs" in data
        assert "applicationLogs" in data
        assert "accessLogs" in data

    def test_logs_with_oom_scenario(self, client):
        client.post("/api/scenarios/oom-kill/activate", json={
            "targetServices": ["payment-api"],
            "parameters": {"memoryGrowthRate": "fast"}
        })
        resp = client.get("/api/adapters/logs?services=payment-api")
        data = resp.json()
        # Should have error logs with OOM patterns
        assert len(data["errorLogs"]) > 0
        oom_found = any("OutOfMemoryError" in log["message"] or "memory" in log["message"].lower()
                        for log in data["errorLogs"])
        assert oom_found, "OOM error patterns should be present in error logs"

    def test_logs_limit_param(self, client):
        resp = client.get("/api/adapters/logs?limit=5")
        assert resp.status_code == 200


# ─── Metrics Adapter ────────────────────────────────────────────────────────

class TestMetricsAdapter:
    def test_get_metrics_all_services(self, client):
        resp = client.get("/api/adapters/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "cpu" in data
        assert "memory" in data
        assert "requestRate" in data
        assert "errorRate" in data
        assert "latency" in data
        assert "p50" in data["latency"]
        assert "p95" in data["latency"]
        assert "p99" in data["latency"]

    def test_metrics_with_latency_spike(self, client):
        client.post("/api/scenarios/latency-spike/activate", json={
            "targetServices": ["payment-api"],
            "parameters": {"latencyMultiplier": 5.0}
        })
        resp = client.get("/api/adapters/metrics?services=payment-api")
        data = resp.json()
        # Latency p99 should have elevated values towards the end
        p99_data = data["latency"]["p99"]
        assert len(p99_data) > 0
        dp = p99_data[0]["dataPoints"]
        if len(dp) > 2:
            assert dp[-1]["value"] > dp[0]["value"], "Latency should increase over time with spike"

    def test_metrics_single_service(self, client):
        resp = client.get("/api/adapters/metrics?services=checkout-service")
        data = resp.json()
        for series in data["cpu"]:
            assert series["service"] == "checkout-service"


# ─── Git Adapter ────────────────────────────────────────────────────────────

class TestGitAdapter:
    def test_get_git_all_services(self, client):
        resp = client.get("/api/adapters/git")
        assert resp.status_code == 200
        data = resp.json()
        assert "recentCommits" in data
        assert "recentDeployments" in data
        assert "rollbacks" in data
        assert len(data["recentCommits"]) > 0
        assert len(data["recentDeployments"]) > 0

    def test_git_commit_has_required_fields(self, client):
        resp = client.get("/api/adapters/git?services=payment-api")
        data = resp.json()
        commit = data["recentCommits"][0]
        assert "sha" in commit
        assert "shortSha" in commit
        assert "author" in commit
        assert "message" in commit
        assert "timestamp" in commit
        assert "filesChanged" in commit

    def test_git_with_deployment_failure(self, client):
        client.post("/api/scenarios/deployment-failure/activate", json={
            "targetServices": ["payment-api"],
            "parameters": {"newVersion": "v2.4.0"}
        })
        resp = client.get("/api/adapters/git?services=payment-api")
        data = resp.json()
        failed_deploys = [d for d in data["recentDeployments"] if d["status"] == "failed"]
        assert len(failed_deploys) > 0, "Should have a failed deployment"


# ─── Scenario Management ────────────────────────────────────────────────────

class TestScenarioManagement:
    def test_list_scenarios(self, client):
        resp = client.get("/api/scenarios")
        assert resp.status_code == 200
        data = resp.json()
        assert "scenarios" in data
        ids = [s["id"] for s in data["scenarios"]]
        assert "pod-crash" in ids
        assert "oom-kill" in ids
        assert "latency-spike" in ids
        assert "error-rate-surge" in ids
        assert "deployment-failure" in ids

    def test_get_specific_scenario(self, client):
        resp = client.get("/api/scenarios/oom-kill")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "oom-kill"
        assert data["status"] == "inactive"

    def test_get_nonexistent_scenario(self, client):
        resp = client.get("/api/scenarios/nonexistent")
        assert resp.status_code == 404

    def test_activate_deactivate_scenario(self, client):
        # Activate
        resp = client.post("/api/scenarios/oom-kill/activate", json={
            "targetServices": ["payment-api"],
            "parameters": {"memoryGrowthRate": "fast"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "active"
        assert data["id"] == "oom-kill"
        assert "payment-api" in data["targetServices"]

        # Verify active
        resp = client.get("/api/scenarios/oom-kill")
        assert resp.json()["status"] == "active"

        # Deactivate
        resp = client.post("/api/scenarios/oom-kill/deactivate")
        assert resp.status_code == 200
        assert resp.json()["status"] == "inactive"

    def test_activate_with_invalid_service(self, client):
        resp = client.post("/api/scenarios/pod-crash/activate", json={
            "targetServices": ["nonexistent-service"],
            "parameters": {}
        })
        assert resp.status_code == 400

    def test_deactivate_inactive_scenario(self, client):
        resp = client.post("/api/scenarios/pod-crash/deactivate")
        assert resp.status_code == 404


# ─── Custom Scenarios ────────────────────────────────────────────────────────

class TestCustomScenarios:
    def test_create_custom_scenario(self, client):
        resp = client.post("/api/scenarios/custom", json={
            "name": "Database Connection Failure",
            "description": "Simulates database connection pool exhaustion",
            "targetServices": ["payment-api"],
            "effects": {
                "logs": {"errorPatterns": ["Connection pool exhausted"]},
                "metrics": {"errorRateSpike": 25.0}
            }
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "custom-" in data["id"]
        assert data["status"] == "inactive"

    def test_delete_custom_scenario(self, client):
        # Create first
        client.post("/api/scenarios/custom", json={
            "name": "Temp Scenario",
            "description": "Temp",
            "targetServices": [],
            "effects": {}
        })
        resp = client.delete("/api/scenarios/custom/custom-temp-scenario")
        assert resp.status_code == 204

    def test_delete_nonexistent_custom(self, client):
        resp = client.delete("/api/scenarios/custom/nonexistent")
        assert resp.status_code == 404


# ─── Service Registry ───────────────────────────────────────────────────────

class TestServiceRegistry:
    def test_list_services(self, client):
        resp = client.get("/api/services")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["services"]) == 5
        names = [s["name"] for s in data["services"]]
        assert "payment-api" in names

    def test_add_service(self, client):
        resp = client.post("/api/services", json={
            "name": "notification-service",
            "namespace": "production",
            "replicas": 2,
            "version": "v1.0.0",
            "dependencies": ["user-service"]
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "notification-service"

        # Verify it appears in list
        resp = client.get("/api/services")
        assert len(resp.json()["services"]) == 6

    def test_add_duplicate_service(self, client):
        resp = client.post("/api/services", json={
            "name": "payment-api",
            "namespace": "production",
            "replicas": 2,
            "version": "v1.0.0",
            "dependencies": []
        })
        assert resp.status_code == 409

    def test_remove_service(self, client):
        resp = client.delete("/api/services/user-service")
        assert resp.status_code == 204

        resp = client.get("/api/services")
        names = [s["name"] for s in resp.json()["services"]]
        assert "user-service" not in names

    def test_remove_nonexistent_service(self, client):
        resp = client.delete("/api/services/nonexistent")
        assert resp.status_code == 404

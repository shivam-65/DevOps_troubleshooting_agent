import pytest
import httpx
import anyio
from src.main import app


@pytest.fixture
def client():
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_investigate_returns_202(client):
    async def _run():
        payload = {
            "investigationId": "inv-test-001",
            "incidentId": "inc-test-001",
            "incident": {
                "title": "Test incident",
                "description": "Test description",
                "severity": "HIGH",
                "affectedServices": ["payment-api"],
            },
            "callbackUrl": "http://localhost:8080/api/internal/investigations/inv-test-001/callback",
            "scope": ["kubernetes", "logs"],
        }
        response = await client.post("/api/investigate", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "ACCEPTED"
        assert data["investigationId"] == "inv-test-001"
    anyio.run(_run)


def test_investigate_validation_error(client):
    async def _run():
        payload = {"investigationId": "inv-test-001"}
        response = await client.post("/api/investigate", json=payload)
        assert response.status_code == 422
    anyio.run(_run)


def test_health_endpoint_exists(client):
    async def _run():
        response = await client.get("/health")
        assert response.status_code in (200, 503)
    anyio.run(_run)


def test_docs_endpoint(client):
    async def _run():
        response = await client.get("/docs")
        assert response.status_code == 200
    anyio.run(_run)

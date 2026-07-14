import sys
import os

# Ensure the simulator root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.state.memory_store import memory_store


@pytest.fixture(autouse=True)
def reset_state():
    """Reset in-memory state before each test."""
    memory_store.active_scenarios.clear()
    memory_store.custom_scenarios.clear()
    memory_store.service_registry._services.clear()
    memory_store.service_registry._load_defaults()
    yield


@pytest.fixture
def client():
    """Synchronous test helper — use async_client for async tests."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

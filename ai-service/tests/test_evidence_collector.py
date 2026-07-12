import pytest
import anyio
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from src.services.evidence_collector import collect_evidence


def test_collect_evidence_handles_failures():
    async def _run():
        with patch("src.services.evidence_collector._safe_fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [
                ("kubernetes", None, "connection error"),
                ("logs", {"errorLogs": [{"message": "test"}]}, None),
            ]

            result = await collect_evidence(
                services=["payment-api"],
                scope=["kubernetes", "logs"],
                incident_created=datetime.now(timezone.utc),
            )

            assert result.kubernetes is None
            assert result.logs is not None
            assert len(result.errors) == 1
    anyio.run(_run)

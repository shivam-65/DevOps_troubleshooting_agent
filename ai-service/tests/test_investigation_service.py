import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from src.models.requests import InvestigationRequest, IncidentContext
from src.models.evidence import CollectedEvidence
from src.services.investigation_service import (
    _build_evidence_payloads,
    _parse_actions,
    _clamp_confidence,
)


def test_clamp_confidence_normal():
    assert _clamp_confidence(0.85) == 0.85


def test_clamp_confidence_exceeds():
    assert _clamp_confidence(1.5) == 1.0


def test_clamp_confidence_negative():
    assert _clamp_confidence(-0.1) == 0.0


def test_clamp_confidence_none():
    assert _clamp_confidence(None) is None


def test_clamp_confidence_string():
    assert _clamp_confidence("0.7") == 0.7


def test_build_evidence_payloads_empty():
    ev = CollectedEvidence()
    payloads = _build_evidence_payloads(ev)
    assert len(payloads) == 0


def test_build_evidence_payloads_with_data():
    ev = CollectedEvidence(
        kubernetes={"podEvents": []},
        logs={"errorLogs": []},
    )
    payloads = _build_evidence_payloads(ev)
    assert len(payloads) == 2
    sources = [p.source for p in payloads]
    assert "kubernetes" in sources
    assert "logs" in sources


def test_parse_actions_valid():
    raw = [
        {
            "type": "RESTART_SERVICE",
            "title": "Restart payment-api",
            "description": "Rolling restart",
            "command": "kubectl rollout restart deployment/payment-api",
            "targetService": "payment-api",
            "risk": "LOW",
            "estimatedImpact": "Brief interruption",
        }
    ]
    actions = _parse_actions(raw)
    assert len(actions) == 1
    assert actions[0].type == "RESTART_SERVICE"
    assert actions[0].risk == "LOW"


def test_parse_actions_empty():
    assert _parse_actions([]) == []

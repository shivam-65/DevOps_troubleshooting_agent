import pytest
import json
from src.services.gemini_service import GeminiService


def test_parse_response_clean_json():
    svc = GeminiService()
    raw = json.dumps({
        "summary": "Test summary",
        "rootCause": "Test root cause",
        "confidence": 0.85,
        "reasoning": "Test reasoning",
        "recommendedActions": [],
    })
    result = svc._parse_response(raw)
    assert result["summary"] == "Test summary"
    assert result["confidence"] == 0.85


def test_parse_response_with_markdown_fences():
    svc = GeminiService()
    raw = '```json\n{"summary": "fenced", "rootCause": "test", "confidence": 0.5}\n```'
    result = svc._parse_response(raw)
    assert result["summary"] == "fenced"


def test_parse_response_with_extra_text():
    svc = GeminiService()
    raw = 'Here is the analysis:\n{"summary": "extra text", "rootCause": "cause", "confidence": 0.9}\nDone.'
    result = svc._parse_response(raw)
    assert result["summary"] == "extra text"


def test_parse_response_invalid_json():
    svc = GeminiService()
    with pytest.raises(ValueError):
        svc._parse_response("not json at all")

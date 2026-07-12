from datetime import datetime, timezone
from typing import Any

from src.config.settings import get_settings
from src.models.requests import InvestigationRequest
from src.models.evidence import CollectedEvidence
from src.models.investigation import (
    InvestigationResult,
    EvidencePayload,
    RecommendedAction,
)
from src.services.evidence_collector import collect_evidence
from src.services.gemini_service import GeminiService
from src.services.callback_service import CallbackService
from src.utils.logger import get_logger

logger = get_logger(__name__)

_gemini_service: GeminiService | None = None
_callback_service: CallbackService | None = None


def _get_gemini() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


def _get_callback() -> CallbackService:
    global _callback_service
    if _callback_service is None:
        _callback_service = CallbackService()
    return _callback_service


async def run_investigation(request: InvestigationRequest) -> None:
    investigation_id = request.investigationId
    started_at = datetime.now(timezone.utc)
    settings = get_settings()

    logger.info("investigation_start", investigationId=investigation_id, incidentId=request.incidentId)

    try:
        # Step 1: Collect evidence
        evidence: CollectedEvidence = await collect_evidence(
            services=request.incident.affectedServices,
            scope=request.scope,
            incident_created=request.incident.createdAt,
        )

        # Check if all adapters failed
        has_any_evidence = any([evidence.kubernetes, evidence.logs, evidence.metrics, evidence.git])
        if not has_any_evidence:
            logger.error("all_adapters_failed", investigationId=investigation_id, errors=evidence.errors)
            error_msg = "All evidence adapters failed: " + "; ".join(evidence.errors)
            result = InvestigationResult(
                investigationId=investigation_id,
                status="FAILED",
                summary=error_msg,
                aiModelUsed=settings.gemini_model,
                error=error_msg,
                startedAt=started_at,
                completedAt=datetime.now(timezone.utc),
            )
            await _send_callback(request.callbackUrl, result)
            return

        # Step 2: Analyze with Gemini
        analysis: dict[str, Any] = await _get_gemini().analyze(request.incident, evidence)

        # Step 3: Build result
        evidence_payloads = _build_evidence_payloads(evidence)
        recommended_actions = _parse_actions(analysis.get("recommendedActions", []))

        result = InvestigationResult(
            investigationId=investigation_id,
            status="COMPLETED",
            summary=analysis.get("summary"),
            rootCause=analysis.get("rootCause"),
            confidence=_clamp_confidence(analysis.get("confidence")),
            aiModelUsed=settings.gemini_model,
            evidence=evidence_payloads,
            recommendedActions=recommended_actions,
            startedAt=started_at,
            completedAt=datetime.now(timezone.utc),
        )

        logger.info(
            "investigation_completed",
            investigationId=investigation_id,
            confidence=result.confidence,
            actions_count=len(recommended_actions),
        )

    except Exception as e:
        logger.error("investigation_failed", investigationId=investigation_id, error=str(e))
        error_msg = f"Investigation failed: {e}"
        result = InvestigationResult(
            investigationId=investigation_id,
            status="FAILED",
            summary=error_msg,
            aiModelUsed=settings.gemini_model,
            error=error_msg,
            startedAt=started_at,
            completedAt=datetime.now(timezone.utc),
        )

    # Step 4: Send callback
    await _send_callback(request.callbackUrl, result)


async def _send_callback(callback_url: str, result: InvestigationResult) -> None:
    try:
        await _get_callback().send_callback(callback_url, result)
    except Exception as e:
        logger.critical("callback_failed", url=callback_url, error=str(e))


def _build_evidence_payloads(evidence: CollectedEvidence) -> list[EvidencePayload]:
    payloads: list[EvidencePayload] = []
    if evidence.kubernetes:
        payloads.append(EvidencePayload(source="kubernetes", type="pod_events", data=evidence.kubernetes))
    if evidence.logs:
        payloads.append(EvidencePayload(source="logs", type="error_logs", data=evidence.logs))
    if evidence.metrics:
        payloads.append(EvidencePayload(source="metrics", type="time_series", data=evidence.metrics))
    if evidence.git:
        payloads.append(EvidencePayload(source="git", type="recent_commits", data=evidence.git))
    return payloads


def _parse_actions(raw_actions: list[dict[str, Any]]) -> list[RecommendedAction]:
    actions: list[RecommendedAction] = []
    for ra in raw_actions:
        try:
            action = RecommendedAction(
                type=ra.get("type", "CUSTOM"),
                title=ra.get("title", "Unnamed Action"),
                description=ra.get("description", ""),
                command=ra.get("command"),
                targetService=ra.get("targetService"),
                parameters=ra.get("parameters"),
                risk=ra.get("risk", "MEDIUM"),
                estimatedImpact=ra.get("estimatedImpact", ""),
            )
            actions.append(action)
        except Exception as e:
            logger.warning("action_parse_failed", action=ra, error=str(e))
    return actions


def _clamp_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
        return max(0.0, min(1.0, v))
    except (TypeError, ValueError):
        return None

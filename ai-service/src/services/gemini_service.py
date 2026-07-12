import json
import re
from typing import Any

from google import genai
from google.genai import types

from src.config.settings import get_settings
from src.models.evidence import CollectedEvidence
from src.models.requests import IncidentContext
from src.prompts.system_prompt import SYSTEM_PROMPT
from src.prompts.investigation_prompt import build_investigation_prompt
from src.utils.logger import get_logger
from src.utils.retry import async_retry

logger = get_logger(__name__)


class GeminiService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
        self._configured = False
        self._client = None

        if settings.gemini_api_key:
            self._client = genai.Client(api_key=settings.gemini_api_key)
            self._configured = True

    def is_available(self) -> bool:
        return self._configured

    @async_retry(max_retries=3, backoff_base=2.0)
    async def analyze(
        self,
        incident: IncidentContext,
        evidence: CollectedEvidence,
    ) -> dict[str, Any]:
        if not self._configured or not self._client:
            raise RuntimeError("Gemini API key not configured")

        prompt = build_investigation_prompt(incident, evidence)
        logger.info("gemini_call_start", model=self.model_name, prompt_length=len(prompt))

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )

        raw_text = response.text
        logger.info("gemini_call_success", model=self.model_name, response_length=len(raw_text))

        return self._parse_response(raw_text)

    def _parse_response(self, raw_text: str) -> dict[str, Any]:
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            json_str = raw_text.strip()

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            brace_start = json_str.find("{")
            brace_end = json_str.rfind("}")
            if brace_start != -1 and brace_end != -1:
                try:
                    parsed = json.loads(json_str[brace_start : brace_end + 1])
                except json.JSONDecodeError as e:
                    logger.error("gemini_parse_failed", raw=raw_text[:500], error=str(e))
                    raise ValueError(f"Failed to parse Gemini response as JSON: {e}")
            else:
                logger.error("gemini_parse_failed", raw=raw_text[:500])
                raise ValueError("Gemini response does not contain valid JSON")

        if "summary" not in parsed or "rootCause" not in parsed:
            logger.warning("gemini_response_incomplete", keys=list(parsed.keys()))

        return parsed

    async def check_health(self) -> tuple[bool, str | None]:
        if not self._configured or not self._client:
            return False, "API key not configured"
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents="Say OK",
            )
            if response and response.text:
                return True, None
            return False, "Empty response from Gemini"
        except Exception as e:
            return False, str(e)

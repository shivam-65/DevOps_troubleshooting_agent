import httpx

from src.models.investigation import InvestigationResult
from src.utils.logger import get_logger
from src.utils.retry import async_retry

logger = get_logger(__name__)


class CallbackService:
    @async_retry(max_retries=3, backoff_base=1.0, retry_on=(httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException))
    async def send_callback(self, callback_url: str, result: InvestigationResult) -> None:
        logger.info("callback_send_start", url=callback_url, status=result.status)
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = result.model_dump(mode="json")
            resp = await client.post(callback_url, json=payload)
            resp.raise_for_status()
            logger.info("callback_send_success", url=callback_url, status_code=resp.status_code)

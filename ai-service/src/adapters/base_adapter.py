from abc import ABC, abstractmethod
from typing import Any

import httpx

from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.retry import async_retry

logger = get_logger(__name__)


class BaseAdapter(ABC):
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.backend_base_url
        self.timeout = float(settings.adapter_timeout)
        self.max_retries = settings.max_retries
        self.backoff_base = settings.retry_backoff_base

    @abstractmethod
    def _endpoint(self) -> str:
        ...

    @abstractmethod
    def _source_name(self) -> str:
        ...

    async def fetch(
        self, services: list[str], since: str | None = None, until: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if services:
            params["services"] = ",".join(services)
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        self._add_extra_params(params)

        url = f"{self.base_url}{self._endpoint()}"
        logger.info("adapter_fetch_start", adapter=self._source_name(), url=url, params=params)

        return await self._do_fetch(url, params)

    @async_retry(max_retries=3, backoff_base=1.0, retry_on=(httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException))
    async def _do_fetch(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("adapter_fetch_success", adapter=self._source_name(), record_keys=list(data.keys()))
            return data

    def _add_extra_params(self, params: dict[str, str]) -> None:
        pass

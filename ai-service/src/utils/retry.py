import asyncio
import functools
from typing import Callable, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


def async_retry(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    no_retry_on: tuple[type[Exception], ...] = (),
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except no_retry_on as e:
                    raise e
                except retry_on as e:
                    last_exc = e
                    if attempt < max_retries:
                        wait = backoff_base * (2 ** (attempt - 1))
                        logger.warning(
                            "retry_attempt",
                            func=func.__name__,
                            attempt=attempt,
                            max_retries=max_retries,
                            wait_seconds=wait,
                            error=str(e),
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            "retry_exhausted",
                            func=func.__name__,
                            attempts=max_retries,
                            error=str(e),
                        )
            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator

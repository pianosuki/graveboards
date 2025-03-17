import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Awaitable

MAX_ATTEMPTS = 5


def auto_retry(max_attempts: int = MAX_ATTEMPTS, retry_exceptions: tuple[type[Exception]] = (TimeoutError,), backoff_strategy: Callable[[int], float] = lambda attempt_no: attempt_no ** 2):
    def decorator(func: Callable[..., Awaitable[Any]]):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"Function '{func.__name__}' must be async to use @auto_retry")

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Awaitable[Any]:
            logger = logging.getLogger(func.__module__)
            result: Any = None
            last_exception: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    last_exception = None
                    break
                except retry_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        break

                    delay = backoff_strategy(attempt)
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e} | Retrying in {delay:.2f} seconds")
                    await asyncio.sleep(backoff_strategy(attempt))

            if last_exception:
                logger.error(f"All {max_attempts} attempts failed for {func.__name__}. Raising exception")
                raise last_exception

            return result

        return wrapper

    return decorator

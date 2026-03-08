"""
Retry / fallback helpers for LLM API calls and tool dispatch.

Usage::

    result = await retry_with_fallback(
        primary=lambda: call_anthropic(prompt),
        fallback=lambda: call_openai(prompt),
        max_retries=3,
    )
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")

# Exceptions that are transient and worth retrying
_TRANSIENT = (TimeoutError, ConnectionError, OSError)


async def retry(
    fn: Callable[[], Coroutine[Any, Any, T]],
    max_retries: int = 3,
    base_delay: float = 2.0,
    label: str = "call",
) -> T:
    """
    Retry ``fn`` up to ``max_retries`` times with exponential back-off.
    Raises the last exception if all attempts fail.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return await fn()
        except _TRANSIENT as exc:
            last_exc = exc
            delay = base_delay * (2 ** (attempt - 1))
            log.warning("%s attempt %d/%d failed (%s) — retrying in %.1fs",
                        label, attempt, max_retries, exc, delay)
            await asyncio.sleep(delay)
        except Exception as exc:
            # Non-transient: fail immediately
            raise exc from exc
    raise last_exc  # type: ignore[misc]


async def retry_with_fallback(
    primary: Callable[[], Coroutine[Any, Any, T]],
    fallback: Callable[[], Coroutine[Any, Any, T]] | None = None,
    max_retries: int = 3,
    base_delay: float = 2.0,
    label: str = "call",
) -> T:
    """
    Try ``primary``; if it exhausts retries and ``fallback`` is provided,
    attempt ``fallback`` once before raising.
    """
    try:
        return await retry(primary, max_retries=max_retries,
                           base_delay=base_delay, label=f"{label}:primary")
    except Exception as primary_exc:
        if fallback is None:
            raise
        log.warning("%s primary failed (%s) — trying fallback", label, primary_exc)
        try:
            return await fallback()
        except Exception as fallback_exc:
            log.error("%s fallback also failed: %s", label, fallback_exc)
            raise fallback_exc from primary_exc


class TokenBudget:
    """
    Simple per-request token guard.  Raises RuntimeError if exceeded.
    """

    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self._used = 0

    def record(self, tokens: int) -> None:
        self._used += tokens
        if self._used > self.max_tokens:
            raise RuntimeError(
                f"Token budget exceeded: {self._used} > {self.max_tokens}"
            )

    @property
    def remaining(self) -> int:
        return max(0, self.max_tokens - self._used)

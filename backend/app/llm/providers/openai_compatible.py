"""
OpenAI-compatible LLM Provider — 07 §4.2, 08 §9.
Supports OpenAI, vLLM, Ollama, DeepSeek, Together, Groq.
"""

import json
import logging
import time
from typing import Any, TypeVar
import httpx
from pydantic import BaseModel

from app.core.errors import LLMError
from app.llm.providers.base import BaseLLMProvider, LLMResult

logger = logging.getLogger("rgf.llm.openai")
T = TypeVar("T", bound=BaseModel)


class OpenAICompatibleProvider(BaseLLMProvider):
    """Client for OpenAI-compatible /v1/chat/completions endpoints."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "",
        timeout_s: int = 60,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.timeout_s = timeout_s

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        response_schema: type[T] | None = None,
    ) -> LLMResult:
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.post(endpoint, headers=headers, json=payload)

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            if resp.status_code == 401 or resp.status_code == 403:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message="LLM API authentication failed. Please check your API key.",
                    details={"status_code": resp.status_code},
                    retryable=False,
                )

            if resp.status_code == 429:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message="LLM provider rate limit exceeded.",
                    details={"status_code": 429},
                    retryable=True,
                )

            if resp.status_code >= 500:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message=f"LLM provider error (status {resp.status_code}).",
                    details={"status_code": resp.status_code},
                    retryable=True,
                )

            resp.raise_for_status()
            data = resp.json()

            choice = data["choices"][0]
            raw_text = choice["message"]["content"] or ""
            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)

            return LLMResult(
                raw_text=raw_text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model=self.model,
                latency_ms=latency_ms,
            )

        except httpx.TimeoutException:
            raise LLMError(
                code="LLM_TIMEOUT",
                message=f"LLM request timed out after {self.timeout_s}s.",
                retryable=True,
            )
        except LLMError:
            raise
        except Exception as exc:
            logger.exception("LLM completion failed: %s", exc)
            raise LLMError(
                code="LLM_UNAVAILABLE",
                message=f"Failed to communicate with LLM provider: {str(exc)}",
                details={"error": str(exc)},
                retryable=True,
            )

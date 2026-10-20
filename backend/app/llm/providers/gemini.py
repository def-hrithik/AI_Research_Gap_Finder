"""
Gemini LLM Provider — Google Generative AI (Gemini) integration.
Uses the google-genai SDK for chat completions with JSON output.
"""

import json
import logging
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.errors import LLMError
from app.llm.providers.base import BaseLLMProvider, LLMResult

logger = logging.getLogger("rgf.llm.gemini")
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini API using the google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash",
        timeout_s: int = 120,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s
        self._client = None

    def _get_client(self):
        """Lazy-initialize the Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message="google-genai package not installed. Run: pip install google-genai",
                    retryable=False,
                )
        return self._client

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        response_schema: type[T] | None = None,
    ) -> LLMResult:
        """Execute a Gemini completion and return structured output."""
        import asyncio

        start_time = time.perf_counter()
        try:
            client = self._get_client()
            from google.genai import types

            # Build generation config
            gen_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                system_instruction=system_prompt,
            )

            # Run synchronous SDK call in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=self.model,
                        contents=user_prompt,
                        config=gen_config,
                    ),
                )
            except Exception as first_exc:
                err_str = str(first_exc).lower()
                # If primary model is unavailable or overloaded (503/429/404), fallback to gemini-3.5-flash-lite
                if ("503" in err_str or "demand" in err_str or "404" in err_str) and self.model != "gemini-3.5-flash-lite":
                    logger.warning("Gemini model %s hit spike/unavailable (%s); falling back to gemini-3.5-flash-lite", self.model, first_exc)
                    response = await loop.run_in_executor(
                        None,
                        lambda: client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=user_prompt,
                            config=gen_config,
                        ),
                    )
                else:
                    raise first_exc

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Extract text from response
            raw_text = ""
            if response.text:
                raw_text = response.text
            elif response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        raw_text = candidate.content.parts[0].text or ""
                        break

            if not raw_text:
                # Check for safety blocks
                if response.candidates and response.candidates[0].finish_reason:
                    finish_reason = str(response.candidates[0].finish_reason)
                    if "SAFETY" in finish_reason.upper():
                        raise LLMError(
                            code="LLM_INVALID_OUTPUT",
                            message=f"Gemini blocked response due to safety filters: {finish_reason}",
                            retryable=False,
                        )
                raise LLMError(
                    code="LLM_INVALID_OUTPUT",
                    message="Gemini returned an empty response.",
                    retryable=True,
                )

            # Extract token usage if available
            tokens_in = 0
            tokens_out = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens_in = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                tokens_out = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            return LLMResult(
                raw_text=raw_text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model=self.model,
                latency_ms=latency_ms,
            )

        except LLMError:
            raise
        except Exception as exc:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            error_str = str(exc).lower()

            if "api_key" in error_str or "401" in error_str or "403" in error_str or "permission" in error_str:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message=f"Gemini API authentication failed: {exc}",
                    retryable=False,
                )
            if "429" in error_str or "quota" in error_str or "rate" in error_str:
                raise LLMError(
                    code="LLM_UNAVAILABLE",
                    message=f"Gemini API rate limit / quota exceeded: {exc}",
                    retryable=True,
                )
            if "timeout" in error_str:
                raise LLMError(
                    code="LLM_TIMEOUT",
                    message=f"Gemini request timed out after {self.timeout_s}s.",
                    retryable=True,
                )

            logger.exception("Gemini completion failed: %s", exc)
            raise LLMError(
                code="LLM_UNAVAILABLE",
                message=f"Gemini API error: {str(exc)}",
                details={"error": str(exc)},
                retryable=True,
            )

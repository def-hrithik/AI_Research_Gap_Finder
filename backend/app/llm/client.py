"""
LLM Client layer — 07 §4, 08 §9.
Manages provider dispatch, concurrency semaphore, JSON extraction & repair,
retry backoff, and token usage accounting.
"""

import asyncio
import json
import logging
import re
from typing import Any, TypeVar
from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.core.errors import LLMError
from app.llm.providers.base import BaseLLMProvider, LLMResult
from app.llm.providers.fake import FakeLLMProvider
from app.llm.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger("rgf.llm.client")
T = TypeVar("T", bound=BaseModel)

# Regex to find balanced JSON blocks or remove markdown code blocks
CODE_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def extract_json_payload(raw_text: str) -> dict[str, Any]:
    """Extract and parse the JSON object from raw LLM output (07 §4.4)."""
    text = raw_text.strip()

    # 1. Strip markdown code fences if present
    fence_match = CODE_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    # 2. Direct JSON load attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Locate first '{' and last '}'
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise LLMError(
        code="LLM_INVALID_OUTPUT",
        message="Model response could not be parsed as valid JSON.",
        details={"raw_sample": text[:200]},
    )


class LLMClient:
    """Provider-agnostic LLM client with retries, validation, and concurrency limiting."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        max_concurrency: int = 4,
        max_retries: int = 2,
    ):
        self.provider = provider
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[T],
        temperature: float = 0.0,
        max_tokens: int = 2500,
    ) -> tuple[T, LLMResult]:
        """Execute completion and validate output against schema T (07 §4.4).

        Returns:
            tuple of (parsed_pydantic_model, llm_result).
        """
        async with self.semaphore:
            last_error: Exception | None = None

            for attempt in range(self.max_retries + 1):
                try:
                    result = await self.provider.complete(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_schema=schema,
                    )

                    # Extract and parse JSON
                    data = extract_json_payload(result.raw_text)

                    # Validate against Pydantic schema
                    validated = schema.model_validate(data)
                    result.parsed = validated
                    return validated, result

                except ValidationError as ve:
                    logger.warning("Pydantic schema validation error on attempt %d: %s", attempt, ve)
                    last_error = LLMError(
                        code="LLM_INVALID_OUTPUT",
                        message=f"Model output violated response schema: {ve.errors()[0]['msg']}",
                        details={"errors": ve.errors()},
                    )
                except LLMError as le:
                    last_error = le
                    if not le.retryable:
                        raise le
                    if attempt < self.max_retries:
                        await asyncio.sleep(1.0 * (attempt + 1))
                except Exception as exc:
                    logger.exception("Unexpected error in complete_json: %s", exc)
                    last_error = LLMError(
                        code="LLM_UNAVAILABLE",
                        message=str(exc),
                        retryable=True,
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(1.0 * (attempt + 1))

            if last_error:
                raise last_error
            raise LLMError(code="LLM_UNAVAILABLE", message="LLM request failed after retries.")


# Global client instance
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client based on settings."""
    global _llm_client
    if _llm_client is None:
        settings = get_settings()

        if settings.llm_provider == "fake" or not settings.llm_api_key:
            provider = FakeLLMProvider(model_name=settings.llm_model or "fake-model")
        else:
            provider = OpenAICompatibleProvider(
                api_key=settings.llm_api_key,
                model=settings.llm_model or "gpt-4o-mini",
                base_url=settings.llm_base_url,
                timeout_s=settings.llm_timeout_s,
            )

        _llm_client = LLMClient(
            provider=provider,
            max_concurrency=settings.llm_max_concurrency,
            max_retries=settings.llm_max_retries,
        )

    return _llm_client

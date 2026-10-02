"""
Base LLM Provider protocol — 07 §4.2, 08 §9.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMResult:
    """Standardized result returned by LLM providers."""

    def __init__(
        self,
        raw_text: str,
        parsed: Any | None = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        model: str = "",
        latency_ms: int = 0,
    ):
        self.raw_text = raw_text
        self.parsed = parsed
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.model = model
        self.latency_ms = latency_ms


class BaseLLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        response_schema: type[T] | None = None,
    ) -> LLMResult:
        """Execute a completion request and return raw output and token usage."""
        pass

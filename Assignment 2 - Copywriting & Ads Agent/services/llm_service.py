"""
LLM Service — Abstract Interface
=================================
Defines the contract that every LLM provider must fulfil.
To swap from Gemini to Claude, create a ClaudeProvider that
inherits from LLMService and pass it wherever GeminiProvider is used.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Holds the result of an LLM call."""
    text: str
    model: str
    provider: str


class LLMService(ABC):
    """
    Abstract base class for LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...

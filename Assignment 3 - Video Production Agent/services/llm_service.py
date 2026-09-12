"""Provider-neutral contract for Agent 3 text generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str


class LLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: Optional[int] = None) -> LLMResponse:
        """Generate a text response."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the configured model identifier."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return a human-readable provider name."""

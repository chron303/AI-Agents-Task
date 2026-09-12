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

    Any provider (Gemini, Claude, OpenAI …) must implement `generate`.
    The rest of the application talks only to this interface.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Send a prompt to the LLM and return the response.

        Args:
            prompt:        The user-facing content to send.
            system_prompt: Optional system-level instruction.
            temperature:   Sampling temperature (0 = deterministic, 1 = creative).
            max_tokens:    Optional hard cap on output length.

        Returns:
            LLMResponse with .text containing the model's reply.
        """
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier string used by this provider."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return a human-readable provider name, e.g. 'Gemini' or 'Claude'."""
        ...

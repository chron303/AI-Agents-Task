"""
Gemini Provider
================
Implements LLMService using Google's Gemini API (google-genai SDK).

Model is read from the GEMINI_MODEL environment variable.
API key is read from GEMINI_API_KEY.

To switch to Claude later:
  1. Create services/claude_provider.py implementing LLMService
  2. Update services/__init__.py or the agent to import ClaudeProvider
  3. No workflow or UI code needs to change.
"""

import os
from typing import Optional

from google import genai
from google.genai import types

from .llm_service import LLMService, LLMResponse


class GeminiProvider(LLMService):
    """
    Gemini implementation of LLMService.

    Uses the google-genai unified SDK (recommended by Google as of 2026).
    Reads model name from GEMINI_MODEL env var.
    """

    # The model requested by the assignment
    REQUESTED_MODEL = "gemini-3.5-flash-lite"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file with GEMINI_API_KEY=<your-key>."
            )

        # Model from env, defaulting to the assignment-specified model
        model_from_env = os.getenv("GEMINI_MODEL", "").strip()
        if not model_from_env:
            raise EnvironmentError(
                "GEMINI_MODEL is not set in your .env file. "
                f"Please set GEMINI_MODEL={self.REQUESTED_MODEL}"
            )

        self._model_name = model_from_env
        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Call the Gemini API and return the text response."""

        config_kwargs: dict = {"temperature": temperature}
        if max_tokens:
            config_kwargs["max_output_tokens"] = max_tokens
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt

        generate_config = types.GenerateContentConfig(**config_kwargs)

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=generate_config,
            )
        except Exception as exc:
            # Surface API errors with clear context
            model_id = self._model_name
            raise RuntimeError(
                f"Gemini API call failed (model: {model_id}).\n"
                f"Error: {exc}\n\n"
                f"If the model '{model_id}' is unavailable, check your GEMINI_MODEL "
                f"environment variable. The assignment requests '{self.REQUESTED_MODEL}'."
            ) from exc

        text = response.text or ""
        return LLMResponse(
            text=text,
            model=self._model_name,
            provider="Gemini",
        )

    def get_model_name(self) -> str:
        return self._model_name

    def get_provider_name(self) -> str:
        return "Gemini"

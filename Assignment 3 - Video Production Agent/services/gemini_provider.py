"""
Gemini Provider
================
Implements LLMService using Google's Gemini API (google-genai SDK).

Model is read from the GEMINI_MODEL environment variable.
API key is read from GEMINI_API_KEY.

This mirrors the provider used by Agent 1 and Agent 2: the model identifier
is never hardcoded or silently swapped, so whatever is configured in .env
is exactly what gets called.
"""

import os
from typing import Optional

from google import genai
from google.genai import types

from .llm_service import LLMService, LLMResponse


class GeminiProvider(LLMService):
    """
    Gemini implementation of LLMService for Agent 3.
    """

    RECOMMENDED_MODEL = "gemini-3.5-flash-lite"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file with GEMINI_API_KEY=<your-key>."
            )

        model_from_env = os.getenv("GEMINI_MODEL", "").strip()
        if not model_from_env:
            raise EnvironmentError(
                "GEMINI_MODEL is not set in your .env file. "
                f"Please set GEMINI_MODEL={self.RECOMMENDED_MODEL}"
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
            raise RuntimeError(
                f"Gemini API call failed (model: {self._model_name}).\n"
                f"Error: {exc}\n\n"
                f"Check the API key, network connection, quota, and model access. "
                f"If the model is unavailable, check your GEMINI_MODEL environment variable."
            ) from exc

        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response. Please try again.")

        return LLMResponse(
            text=text,
            model=self._model_name,
            provider="Gemini",
        )

    def get_model_name(self) -> str:
        return self._model_name

    def get_provider_name(self) -> str:
        return "Gemini"

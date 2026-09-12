"""
Image Generator Service
=======================
Handles image generation for ads.
Falls back gracefully if the API fails, returning a descriptive placeholder.
"""

import os
from typing import Optional

from google import genai
from google.genai import types

class ImageGenerator:
    """
    Service for generating ad creative images.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self._client = None
        else:
            self._client = genai.Client(api_key=api_key)

    def generate_image(self, prompt: str) -> dict:
        """
        Attempts to generate an image using Google's Imagen model via the GenAI SDK.
        Returns a dict with status and image bytes or fallback text.
        """
        if not self._client:
            return {
                "success": False,
                "error": "API Key not configured.",
                "fallback": f"Image API unavailable. Recommended visual: {prompt}"
            }

        try:
            # We attempt to use imagen-3.0-generate-001 (or latest available)
            # as the image generation model.
            response = self._client.models.generate_images(
                model='imagen-3.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1"
                )
            )
            
            # Extract bytes of the first image
            generated_image = response.generated_images[0]
            
            return {
                "success": True,
                "image_bytes": generated_image.image.image_bytes,
                "mime_type": generated_image.image.mime_type,
                "prompt_used": prompt
            }
            
        except Exception as e:
            # Graceful fallback: If image generation fails (e.g., quota, unsupported model)
            return {
                "success": False,
                "error": str(e),
                "fallback": f"[Image Generation Failed] Recommended visual: {prompt}"
            }

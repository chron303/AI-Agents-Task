"""
Storyboard Image Generator
==========================
Optional visual-reference image generation for the Storyboard workflow.

This follows the same contract as Agent 2's `ImageGenerator`: it is
completely decoupled from text generation, never raises on failure, and
always returns a dict describing success/failure so a workflow can keep
going with the text-only storyboard if the image API is unavailable.

It is a separate implementation rather than a cross-folder import because
Agent 1 and Agent 2 already establish the project convention that every
agent folder is self-contained and can run independently of the others.
"""

import os

from google import genai
from google.genai import types

# Same default Imagen model Agent 2 uses, overridable per-agent via .env.
DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-001"


class StoryboardImageGenerator:
    """
    Generates a single optional visual reference for a storyboard scene.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self._model = os.getenv("GEMINI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL).strip() or DEFAULT_IMAGE_MODEL
        self._client = genai.Client(api_key=api_key) if api_key else None

    def generate_image(self, visual_prompt: str) -> dict:
        """
        Attempt to generate one 16:9 reference image for a storyboard scene.

        Returns a dict with 'success' plus either image bytes or a text
        fallback. Never raises — image generation failure must never break
        the rest of the storyboard.
        """
        if not self._client:
            return {
                "success": False,
                "error": "GEMINI_API_KEY not configured.",
                "fallback": f"No visual reference was generated. Use this description on set: {visual_prompt}",
            }

        try:
            response = self._client.models.generate_images(
                model=self._model,
                prompt=visual_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/png",
                    aspect_ratio="16:9",
                ),
            )
            generated_image = response.generated_images[0]
            return {
                "success": True,
                "image_bytes": generated_image.image.image_bytes,
                "mime_type": generated_image.image.mime_type,
                "prompt_used": visual_prompt,
            }
        except Exception as exc:
            # Graceful fallback: quota limits, unsupported model, network issues, etc.
            return {
                "success": False,
                "error": str(exc),
                "fallback": f"Image generation was unavailable. Recommended visual reference: {visual_prompt}",
            }

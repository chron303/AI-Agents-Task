"""
Storyboard Workflow
====================
Pipeline:
  1. plan_visual_language — establish the visual approach (palette, framing
                             style, pacing of cuts) before any scene detail
  2. generate_storyboard   — produce the full scene-by-scene visual storyboard
  3. check_scene_consistency — sanity-check scene durations against the
                             requested runtime and note any mismatch
  4. (optional) generate one reference image for the hero scene — entirely
                             separate from text generation, never blocking

Each text step is a real LLM call. Image generation is optional and its
failure never breaks the text storyboard.
"""

import re
from pathlib import Path
from typing import Callable, Optional

from services import LLMService, StoryboardImageGenerator, assess_scene_consistency, parse_duration


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "storyboard_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class StoryboardWorkflow:
    def __init__(self, llm: LLMService, image_generator: Optional[StoryboardImageGenerator] = None):
        self._llm = llm
        self._image_gen = image_generator
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        concept_or_script: str,
        platform: str,
        duration: str,
        tone: str,
        style: str = "",
        additional_instructions: str = "",
        generate_reference_image: bool = False,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        def notify(message: str):
            if on_progress:
                on_progress(message)

        requested_seconds = parse_duration(duration)
        brief = self._format_brief(concept_or_script, platform, duration, tone, style, additional_instructions)

        notify("🎨 Step 1/3 — Planning visual language and shot approach…")
        visual_plan = self._plan_visual_language(brief)

        notify("🖼️  Step 2/3 — Building the scene-by-scene storyboard…")
        storyboard = self._generate_storyboard(brief, visual_plan)

        notify("⏱️  Step 3/3 — Checking scene timing consistency…")
        scene_timing = assess_scene_consistency(storyboard, requested_seconds)

        image_result = None
        if generate_reference_image:
            notify("🎞️  Generating an optional visual reference for the hero scene…")
            image_result = self._generate_reference_image(storyboard)

        notify("✅ Storyboard complete.")

        return {
            "visual_plan": visual_plan,
            "final": storyboard,
            "timing_report": scene_timing.as_markdown(),
            "timing_status": scene_timing.status,
            "image": image_result,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(self, concept_or_script, platform, duration, tone, style, additional) -> str:
        parts = [
            f"Concept or script to storyboard:\n{concept_or_script}",
            f"Platform: {platform}",
            f"Requested duration: {duration}",
            f"Tone: {tone}",
        ]
        if style.strip():
            parts.append(f"Visual style: {style}")
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _plan_visual_language(self, brief: str) -> str:
        prompt = f"""Before storyboarding individual scenes, establish the visual language for this video.

Brief:
{brief}

Define:
- Color palette / visual mood
- Framing style (how tight or wide the video generally feels)
- Pacing of cuts (fast and punchy vs. slower and deliberate)
- One sentence on the overall cinematographic approach

Return only this visual-language plan in markdown. Do not storyboard individual scenes yet."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.5)
        return response.text

    def _generate_storyboard(self, brief: str, visual_plan: str) -> str:
        prompt = f"""Build the full scene-by-scene storyboard using the approved visual language.

Brief:
{brief}

Approved Visual Language:
{visual_plan}

Present the storyboard as a markdown table with one row per scene, with these exact columns:
Scene | Duration | Visual Description | Subject/Action | Camera Angle | Camera Movement | Composition | Lighting/Mood | Voice-over/Dialogue | On-screen Text | Audio | Transition

Include a duration for every scene (e.g. "0:00-0:05") so the scenes can be totalled against the runtime.
Return only the storyboard table in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.7)
        return response.text

    def _generate_reference_image(self, storyboard: str) -> dict:
        if not self._image_gen:
            return {
                "success": False,
                "error": "Image generator not configured for this run.",
                "fallback": "Text-based storyboard is complete and usable without a reference image.",
            }

        # Extract a clean visual prompt for the first/hero scene from the storyboard text
        # rather than reusing the whole table (which includes non-visual columns).
        extract_prompt = f"""From the storyboard below, extract a single, highly descriptive image-generation prompt
for the most visually important scene (usually the hero/establishing scene). Describe only what should be seen —
subject, setting, lighting, mood, composition — in one dense paragraph. Do not include any on-screen text or dialogue,
and do not mention that this is a storyboard.

Storyboard:
{storyboard}

Return only the raw image-generation prompt string."""

        try:
            prompt_response = self._llm.generate(prompt=extract_prompt, system_prompt=self._system_prompt,
                                                   temperature=0.4, max_tokens=150)
            visual_prompt = prompt_response.text.strip()
        except RuntimeError as exc:
            return {
                "success": False,
                "error": f"Could not extract a visual prompt: {exc}",
                "fallback": "Text-based storyboard is complete and usable without a reference image.",
            }

        return self._image_gen.generate_image(visual_prompt)

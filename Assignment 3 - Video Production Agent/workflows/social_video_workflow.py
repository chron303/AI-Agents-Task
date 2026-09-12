"""
Social Media Video Workflow
=============================
Pipeline:
  1. plan_hook_and_retention — design the hook and a scene-change/retention
                                strategy before any full script is written
  2. draft_social_video       — write the full short-form video plan (hook,
                                scenes, captions, audio, CTA)
  3. validate_and_finalize    — check pacing/timing fit the short runtime and
                                revise once if the draft runs long or thin

Each step is a real LLM call.
"""

from pathlib import Path
from typing import Callable, Optional

from services import LLMService, assess_timing, parse_duration

PLATFORM_NOTES = {
    "instagram reels": "native, raw-feeling, trend-aware pacing",
    "tiktok": "fastest cuts, most native/unpolished feel, trend-aware",
    "youtube shorts": "slightly more polish tolerated, still fast-paced",
    "linkedin short-form video": "professional feed-native, fast but not gimmicky",
}


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "social_video_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class SocialVideoWorkflow:
    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        topic: str,
        platform: str,
        audience: str,
        duration: str,
        tone: str,
        key_message: str = "",
        cta: str = "",
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        def notify(message: str):
            if on_progress:
                on_progress(message)

        requested_seconds = parse_duration(duration)
        brief = self._format_brief(topic, platform, audience, duration, tone,
                                    key_message, cta, additional_instructions)

        notify("🪝 Step 1/3 — Designing the hook and retention strategy…")
        hook_plan = self._plan_hook_and_retention(brief, platform, requested_seconds)

        notify("📱 Step 2/3 — Drafting the short-form video…")
        draft = self._draft_social_video(brief, hook_plan)

        notify("⏱️  Step 3/3 — Validating pacing and finalizing…")
        timing = assess_timing(draft, requested_seconds)
        final = draft
        revised = False
        if not timing.is_within_target:
            notify(f"   → Content is {timing.status} for a {requested_seconds}s video. Tightening…")
            final = self._revise_for_pacing(brief, draft, timing)
            timing = assess_timing(final, requested_seconds)
            revised = True

        notify("✅ Social video plan complete.")

        return {
            "hook_plan": hook_plan,
            "draft": draft,
            "final": final,
            "timing_report": timing.as_markdown(),
            "timing_status": timing.status,
            "revised_for_timing": revised,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(self, topic, platform, audience, duration, tone,
                       key_message, cta, additional) -> str:
        parts = [
            f"Topic: {topic}",
            f"Platform: {platform}",
            f"Target audience: {audience}",
            f"Requested duration: {duration}",
            f"Tone: {tone}",
        ]
        if key_message.strip():
            parts.append(f"Key message: {key_message}")
        if cta.strip():
            parts.append(f"Call to action: {cta}")
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _plan_hook_and_retention(self, brief: str, platform: str, requested_seconds: int) -> str:
        platform_note = PLATFORM_NOTES.get(platform.strip().lower(), "fast-paced, native short-form video behavior")
        prompt = f"""Design the hook and retention strategy for a {requested_seconds}-second short-form video
before writing the full script.

Platform behavior to account for: {platform_note}

Brief:
{brief}

Define:
- The exact hook (first 1-3 seconds) — written to stand alone
- A scene-change/retention plan: roughly how many scenes and how fast the cuts need to be for this duration
- What must be visible in captions since sound-off viewing is the default assumption

Return only this hook and retention plan in markdown. Do not write the full scene-by-scene script yet."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.6)
        return response.text

    def _draft_social_video(self, brief: str, hook_plan: str) -> str:
        prompt = f"""Write the complete short-form video plan following the approved hook and retention plan.

Brief:
{brief}

Approved Hook & Retention Plan:
{hook_plan}

Include: Hook (verbatim), then a numbered Scene Sequence with timing for each scene, Spoken Content (or "(silent — visual + caption only)"),
Visual Direction (framed for vertical 9:16), On-screen Captions (exact text), Audio Suggestions, and a single closing CTA.

Return the full plan in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.75)
        return response.text

    def _revise_for_pacing(self, brief: str, draft: str, timing) -> str:
        direction = (
            "cut spoken/caption content and shorten scenes"
            if timing.status == "over target"
            else "add another quick scene or expand the payoff slightly"
        )
        prompt = f"""The short-form video draft below is {timing.status} for its requested runtime.

Requested runtime: {timing.requested_seconds}s
Estimated spoken/caption runtime: {timing.estimated_seconds}s

Brief:
{brief}

Draft:
{draft}

Revise so the pacing fits a {timing.requested_seconds}-second video. Specifically {direction}.
Keep the hook, scene numbering, and CTA. Return the complete, corrected plan in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.6)
        return response.text

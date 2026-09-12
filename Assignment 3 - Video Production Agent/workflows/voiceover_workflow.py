"""
Voice-over Workflow
====================
Pipeline:
  1. plan_delivery       — decide the emotional throughline and pacing before
                            any lines are written
  2. draft_voiceover     — write the full VO script with delivery direction,
                            pauses/emphasis, and pronunciation notes
  3. validate_and_finalize — check estimated spoken timing against the
                            requested duration; revise once if off target

Each step is a real LLM call.
"""

from pathlib import Path
from typing import Callable, Optional

from services import LLMService, assess_timing, parse_duration


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "voiceover_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class VoiceoverWorkflow:
    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        topic: str,
        audience: str,
        platform: str,
        duration: str,
        tone: str,
        key_message: str = "",
        desired_emotion: str = "",
        cta: str = "",
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        def notify(message: str):
            if on_progress:
                on_progress(message)

        requested_seconds = parse_duration(duration)
        brief = self._format_brief(topic, audience, platform, duration, tone,
                                    key_message, desired_emotion, cta, additional_instructions)

        notify("🎭 Step 1/3 — Planning delivery and emotional throughline…")
        delivery_plan = self._plan_delivery(brief, requested_seconds)

        notify("🎙️  Step 2/3 — Writing the voice-over script with direction…")
        draft = self._draft_voiceover(brief, delivery_plan)

        notify("⏱️  Step 3/3 — Validating timing and finalizing…")
        timing = assess_timing(draft, requested_seconds)
        final = draft
        revised = False
        if not timing.is_within_target:
            notify(f"   → Script is {timing.status} ({timing.estimated_seconds}s vs {requested_seconds}s requested). Revising…")
            final = self._revise_for_timing(brief, draft, timing)
            timing = assess_timing(final, requested_seconds)
            revised = True

        notify("✅ Voice-over script complete.")

        return {
            "delivery_plan": delivery_plan,
            "draft": draft,
            "final": final,
            "timing_report": timing.as_markdown(),
            "timing_status": timing.status,
            "revised_for_timing": revised,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(self, topic, audience, platform, duration, tone,
                       key_message, desired_emotion, cta, additional) -> str:
        parts = [
            f"Topic: {topic}",
            f"Target audience: {audience}",
            f"Platform: {platform}",
            f"Requested duration: {duration}",
            f"Tone: {tone}",
        ]
        if key_message.strip():
            parts.append(f"Key message: {key_message}")
        if desired_emotion.strip():
            parts.append(f"Desired emotion: {desired_emotion}")
        if cta.strip():
            parts.append(f"Call to action: {cta}")
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _plan_delivery(self, brief: str, requested_seconds: int) -> str:
        prompt = f"""Plan the delivery approach for this voice-over before writing any lines.

Brief:
{brief}

The voice-over must run approximately {requested_seconds} seconds at a natural, unhurried pace
(roughly 140-150 words per minute), so target about {round(requested_seconds / 60 * 145)} words total.

Define:
- The emotional throughline (how the feeling should build or shift across the script)
- Overall pacing (unhurried / brisk / building urgency, etc.)
- Where the single most important pause or beat should land

Return only this delivery plan in markdown. Do not write the script yet."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.5)
        return response.text

    def _draft_voiceover(self, brief: str, delivery_plan: str) -> str:
        prompt = f"""Write the complete voice-over script following the approved delivery plan.

Brief:
{brief}

Approved Delivery Plan:
{delivery_plan}

Break the script into short delivery beats, each with an estimated duration. For each beat, include delivery
direction (pacing/emphasis/tone). Mark meaningful pauses as [pause Xs]. Add pronunciation notes only where a
word is genuinely ambiguous. Clearly mark the CTA line if one was requested. End with an estimated total timing line.

Return the full voice-over script with direction in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.7)
        return response.text

    def _revise_for_timing(self, brief: str, draft: str, timing) -> str:
        direction = (
            "cut lines or tighten phrasing"
            if timing.status == "over target"
            else "add a meaningful beat or expand on the key message"
        )
        prompt = f"""The voice-over draft below is {timing.status} for its requested runtime.

Requested runtime: {timing.requested_seconds}s (~{timing.target_words} words at a natural pace)
Estimated spoken runtime of the draft: {timing.estimated_seconds}s ({timing.estimated_words} words)

Brief:
{brief}

Draft Voice-over:
{draft}

Revise the script so the spoken word count fits the requested runtime. Specifically {direction}.
Keep the delivery direction, pauses, and CTA formatting intact. Return the complete, corrected script."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.6)
        return response.text

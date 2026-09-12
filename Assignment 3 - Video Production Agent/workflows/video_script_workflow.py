"""
Video Script Workflow
======================
Pipeline:
  1. plan_structure   — turn the brief into a scene-by-scene beat plan that
                         allocates the requested duration across scenes
  2. draft_script      — write the full scene-by-scene script from that plan
  3. validate_and_finalize — check estimated narration timing against the
                         requested duration; if it's off target, send it back
                         for one corrective revision pass, then finalize

Each step is a real LLM call. No stage is faked or skipped.
"""

from pathlib import Path
from typing import Callable, Optional

from services import LLMService, assess_timing, parse_duration


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "video_script_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class VideoScriptWorkflow:
    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        topic: str,
        objective: str,
        audience: str,
        platform: str,
        duration: str,
        tone: str,
        style: str = "",
        key_message: str = "",
        cta: str = "",
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        def notify(message: str):
            if on_progress:
                on_progress(message)

        requested_seconds = parse_duration(duration)
        brief = self._format_brief(
            topic, objective, audience, platform, duration, tone,
            style, key_message, cta, additional_instructions,
        )

        notify("🎯 Step 1/3 — Understanding the objective and planning scene structure…")
        plan = self._plan_structure(brief, requested_seconds)

        notify("✍️  Step 2/3 — Writing the full scene-by-scene script…")
        draft = self._draft_script(brief, plan)

        notify("⏱️  Step 3/3 — Validating timing and finalizing…")
        timing = assess_timing(draft, requested_seconds)
        final = draft
        revised = False
        if not timing.is_within_target:
            notify(f"   → Narration is {timing.status} ({timing.estimated_seconds}s vs {requested_seconds}s requested). Revising…")
            final = self._revise_for_timing(brief, draft, timing)
            timing = assess_timing(final, requested_seconds)
            revised = True
        else:
            final = self._polish(brief, draft)

        notify("✅ Video script complete.")

        return {
            "plan": plan,
            "draft": draft,
            "final": final,
            "timing_report": timing.as_markdown(),
            "timing_status": timing.status,
            "revised_for_timing": revised,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(self, topic, objective, audience, platform, duration, tone,
                       style, key_message, cta, additional) -> str:
        parts = [
            f"Topic/Concept: {topic}",
            f"Objective: {objective}",
            f"Target audience: {audience}",
            f"Platform: {platform}",
            f"Requested duration: {duration}",
            f"Tone: {tone}",
        ]
        if style.strip():
            parts.append(f"Style: {style}")
        if key_message.strip():
            parts.append(f"Key message: {key_message}")
        if cta.strip():
            parts.append(f"Call to action: {cta}")
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _plan_structure(self, brief: str, requested_seconds: int) -> str:
        prompt = f"""Plan the scene structure for a video script before any script is written.

Brief:
{brief}

The video must run approximately {requested_seconds} seconds total.

Produce a scene-by-scene beat plan:
- List each scene with an allocated time range (the ranges must sum to ~{requested_seconds}s)
- One line describing what happens in that scene and why it's there
- Note which scene carries the hook and which carries the CTA (if any)

Return only the beat plan in markdown. Do not write any dialogue or full script yet."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.5)
        return response.text

    def _draft_script(self, brief: str, plan: str) -> str:
        prompt = f"""Write the complete video script following the approved scene plan.

Brief:
{brief}

Approved Scene Plan:
{plan}

For every scene include: Scene number, Timing, Visual/Action, Dialogue/Narration, On-screen text, Audio.
Follow the scene plan's timing allocations closely. Return the full script in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.75)
        return response.text

    def _revise_for_timing(self, brief: str, draft: str, timing) -> str:
        direction = (
            "cut spoken lines and lean more on visuals-only scenes"
            if timing.status == "over target"
            else "add meaningful spoken detail or extend scene timings"
        )
        prompt = f"""The draft script below is {timing.status} for its requested runtime.

Requested runtime: {timing.requested_seconds}s
Estimated narration runtime at natural pace: {timing.estimated_seconds}s

Brief:
{brief}

Draft Script:
{draft}

Revise the script so the total narration fits the requested runtime. Specifically {direction}.
Keep the same scene numbering and structure where possible. Return the complete, corrected script in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.6)
        return response.text

    def _polish(self, brief: str, draft: str) -> str:
        prompt = f"""Review and finalize the video script below. Its timing is already on target.

Brief:
{brief}

Draft Script:
{draft}

Tighten any awkward dialogue, make sure the hook lands in scene 1, and confirm the CTA (if requested) is clear.
Return only the final, polished script in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.55)
        return response.text

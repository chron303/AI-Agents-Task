"""
Shot List Workflow
===================
Pipeline:
  1. analyze_production_needs — work out locations, setups, and coverage
                                 needed before listing individual shots
  2. generate_shot_list        — produce the full technical shot list
  3. review_for_practicality   — check the list is genuinely shootable and
                                  timing is plausible against the requested
                                  runtime; tighten anything vague

Each step is a real LLM call.
"""

from pathlib import Path
from typing import Callable, Optional

from services import LLMService, assess_scene_consistency, parse_duration


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "shot_list_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class ShotListWorkflow:
    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        concept_or_script: str,
        duration: str,
        locations: str = "",
        cast_or_talent: str = "",
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        def notify(message: str):
            if on_progress:
                on_progress(message)

        requested_seconds = parse_duration(duration)
        brief = self._format_brief(concept_or_script, duration, locations, cast_or_talent, additional_instructions)

        notify("📋 Step 1/3 — Analyzing production needs (locations, setups, coverage)…")
        production_plan = self._analyze_production_needs(brief)

        notify("🎬 Step 2/3 — Building the shot list…")
        shot_list = self._generate_shot_list(brief, production_plan)

        notify("🔍 Step 3/3 — Reviewing for practicality and timing…")
        scene_timing = assess_scene_consistency(shot_list, requested_seconds)
        final = self._review_for_practicality(brief, shot_list)

        notify("✅ Shot list complete.")

        return {
            "production_plan": production_plan,
            "draft": shot_list,
            "final": final,
            "timing_report": scene_timing.as_markdown(),
            "timing_status": scene_timing.status,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(self, concept_or_script, duration, locations, cast, additional) -> str:
        parts = [
            f"Concept, script, or storyboard to build a shot list from:\n{concept_or_script}",
            f"Requested video duration: {duration}",
        ]
        if locations.strip():
            parts.append(f"Known locations: {locations}")
        if cast.strip():
            parts.append(f"Cast/talent: {cast}")
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _analyze_production_needs(self, brief: str) -> str:
        prompt = f"""Before listing individual shots, analyze what this shoot actually needs.

Brief:
{brief}

Identify:
- Distinct locations/setups required
- Cast or talent needed per setup
- Any special equipment implied by the concept (drone, gimbal, tripod, lighting rig, etc.)
- A sensible shooting order grouped by location/setup (not necessarily script order)

Return only this production analysis in markdown. Do not list individual shots yet."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.5)
        return response.text

    def _generate_shot_list(self, brief: str, production_plan: str) -> str:
        prompt = f"""Build the full technical shot list using the production analysis below.

Brief:
{brief}

Production Analysis:
{production_plan}

Present the shot list as a markdown table with one row per shot, with these exact columns:
Shot # | Scene | Shot Type | Camera Angle | Camera Movement | Subject | Action | Location | Props | Audio | Duration | Production Notes

Use precise cinematography terminology for shot type, angle, and movement.
Include a duration for every shot so shots can be totalled against the runtime.
Return only the shot list table in markdown."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.65)
        return response.text

    def _review_for_practicality(self, brief: str, shot_list: str) -> str:
        prompt = f"""Review the shot list below for real-world practicality.

Brief:
{brief}

Draft Shot List:
{shot_list}

Check for and fix:
1. Any shot type/angle/movement that's vague rather than a precise term
2. Missing production notes where a shot genuinely needs special equipment, multiple takes, or timing care
3. Shots that would be inefficient to schedule as ordered (regroup if it clearly helps)
4. Confirm the shot list is genuinely shootable by a real crew

Return the complete, finalized shot list table in markdown. Do not include commentary outside the table."""

        response = self._llm.generate(prompt=prompt, system_prompt=self._system_prompt, temperature=0.5)
        return response.text

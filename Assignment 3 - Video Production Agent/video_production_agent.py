"""
Video Production Agent (Agent 3) — Orchestrator and CLI
=========================================================
Acts as the central router for all five video-production workflows.

Both the Streamlit UI (app.py) and the CLI use this module.
No generation logic is duplicated between them.

Usage (as a library):
    from video_production_agent import VideoProductionAgent
    from services import GeminiProvider

    agent = VideoProductionAgent(provider=GeminiProvider())
    result = agent.generate(content_type="video_script", params={...})

Usage (as a CLI):
    python video_production_agent.py
"""

import sys
from typing import Callable, Optional

from dotenv import load_dotenv

from services import GeminiProvider, LLMService, StoryboardImageGenerator
from workflows import (
    VideoScriptWorkflow,
    StoryboardWorkflow,
    ShotListWorkflow,
    VoiceoverWorkflow,
    SocialVideoWorkflow,
)

load_dotenv()

CAPABILITIES = {
    "video_script": "Video Script",
    "storyboard": "Storyboard",
    "shot_list": "Shot List",
    "voiceover": "Voice-over Script",
    "social_video": "Social Media Video",
}

PLATFORM_OPTIONS = [
    "Instagram Reels", "TikTok", "YouTube Shorts", "LinkedIn short-form video",
    "YouTube (long-form)", "Website / landing page", "Broadcast / TV", "Other",
]


class VideoProductionAgent:
    """
    The Video Production Agent.

    Accepts any LLMService implementation — currently Gemini, later Claude.
    Selects and runs the correct workflow for each of the five capabilities.
    """

    def __init__(self, provider: Optional[LLMService] = None):
        self._llm = provider or GeminiProvider()
        self._image_gen = StoryboardImageGenerator()

        self.workflows = {
            "video_script": VideoScriptWorkflow(self._llm),
            "storyboard": StoryboardWorkflow(self._llm, self._image_gen),
            "shot_list": ShotListWorkflow(self._llm),
            "voiceover": VoiceoverWorkflow(self._llm),
            "social_video": SocialVideoWorkflow(self._llm),
        }

    def get_provider_info(self) -> dict:
        return {
            "provider": self._llm.get_provider_name(),
            "model": self._llm.get_model_name(),
        }

    def generate(
        self,
        content_type: str,
        params: dict,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Generate video-production content based on capability and parameters.

        Args:
            content_type: One of 'video_script', 'storyboard', 'shot_list',
                           'voiceover', 'social_video'
            params:       Dictionary of inputs specific to the capability
            on_progress:  Optional callback to receive progress messages

        Returns:
            A dict with 'final' (the finished output) plus intermediate stages
            and a 'timing_report'.

        Raises:
            ValueError: If content_type is not recognised.
            RuntimeError: If the LLM call fails.
        """
        content_type = content_type.lower().strip()
        if content_type not in CAPABILITIES:
            valid = ", ".join(CAPABILITIES.keys())
            raise ValueError(f"Unknown capability '{content_type}'. Valid options: {valid}")

        if content_type == "video_script":
            return self._run_video_script(params, on_progress)
        elif content_type == "storyboard":
            return self._run_storyboard(params, on_progress)
        elif content_type == "shot_list":
            return self._run_shot_list(params, on_progress)
        elif content_type == "voiceover":
            return self._run_voiceover(params, on_progress)
        elif content_type == "social_video":
            return self._run_social_video(params, on_progress)

    # ── Workflow dispatchers ──────────────────────────────────────────────────

    def _run_video_script(self, params: dict, on_progress) -> dict:
        return self.workflows["video_script"].run(
            topic=params.get("topic", ""),
            objective=params.get("objective", ""),
            audience=params.get("audience", "General audience"),
            platform=params.get("platform", "YouTube (long-form)"),
            duration=params.get("duration", "60 seconds"),
            tone=params.get("tone", "Informative"),
            style=params.get("style", ""),
            key_message=params.get("key_message", ""),
            cta=params.get("cta", ""),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_storyboard(self, params: dict, on_progress) -> dict:
        return self.workflows["storyboard"].run(
            concept_or_script=params.get("concept_or_script", ""),
            platform=params.get("platform", "YouTube (long-form)"),
            duration=params.get("duration", "60 seconds"),
            tone=params.get("tone", "Informative"),
            style=params.get("style", ""),
            additional_instructions=params.get("additional_instructions", ""),
            generate_reference_image=bool(params.get("generate_reference_image", False)),
            on_progress=on_progress,
        )

    def _run_shot_list(self, params: dict, on_progress) -> dict:
        return self.workflows["shot_list"].run(
            concept_or_script=params.get("concept_or_script", ""),
            duration=params.get("duration", "60 seconds"),
            locations=params.get("locations", ""),
            cast_or_talent=params.get("cast_or_talent", ""),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_voiceover(self, params: dict, on_progress) -> dict:
        return self.workflows["voiceover"].run(
            topic=params.get("topic", ""),
            audience=params.get("audience", "General audience"),
            platform=params.get("platform", "YouTube (long-form)"),
            duration=params.get("duration", "30 seconds"),
            tone=params.get("tone", "Warm"),
            key_message=params.get("key_message", ""),
            desired_emotion=params.get("desired_emotion", ""),
            cta=params.get("cta", ""),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_social_video(self, params: dict, on_progress) -> dict:
        return self.workflows["social_video"].run(
            topic=params.get("topic", ""),
            platform=params.get("platform", "Instagram Reels"),
            audience=params.get("audience", "General audience"),
            duration=params.get("duration", "15 seconds"),
            tone=params.get("tone", "Energetic"),
            key_message=params.get("key_message", ""),
            cta=params.get("cta", ""),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def run_cli():
    """
    Interactive command-line interface for the Video Production Agent.

    Shares 100% of the generation code with the Streamlit UI.
    """
    print("\n" + "=" * 60)
    print("  VIDEO PRODUCTION AGENT  |  Technians AI Engineer Assignment")
    print("=" * 60)

    try:
        agent = VideoProductionAgent()
        info = agent.get_provider_info()
        print(f"\n✓ Connected to {info['provider']} | Model: {info['model']}")
    except EnvironmentError as e:
        print(f"\n✗ Configuration error: {e}")
        print("  → Create a .env file with GEMINI_API_KEY and GEMINI_MODEL set.")
        sys.exit(1)

    print("\nSelect a capability:")
    options = list(CAPABILITIES.items())
    for i, (key, label) in enumerate(options, 1):
        print(f"  {i}. {label}")

    choice = input("\nEnter number (1–5): ").strip()
    try:
        idx = int(choice) - 1
        content_type, label = options[idx]
    except (ValueError, IndexError):
        print("✗ Invalid choice. Exiting.")
        sys.exit(1)

    print(f"\n── {label} ──")
    params = _collect_params_cli(content_type)

    print(f"\n{'─' * 60}")
    print("Generating…")
    print("─" * 60)

    try:
        result = agent.generate(
            content_type=content_type,
            params=params,
            on_progress=lambda msg: print(f"\n  {msg}"),
        )
    except (ValueError, RuntimeError) as e:
        print(f"\n✗ Generation failed:\n{e}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"  FINAL OUTPUT — {label}")
    print("=" * 60)
    print(result["final"])

    if result.get("timing_report"):
        print(f"\n{'-' * 60}")
        print(result["timing_report"])

    if result.get("image"):
        if result["image"].get("success"):
            print("\n[✓ Reference image generated successfully (bytes available in memory)]")
        else:
            print(f"\n[!] Image info: {result['image'].get('fallback', result['image'].get('error'))}")

    save = input("\n\nSave output to a file? (y/n): ").strip().lower()
    if save == "y":
        filename = input("Filename (e.g. my_script.md): ").strip() or "output.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result["final"])
        print(f"✓ Saved to {filename}")


def _collect_params_cli(content_type: str) -> dict:
    """Collect user inputs for the selected capability via CLI."""

    def ask(label: str, default: str = "") -> str:
        prompt = f"  {label}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        val = input(prompt).strip()
        return val if val else default

    def ask_platform(default_idx: int = 0) -> str:
        print("  Platform options: " + ", ".join(f"{i+1}. {p}" for i, p in enumerate(PLATFORM_OPTIONS)))
        choice = ask("Platform (number or name)", str(default_idx + 1))
        try:
            return PLATFORM_OPTIONS[int(choice) - 1]
        except (ValueError, IndexError):
            return choice

    params = {}

    if content_type == "video_script":
        params["topic"] = ask("Topic/Concept")
        params["objective"] = ask("Objective", "Educate and build trust")
        params["audience"] = ask("Target audience", "General audience")
        params["platform"] = ask_platform(4)
        params["duration"] = ask("Duration (e.g. 30 seconds, 2 minutes)", "60 seconds")
        params["tone"] = ask("Tone", "Informative")
        params["style"] = ask("Style (optional)")
        params["key_message"] = ask("Key message (optional)")
        params["cta"] = ask("CTA (optional)")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "storyboard":
        params["concept_or_script"] = ask("Concept or paste a script to storyboard")
        params["platform"] = ask_platform(4)
        params["duration"] = ask("Duration", "60 seconds")
        params["tone"] = ask("Tone", "Informative")
        params["style"] = ask("Visual style (optional)")
        params["additional_instructions"] = ask("Additional instructions (optional)")
        img = ask("Generate an optional reference image? (y/n)", "n")
        params["generate_reference_image"] = img.lower() == "y"

    elif content_type == "shot_list":
        params["concept_or_script"] = ask("Concept, script, or storyboard to build a shot list from")
        params["duration"] = ask("Duration", "60 seconds")
        params["locations"] = ask("Known locations (optional)")
        params["cast_or_talent"] = ask("Cast/talent (optional)")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "voiceover":
        params["topic"] = ask("Topic")
        params["audience"] = ask("Target audience", "General audience")
        params["platform"] = ask_platform(4)
        params["duration"] = ask("Duration", "30 seconds")
        params["tone"] = ask("Tone", "Warm")
        params["key_message"] = ask("Key message (optional)")
        params["desired_emotion"] = ask("Desired emotion (optional)")
        params["cta"] = ask("CTA (optional)")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "social_video":
        params["topic"] = ask("Topic")
        params["platform"] = ask_platform(0)
        params["audience"] = ask("Target audience", "General audience")
        params["duration"] = ask("Duration (e.g. 15 seconds)", "15 seconds")
        params["tone"] = ask("Tone", "Energetic")
        params["key_message"] = ask("Key message (optional)")
        params["cta"] = ask("CTA (optional)")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    return params


if __name__ == "__main__":
    run_cli()

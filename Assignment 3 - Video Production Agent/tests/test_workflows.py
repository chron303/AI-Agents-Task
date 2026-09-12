"""
Agent 3 Test Suite
===================
Exercises every workflow's pipeline logic, the timing-validation module, and
the orchestrator's routing — all without requiring a live Gemini API call.

A FakeLLMService stands in for GeminiProvider so these tests can run in any
environment (including sandboxes with no network access to Google's API).
Real API connectivity is separately covered by test_connection.py, which
does require GEMINI_API_KEY and network access.

Run with: python tests/test_workflows.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services import LLMResponse, LLMService, parse_duration, assess_timing, assess_scene_consistency
from workflows import (
    VideoScriptWorkflow,
    StoryboardWorkflow,
    ShotListWorkflow,
    VoiceoverWorkflow,
    SocialVideoWorkflow,
)


class FakeLLMService(LLMService):
    """
    Deterministic stand-in for GeminiProvider. Returns canned, realistic-shaped
    text so workflow logic (call counts, revision triggering, dict shape) can
    be verified without a live API call.
    """

    def __init__(self, script_lines=8, words_per_line=18):
        self.calls = []
        self._script_lines = script_lines
        self._words_per_line = words_per_line

    def generate(self, prompt: str, system_prompt=None, temperature: float = 0.7, max_tokens=None) -> LLMResponse:
        self.calls.append(prompt[:60])
        lower = prompt.lower()

        if "extract" in lower and "image" in lower:
            text = "a modern ergonomic chair in a bright sunlit home office, warm natural light"
        elif "storyboard" in lower and "table" in lower:
            text = self._fake_storyboard_table()
        elif "shot list" in lower or ("shot" in lower and "table" in lower):
            text = self._fake_shot_list_table()
        elif "scene" in lower and ("plan" in lower or "beat" in lower):
            text = "## Scene Plan\n1. 0:00-0:05 — Hook\n2. 0:05-0:20 — Body\n3. 0:20-0:30 — CTA"
        elif "voice-over" in lower or "voiceover" in lower:
            text = self._fake_voiceover()
        elif "hook" in lower:
            text = "## Hook & Retention Plan\nHook: 'Wait, you're brewing coffee wrong.'\n3 fast scenes, captions on every scene."
        elif "visual language" in lower:
            text = "## Visual Language\nWarm, natural palette. Medium-tight framing. Moderate cut pace."
        elif "production" in lower and "analysis" in lower.replace("analyze", "analysis"):
            text = "## Production Analysis\n1 location (home office). 1 talent. Tripod + softbox needed."
        else:
            text = self._fake_scene_script()

        return LLMResponse(text=text, model="gemini-3.5-flash-lite", provider="Gemini")

    def get_model_name(self) -> str:
        return "gemini-3.5-flash-lite"

    def get_provider_name(self) -> str:
        return "Gemini"

    def _fake_scene_script(self) -> str:
        lines = []
        for i in range(1, self._script_lines + 1):
            words = " ".join(["word"] * self._words_per_line)
            lines.append(
                f"**Scene {i}**\nTiming: 0:{(i-1)*3:02d}-0:{i*3:02d}\n"
                f"Visual/Action: something happens\n"
                f"Dialogue/Narration: {words}\n"
                f"On-screen text: none\nAudio: light music\n"
            )
        return "\n".join(lines)

    def _fake_voiceover(self) -> str:
        words = " ".join(["word"] * self._words_per_line)
        return f"Beat 1 (0:00-0:05): {words} [pause 1s]\nBeat 2 (0:05-0:10): {words}\n\nEstimated total: ~10s"

    def _fake_storyboard_table(self) -> str:
        header = "| Scene | Duration | Visual Description | Subject/Action | Camera Angle | Camera Movement | Composition | Lighting/Mood | Voice-over/Dialogue | On-screen Text | Audio | Transition |\n"
        sep = "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        rows = ""
        for i in range(1, 4):
            rows += f"| Scene {i} | 0:{(i-1)*5:02d}-0:{i*5:02d} | wide shot of a home office | presenter gestures | eye-level | static | rule of thirds | warm natural | brief VO line | none | soft music | cut |\n"
        return header + sep + rows

    def _fake_shot_list_table(self) -> str:
        header = "| Shot # | Scene | Shot Type | Camera Angle | Camera Movement | Subject | Action | Location | Props | Audio | Duration | Production Notes |\n"
        sep = "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        rows = ""
        for i in range(1, 4):
            rows += f"| {i} | Scene {i} | medium | eye-level | static | presenter | speaks to camera | home office | laptop | sync sound | 0:{(i-1)*5:02d}-0:{i*5:02d} | needs softbox |\n"
        return header + sep + rows


class TimingModuleTests(unittest.TestCase):
    def test_parse_duration_seconds(self):
        self.assertEqual(parse_duration("30 seconds"), 30)
        self.assertEqual(parse_duration("45s"), 45)
        self.assertEqual(parse_duration(20), 20)

    def test_parse_duration_minutes(self):
        self.assertEqual(parse_duration("2 minutes"), 120)
        self.assertEqual(parse_duration("1 min"), 60)

    def test_parse_duration_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            parse_duration("2 seconds")
        with self.assertRaises(ValueError):
            parse_duration("10000 seconds")

    def test_parse_duration_no_number_raises(self):
        with self.assertRaises(ValueError):
            parse_duration("soon")

    def test_assess_timing_within_target(self):
        # ~145 wpm -> 30s of narration is ~72 words
        text = "Dialogue/Narration: " + " ".join(["word"] * 72)
        report = assess_timing(text, 30)
        self.assertEqual(report.status, "within target")
        self.assertTrue(report.is_within_target)

    def test_assess_timing_over_target(self):
        text = "Dialogue/Narration: " + " ".join(["word"] * 400)
        report = assess_timing(text, 30)
        self.assertEqual(report.status, "over target")

    def test_assess_scene_consistency_sums_durations(self):
        text = "Scene 1\nDuration: 0:00-0:05\n\nScene 2\nDuration: 0:05-0:15\n"
        report = assess_scene_consistency(text, 15)
        self.assertEqual(report.total_scene_seconds, 15)
        self.assertEqual(report.status, "within target")

    def test_assess_scene_consistency_no_scenes_found(self):
        report = assess_scene_consistency("no scene markers here", 30)
        self.assertEqual(report.status, "unverified")


class VideoScriptWorkflowTests(unittest.TestCase):
    def test_run_returns_expected_shape(self):
        llm = FakeLLMService(script_lines=6, words_per_line=9)  # sized to land near target
        workflow = VideoScriptWorkflow(llm)
        progress = []
        result = workflow.run(
            topic="A productivity app", objective="Drive sign-ups", audience="Busy professionals",
            platform="Instagram Reels", duration="30 seconds", tone="Energetic",
            on_progress=progress.append,
        )
        self.assertIn("final", result)
        self.assertIn("plan", result)
        self.assertIn("draft", result)
        self.assertIn("timing_report", result)
        self.assertEqual(result["model"], "gemini-3.5-flash-lite")
        self.assertTrue(len(progress) >= 3)
        # plan, draft, then either finalize or revise = at least 3 LLM calls
        self.assertGreaterEqual(len(llm.calls), 3)

    def test_over_duration_triggers_revision_call(self):
        llm = FakeLLMService(script_lines=20, words_per_line=20)  # deliberately way too long
        workflow = VideoScriptWorkflow(llm)
        result = workflow.run(
            topic="X", objective="X", audience="X", platform="TikTok",
            duration="10 seconds", tone="Bold",
        )
        self.assertTrue(result["revised_for_timing"])


class StoryboardWorkflowTests(unittest.TestCase):
    def test_run_without_image(self):
        llm = FakeLLMService()
        workflow = StoryboardWorkflow(llm, image_generator=None)
        result = workflow.run(
            concept_or_script="A short ad for a chair", platform="YouTube (long-form)",
            duration="15 seconds", tone="Cinematic", generate_reference_image=False,
        )
        self.assertIn("final", result)
        self.assertIsNone(result["image"])
        self.assertIn("timing_report", result)

    def test_run_with_image_generator_unconfigured(self):
        """generate_reference_image=True but no image generator passed -> graceful fallback, never raises."""
        llm = FakeLLMService()
        workflow = StoryboardWorkflow(llm, image_generator=None)
        result = workflow.run(
            concept_or_script="A short ad for a chair", platform="YouTube (long-form)",
            duration="15 seconds", tone="Cinematic", generate_reference_image=True,
        )
        self.assertIsNotNone(result["image"])
        self.assertFalse(result["image"]["success"])
        self.assertIn("fallback", result["image"])


class ShotListWorkflowTests(unittest.TestCase):
    def test_run_returns_expected_shape(self):
        llm = FakeLLMService()
        workflow = ShotListWorkflow(llm)
        result = workflow.run(
            concept_or_script="Office product demo", duration="20 seconds",
            locations="Home office", cast_or_talent="1 presenter",
        )
        self.assertIn("final", result)
        self.assertIn("production_plan", result)
        self.assertIn("timing_report", result)


class VoiceoverWorkflowTests(unittest.TestCase):
    def test_run_returns_expected_shape(self):
        llm = FakeLLMService(words_per_line=10)
        workflow = VoiceoverWorkflow(llm)
        result = workflow.run(
            topic="New savings feature", audience="Existing users", platform="YouTube (long-form)",
            duration="15 seconds", tone="Warm",
        )
        self.assertIn("final", result)
        self.assertIn("delivery_plan", result)
        self.assertIn("timing_report", result)


class SocialVideoWorkflowTests(unittest.TestCase):
    def test_run_returns_expected_shape(self):
        llm = FakeLLMService(script_lines=3, words_per_line=8)
        workflow = SocialVideoWorkflow(llm)
        result = workflow.run(
            topic="3 coffee brewing mistakes", platform="TikTok", audience="Coffee lovers",
            duration="15 seconds", tone="Energetic", cta="Follow for more",
        )
        self.assertIn("final", result)
        self.assertIn("hook_plan", result)
        self.assertIn("timing_report", result)


class OrchestratorTests(unittest.TestCase):
    def test_unknown_capability_raises(self):
        from video_production_agent import VideoProductionAgent
        agent = VideoProductionAgent(provider=FakeLLMService())
        with self.assertRaises(ValueError):
            agent.generate("not_a_real_capability", {})

    def test_all_five_capabilities_routable(self):
        from video_production_agent import VideoProductionAgent
        agent = VideoProductionAgent(provider=FakeLLMService(script_lines=4, words_per_line=8))
        base_params = {"duration": "20 seconds", "topic": "Test", "concept_or_script": "Test concept"}
        for capability in ["video_script", "storyboard", "shot_list", "voiceover", "social_video"]:
            result = agent.generate(capability, dict(base_params))
            self.assertIn("final", result, f"{capability} did not return a 'final' key")


if __name__ == "__main__":
    unittest.main(verbosity=2)

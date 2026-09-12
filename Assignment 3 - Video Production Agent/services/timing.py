"""Deterministic timing estimates used after every production workflow.

The speaking-rate assumption (WORDS_PER_MINUTE) and tolerance band (TOLERANCE)
are intentionally centralised and documented here rather than buried inside
a prompt, so the whole agent uses one consistent, configurable assumption.
"""

import re
from dataclasses import dataclass
from typing import List

WORDS_PER_MINUTE = 145   # Conversational voice-over pace used for all planning estimates.
TOLERANCE = 0.20         # +/-20% of the requested runtime is treated as "within target".


@dataclass
class TimingReport:
    requested_seconds: int
    estimated_words: int
    estimated_seconds: int
    target_words: int
    status: str
    guidance: str

    def as_markdown(self) -> str:
        return (
            "### Timing check\n"
            f"- Requested runtime: **{self.requested_seconds}s**\n"
            f"- Estimated spoken words: **{self.estimated_words}** (planning rate: {WORDS_PER_MINUTE} words/minute)\n"
            f"- Estimated narration runtime: **{self.estimated_seconds}s**\n"
            f"- Result: **{self.status}** — {self.guidance}"
        )

    @property
    def is_within_target(self) -> bool:
        return self.status == "within target"


@dataclass
class SceneTimingReport:
    requested_seconds: int
    scene_seconds: List[int]
    total_scene_seconds: int
    status: str
    guidance: str

    def as_markdown(self) -> str:
        breakdown = " + ".join(str(s) for s in self.scene_seconds) or "0"
        return (
            "### Scene timing check\n"
            f"- Requested runtime: **{self.requested_seconds}s**\n"
            f"- Scene breakdown: {breakdown} = **{self.total_scene_seconds}s**\n"
            f"- Result: **{self.status}** — {self.guidance}"
        )

    @property
    def is_within_target(self) -> bool:
        return self.status == "within target"


def parse_duration(value) -> int:
    if isinstance(value, int):
        seconds = value
    else:
        match = re.search(r"\d+", str(value))
        if not match:
            raise ValueError("Duration must contain a positive number of seconds.")
        seconds = int(match.group())
        if "min" in str(value).lower() and "sec" not in str(value).lower():
            seconds *= 60
    if not 5 <= seconds <= 3600:
        raise ValueError("Duration must be between 5 seconds and 3600 seconds.")
    return seconds


def assess_timing(text: str, requested_seconds: int) -> TimingReport:
    # Count prose after production labels; labels and markdown are excluded where possible.
    spoken_lines = [line for line in text.splitlines()
                    if re.search(r"(dialogue|narration|voice-over|spoken|say)", line, re.I)]
    source = " ".join(spoken_lines) if spoken_lines else text
    source = re.sub(r"^.*?:", "", source, flags=re.M)
    words = len(re.findall(r"\b[\w’'-]+\b", source))
    estimated = round(words / WORDS_PER_MINUTE * 60)
    target_words = round(requested_seconds / 60 * WORDS_PER_MINUTE)
    lower, upper = requested_seconds * (1 - TOLERANCE), requested_seconds * (1 + TOLERANCE)
    if lower <= estimated <= upper:
        status, guidance = "within target", "Narration is close to the requested runtime."
    elif estimated > upper:
        status, guidance = "over target", "Trim spoken lines or leave more of the story to visuals before recording."
    else:
        status, guidance = "under target", "Add useful spoken detail or allow the visuals and pauses to carry the remaining time."
    return TimingReport(requested_seconds, words, estimated, target_words, status, guidance)


def extract_scene_seconds(text: str) -> List[int]:
    """
    Pull per-scene duration figures (e.g. '0:00-0:05', '5s', '5 seconds')
    out of a scene-labelled production document. Used to sanity-check that
    a storyboard or shot list's scene durations add up to the requested runtime.
    """
    scene_blocks = re.split(r"(?im)^\s*#{0,4}\s*(?:scene|shot)\b", text)[1:]
    seconds: List[int] = []
    for block in scene_blocks:
        head = block[:200]
        range_match = re.search(r"(\d+):(\d{2})\s*[-–—]\s*(\d+):(\d{2})", head)
        if range_match:
            start = int(range_match.group(1)) * 60 + int(range_match.group(2))
            end = int(range_match.group(3)) * 60 + int(range_match.group(4))
            if end > start:
                seconds.append(end - start)
                continue
        dur_match = re.search(r"(\d+(?:\.\d+)?)\s*(sec|second)", head, re.I)
        if dur_match:
            seconds.append(round(float(dur_match.group(1))))
    return seconds


def assess_scene_consistency(text: str, requested_seconds: int) -> SceneTimingReport:
    """Check whether a scene-by-scene document's durations sum close to the requested runtime."""
    scene_seconds = extract_scene_seconds(text)
    total = sum(scene_seconds)
    lower, upper = requested_seconds * (1 - TOLERANCE), requested_seconds * (1 + TOLERANCE)

    if not scene_seconds:
        status = "unverified"
        guidance = "No explicit per-scene durations were detected to total against the runtime."
    elif lower <= total <= upper:
        status, guidance = "within target", "Scene durations add up close to the requested runtime."
    elif total > upper:
        status, guidance = "over target", "Trim or merge scenes so the total matches the requested runtime."
    else:
        status, guidance = "under target", "Add scenes or extend timings to fill the requested runtime."

    return SceneTimingReport(requested_seconds, scene_seconds, total, status, guidance)

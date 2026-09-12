"""
Blog Workflow
=============
A three-step pipeline:
  1. plan_outline    — produce a structured blog outline from the brief
  2. draft_content   — write the full draft from the outline
  3. review_and_finalize — polish and return the publication-ready post

Each step makes one real LLM call. Progress callbacks allow the UI
to display accurate status without faking stages.
"""

import os
from pathlib import Path
from typing import Callable, Optional

from services.llm_service import LLMService


def _load_system_prompt() -> str:
    """Load the blog system prompt from the prompts directory."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "blog_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class BlogWorkflow:
    """
    Orchestrates the three-stage blog writing pipeline.

    Args:
        llm: Any LLMService implementation (Gemini, Claude, etc.)
    """

    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        topic: str,
        audience: str,
        tone: str,
        purpose: str,
        desired_length: str,
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Execute the full blog writing pipeline.

        Returns a dict with keys:
          - 'outline': the planned structure
          - 'draft': the raw draft
          - 'final': the polished final post
          - 'model': model identifier used
          - 'provider': provider name
        """

        def notify(message: str):
            if on_progress:
                on_progress(message)

        brief = self._format_brief(
            topic, audience, tone, purpose, desired_length, additional_instructions
        )

        # ── Step 1: Plan the outline ──────────────────────────────────────────
        notify("📋 Step 1/3 — Analysing brief and planning blog structure…")
        outline = self._plan_outline(brief)

        # ── Step 2: Write the full draft ──────────────────────────────────────
        notify("✍️  Step 2/3 — Writing the full blog draft…")
        draft = self._draft_content(brief, outline)

        # ── Step 3: Review and finalise ───────────────────────────────────────
        notify("🔍 Step 3/3 — Reviewing and finalising content…")
        final = self._review_and_finalize(brief, outline, draft)

        notify("✅ Blog post complete.")

        return {
            "outline": outline,
            "draft": draft,
            "final": final,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(
        self, topic, audience, tone, purpose, desired_length, additional
    ) -> str:
        parts = [
            f"Topic: {topic}",
            f"Target audience: {audience}",
            f"Tone: {tone}",
            f"Purpose of this blog post: {purpose}",
            f"Desired length: {desired_length}",
        ]
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _plan_outline(self, brief: str) -> str:
        prompt = f"""You are planning the structure of a blog post.

Based on the brief below, produce a clear, detailed blog outline.
Include:
- A working title
- The opening hook approach (one sentence describing the hook strategy)
- Each major H2 section with a brief description of its content
- H3 sub-points where helpful
- A closing direction

Brief:
{brief}

Return only the outline in markdown format. Do not write any blog content yet."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.5,
        )
        return response.text

    def _draft_content(self, brief: str, outline: str) -> str:
        prompt = f"""Write a complete blog post following the outline provided.

Brief:
{brief}

Approved Outline:
{outline}

Instructions:
- Write the full blog post in markdown
- Follow the outline structure exactly
- Apply the tone and audience level from the brief
- Make it engaging, human, and genuinely useful
- Do not add a meta description or SEO elements — this is a blog draft

Return only the blog post content in markdown."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.75,
        )
        return response.text

    def _review_and_finalize(self, brief: str, outline: str, draft: str) -> str:
        prompt = f"""Review and finalise the blog post below.

Original Brief:
{brief}

Planned Outline:
{outline}

Draft:
{draft}

Your task:
1. Fix any flow issues — transitions between sections should feel natural
2. Sharpen the opening hook if it does not immediately grab attention
3. Improve any sentences that are awkward, repetitive, or unclear
4. Ensure the tone matches the brief throughout
5. Verify the conclusion provides a satisfying close and a clear next step
6. Return the complete, polished, publication-ready blog post in markdown

Return only the final blog post. Do not include commentary or notes."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.6,
        )
        return response.text

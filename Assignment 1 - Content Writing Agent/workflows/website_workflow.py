"""
Website Content Workflow
========================
A two-step pipeline:
  1. analyze_and_structure — understand the page purpose, map the content hierarchy
  2. generate_page_content  — write all copy sections with CTAs

Different page types (Homepage, Product, Service, About, Landing) require
different copy strategies. This workflow handles that distinction automatically.
"""

from pathlib import Path
from typing import Callable, Optional

from services.llm_service import LLMService


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "website_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class WebsiteWorkflow:
    """
    Orchestrates the two-stage website content writing pipeline.

    Args:
        llm: Any LLMService implementation.
    """

    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        page_type: str,
        business_name: str,
        product_or_service: str,
        target_audience: str,
        value_proposition: str,
        tone: str,
        conversion_goal: str,
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Execute the website content pipeline.

        Returns a dict with:
          - 'content_strategy': the structural plan and copy strategy
          - 'final': the complete page copy
          - 'model': model identifier used
          - 'provider': provider name
        """

        def notify(message: str):
            if on_progress:
                on_progress(message)

        brief = self._format_brief(
            page_type,
            business_name,
            product_or_service,
            target_audience,
            value_proposition,
            tone,
            conversion_goal,
            additional_instructions,
        )

        # ── Step 1: Analyse and structure ─────────────────────────────────────
        notify("📐 Step 1/2 — Analysing page purpose and planning content structure…")
        strategy = self._analyze_and_structure(brief, page_type)

        # ── Step 2: Generate the full page copy ───────────────────────────────
        notify("✍️  Step 2/2 — Writing page copy with CTAs…")
        final = self._generate_page_content(brief, strategy, page_type)

        notify("✅ Website content complete.")

        return {
            "content_strategy": strategy,
            "final": final,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(
        self,
        page_type,
        business_name,
        product_or_service,
        target_audience,
        value_proposition,
        tone,
        conversion_goal,
        additional,
    ) -> str:
        parts = [
            f"Page type: {page_type}",
            f"Business / brand name: {business_name}",
            f"Product or service: {product_or_service}",
            f"Target audience: {target_audience}",
            f"Core value proposition: {value_proposition}",
            f"Brand tone: {tone}",
            f"Primary conversion goal: {conversion_goal}",
        ]
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _analyze_and_structure(self, brief: str, page_type: str) -> str:
        prompt = f"""You are planning the content structure for a {page_type} page.

Brief:
{brief}

Produce a content strategy document that includes:
1. The primary message this page must communicate (one sentence)
2. The sections this page needs, in order from top to bottom
3. For each section: its purpose, what it communicates, and the emotional job it does
4. Where CTAs should appear and what action they should prompt
5. One or two trust signals or objection handlers to include

Return this as a structured plan in markdown. Do not write any final copy yet."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.5,
        )
        return response.text

    def _generate_page_content(
        self, brief: str, strategy: str, page_type: str
    ) -> str:
        prompt = f"""Write the complete {page_type} page copy following the content strategy below.

Brief:
{brief}

Content Strategy:
{strategy}

Instructions:
- Write all copy sections in full — headlines, subheadings, body copy, CTAs
- Label each section clearly (e.g., ## Hero Section, ## Features, ## CTA)
- Every CTA must be specific and action-oriented
- Apply the brand tone from the brief consistently
- Benefits must be stated from the customer's perspective, not the company's
- The most important message must appear in the first visible section
- Return the complete page copy in markdown

Return only the page copy. No commentary."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.7,
        )
        return response.text

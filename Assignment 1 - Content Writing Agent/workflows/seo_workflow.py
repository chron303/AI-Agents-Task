"""
SEO Article Workflow
====================
A three-step pipeline:
  1. research_keywords_and_intent — map search intent, plan keyword strategy
  2. draft_seo_article            — write the article with proper heading hierarchy
  3. optimize_and_add_meta        — add meta title, meta description, FAQ section

The goal is content that serves readers first and search engines second.
Keyword stuffing is never appropriate; natural integration is always the target.
"""

from pathlib import Path
from typing import Callable, Optional

from services.llm_service import LLMService


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "seo_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class SEOWorkflow:
    """
    Orchestrates the three-stage SEO article writing pipeline.

    Args:
        llm: Any LLMService implementation.
    """

    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        topic: str,
        primary_keyword: str,
        secondary_keywords: str,
        target_audience: str,
        search_intent: str,
        desired_length: str,
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Execute the full SEO article pipeline.

        Returns a dict with:
          - 'keyword_strategy': the keyword and intent analysis
          - 'draft': the written article
          - 'final': the complete optimised article with meta elements
          - 'model': model identifier used
          - 'provider': provider name
        """

        def notify(message: str):
            if on_progress:
                on_progress(message)

        brief = self._format_brief(
            topic,
            primary_keyword,
            secondary_keywords,
            target_audience,
            search_intent,
            desired_length,
            additional_instructions,
        )

        # ── Step 1: Research keyword strategy and intent ───────────────────────
        notify("🔍 Step 1/3 — Analysing search intent and building keyword strategy…")
        keyword_strategy = self._research_keywords_and_intent(brief)

        # ── Step 2: Draft the article ─────────────────────────────────────────
        notify("✍️  Step 2/3 — Drafting the SEO article with H1/H2/H3 structure…")
        draft = self._draft_seo_article(brief, keyword_strategy)

        # ── Step 3: Optimise and add meta elements ────────────────────────────
        notify("📊 Step 3/3 — Adding meta elements, FAQs, and final optimisation…")
        final = self._optimize_and_add_meta(brief, keyword_strategy, draft)

        notify("✅ SEO article complete.")

        return {
            "keyword_strategy": keyword_strategy,
            "draft": draft,
            "final": final,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(
        self,
        topic,
        primary_keyword,
        secondary_keywords,
        target_audience,
        search_intent,
        desired_length,
        additional,
    ) -> str:
        parts = [
            f"Article topic: {topic}",
            f"Primary keyword: {primary_keyword}",
            f"Secondary keywords: {secondary_keywords}",
            f"Target audience: {target_audience}",
            f"Search intent type: {search_intent}",
            f"Desired article length: {desired_length}",
        ]
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _research_keywords_and_intent(self, brief: str) -> str:
        prompt = f"""You are planning an SEO article.

Brief:
{brief}

Produce a keyword and search intent strategy document that includes:
1. Search intent analysis: Why is someone searching for this? What do they want to find?
2. Primary keyword placement plan: where it should appear naturally (title, intro, 1–2 body sections, conclusion)
3. Secondary keyword integration: which sections each secondary keyword fits most naturally
4. 5–8 LSI/semantic terms that signal topical authority for this subject
5. Recommended H2 section structure with the keyword/topic each section targets
6. 4–6 FAQ questions that target long-tail search queries around this topic
7. Recommended article angle (the specific perspective that makes this article useful and distinct)

Return this as a structured strategy document in markdown. Do not write the article yet."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.5,
        )
        return response.text

    def _draft_seo_article(self, brief: str, keyword_strategy: str) -> str:
        prompt = f"""Write the complete SEO article following the brief and keyword strategy.

Brief:
{brief}

Keyword Strategy:
{keyword_strategy}

Writing Instructions:
- Begin with an H1 title that includes the primary keyword naturally
- Write an introduction (no heading) that hooks the reader and includes the primary keyword within the first 100 words
- Structure the body with H2 for major sections, H3 for sub-topics
- Use keywords as specified in the strategy — natural integration only, no stuffing
- Write for the reader first; SEO structure is the scaffold, not the purpose
- Include practical examples, explanations, or step-by-step instructions where appropriate
- End with a conclusion that summarises key takeaways and reinforces the primary keyword naturally

Return only the article body (H1 through conclusion) in markdown.
Do not include meta title, meta description, or FAQ yet — those come in the next step."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.7,
        )
        return response.text

    def _optimize_and_add_meta(
        self, brief: str, keyword_strategy: str, draft: str
    ) -> str:
        prompt = f"""Complete the SEO article by adding meta elements and FAQ, then present the final optimised version.

Brief:
{brief}

Keyword Strategy:
{keyword_strategy}

Article Draft:
{draft}

Your task:
1. Write a Meta Title (50–60 characters, primary keyword near the front, compelling)
2. Write a Meta Description (150–160 characters, includes primary keyword, implies benefit)
3. Add an FAQ section at the end of the article targeting the long-tail questions from the strategy
4. Review the draft for any keyword over-use or under-use and make corrections
5. Check that the H1/H2/H3 hierarchy is clean and logical

Return the final complete article in this order:
```
**Meta Title:** [your meta title]
**Meta Description:** [your meta description]

---

[Full article from H1 to conclusion]

---

## Frequently Asked Questions

[FAQ content]
```

Return only this final formatted output."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.6,
        )
        return response.text

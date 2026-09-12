"""
E-book Workflow
===============
A three-step pipeline:
  1. design_chapter_plan — create the full e-book structure with chapter objectives
  2. write_chapters       — write each chapter with depth and consistency
  3. assemble_ebook       — add front matter, introduction, and conclusion to complete the book

An e-book is not a long blog post. This workflow treats it as a structured
learning resource with deliberate chapter progression.
"""

from pathlib import Path
from typing import Callable, Optional

from services.llm_service import LLMService


def _load_system_prompt() -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / "ebook_prompt.md"
    return prompt_path.read_text(encoding="utf-8")


class EbookWorkflow:
    """
    Orchestrates the three-stage e-book writing pipeline.

    Args:
        llm: Any LLMService implementation.
    """

    def __init__(self, llm: LLMService):
        self._llm = llm
        self._system_prompt = _load_system_prompt()

    def run(
        self,
        title: str,
        overall_topic: str,
        target_reader: str,
        book_objective: str,
        num_chapters: int,
        depth_level: str,
        tone: str,
        additional_instructions: str = "",
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Execute the full e-book writing pipeline.

        Returns a dict with:
          - 'chapter_plan': the structured chapter outline
          - 'chapters': the written chapter content
          - 'final': the assembled complete e-book
          - 'model': model identifier used
          - 'provider': provider name
        """

        def notify(message: str):
            if on_progress:
                on_progress(message)

        brief = self._format_brief(
            title,
            overall_topic,
            target_reader,
            book_objective,
            num_chapters,
            depth_level,
            tone,
            additional_instructions,
        )

        # ── Step 1: Design the chapter plan ───────────────────────────────────
        notify("📚 Step 1/3 — Designing chapter structure and learning progression…")
        chapter_plan = self._design_chapter_plan(brief, num_chapters)

        # ── Step 2: Write all chapters ────────────────────────────────────────
        notify("✍️  Step 2/3 — Writing e-book chapters with depth and examples…")
        chapters = self._write_chapters(brief, chapter_plan)

        # ── Step 3: Assemble the complete e-book ──────────────────────────────
        notify("📖 Step 3/3 — Assembling the complete e-book with front matter…")
        final = self._assemble_ebook(brief, chapter_plan, chapters)

        notify("✅ E-book complete.")

        return {
            "chapter_plan": chapter_plan,
            "chapters": chapters,
            "final": final,
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _format_brief(
        self,
        title,
        overall_topic,
        target_reader,
        book_objective,
        num_chapters,
        depth_level,
        tone,
        additional,
    ) -> str:
        parts = [
            f"E-book title: {title}",
            f"Overall topic: {overall_topic}",
            f"Target reader: {target_reader}",
            f"Book objective (what the reader will achieve): {book_objective}",
            f"Number of chapters: {num_chapters}",
            f"Depth level: {depth_level}",
            f"Tone: {tone}",
        ]
        if additional.strip():
            parts.append(f"Additional instructions: {additional}")
        return "\n".join(parts)

    def _design_chapter_plan(self, brief: str, num_chapters: int) -> str:
        prompt = f"""You are structuring an e-book.

Brief:
{brief}

Design a complete chapter plan for a {num_chapters}-chapter e-book.

For each chapter provide:
- Chapter number and title
- Core learning objective (what the reader will understand/be able to do after this chapter)
- 4–6 key topics or sub-sections to be covered
- How this chapter connects to the previous and next chapter (show the progression)

Also include:
- The book introduction objective (what it promises and who it's for)
- The conclusion objective (how it synthesises and motivates the reader)

Return only the chapter plan in structured markdown."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.5,
        )
        return response.text

    def _write_chapters(self, brief: str, chapter_plan: str) -> str:
        prompt = f"""Write the complete chapter content for this e-book.

Brief:
{brief}

Chapter Plan:
{chapter_plan}

Instructions:
- Write each chapter in full — do not summarise or shortcut
- Begin each chapter with a brief engaging hook or scenario
- Use H2 for the chapter title, H3 for sub-sections within the chapter
- Include at least one practical example or case study per chapter
- End each chapter with 3–5 key takeaways in a bullet list
- Add a one-sentence transition at the end of each chapter leading into the next
- Maintain consistent depth across all chapters — no chapter should feel rushed
- Match the tone and depth level specified in the brief

Return all chapters in sequence, clearly labelled, in markdown format.
Do not include the introduction or conclusion — those come separately."""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.7,
            max_tokens=8000,
        )
        return response.text

    def _assemble_ebook(
        self, brief: str, chapter_plan: str, chapters: str
    ) -> str:
        prompt = f"""Assemble the complete e-book by adding front matter, introduction, and conclusion.

Brief:
{brief}

Chapter Plan:
{chapter_plan}

Chapters Already Written:
{chapters}

Your task:
1. Write a Title Page section (title, subtitle if appropriate, brief author context line)
2. Write a compelling Introduction (300–500 words) that:
   - Hooks the reader with the core problem or opportunity
   - States clearly who this book is for
   - Explains what the reader will gain by the end
   - Briefly previews the chapter journey
3. Insert the chapters exactly as written (do not modify them)
4. Write a Conclusion (250–400 words) that:
   - Synthesises the key insights across all chapters
   - Gives the reader a motivating close and clear next step
   - Does not introduce new major concepts

Return the complete assembled e-book in markdown, in this order:
Title Page → Introduction → Chapters → Conclusion"""

        response = self._llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            temperature=0.65,
            max_tokens=10000,
        )
        return response.text

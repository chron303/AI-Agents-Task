"""
Content Writing Agent
=====================
The central orchestrator for the Content Writing Agent.

This module:
  - Accepts a content brief (type + parameters)
  - Selects the appropriate workflow
  - Executes the workflow via the LLM service
  - Returns the final result

Both the Streamlit UI (app.py) and the CLI use this module.
No generation logic is duplicated between them.

Usage (as a library):
    from content_writing_agent import ContentWritingAgent
    from services import GeminiProvider

    agent = ContentWritingAgent(provider=GeminiProvider())
    result = agent.generate(content_type="blog", params={...})

Usage (as a CLI):
    python content_writing_agent.py
"""

import os
import sys
from typing import Callable, Optional

from dotenv import load_dotenv

from services import GeminiProvider, LLMService
from workflows import BlogWorkflow, EbookWorkflow, SEOWorkflow, WebsiteWorkflow

load_dotenv()


CONTENT_TYPES = {
    "blog": "Blog Post",
    "website": "Website Content",
    "ebook": "E-book",
    "seo": "SEO Article",
}


class ContentWritingAgent:
    """
    The Content Writing Agent.

    Accepts any LLMService implementation — currently Gemini, later Claude.
    Selects and runs the correct workflow for each content type.
    """

    def __init__(self, provider: Optional[LLMService] = None):
        """
        Initialise the agent with an LLM provider.

        If no provider is passed, defaults to GeminiProvider (reads from .env).
        """
        self._llm = provider or GeminiProvider()

    def generate(
        self,
        content_type: str,
        params: dict,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> dict:
        """
        Generate content based on type and parameters.

        Args:
            content_type:  One of 'blog', 'website', 'ebook', 'seo'
            params:        Dictionary of inputs specific to the content type
            on_progress:   Optional callback to receive progress messages

        Returns:
            A dict with 'final' (the finished content) and intermediate outputs.

        Raises:
            ValueError: If content_type is not recognised.
            RuntimeError: If the LLM call fails.
        """
        content_type = content_type.lower().strip()

        if content_type not in CONTENT_TYPES:
            valid = ", ".join(CONTENT_TYPES.keys())
            raise ValueError(
                f"Unknown content type '{content_type}'. Valid types: {valid}"
            )

        if content_type == "blog":
            return self._run_blog(params, on_progress)
        elif content_type == "website":
            return self._run_website(params, on_progress)
        elif content_type == "ebook":
            return self._run_ebook(params, on_progress)
        elif content_type == "seo":
            return self._run_seo(params, on_progress)

    def get_provider_info(self) -> dict:
        """Return current provider and model information."""
        return {
            "provider": self._llm.get_provider_name(),
            "model": self._llm.get_model_name(),
        }

    # ── Workflow dispatchers ──────────────────────────────────────────────────

    def _run_blog(self, params: dict, on_progress) -> dict:
        workflow = BlogWorkflow(self._llm)
        return workflow.run(
            topic=params.get("topic", ""),
            audience=params.get("audience", "General audience"),
            tone=params.get("tone", "Informative"),
            purpose=params.get("purpose", "Inform and educate"),
            desired_length=params.get("desired_length", "1000–1500 words"),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_website(self, params: dict, on_progress) -> dict:
        workflow = WebsiteWorkflow(self._llm)
        return workflow.run(
            page_type=params.get("page_type", "Homepage"),
            business_name=params.get("business_name", ""),
            product_or_service=params.get("product_or_service", ""),
            target_audience=params.get("target_audience", ""),
            value_proposition=params.get("value_proposition", ""),
            tone=params.get("tone", "Professional"),
            conversion_goal=params.get("conversion_goal", ""),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_ebook(self, params: dict, on_progress) -> dict:
        workflow = EbookWorkflow(self._llm)
        return workflow.run(
            title=params.get("title", ""),
            overall_topic=params.get("overall_topic", ""),
            target_reader=params.get("target_reader", ""),
            book_objective=params.get("book_objective", ""),
            num_chapters=int(params.get("num_chapters", 5)),
            depth_level=params.get("depth_level", "Intermediate"),
            tone=params.get("tone", "Educational"),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )

    def _run_seo(self, params: dict, on_progress) -> dict:
        workflow = SEOWorkflow(self._llm)
        return workflow.run(
            topic=params.get("topic", ""),
            primary_keyword=params.get("primary_keyword", ""),
            secondary_keywords=params.get("secondary_keywords", ""),
            target_audience=params.get("target_audience", ""),
            search_intent=params.get("search_intent", "Informational"),
            desired_length=params.get("desired_length", "1200–1800 words"),
            additional_instructions=params.get("additional_instructions", ""),
            on_progress=on_progress,
        )


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def run_cli():
    """
    Interactive command-line interface for the Content Writing Agent.

    Shares 100% of the generation code with the Streamlit UI.
    """
    print("\n" + "=" * 60)
    print("  CONTENT WRITING AGENT  |  Technians AI Engineer Assignment")
    print("=" * 60)

    try:
        agent = ContentWritingAgent()
        info = agent.get_provider_info()
        print(f"\n✓ Connected to {info['provider']} | Model: {info['model']}")
    except EnvironmentError as e:
        print(f"\n✗ Configuration error: {e}")
        print("  → Create a .env file with GEMINI_API_KEY and GEMINI_MODEL set.")
        sys.exit(1)

    print("\nSelect content type:")
    options = list(CONTENT_TYPES.items())
    for i, (key, label) in enumerate(options, 1):
        print(f"  {i}. {label}")

    choice = input("\nEnter number (1–4): ").strip()
    try:
        idx = int(choice) - 1
        content_type, label = options[idx]
    except (ValueError, IndexError):
        print("✗ Invalid choice. Exiting.")
        sys.exit(1)

    print(f"\n── {label} ──")
    params = _collect_params_cli(content_type)

    print(f"\n{'─' * 60}")
    print("Generating content…")
    print("─" * 60)

    try:
        result = agent.generate(
            content_type=content_type,
            params=params,
            on_progress=lambda msg: print(f"\n  {msg}"),
        )
    except RuntimeError as e:
        print(f"\n✗ Generation failed:\n{e}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"  FINAL OUTPUT — {label}")
    print("=" * 60)
    print(result["final"])

    # Offer to save
    save = input("\n\nSave output to a file? (y/n): ").strip().lower()
    if save == "y":
        filename = input("Filename (e.g. my_blog.md): ").strip() or "output.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result["final"])
        print(f"✓ Saved to {filename}")


def _collect_params_cli(content_type: str) -> dict:
    """Collect user inputs for the selected content type via CLI."""

    def ask(label: str, default: str = "") -> str:
        prompt = f"  {label}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        val = input(prompt).strip()
        return val if val else default

    params = {}

    if content_type == "blog":
        params["topic"] = ask("Topic")
        params["audience"] = ask("Target audience", "General readers")
        params["tone"] = ask("Tone (e.g. Conversational, Professional, Witty)", "Informative")
        params["purpose"] = ask("Purpose (e.g. Educate, Inspire, Drive traffic)", "Inform and educate")
        params["desired_length"] = ask("Desired length (e.g. 800–1200 words)", "1000–1500 words")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "website":
        page_opts = ["Homepage", "Product Page", "Service Page", "About Page", "Landing Page"]
        print("  Page type options: " + ", ".join(f"{i+1}. {p}" for i, p in enumerate(page_opts)))
        pt_choice = ask("Page type (enter number or name)", "1")
        try:
            params["page_type"] = page_opts[int(pt_choice) - 1]
        except (ValueError, IndexError):
            params["page_type"] = pt_choice
        params["business_name"] = ask("Business / brand name")
        params["product_or_service"] = ask("Product or service being promoted")
        params["target_audience"] = ask("Target audience")
        params["value_proposition"] = ask("Core value proposition (what makes you different)")
        params["tone"] = ask("Brand tone (e.g. Professional, Friendly, Bold)", "Professional")
        params["conversion_goal"] = ask("Primary conversion goal (e.g. Book a demo, Buy now)")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "ebook":
        params["title"] = ask("E-book title")
        params["overall_topic"] = ask("Overall topic")
        params["target_reader"] = ask("Target reader / audience")
        params["book_objective"] = ask("What will the reader achieve / learn?")
        params["num_chapters"] = ask("Number of chapters", "5")
        params["depth_level"] = ask("Depth level (Beginner / Intermediate / Advanced)", "Intermediate")
        params["tone"] = ask("Tone (e.g. Educational, Conversational, Academic)", "Educational")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    elif content_type == "seo":
        params["topic"] = ask("Article topic")
        params["primary_keyword"] = ask("Primary keyword")
        params["secondary_keywords"] = ask("Secondary keywords (comma-separated)")
        params["target_audience"] = ask("Target audience")
        intent_opts = ["Informational", "Commercial", "Transactional", "Navigational"]
        print("  Search intent: " + ", ".join(f"{i+1}. {o}" for i, o in enumerate(intent_opts)))
        si = ask("Search intent (number or type)", "1")
        try:
            params["search_intent"] = intent_opts[int(si) - 1]
        except (ValueError, IndexError):
            params["search_intent"] = si
        params["desired_length"] = ask("Desired length (e.g. 1200–1800 words)", "1200–1800 words")
        params["additional_instructions"] = ask("Additional instructions (optional)")

    return params


if __name__ == "__main__":
    run_cli()

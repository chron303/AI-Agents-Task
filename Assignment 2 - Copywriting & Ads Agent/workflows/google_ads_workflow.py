import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService


class GoogleAdsWorkflow:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "google_ads_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        # Step 1: Analyze Search Intent
        on_progress("Analyzing search intent and keywords...")
        intent_prompt = f"""
        Analyze the following brief for a Google Search Ad:
        Product/Service: {params.get('product_or_service', 'N/A')}
        Target Keywords: {params.get('target_keywords', 'N/A')}
        Search Intent: {params.get('search_intent', 'N/A')}
        Target Audience: {params.get('target_audience', 'N/A')}
        Key Benefits: {params.get('key_benefits', 'N/A')}
        Offer/CTA: {params.get('offer', 'N/A')}
        
        Provide a brief strategy on how to map these keywords to headlines and how to address the search intent directly.
        """
        intent_res = self.llm.generate(prompt=intent_prompt, system_prompt=system_prompt)
        intent_text = intent_res.text
        
        # Step 2: Generate Constrained Copy
        on_progress("Drafting headlines and descriptions...")
        draft_prompt = f"""
        Based on the strategy:
        {intent_text}
        
        Generate the Google Ad components strictly adhering to character limits:
        - 5 Headlines (Max 30 characters each)
        - 3 Descriptions (Max 90 characters each)
        - 2 Display URL Paths (Max 15 characters each)
        
        Include the character count in brackets after each line e.g., "Headline 1: Fast Shipping [13 chars]".
        """
        draft_res = self.llm.generate(prompt=draft_prompt, system_prompt=system_prompt)
        draft_text = draft_res.text

        # Step 3: Review and Validate
        on_progress("Validating against Google Ads constraints...")
        val_prompt = f"""
        Review the following Google Ad copy:
        {draft_text}
        
        Ensure NO headline exceeds 30 characters.
        Ensure NO description exceeds 90 characters.
        Ensure there are no exclamation marks in the headlines.
        
        If there are errors, fix them. Return the final, validated ad copy clearly formatted.
        """
        val_res = self.llm.generate(prompt=val_prompt, system_prompt=system_prompt)
        final_copy = val_res.text

        return {
            "analysis": intent_text,
            "draft": draft_text,
            "final": final_copy,
            "model": val_res.model,
            "provider": val_res.provider
        }

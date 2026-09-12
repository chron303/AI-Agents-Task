import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService


class LinkedInAdsWorkflow:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "linkedin_ads_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        on_progress("Analyzing professional audience...")
        plan_prompt = f"""
        Analyze this brief for a LinkedIn Ad:
        Product/Service: {params.get('product_or_service', 'N/A')}
        Target Audience: {params.get('target_audience', 'N/A')}
        Business Pain Point: {params.get('pain_point', 'N/A')}
        Business Value/ROI: {params.get('key_benefit', 'N/A')}
        Offer: {params.get('offer', 'N/A')}
        
        Determine the most effective angle to appeal to this B2B audience's professional goals.
        """
        plan_res = self.llm.generate(prompt=plan_prompt, system_prompt=system_prompt)
        plan_text = plan_res.text
        
        on_progress("Generating B2B copy variations...")
        draft_prompt = f"""
        Based on the B2B angle:
        {plan_text}
        
        Generate exactly 2 distinct variations of the LinkedIn Ad.
        For each variation, include:
        - Introductory Text (Max 150 chars for the hook before 'See more')
        - Headline (Max 70 chars)
        - Description
        - CTA
        - Visual/Image Recommendation
        """
        draft_res = self.llm.generate(prompt=draft_prompt, system_prompt=system_prompt)
        final_copy = draft_res.text

        return {
            "analysis": plan_text,
            "final": final_copy,
            "model": draft_res.model,
            "provider": draft_res.provider
        }

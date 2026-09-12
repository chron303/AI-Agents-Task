import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService


class EmailCopyWorkflow:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "email_copy_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        on_progress("Analyzing email objective and audience intent...")
        plan_prompt = f"""
        Analyze this email marketing brief:
        Email Objective: {params.get('objective', 'N/A')}
        Product/Service: {params.get('product_or_service', 'N/A')}
        Target Audience: {params.get('target_audience', 'N/A')}
        Offer: {params.get('offer', 'N/A')}
        Brand Tone: {params.get('brand_tone', 'N/A')}
        
        Determine the psychological angle required to achieve this specific email objective.
        """
        plan_res = self.llm.generate(prompt=plan_prompt, system_prompt=system_prompt)
        plan_text = plan_res.text
        
        on_progress("Drafting email copy...")
        draft_prompt = f"""
        Based on the psychological angle:
        {plan_text}
        
        Generate the complete email copy including:
        - 3 Subject Line Variations
        - Preview Text
        - Email Body
        - CTA
        """
        draft_res = self.llm.generate(prompt=draft_prompt, system_prompt=system_prompt)
        final_copy = draft_res.text

        return {
            "analysis": plan_text,
            "final": final_copy,
            "model": draft_res.model,
            "provider": draft_res.provider
        }

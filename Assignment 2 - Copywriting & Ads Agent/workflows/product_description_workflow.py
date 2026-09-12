import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService


class ProductDescriptionWorkflow:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "product_description_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        on_progress("Extracting features and mapping to benefits...")
        plan_prompt = f"""
        Analyze this product brief:
        Product Name: {params.get('product_name', 'N/A')}
        Category: {params.get('product_category', 'N/A')}
        Features: {params.get('features', 'N/A')}
        Target Customer: {params.get('target_customer', 'N/A')}
        Brand Tone: {params.get('brand_tone', 'N/A')}
        
        Map each provided feature to a compelling, customer-centric benefit.
        """
        plan_res = self.llm.generate(prompt=plan_prompt, system_prompt=system_prompt)
        plan_text = plan_res.text
        
        on_progress("Drafting product descriptions...")
        draft_prompt = f"""
        Using the feature-to-benefit mapping:
        {plan_text}
        
        Generate the final product description components:
        - Short Description (2-3 sentences)
        - Long Description (narrative)
        - Key Selling Points (4-6 bullet points)
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

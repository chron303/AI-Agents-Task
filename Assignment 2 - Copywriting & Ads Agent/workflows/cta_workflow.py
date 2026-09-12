import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService


class CTAWorkflow:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "cta_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        on_progress("Analyzing desired action and context...")
        plan_prompt = f"""
        Analyze this CTA brief:
        Product/Service: {params.get('product_or_service', 'N/A')}
        Desired Action: {params.get('desired_action', 'N/A')}
        Target Audience: {params.get('target_audience', 'N/A')}
        Context/Placement: {params.get('context', 'N/A')}
        Brand Tone: {params.get('brand_tone', 'N/A')}
        
        Identify the primary friction points preventing the user from taking this action.
        """
        plan_res = self.llm.generate(prompt=plan_prompt, system_prompt=system_prompt)
        plan_text = plan_res.text
        
        on_progress("Generating CTA variations...")
        draft_prompt = f"""
        Using the friction analysis:
        {plan_text}
        
        Generate exactly 5 categories of CTA variations (2-3 options each):
        1. Benefit-Led
        2. Action/Direct
        3. Urgency/Scarcity
        4. Low-Friction
        5. Conversational/Playful
        """
        draft_res = self.llm.generate(prompt=draft_prompt, system_prompt=system_prompt)
        final_copy = draft_res.text

        return {
            "analysis": plan_text,
            "final": final_copy,
            "model": draft_res.model,
            "provider": draft_res.provider
        }

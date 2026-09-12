import os
from pathlib import Path
from typing import Callable, Any

from services import LLMService, ImageGenerator


class FacebookAdsWorkflow:
    def __init__(self, llm_service: LLMService, image_generator: ImageGenerator):
        self.llm = llm_service
        self.image_gen = image_generator
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "facebook_ads_prompt.md"
        
    def _load_system_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, params: dict, on_progress: Callable[[str], Any]) -> dict:
        system_prompt = self._load_system_prompt()

        # Step 1: Analyze and Plan
        on_progress("Analyzing objective and audience...")
        plan_prompt = f"""
        Analyze the following brief for a Facebook Ad:
        Product/Service: {params.get('product_or_service', 'N/A')}
        Target Audience: {params.get('target_audience', 'N/A')}
        Campaign Objective: {params.get('campaign_objective', 'N/A')}
        Key Benefit: {params.get('key_benefit', 'N/A')}
        Pain Point: {params.get('pain_point', 'N/A')}
        Offer: {params.get('offer', 'N/A')}
        Brand Tone: {params.get('brand_tone', 'N/A')}
        
        Provide a short strategic analysis of how to hook this specific audience and what psychological triggers to use.
        """
        analysis_res = self.llm.generate(prompt=plan_prompt, system_prompt=system_prompt)
        analysis_text = analysis_res.text
        
        # Step 2: Generate Copy
        on_progress("Generating ad copy variations...")
        draft_prompt = f"""
        Based on the brief and this strategic analysis:
        {analysis_text}
        
        Generate exactly 2 completely distinct variations of the Facebook Ad.
        For each variation, include:
        - Primary Text
        - Headline
        - Description
        - CTA Button
        - Image/Visual Recommendation
        
        Ensure you follow the system instructions regarding scroll-stopping hooks and compliance.
        """
        draft_res = self.llm.generate(prompt=draft_prompt, system_prompt=system_prompt)
        final_copy = draft_res.text

        # Step 3: Optional Image Generation
        image_result = None
        if params.get("generate_image", False):
            on_progress("Generating advertising creative...")
            # We ask the LLM to extract a pure image prompt from the visual recommendation
            extract_prompt = f"""
            Extract a highly descriptive image generation prompt from the following ad copy's visual recommendations.
            Make it suitable for an AI image generator (detailed, specific style, high quality).
            Do not include text in the image prompt as AI struggles with text.
            Ad Copy:\n{final_copy}
            
            Return ONLY the raw image generation prompt string.
            """
            prompt_res = self.llm.generate(prompt=extract_prompt, system_prompt=system_prompt, max_tokens=100)
            img_prompt = prompt_res.text.strip()
            image_result = self.image_gen.generate_image(img_prompt)

        return {
            "analysis": analysis_text,
            "final": final_copy,
            "image": image_result,
            "model": draft_res.model,
            "provider": draft_res.provider
        }

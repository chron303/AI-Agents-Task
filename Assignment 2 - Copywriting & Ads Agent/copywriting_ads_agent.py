"""
Copywriting & Ads Agent (Agent 2) — Orchestrator and CLI
========================================================
Acts as the central router for all 6 marketing workflows.
Can be imported by app.py or run directly as a CLI tool.
"""

import sys
from typing import Callable, Any

from services import GeminiProvider, ImageGenerator, LLMService
from workflows import (
    FacebookAdsWorkflow,
    GoogleAdsWorkflow,
    LinkedInAdsWorkflow,
    ProductDescriptionWorkflow,
    EmailCopyWorkflow,
    CTAWorkflow
)

class CopywritingAdsAgent:
    def __init__(self, provider: LLMService = None):
        """Initialize the agent with an LLM provider and Image Generator."""
        self._llm = provider or GeminiProvider()
        self._image_gen = ImageGenerator()
        
        self.workflows = {
            "facebook": FacebookAdsWorkflow(self._llm, self._image_gen),
            "google": GoogleAdsWorkflow(self._llm),
            "linkedin": LinkedInAdsWorkflow(self._llm),
            "product": ProductDescriptionWorkflow(self._llm),
            "email": EmailCopyWorkflow(self._llm),
            "cta": CTAWorkflow(self._llm)
        }

    def get_provider_info(self) -> dict:
        return {
            "model": self._llm.get_model_name(),
            "provider": self._llm.get_provider_name()
        }

    def generate(self, content_type: str, params: dict, on_progress: Callable[[str], Any]) -> dict:
        """Route the request to the correct workflow."""
        if content_type not in self.workflows:
            raise ValueError(f"Unknown content type: {content_type}")
            
        workflow = self.workflows[content_type]
        return workflow.run(params, on_progress)

# ==========================================
# CLI IMPLEMENTATION
# ==========================================

def run_cli():
    print("\n=============================================")
    print("  AGENT 2 — COPYWRITING & ADS AGENT (CLI)  ")
    print("=============================================\n")

    try:
        agent = CopywritingAdsAgent()
        info = agent.get_provider_info()
        print(f"✓ Connected to {info['provider']} ({info['model']})\n")
    except EnvironmentError as e:
        print(f"✗ Configuration Error: {e}")
        sys.exit(1)

    print("Select a workflow:")
    print("  1. Facebook Ads")
    print("  2. Google Ads")
    print("  3. LinkedIn Ads")
    print("  4. Product Description")
    print("  5. Email Copy")
    print("  6. CTA Variations")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    mapping = {
        "1": "facebook",
        "2": "google",
        "3": "linkedin",
        "4": "product",
        "5": "email",
        "6": "cta"
    }
    
    content_type = mapping.get(choice)
    if not content_type:
        print("✗ Invalid choice.")
        sys.exit(1)

    params = {}
    print("\n--- Enter Brief Details ---")
    
    if content_type == "facebook":
        params['product_or_service'] = input("Product/Service: ")
        params['target_audience'] = input("Target Audience: ")
        params['campaign_objective'] = input("Campaign Objective: ")
        params['key_benefit'] = input("Key Benefit: ")
        params['pain_point'] = input("Pain Point: ")
        params['offer'] = input("Offer (optional): ")
        params['brand_tone'] = input("Brand Tone: ")
        img_prompt = input("Generate Image Creative? (y/n): ")
        params['generate_image'] = img_prompt.lower() == 'y'
        
    elif content_type == "google":
        params['product_or_service'] = input("Product/Service: ")
        params['target_keywords'] = input("Target Keywords (comma separated): ")
        params['search_intent'] = input("Search Intent: ")
        params['target_audience'] = input("Target Audience: ")
        params['key_benefits'] = input("Key Benefits: ")
        params['offer'] = input("Offer/CTA: ")
        
    elif content_type == "linkedin":
        params['product_or_service'] = input("Product/Service: ")
        params['target_audience'] = input("Target Professional Audience: ")
        params['pain_point'] = input("Business Pain Point: ")
        params['key_benefit'] = input("Business Value/ROI: ")
        params['offer'] = input("Offer/CTA: ")
        
    elif content_type == "product":
        params['product_name'] = input("Product Name: ")
        params['product_category'] = input("Category: ")
        params['features'] = input("Features (comma separated): ")
        params['target_customer'] = input("Target Customer: ")
        params['brand_tone'] = input("Brand Tone: ")
        
    elif content_type == "email":
        params['objective'] = input("Email Objective (e.g. Product Launch): ")
        params['product_or_service'] = input("Product/Service: ")
        params['target_audience'] = input("Target Audience: ")
        params['offer'] = input("Offer: ")
        params['brand_tone'] = input("Brand Tone: ")
        
    elif content_type == "cta":
        params['product_or_service'] = input("Product/Service: ")
        params['desired_action'] = input("Desired Action: ")
        params['target_audience'] = input("Target Audience: ")
        params['context'] = input("Context/Placement: ")
        params['brand_tone'] = input("Brand Tone: ")

    def progress_callback(msg: str):
        print(f"  [Wait] {msg}")

    print("\n--- Generating ---")
    try:
        result = agent.generate(content_type, params, on_progress=progress_callback)
    except RuntimeError as e:
        print(f"\n✗ Error during generation: {e}")
        sys.exit(1)

    print("\n=============================================")
    print("                FINAL OUTPUT                 ")
    print("=============================================\n")
    print(result['final'])
    
    if result.get("image") and result["image"].get("success"):
        print("\n[✓ Image Creative Generated Successfully (Bytes available in memory)]")
    elif result.get("image") and not result["image"].get("success"):
        print(f"\n[!] Image Info: {result['image']['fallback']}")

if __name__ == "__main__":
    run_cli()

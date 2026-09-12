# Copywriting & Ads Agent (Agent 2)

> **Technians AI Engineer Assignment — Agent 2**

A specialized AI agent that generates highly persuasive, platform-optimized marketing copy for Facebook, Google, LinkedIn, Email, Product Descriptions, and CTAs.

---

## 1. Overview
Unlike Agent 1 (Content Writing), Agent 2 is optimized for **conversion and persuasion**. It focuses on interrupting scrolls, matching search intent, highlighting benefits over features, and driving action. It includes an optional Image Generation pipeline for ad creatives.

## 2. Purpose
To automate the creation of effective advertising and marketing copy while strictly adhering to platform constraints (like Google Ads character limits) and marketing best practices.

## 3. Supported Capabilities
1. **Facebook Ads:** Scroll-stopping hooks, emotional pain points, and accompanying image generation.
2. **Google Ads:** Exact search intent matching with strict character limits (30 char headlines, 90 char descriptions).
3. **LinkedIn Ads:** B2B focused, ROI-driven professional copy.
4. **Product Descriptions:** Translates technical features into compelling benefits.
5. **Email Copy:** Subject lines, preview text, and conversion-focused bodies.
6. **CTA Variations:** Action-oriented, friction-reducing microcopy variations.

## 4. Architecture
```
User
  │
  ├── Streamlit UI (app.py)
  └── CLI (copywriting_ads_agent.py)
            │
            ▼
  CopywritingAdsAgent (Orchestrator)
            │
            ▼
  Workflow (selected by content type)
  ├── FacebookAdsWorkflow
  ├── GoogleAdsWorkflow
  ├── LinkedInAdsWorkflow
  ├── ProductDescriptionWorkflow
  ├── EmailCopyWorkflow
  └── CTAWorkflow
            │
            ▼
  LLMService & ImageGenerator (Abstract interfaces)
            │
            ▼
  GeminiProvider
            │
            ▼
  Gemini 3.5 Flash-Lite & Imagen API
```

## 5. Workflows
Each capability uses a specialized multi-step workflow. For example:
- **Facebook Ads:** Analyze Audience → Generate Variations → Extract Image Prompt → Generate Image.
- **Google Ads:** Analyze Intent → Draft Constrained Copy → Validate Limits.

## 6. Prompt Design
Every workflow uses a dedicated prompt located in the `prompts/` directory. The instructions emphasize specific marketing frameworks (like PAS/AIDA), platform cultural differences (social vs. search), and compliance.

## 7. Gemini Integration
Powered by **Gemini 3.5 Flash-Lite** via the new `google-genai` SDK. The architecture abstracts the LLM behind an `LLMService` interface, making it trivial to swap to Claude later.

## 8. Image-Generation Architecture
Image generation is entirely decoupled from copy generation. The `FacebookAdsWorkflow` generates the copy, then extracts a clean visual description, and passes it to the `ImageGenerator` service. If the Imagen API fails, the service fails gracefully, returning a text-based fallback visual recommendation without crashing the application.

## 9. Environment Setup
Create a `.env` file in this directory:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

## 10. Installation
```bash
pip install -r requirements.txt
```

## 11. Streamlit Usage
```bash
streamlit run app.py
```

## 12. CLI Usage
```bash
python copywriting_ads_agent.py
```

## 13. Sample Outputs
Sample outputs are stored in the shared workspace directory:
`../deliverables/samples/copywriting-ads/`

## 14. Demo
Demo documentation is available at:
`../deliverables/demo/copywriting-ads-agent-demo.md`

## 15. Error Handling
The application handles missing API keys, incorrect models, generation errors, and Imagen API failures gracefully. Invalid inputs are caught by the UI.

## 16. Future Claude Integration
Because Agent 2 uses the same `LLMService` abstraction pattern as Agent 1, migrating to Claude requires only creating a `ClaudeProvider` class and replacing `GeminiProvider` in the agent initialization. Workflows and UI require zero changes.

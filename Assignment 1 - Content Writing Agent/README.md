# Content Writing Agent

> **Technians AI Engineer Assignment — Agent 1**

A production-quality content generation agent that creates blog posts, website copy, e-books, and SEO articles using a multi-step intelligent workflow powered by **Gemini 3.5 Flash-Lite**.

---

## Overview

The Content Writing Agent is not a simple prompt-to-output tool. Each content type runs through a dedicated pipeline with multiple, purposeful LLM calls — planning, drafting, and reviewing — before returning the final result.

This architecture ensures that output quality is consistently higher than a single-prompt approach, and that each content type is handled according to its own standards and requirements.

---

## Assignment Context

This is **Agent 1** of a three-agent AI Engineer assignment for Technians. The full assignment will include:

- **Agent 1** — Content Writing Agent ← *this project*
- Agent 2 — Copywriting & Ads Agent *(future)*
- Agent 3 — Video Production Agent *(future)*

All agents share the same `deliverables/` folder structure.

---

## Content Writing Agent Capabilities

| Capability | Workflow Steps | Description |
|---|---|---|
| Blog Post | 3 steps | Outline → Draft → Review & Finalise |
| Website Content | 2 steps | Content Strategy → Page Copy |
| E-book | 3 steps | Chapter Plan → Write Chapters → Assemble |
| SEO Article | 3 steps | Keyword Strategy → Draft → Meta + FAQ |

---

## Architecture

```
User
  │
  ├── Streamlit UI (app.py)
  └── CLI (content_writing_agent.py)
            │
            ▼
  ContentWritingAgent  ← orchestrator
            │
            ▼
  Workflow (selected by content type)
  ├── BlogWorkflow
  ├── WebsiteWorkflow
  ├── EbookWorkflow
  └── SEOWorkflow
            │
            ▼
  LLMService  ← abstract interface
            │
            ▼
  GeminiProvider  ← current implementation
            │
            ▼
  Gemini 3.5 Flash-Lite API
```

The `LLMService` interface means that replacing Gemini with Claude requires only adding a `ClaudeProvider` class — no workflow or UI code changes. See [Switching to Claude](#switching-to-claude) below.

---

## Workflows

### Blog Post Workflow

```
Brief Analysis → Outline Planning → Full Draft → Review & Finalise
      (1 call)         (1 call)         (1 call)
```

The workflow first generates a structured outline, then writes the full draft following that outline, and finally reviews the draft for flow, readability, and tone alignment before producing the polished final post.

### Website Content Workflow

```
Brief Analysis → Content Strategy → Page Copy Generation
                    (1 call)              (1 call)
```

The agent first maps the page structure — understanding the page type (Homepage, Product, Service, About, or Landing), the conversion goal, and the value proposition. It then generates the complete page copy with appropriate CTAs for each section.

### E-book Workflow

```
Brief Analysis → Chapter Plan → Write All Chapters → Assemble Complete E-book
                  (1 call)          (1 call)               (1 call)
```

The agent treats an e-book as a structured learning resource, not a long blog post. Chapter planning establishes learning objectives and progression before any content is written.

### SEO Article Workflow

```
Brief Analysis → Keyword & Intent Strategy → Draft Article → Meta + FAQ + Optimise
                       (1 call)                (1 call)            (1 call)
```

Search intent analysis happens before writing begins. The final step adds meta title, meta description, and an FAQ section targeting long-tail queries.

---

## Prompt Design

Each content type has a dedicated system prompt in `prompts/`:

| File | Purpose |
|---|---|
| `blog_prompt.md` | Emphasises hooks, readability, structure, and engagement |
| `website_prompt.md` | Focuses on conversion hierarchy, CTAs, and benefit-led copy |
| `ebook_prompt.md` | Covers long-form coherence, chapter progression, and depth |
| `seo_prompt.md` | Handles search intent, keyword integration, and heading hierarchy |

Prompts are stored as markdown files outside the Python code, making them easy to review, refine, and swap without touching application logic.

The `instructions.md` file defines the agent's overall quality standards and behavioural constraints.

---

## Gemini 3.5 Flash-Lite Integration

- **Model identifier**: `gemini-3.5-flash-lite`
- **SDK**: `google-genai` (Google's unified SDK, recommended as of 2026)
- **API key**: Read from `GEMINI_API_KEY` environment variable — never hardcoded
- **Model name**: Read from `GEMINI_MODEL` environment variable

If the configured model is unavailable, the application raises a clear error rather than silently substituting another model.

---

## Environment Setup

**1. Clone or navigate to the project directory:**

```bash
cd "Assignment 1 - Content Writing Agent"
```

**2. Create your `.env` file:**

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Get a Gemini API key from: https://aistudio.google.com/app/apikey

---

## Installation

```bash
pip install -r requirements.txt
```

**Requirements:**
- `google-genai` — Gemini API SDK
- `streamlit` — Web UI
- `python-dotenv` — Environment variable loading

---

## Running the Application

### Streamlit UI

```bash
streamlit run app.py
```

Open the displayed URL (usually `http://localhost:8501`) in your browser.

### CLI

```bash
python content_writing_agent.py
```

The CLI prompts you to select a content type and enter parameters, then runs the same workflow as the Streamlit UI.

---

## Sample Outputs

Three sample outputs are included in `deliverables/samples/content-writing/`:

| File | Content Type | Topic |
|---|---|---|
| `sample-1-blog.md` | Blog Post | The hidden cost of poor sleep on work performance |
| `sample-2-website-content.md` | Website Content | SaaS project management tool homepage |
| `sample-3-seo-article.md` | SEO Article | How to build a morning routine for productivity |

---

## Demo

Demo documentation for the recording session is at:

`deliverables/demo/content-writing-agent-demo.md`

---

## Error Handling

| Error | Cause | Resolution |
|---|---|---|
| `GEMINI_API_KEY is not set` | Missing `.env` file or key | Create `.env` with your API key |
| `GEMINI_MODEL is not set` | Missing model env var | Add `GEMINI_MODEL=gemini-3.5-flash-lite` to `.env` |
| `Gemini API call failed` | Invalid key, quota exceeded, or model unavailable | Check API key validity and quota |
| `Unknown content type` | Invalid type passed programmatically | Use: blog, website, ebook, seo |

---

## Switching to Claude

To replace Gemini with Claude:

**1. Create `services/claude_provider.py`:**

```python
from anthropic import Anthropic
from .llm_service import LLMService, LLMResponse

class ClaudeProvider(LLMService):
    def __init__(self):
        self._client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self._model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=None):
        # ... implementation
        pass

    def get_model_name(self): return self._model
    def get_provider_name(self): return "Claude"
```

**2. Update `content_writing_agent.py`:**

```python
# Change:
from services import GeminiProvider
# To:
from services.claude_provider import ClaudeProvider

# Change:
self._llm = provider or GeminiProvider()
# To:
self._llm = provider or ClaudeProvider()
```

No workflow, prompt, or UI code needs to change.

---

## Project Structure

```
Assignment 1 - Content Writing Agent/
│
├── app.py                        # Streamlit UI
├── content_writing_agent.py      # CLI + agent orchestrator
│
├── workflows/
│   ├── blog_workflow.py          # 3-step blog pipeline
│   ├── website_workflow.py       # 2-step website pipeline
│   ├── ebook_workflow.py         # 3-step e-book pipeline
│   └── seo_workflow.py           # 3-step SEO pipeline
│
├── prompts/
│   ├── blog_prompt.md            # Blog system instructions
│   ├── website_prompt.md         # Website system instructions
│   ├── ebook_prompt.md           # E-book system instructions
│   └── seo_prompt.md             # SEO system instructions
│
├── services/
│   ├── llm_service.py            # Abstract interface
│   └── gemini_provider.py        # Gemini implementation
│
├── instructions.md               # Agent behaviour standards
├── requirements.txt
├── .env.example
└── README.md
```

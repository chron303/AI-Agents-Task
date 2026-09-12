# Demo Documentation — Content Writing Agent

## Demo Objective

Demonstrate that Agent 1 (the Content Writing Agent) is a genuine multi-step AI agent, not simply a wrapper around a single LLM prompt. Show how the agent plans, writes, and reviews content through separate, purposeful workflow stages.

---

## What to Demonstrate

### Core Capability
- The agent supports four distinct content types with different workflows
- Each workflow makes multiple real LLM calls — not a single prompt
- Progress is displayed in real time as each step executes
- Output quality is consistently professional

### Differentiator from a Basic Chatbot
A basic chatbot would take your input and produce output in one step. This agent:
1. Analyses the brief and plans structure
2. Writes the content following that plan
3. Reviews and refines the output

Each stage improves on the previous. The user sees this happening in real time.

---

## Recommended Demo Scenario

### Scenario: SEO Article (Best for demonstrating all 3 workflow steps clearly)

**Why this scenario:**
- 3 distinct, visible steps (keyword strategy → draft → meta + FAQ)
- Each step's output is visually distinct and easy to explain
- Shows both the strategic thinking and the writing capability

**Inputs to use:**

| Field | Value |
|---|---|
| Topic | How to build a morning routine for productivity |
| Primary keyword | morning routine for productivity |
| Secondary keywords | morning habits, daily routine tips, productivity hacks, wake up early |
| Target audience | Working professionals aged 25–40 |
| Search intent | Informational |
| Desired length | 1200–1800 words |
| Additional instructions | *(leave blank)* |

---       

## Recommended Demo Flow

### 1. Open the application (30 seconds)
- Show the browser running at `localhost:8501`
- Point out the sidebar navigation
- Explain: "This is the Streamlit UI. The same agent logic also runs in the terminal via the CLI."

### 2. Select SEO Article (15 seconds)
- Click "SEO Article" in the sidebar
- Briefly explain the four content types available

### 3. Fill in the brief (45 seconds)
- Enter the inputs from the table above
- Explain while typing: "The agent takes a structured brief — topic, keywords, audience, search intent"

### 4. Click Generate and watch the progress (60–90 seconds)
- Point to each progress message as it appears:
  - "Step 1: Analysing search intent and building keyword strategy"
  - "Step 2: Drafting the SEO article with H1/H2/H3 structure"
  - "Step 3: Adding meta elements, FAQs, and final optimisation"
- Explain: "Each of these is a real LLM call. The keyword strategy from Step 1 is passed into Step 2. The draft from Step 2 is passed into Step 3. This is what makes it a pipeline, not a single prompt."

### 5. Show the results tabs (60 seconds)
- Final Article tab: Show the full article with meta title, meta description, FAQ section
- Keyword Strategy tab: Show the planning document from Step 1
- Draft tab: Show the raw draft from Step 2, noting what was improved in the final version

### 6. Briefly show the architecture (30 seconds, optional)
- Show `content_writing_agent.py` — the orchestrator
- Show `services/llm_service.py` — "This is the abstraction. If we wanted to use Claude, we'd create a Claude provider and nothing else changes."

---

## What to Explain During the Demo

### On the multi-step workflow:
> "A single prompt approach gives you whatever the model thinks is a good blog post. A workflow approach means the model plans first, then writes according to that plan, then reviews its own work. The output is consistently better because each step has a focused job."

### On the LLM abstraction:
> "The application never calls Gemini directly. It calls `LLMService.generate()`. Gemini happens to be what's behind that right now. To switch to Claude, I'd write a Claude provider class — two dozen lines — and change one import. Every workflow, every prompt, every UI element stays exactly the same."

### On prompt engineering:
> "Each content type has its own dedicated system prompt. The blog prompt focuses on hooks and readability. The SEO prompt focuses on keyword integration and heading hierarchy. These live in markdown files, not in the Python code — so you can refine the prompts without touching the application logic."

### On the CLI:
> "The CLI and the web interface share the same agent code. There's no duplicated logic. If you test it in the terminal, you're testing exactly what runs in the browser."

---

## How Gemini Is Involved

- Model: `gemini-3.5-flash-lite` (fast, cost-efficient, Google's recommended 2026 model)
- SDK: `google-genai` (Google's unified, current SDK)
- API key: Read from environment variable — never exposed in the UI or committed to code
- Each workflow step = one `client.models.generate_content()` call
- The model receives a system prompt (the content-type-specific instructions) plus the user prompt (the brief + any previous step output)

---

## Speaking Script (1–2 minutes)

> "This is the Content Writing Agent — Agent 1 of my Technians AI Engineer assignment.
>
> The agent supports four types of content: blog posts, website copy, e-books, and SEO articles. What makes it an *agent* rather than a simple chatbot is the multi-step workflow. For every content type, the agent plans first, then writes, then reviews — three separate AI calls that each build on the previous.
>
> I'm going to demonstrate the SEO article workflow, because it clearly shows all three stages. [Fill in the form.] The agent takes a structured brief — the topic, keywords, audience, and search intent.
>
> When I click Generate, watch the progress bar. [Click Generate.] Step 1 is analysing the search intent and building a keyword strategy — the AI figures out *why* someone is searching for this and maps where each keyword should appear. Step 2 takes that strategy and writes the full article. Step 3 adds the meta title, meta description, and FAQ section, and does a final optimisation pass.
>
> [Show the results.] You can see the final SEO-ready article here, with proper heading hierarchy. In the other tabs you can see the keyword strategy and the draft — which shows exactly what the agent improved in the final pass.
>
> The code is built so that Gemini — which is what's running today — can be swapped for Claude by creating one new provider class. The workflows, the prompts, and the UI don't need to change. That's the value of the LLM abstraction layer."

---

## Notes for the Recording

- Record at 1080p minimum
- Keep the browser font size large enough to read on screen
- Pause briefly on each progress step so viewers can read it
- When showing code, zoom in on the key parts: `LLMService`, `GeminiProvider`, the workflow run method
- Total demo length target: 3–5 minutes

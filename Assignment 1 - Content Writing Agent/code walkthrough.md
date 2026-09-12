# Code Walkthrough — Content Writing Agent

> A beginner-friendly explanation of how the project works, written so you can confidently explain it in an interview.

---

## The Big Picture

This project is a **Content Writing Agent** — an AI assistant that generates professional content by thinking through the task in multiple steps, just like a real writer would.

When you give it a topic, it doesn't just fire a single question at an AI and paste the answer. Instead, it follows a *structured workflow*:

1. **Plan** — What structure should this content have?
2. **Write** — Produce the actual content following that plan
3. **Review** — Read it back, fix problems, polish it

This is what makes it an *agent* rather than just a chatbot wrapper.

---

## File by File Explanation

### `content_writing_agent.py` — The Brain

This is the central coordinator. Think of it as a manager who receives a request and decides which team (workflow) handles it.

```python
class ContentWritingAgent:
    def generate(self, content_type, params, on_progress):
        # Looks at content_type, picks the right workflow, runs it
```

It also contains the **CLI** — the command-line version where you can type your request into the terminal. Both the CLI and the Streamlit web app call the same `generate()` method, so there's no duplicated code.

### `app.py` — The Web Interface

This is the Streamlit application — the browser-based UI. It:
- Shows a form where you fill in your content brief
- Calls the same `ContentWritingAgent.generate()` method
- Displays real-time progress as each step runs
- Shows the final result in tabs (Final Output, Intermediate Steps)
- Offers a download button

Streamlit makes building this interface simple — it's pure Python, no HTML/CSS framework required (though we add some custom CSS for polish).

### `services/llm_service.py` — The Contract

This file defines what *any* AI provider must be able to do:

```python
class LLMService(ABC):
    def generate(self, prompt, system_prompt, temperature, max_tokens) -> LLMResponse:
        ...
```

It's an **abstract class** — a template that says "any AI service must have a `generate` method". The application talks to this interface, never directly to Gemini.

**Why this matters**: If you later want to use Claude instead of Gemini, you just create a new class that follows this contract. The rest of the application doesn't need to change at all.

### `services/gemini_provider.py` — The Gemini Implementation

This is where actual Gemini API calls happen. It reads your API key and model name from environment variables (not hardcoded), calls the API, and returns the text response.

```python
class GeminiProvider(LLMService):
    def generate(self, prompt, ...):
        response = self._client.models.generate_content(model=..., contents=prompt)
        return LLMResponse(text=response.text, ...)
```

We use Google's newest `google-genai` SDK (the old `google-generativeai` is being phased out).

### `workflows/` — The Four Workflows

Each workflow is a separate class that knows how to produce one type of content. They all share the same pattern:

```
Step 1: LLM call to plan/analyse
Step 2: LLM call to write/generate
Step 3: LLM call to review/finalise/assemble
```

Let's walk through the blog workflow as an example:

#### `workflows/blog_workflow.py`

```
Step 1 — _plan_outline()
  Sends: "Here's the brief. Create a blog outline."
  Returns: A structured outline with H2s, H3s, hook strategy

Step 2 — _draft_content()
  Sends: "Here's the brief AND the outline. Write the full blog post."
  Returns: The complete draft

Step 3 — _review_and_finalize()
  Sends: "Here's the brief, the outline, and the draft. Polish it."
  Returns: The publication-ready final post
```

Each step uses the draft from the previous step. This is *iterative refinement* — each step improves on what the previous step produced.

#### Why Not Just One LLM Call?

Good question! A single prompt like "Write a 1200-word blog post about X" often produces:
- Generic, predictable structure
- Weak openings
- Rambling sections
- Abrupt endings

By separating planning from writing, the model can focus fully on structure first, then content — much like a real writer who outlines before drafting.

### `prompts/` — The System Instructions

Each content type has a dedicated system prompt file. These are the "rules" the AI must follow.

- `blog_prompt.md` — Rules for blog writing: hooks, readability, flow
- `website_prompt.md` — Rules for website copy: conversion, CTAs, benefits vs features
- `ebook_prompt.md` — Rules for e-books: chapter progression, sustained depth
- `seo_prompt.md` — Rules for SEO: keyword integration, heading hierarchy, meta elements

These are stored as markdown files rather than hardcoded strings in Python. This means:
- They're easy to read and edit
- Non-technical team members can review them
- You can change the AI's behaviour without touching Python code

### `instructions.md` — The Agent's Core Principles

This defines the agent's overall identity and quality standards. It's loaded into the system prompt for all content types. Think of it as the agent's "values" — it tells the AI what kind of content writer it should be.

---

## How the Pieces Connect (Data Flow)

```
User fills in form or CLI inputs
         ↓
app.py / CLI collects params into a dict
         ↓
ContentWritingAgent.generate(content_type, params) is called
         ↓
The correct workflow is selected (e.g. BlogWorkflow)
         ↓
BlogWorkflow.run(topic, audience, tone, ...) runs
         ↓
  Step 1: blog_workflow._plan_outline()
    → Calls GeminiProvider.generate(prompt, system_prompt)
    → Google Gemini 3.5 Flash-Lite processes the request
    → Returns the outline text
         ↓
  Step 2: blog_workflow._draft_content()
    → Calls GeminiProvider.generate() with outline included
    → Returns the draft
         ↓
  Step 3: blog_workflow._review_and_finalize()
    → Calls GeminiProvider.generate() with draft included
    → Returns the polished final post
         ↓
BlogWorkflow returns dict: {outline, draft, final, model, provider}
         ↓
app.py displays results in tabs, offers download
```

---

## Environment Variables — Why They Matter

We never put the API key directly in the code. Reasons:
1. If you commit the code to GitHub, your key is exposed to the world
2. Different environments (dev, staging, prod) need different keys
3. You might switch from Gemini to Claude later — environment variables make this easy

The `.env` file stores your secrets locally. `python-dotenv` reads them automatically.

`.env.example` is a template without real values — safe to commit.

---

## The Progress Callback Pattern

You might notice `on_progress` appears in many function signatures. This is a **callback** — a function you pass in that gets called when something happens.

```python
def on_progress(message):
    print(message)  # or update a UI element

workflow.run(..., on_progress=on_progress)
```

Inside the workflow:
```python
def run(self, ..., on_progress):
    on_progress("Step 1/3 — Planning...")
    outline = self._plan_outline(...)
    on_progress("Step 2/3 — Writing...")
    ...
```

This pattern lets the CLI and the Streamlit app both receive progress updates through the same workflow code, displaying them in their own way (CLI: `print()`, Streamlit: updating a text element).

---

## Common Interview Questions

**Q: What makes this an agent rather than a chatbot?**  
A: An agent has goals, makes decisions, and executes multi-step plans. This agent selects a workflow, plans the content structure, generates it, then reviews the output — three separate decisions and actions to produce one result.

**Q: How would you add a new content type?**  
A: Create a new workflow class in `workflows/`, a new prompt file in `prompts/`, add a routing branch in `ContentWritingAgent.generate()`, and add the UI form in `app.py`. The LLM layer doesn't change.

**Q: How would you switch to Claude?**  
A: Create `services/claude_provider.py` implementing `LLMService`. Change one line in `ContentWritingAgent.__init__()`. Done.

**Q: Why are the prompts in separate files?**  
A: Separation of concerns. Prompts are content, not code. Storing them as markdown files makes them readable, editable, and version-controllable independently of the Python logic.

**Q: What's the Gemini model used and why?**  
A: `gemini-3.5-flash-lite` — Google's cost-efficient, low-latency model released in July 2026. It's well-suited for content generation tasks that don't require the heaviest models. The identifier is read from an environment variable, not hardcoded.

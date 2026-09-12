# Code Walkthrough — Agent 2: Copywriting & Ads

> A beginner-friendly explanation of Agent 2's implementation.

## How is Agent 2 Different from Agent 1?

Agent 1 is about **Content Creation** (blogs, e-books). It focuses on narrative, flow, and information.
Agent 2 is about **Persuasion and Conversion** (ads, CTAs). It focuses on psychology, platform constraints, and driving action. 

To keep them perfectly independent, Agent 2 has its own directory. The `services/` layer (which handles talking to Gemini) was duplicated into Agent 2. This means you can delete Agent 1 and Agent 2 will still run perfectly, or vice versa. 

## The Central Router: `copywriting_ads_agent.py`

This file is the brain. When a user requests an ad, this class looks at the `content_type` and routes it to one of six specific workflows.

It also contains the **CLI** logic. If you run this file directly in the terminal, it asks you a series of questions to build the brief, passes it to the agent, and prints the result.

## The Workflows

Unlike Agent 1 which was mostly Draft -> Review, Agent 2 workflows are highly specialized for marketing:

### 1. Facebook Ads
- **Step 1:** Analyze the audience and objective to find a psychological angle.
- **Step 2:** Generate the copy (hook, primary text, headline).
- **Step 3 (Optional):** Extract a visual prompt and call the Image Generation API to create an ad creative.

### 2. Google Ads
- **Step 1:** Analyze the search intent.
- **Step 2:** Draft the copy, counting characters.
- **Step 3:** A strict validation step where the LLM is told: "Check your work. Ensure no headline is over 30 characters."

### 3. Product Descriptions
- **Step 1:** The LLM takes the raw *features* and maps them to *benefits*.
- **Step 2:** It writes the description using those benefits. 

## Image Generation (`image_generator.py`)

Agent 2 introduces a new capability: generating images for ads. 

**How it works:**
1. The copy is generated first.
2. The LLM is asked to extract a pure visual prompt from the copy (e.g., "A modern ergonomic chair in a bright home office").
3. We pass this to `genai.Client.models.generate_images()` using Google's `imagen-3.0-generate-001` model.

**Graceful Fallback:** 
Image generation APIs often fail (rate limits, missing permissions). The code uses a `try/except` block. If it fails, it doesn't crash the app. Instead, it returns `success: False` and provides the text prompt as a "fallback visual recommendation."

## The User Interface (`app.py`)

The Streamlit app uses `st.sidebar.radio` to select the workflow. 
Based on the selection, the form dynamically changes. For example, Google Ads asks for "Target Keywords", while Email Copy asks for "Email Objective".

When generated, the results appear in Tabs:
- **Final Output:** The generated copy.
- **Strategic Analysis:** The "thinking" the agent did before writing.
- **Ad Creative (Image):** Only shows if image generation was requested.

## Prompts

Just like Agent 1, all system prompts live in the `prompts/` folder as Markdown files. 
- `facebook_ads_prompt.md` tells the LLM to stop the scroll.
- `google_ads_prompt.md` enforces strict character limits.
- `cta_prompt.md` focuses on reducing friction.

This separation means a marketing expert can tweak the prompts without needing to understand the Python code.

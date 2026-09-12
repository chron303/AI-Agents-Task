# Code Walkthrough — Agent 3: Video Production

> A beginner-friendly explanation of Agent 3's implementation, written so you can confidently explain it in an interview.

## How Is Agent 3 Different From Agent 1 and Agent 2?

Agent 1 writes **long-form content** (blogs, e-books) — it's about narrative and information depth.
Agent 2 writes **persuasive marketing copy** (ads, CTAs) — it's about psychology and conversion.
Agent 3 plans **video production** — it's about **time, visuals, and craft-specific formats**. A video script, a storyboard, and a shot list all describe the *same* video, but each is a genuinely different document with different rules. That's why Agent 3 isn't "Agent 1 with a video prompt swapped in" — it has five distinct workflows, five distinct prompts, and a timing-validation layer none of the other agents need.

Like Agent 1 and Agent 2, Agent 3 lives in its own self-contained folder with its own `services/` layer. This means you could delete Agent 1 and Agent 2 entirely and Agent 3 would still run.

## The Central Router: `video_production_agent.py`

This is the brain of Agent 3. `VideoProductionAgent.__init__` creates one `GeminiProvider`, one `StoryboardImageGenerator`, and one instance of each of the five workflow classes, storing them in a `self.workflows` dict keyed by capability name (`"video_script"`, `"storyboard"`, etc.).

`generate(content_type, params, on_progress)` just looks up the right workflow and calls `.run(...)` on it with the params unpacked into named arguments. This file also contains the **CLI** — running `python video_production_agent.py` directly asks you which of the five capabilities you want, collects the relevant brief fields with `input()`, and prints the same `result` dict the Streamlit UI would receive.

## The Five Workflows

Every workflow lives in its own file under `workflows/` and follows the same shape: an `__init__` that loads its own system prompt from `prompts/`, and a `run(...)` method that executes a multi-step pipeline of real LLM calls.

### 1. Video Script (`video_script_workflow.py`)
1. **Plan structure** — the LLM is asked to allocate the requested runtime across a sequence of scenes *before* writing any dialogue. This is the step that keeps a 30-second script from accidentally becoming a 3-minute one.
2. **Draft script** — writes the full scene-by-scene script following that approved plan.
3. **Validate & finalize** — `assess_timing()` estimates how long the narration would actually take to speak (at 145 words/minute) and compares it to the requested duration. If it's more than 20% off, one corrective revision call is made with explicit instructions ("cut spoken lines" or "add more detail"). If it's already on target, a lighter polish pass runs instead.

### 2. Storyboard (`storyboard_workflow.py`)
1. **Plan visual language** — decides the color palette, framing style, and cut pacing *before* any individual scene is storyboarded, so the whole thing feels visually consistent.
2. **Generate storyboard** — produces a markdown table with one row per scene: camera angle, movement, composition, lighting, transitions, etc. Note this step deliberately asks for a *different* kind of content than the script — camera language, not dialogue.
3. **Check scene consistency** — `assess_scene_consistency()` extracts per-scene durations from the generated table (e.g. "0:00-0:05") and sums them against the requested runtime, flagging any mismatch.
4. **(Optional) Reference image** — if requested, a small extra LLM call pulls a clean, dialogue-free visual description out of the storyboard's hero scene, which is then passed to `StoryboardImageGenerator`.

### 3. Shot List (`shot_list_workflow.py`)
1. **Analyze production needs** — figures out distinct locations, cast, and equipment implied by the brief, and a sensible shooting order (often grouped by location, not script order — that's how real productions actually schedule shoots).
2. **Generate shot list** — a markdown table with real cinematography terms (shot type, angle, movement) per shot.
3. **Review for practicality** — a dedicated pass that checks for vague terminology, missing production notes, and inefficient shot ordering, and fixes them.

### 4. Voice-over (`voiceover_workflow.py`)
1. **Plan delivery** — decides the emotional throughline and pacing before writing lines, and computes a target word count from the requested duration (`duration_seconds / 60 * 145`).
2. **Draft voice-over** — writes short delivery beats with direction (pacing, emphasis, pauses like `[pause 1s]`), not one long paragraph.
3. **Validate & finalize** — same timing check as the video script; revises once if the spoken word count doesn't fit the runtime.

### 5. Social Media Video (`social_video_workflow.py`)
1. **Plan hook & retention** — writes the exact opening hook and a scene-change/retention strategy tuned to the platform (TikTok/Reels need the fastest cuts; LinkedIn short-form is fast but more professional).
2. **Draft social video** — the full plan: hook, numbered scene sequence, spoken content (or explicitly "(silent — visual + caption only)"), captions, audio, and one CTA.
3. **Validate & finalize** — checks pacing/timing fits the (usually very short) runtime and tightens once if it doesn't.

## Timing Validation (`services/timing.py`)

This is the piece unique to Agent 3. Two functions do the work:
- `assess_timing(text, requested_seconds)` — used for Video Script, Voice-over, and Social Video. It scans generated text for spoken/narration lines, counts words, and estimates duration at a documented **145 words/minute**. A ±20% tolerance band decides "within target" vs. "over"/"under" target.
- `assess_scene_consistency(text, requested_seconds)` — used for Storyboard and Shot List. It regex-extracts per-scene duration ranges (like `0:00-0:05`) from the generated table and sums them.

Both return a small dataclass with a `.as_markdown()` method so the Streamlit UI and CLI can display the same report without reformatting it.

`parse_duration()` turns flexible user input ("30 seconds", "2 minutes", "45s") into a plain integer number of seconds used throughout the pipeline.

## Image Generation (`services/image_generator.py`)

Agent 3 introduces a storyboard-specific twist on Agent 2's image generation pattern: instead of always generating an image, it's opt-in (checkbox in the UI), and it targets one 16:9 reference image for the *hero* scene rather than a square ad creative. The contract is identical to Agent 2's `ImageGenerator`: never raises, always returns a dict with `success` plus either image bytes or a fallback text description.

**Graceful fallback:** if `GEMINI_API_KEY` is missing, if the Imagen model is unavailable, or if the API call fails for any reason, the function returns `{"success": False, "error": ..., "fallback": ...}`. The workflow — and the UI — always check this flag and never claim an image exists when it doesn't.

## The User Interface (`app.py`)

`st.sidebar.radio` selects one of the five capabilities. The form section below is built with `if/elif` blocks so only the fields relevant to that capability are shown — Storyboard shows a "Generate reference image" checkbox that Video Script doesn't, Shot List asks about locations and cast that Voice-over doesn't, and so on.

After generation, results are shown in tabs: the final output first, then the intermediate planning stage (scene plan, visual plan, production plan, delivery plan, or hook plan depending on capability), then a "⏱️ Timing" tab showing the `TimingReport`/`SceneTimingReport` markdown. Storyboard gets an extra "🖼️ Reference Image" tab only when an image was actually requested.

## Prompts

Just like Agent 1 and Agent 2, every system prompt lives in `prompts/` as a standalone markdown file, loaded once per workflow instance and passed as `system_prompt` on every LLM call for that capability. Keeping prompts out of the Python code means you can tune the agent's "voice" for a capability without touching any logic.

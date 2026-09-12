# Video Production Agent (Agent 3)

> **Technians AI Engineer Assignment — Agent 3**

A specialized AI agent that transforms a video idea, topic, product, or campaign brief into structured, production-ready video content: scripts, storyboards, shot lists, voice-over scripts, and short-form social video plans.

---

## 1. Overview
Unlike Agent 1 (long-form written content) and Agent 2 (persuasive marketing copy), Agent 3 is optimized for **video pre-production**. Its output is judged by whether a real production crew — director, cinematographer, voice-over artist, editor — could act on it directly. It treats duration as a hard constraint, separates visual direction from spoken/audio content, and validates its own timing before returning a final result.

## 2. Purpose
To automate the early, structure-heavy stages of video production (script, storyboard, shot list, voice-over, short-form social cut) while respecting runtime constraints, platform behavior, and real cinematography/production terminology.

## 3. Supported Capabilities
1. **Video Script** — scene-by-scene script with timing, visual/action, dialogue/narration, on-screen text, and audio.
2. **Storyboard** — visually-oriented scene plan (camera angle, movement, composition, lighting, transitions) with an optional AI-generated reference image for the hero scene.
3. **Shot List** — technical, shootable production document using real cinematography terminology (shot type, angle, movement, props, production notes).
4. **Voice-over Script** — performance-ready narration with delivery direction, pauses/emphasis, pronunciation notes, and timing.
5. **Social Media Video** — short-form plan (Reels/TikTok/Shorts/LinkedIn) built around hooks, retention, fast pacing, and sound-off-safe captions.

## 4. Architecture
```
User
  │
  ├── Streamlit UI (app.py)
  └── CLI (video_production_agent.py)
            │
            ▼
  VideoProductionAgent (Orchestrator)
            │
            ▼
  Workflow (selected by capability)
  ├── VideoScriptWorkflow
  ├── StoryboardWorkflow
  ├── ShotListWorkflow
  ├── VoiceoverWorkflow
  └── SocialVideoWorkflow
            │
            ▼
  LLMService & StoryboardImageGenerator (Abstract interfaces)
            │
            ▼
  GeminiProvider
            │
            ▼
  Gemini 3.5 Flash-Lite & Imagen (optional, storyboard only)
```

## 5. Workflows
Every capability runs a genuine multi-step pipeline — never a single generic prompt:
- **Video Script:** Plan scene structure (allocates the requested runtime across scenes) → Draft full script → Validate estimated narration timing, revise once if off target, otherwise polish.
- **Storyboard:** Plan visual language (palette, framing, pacing) → Generate the scene-by-scene storyboard table → Check scene-duration consistency against the runtime → (optional) generate one reference image for the hero scene.
- **Shot List:** Analyze production needs (locations, setups, equipment) → Generate the technical shot list → Review for real-world shootability and timing.
- **Voice-over:** Plan delivery (emotional throughline, pacing) → Draft the script with direction, pauses, and pronunciation notes → Validate spoken-word timing, revise once if off target.
- **Social Video:** Plan the hook and retention/scene-change strategy → Draft the full short-form plan (hook, scenes, captions, audio, CTA) → Validate pacing/timing, tighten once if off target.

## 6. Prompt Design
Every workflow uses a dedicated, originally-written system prompt in `prompts/`. Each prompt is deliberately distinct in its craft focus:
- Video Script → storytelling and scene construction
- Storyboard → visual planning and cinematography
- Shot List → production planning and real cinematography terminology
- Voice-over → spoken delivery, performance direction
- Social Video → hooks, retention, sound-off-safe short-form pacing

## 7. Gemini Integration
Powered by **Gemini 3.5 Flash-Lite** via the `google-genai` SDK, using the same `LLMService` abstraction as Agent 1 and Agent 2. The model name is read from `.env` (`GEMINI_MODEL`) and is never hardcoded or silently swapped — if the configured model is unavailable, the agent raises a clear configuration error rather than substituting a different one.

## 8. Timing Validation
Duration correctness is treated as a first-class requirement, not an afterthought:
- `services/timing.py` centralizes a documented speaking-rate assumption (**145 words/minute**) and tolerance band (**±20%**), rather than burying the assumption inside a prompt.
- `assess_timing()` estimates spoken/narration duration from generated text and compares it to the requested runtime for Video Script, Voice-over, and Social Video.
- `assess_scene_consistency()` sums per-scene durations for Storyboard and Shot List and compares the total to the requested runtime.
- If a draft is meaningfully outside the tolerance band, the workflow automatically sends it back for **one** corrective revision pass with explicit guidance (trim vs. extend); the final timing report is always shown to the user either way.

## 9. Image-Generation Architecture
Storyboard generation can optionally produce **one** AI reference image for the hero scene, using `StoryboardImageGenerator` (Imagen, via the `google-genai` SDK). It is:
- **Entirely decoupled from text generation** — the storyboard table is generated first and is complete and usable on its own.
- **Optional** — off by default, enabled via a checkbox (UI) or prompt (CLI).
- **Fail-safe** — any failure (missing key, quota, unsupported model) returns a graceful fallback with a text visual recommendation instead of crashing the workflow, and the UI is always shown the true success/failure state. The agent never claims an image was generated when it wasn't.

This mirrors Agent 2's `ImageGenerator` contract for Facebook Ads creative. It is implemented as a separate class within Agent 3's own `services/` folder rather than a cross-folder import, because Agent 1 and Agent 2 already establish the project convention that each agent folder is fully self-contained and can run independently of the others.

## 10. Environment Setup
Create a `.env` file in this directory:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_IMAGE_MODEL=imagen-3.0-generate-001
```
`GEMINI_IMAGE_MODEL` is optional — storyboard generation works fully without it; only the reference-image feature needs it.

## 11. Installation
```bash
pip install -r requirements.txt
```

## 12. Streamlit Usage
```bash
streamlit run app.py
```
Select a capability from the sidebar, fill in the dynamically-shown brief fields, and click Generate. Results appear in tabs (final output, intermediate planning stage, and a timing report).

## 13. CLI Usage
```bash
python video_production_agent.py
```
Shares 100% of the generation logic with the Streamlit UI — no duplicated workflow code.

## 14. Sample Outputs
Sample outputs are stored in the shared workspace directory:
`../deliverables/samples/video-production/`

## 15. Demo
Demo documentation is available at:
`../deliverables/demo/video-production-agent-demo.md`

## 16. Error Handling
- Missing/invalid `GEMINI_API_KEY` or `GEMINI_MODEL` → clear `EnvironmentError` at startup, before any generation attempt.
- Gemini API failures (quota, network, invalid model) → caught and re-raised as a descriptive `RuntimeError`; the UI surfaces this without crashing.
- Invalid or unparseable duration input → `ValueError` from `parse_duration()`, shown to the user for correction.
- Storyboard image generation failure → never raised; always returns a `{"success": False, ...}` fallback dict, and the rest of the storyboard remains fully usable.

## 17. Future Claude Integration
Because Agent 3 uses the same `LLMService` abstraction pattern as Agent 1 and Agent 2, migrating to Claude requires only creating a `ClaudeProvider` class and passing it into `VideoProductionAgent(provider=...)`. Workflows, prompts, and the UI require zero changes.

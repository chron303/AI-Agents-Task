# AI Engineer Assignment — Deliverables

**Assignment:** Technians AI Engineer  
**Student:** Nian  
**Date:** September 2026

---

## Agent 1 — Content Writing Agent

### Capabilities

- [x] Blog writing workflow implemented and tested
- [x] Website content workflow implemented and tested
- [x] E-book workflow implemented and tested
- [x] SEO article workflow implemented and tested

### Samples

- [x] Blog sample
- [x] Website content sample
- [x] SEO article sample

### Demo

- [x] Demo documentation — created at `deliverables/demo/content-writing-agent-demo.md`
- [ ] Demo recording — to be recorded by student

---

## Agent 2 — Copywriting & Ads Agent

### Capabilities

- [x] Facebook Ads
- [x] Google Ads
- [x] LinkedIn Ads
- [x] Product Descriptions
- [x] Email Copy
- [x] CTA Variations

### Samples

- [x] Sample 1 — Facebook Ad
- [x] Sample 2 — Google Ads
- [x] Sample 3 — Email Copy

### Demo

- [x] Demo documentation — created at `deliverables/demo/copywriting-ads-agent-demo.md`
- [ ] Demo recording — to be recorded by student

---

## Agent 3 — Video Production Agent

**Status: Complete**

### Capabilities

- [x] Video Script — scene-by-scene script with timing, visual/action, dialogue/narration, on-screen text, audio
- [x] Storyboard — visual/cinematography plan with optional AI reference image
- [x] Shot List — technical production shot list with real cinematography terminology
- [x] Voice-over Script — performance-ready narration with delivery direction and timing
- [x] Social Media Video — short-form plan for Reels/TikTok/Shorts/LinkedIn video

### Samples

- [x] Sample 1 — Video Script (Lumina Ergonomic Chair, 45s, YouTube)
- [x] Sample 2 — Storyboard (same concept, 20s, Instagram Reels)
- [x] Sample 3 — Social Media Video (TikTok, 15s)

> Note: The three samples above were authored manually as reference examples rather than generated live, because the build environment used to construct Agent 3 has network access restricted to package registries and cannot reach Google's Generative Language API. Each sample file states this plainly at the top. The agent's code is fully implemented and tested; running `generate_samples.py` locally with a working `GEMINI_API_KEY` produces authentic Gemini-generated versions of the same three samples.

### Demo

- [x] Demo documentation — created at `deliverables/demo/video-production-agent-demo.md` (includes a 1–2 minute speaking script for recording)
- [ ] Demo recording — to be recorded by student

### Testing Actually Performed

- [x] 17 automated unit tests (`Assignment 3 - Video Production Agent/tests/test_workflows.py`) covering all 5 workflows, the timing-validation module (`parse_duration`, `assess_timing`, `assess_scene_consistency`), and the orchestrator's routing/error handling — all passing, run against a deterministic fake LLM service so they execute without live API access
- [x] `py_compile` syntax check across every Agent 3 Python file
- [x] Streamlit app boot test (`streamlit run app.py`, confirmed HTTP 200, no runtime errors in logs)
- [x] `GeminiProvider` environment-variable validation tested (missing key/model correctly raises `EnvironmentError`)
- [x] `GeminiProvider` initialization tested with a real API key (initializes correctly; the live `generate()` call correctly surfaces a network-egress error from the sandbox, confirming the error-handling path works as designed)
- [x] Storyboard image-generation fallback tested (missing generator / failed call returns a graceful `{"success": False, ...}` result, never raises)
- [x] Regression check — Agent 1 and Agent 2 re-compiled and their Streamlit apps re-booted (HTTP 200, no errors) after Agent 3 was integrated, confirming no existing functionality was broken

> Live Gemini API connectivity itself (`test_connection.py`) could **not** be executed end-to-end in this build environment for the reason above, and should be run once by the student in an environment with normal internet access before recording the demo.

---

## Notes

- All deliverables for all agents are stored in this shared `deliverables/` folder
- Agent 3 follows the same self-contained folder pattern, `LLMService` abstraction, and prompts/workflows separation established by Agent 1 and Agent 2
- Agent 1 and Agent 2 were not modified or rebuilt during Agent 3's integration

# Video Production Agent — Demo Documentation

> **A note on this document:** The walkthrough below describes exactly how a live demo of Agent 3 would run against the real Gemini API. The generated-result excerpts shown here are drawn from the manually-authored reference samples in `deliverables/samples/video-production/` (see the note at the top of each sample file) because this build environment's network access does not extend to Google's Generative Language API. When recording the actual demo locally with a working `GEMINI_API_KEY`, the live Gemini output will replace these excerpts — the workflow, steps, and UI described here do not change.

## 1. Objective
Demonstrate that Agent 3 turns a short creative brief into a structured, timing-validated, production-ready video deliverable — not a single generic prompt dressed up as five features.

## 2. Demo Scenario
A small ergonomic-furniture brand, **Lumina**, wants a 45-second product video script for YouTube explaining why their chair fixes the "4pm slump," followed by a matching storyboard for their social team.

## 3. Input
Using the **Video Script** capability in the Streamlit UI:

| Field | Value |
|---|---|
| Topic/Concept | How Lumina Ergonomic Chair fixes 4pm back pain for remote workers |
| Objective | Drive traffic to the product page and build desire before the offer |
| Audience | Remote workers in their late 20s–40s who sit for 8+ hours a day |
| Platform | YouTube (long-form) |
| Duration | 45 seconds |
| Tone | Empathetic, modern |
| Key Message | Your chair is quietly breaking your body down — Lumina fixes that |
| CTA | Shop Lumina today and take 15% off with code POSTURE |

## 4. Steps
1. Open the Streamlit app (`streamlit run app.py`) and select **🎬 Video Script** from the sidebar.
2. Fill in the brief fields above.
3. Click **Generate**.
4. Watch the live progress log stream three steps: planning, drafting, and timing validation/finalization.
5. Review the result across the **Final Output**, **Scene Plan**, **Draft**, and **Timing** tabs.
6. Switch capability to **🖼️ Storyboard**, paste the finished script's concept in, and generate a matching storyboard — optionally checking "Generate reference image" to also produce a hero-scene visual.

## 5. Workflow (What Actually Happens Behind the UI)
```
Brief submitted
     │
     ▼
Step 1 — Plan scene structure (LLM call #1)
     │   Allocates the 45-second runtime across scenes before any dialogue is written
     ▼
Step 2 — Draft full script (LLM call #2)
     │   Writes scene-by-scene: timing, visual/action, dialogue, on-screen text, audio
     ▼
Step 3 — Validate timing (services/timing.py, no LLM call)
     │   Estimates spoken word count vs. 45s at 145 words/minute
     ▼
   ┌─┴─┐
   │   │
 on      off
target  target
   │       │
   ▼       ▼
Polish   Revise for timing (LLM call #3)
(LLM      then re-validate
call #3)
     │
     ▼
Final script + timing report returned to UI
```
Three real LLM calls, not one. The revision branch only fires when the timing check actually finds a problem — no wasted calls "for show."

## 6. Generated Result
See `deliverables/samples/video-production/sample-1-video-script.md` for the full scene-by-scene output and timing report (Lumina video script), and `sample-2-storyboard.md` for the matching storyboard.

## 7. Optional Storyboard Image
When "Generate reference image" is checked, the Storyboard workflow makes one additional call to extract a clean, dialogue-free visual description of the hero scene, then passes it to Imagen via `StoryboardImageGenerator`. If image generation is unavailable (no key, quota, network), the UI shows a clear warning and the text storyboard — which is already complete on its own — is unaffected. No demo should ever claim an image was generated if the call actually failed; the UI is built to prevent that (see `image["success"]` handling in `app.py`).

## 8. Explanation
This is not "Agent 1 with the word 'video' inserted into the prompt." The Video Script workflow allocates time across scenes *before* writing dialogue, separates visual direction from spoken words from on-screen text from audio, and runs a dedicated timing-validation step that can trigger an automatic revision — none of which exists in Agent 1's blog/e-book pipeline. The Storyboard, Shot List, Voice-over, and Social Video capabilities each have their own distinct prompt and pipeline built around what a director, a crew, a voice-over artist, or a social editor actually need — not a shared template.

## 9. How Gemini Is Used
Every text-generation step (planning, drafting, revision, review) is a real call to **Gemini 3.5 Flash-Lite** through the shared `LLMService` → `GeminiProvider` abstraction, exactly as Agent 1 and Agent 2 use it. The model name is read from `.env` (`GEMINI_MODEL`) and never hardcoded. Optional storyboard reference images use Imagen through the same `google-genai` SDK, in a completely separate, fail-safe code path.

## 10. How This Differs From a Simple Chatbot
A chatbot would take "write me a 45-second video script about my chair" and return one block of text in one pass, with no guarantee it fits 45 seconds, no separation between what's seen and what's heard, and no way to know if the timing is actually right. Agent 3:
- Plans structure before drafting, so time allocation is a deliberate decision, not a side effect.
- Separates visual, spoken, on-screen text, and audio into distinct fields a real crew can use.
- Deterministically measures its own output against the requested duration (`services/timing.py`) rather than trusting the model's self-report.
- Automatically revises when the measurement says it's wrong, and always shows the timing report either way — so the user is never told "trust me, it's 45 seconds" without evidence.

## 11. Speaking Script (1–2 Minutes, For Recording the Demo)

> "This is Agent 3, the Video Production Agent — the third agent in this assignment, alongside a content-writing agent and a copywriting agent.
>
> Where those agents write articles and ad copy, Agent 3 plans actual video production: scripts, storyboards, shot lists, voice-over, and short-form social video. I'll show the Video Script workflow.
>
> I give it a brief — a chair brand, a 45-second YouTube video, a target audience, and a call to action — and hit generate.
>
> Watch the progress log: it's not one prompt. First it plans the scene structure and allocates the 45 seconds across scenes. Then it drafts the full script — scene by scene, with timing, visuals, dialogue, on-screen text, and audio kept as separate fields. Then — and this is the part that matters — it actually measures its own narration against the requested 45 seconds using a documented speaking-rate assumption, and if it's off, it automatically revises before finalizing.
>
> Here's the result: five scenes, each with precise timing, and a timing report confirming it lands within target.
>
> Now I'll switch to the Storyboard capability and feed in the same concept — notice it produces a completely different kind of document: camera angles, movement, lighting, composition — not a repeat of the script.
>
> That's Agent 3: five real production workflows, genuine multi-step reasoning, and built-in timing validation — running on Gemini, in the same architecture as the other two agents."

## 12. Testing Performed
See `deliverables/deliverables.md` and `Assignment 3 - Video Production Agent/tests/test_workflows.py` for the full list of automated tests actually executed (17 unit tests covering all 5 workflows, the timing module, and the orchestrator) and the manual verification steps performed (Streamlit boot check, CLI dry run, regression check on Agents 1 and 2).

"""
Video Production Agent — Streamlit UI
=======================================
Provides an intuitive UI for the five video-production workflows:
Video Script, Storyboard, Shot List, Voice-over Script, Social Media Video.

Run with: streamlit run app.py
"""

import sys
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from video_production_agent import VideoProductionAgent, PLATFORM_OPTIONS

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent 3 — Video Production",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (consistent with Agent 1 / Agent 2 dark header + card style) ───
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        color: #94a3b8;
    }
    .badge {
        display: inline-block;
        background: #7c3aed;
        color: #f5f3ff !important;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        margin-top: 0.75rem;
        letter-spacing: 0.5px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #1d4ed8);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2.5rem;
        width: 100%;
    }
    .stButton > button:hover {
        opacity: 0.92;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Agent initialization ──────────────────────────────────────────────────────
@st.cache_resource
def get_agent():
    try:
        return VideoProductionAgent()
    except EnvironmentError as e:
        st.error(f"**Configuration Error**\n\n{e}")
        st.info(
            "Create a `.env` file in this directory with:\n"
            "```\nGEMINI_API_KEY=your_api_key_here\n"
            "GEMINI_MODEL=gemini-3.5-flash-lite\n```"
        )
        st.stop()


agent = get_agent()
info = agent.get_provider_info()

CAPABILITY_LABELS = {
    "video_script": "🎬 Video Script",
    "storyboard": "🖼️ Storyboard",
    "shot_list": "📋 Shot List",
    "voiceover": "🎙️ Voice-over Script",
    "social_video": "📱 Social Media Video",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 Video Production Agent")
    st.markdown("---")
    st.markdown("**Select Capability**")
    selection = st.radio(
        label="capability_radio",
        options=list(CAPABILITY_LABELS.keys()),
        format_func=lambda x: CAPABILITY_LABELS[x],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### About This Agent")
    st.markdown(
        """
        Transforms a brief into structured, production-ready video content
        across five specialized workflows — each with real planning,
        drafting, and validation steps.

        **Current LLM**

        Gemini 3.5 Flash-Lite

        **Assignment**

        Technians AI Engineer
        Agent 3 — Video Production
        """
    )
    st.markdown("---")
    st.caption(f"**Provider:** {info['provider']}")
    st.caption(f"**Model:** `{info['model']}`")


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="main-header">
        <h1>{CAPABILITY_LABELS[selection]}</h1>
        <p>Transform a brief into structured, production-ready video content
           using a multi-step workflow with built-in timing validation.</p>
        <span class="badge">Gemini 3.5 Flash-Lite · Multi-Step Workflow</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Dynamic input form ────────────────────────────────────────────────────────
with st.form(key="brief_form"):
    params = {}

    if selection == "video_script":
        st.subheader("🎬 Video Script Brief")
        col1, col2 = st.columns(2)
        with col1:
            params["topic"] = st.text_input("Topic/Concept *", placeholder="e.g. Why our app saves teams 5 hours a week")
            params["objective"] = st.text_input("Objective", value="Educate and build trust", placeholder="e.g. Drive sign-ups")
            params["audience"] = st.text_input("Target Audience", value="General audience")
            params["platform"] = st.selectbox("Platform", PLATFORM_OPTIONS, index=4)
        with col2:
            params["duration"] = st.text_input("Duration *", value="60 seconds", placeholder="e.g. 30 seconds, 2 minutes")
            params["tone"] = st.selectbox("Tone", ["Informative", "Conversational", "Inspirational", "Bold", "Playful", "Authoritative"])
            params["style"] = st.text_input("Style (optional)", placeholder="e.g. Fast-cut, documentary, minimalist")
            params["cta"] = st.text_input("CTA (optional)", placeholder="e.g. Start your free trial")
        params["key_message"] = st.text_input("Key Message (optional)")
        params["additional_instructions"] = st.text_area("Additional Instructions (optional)", height=70)

    elif selection == "storyboard":
        st.subheader("🖼️ Storyboard Brief")
        params["concept_or_script"] = st.text_area(
            "Concept or Script to Storyboard *", height=140,
            placeholder="Paste a script, or describe the concept to storyboard...",
        )
        col1, col2 = st.columns(2)
        with col1:
            params["platform"] = st.selectbox("Platform", PLATFORM_OPTIONS, index=4)
            params["duration"] = st.text_input("Duration *", value="60 seconds")
        with col2:
            params["tone"] = st.selectbox("Tone", ["Informative", "Cinematic", "Playful", "Dramatic", "Minimalist"])
            params["style"] = st.text_input("Visual Style (optional)", placeholder="e.g. Warm and natural, high-contrast noir")
        params["additional_instructions"] = st.text_area("Additional Instructions (optional)", height=70)
        params["generate_reference_image"] = st.checkbox(
            "Generate an optional visual reference image for the hero scene (uses Imagen API if configured)",
            value=False,
        )

    elif selection == "shot_list":
        st.subheader("📋 Shot List Brief")
        params["concept_or_script"] = st.text_area(
            "Concept, Script, or Storyboard *", height=140,
            placeholder="Paste a script or storyboard, or describe the concept...",
        )
        col1, col2 = st.columns(2)
        with col1:
            params["duration"] = st.text_input("Duration *", value="60 seconds")
            params["locations"] = st.text_input("Known Locations (optional)", placeholder="e.g. Office interior, city rooftop")
        with col2:
            params["cast_or_talent"] = st.text_input("Cast/Talent (optional)", placeholder="e.g. One presenter, two extras")
        params["additional_instructions"] = st.text_area("Additional Instructions (optional)", height=70)

    elif selection == "voiceover":
        st.subheader("🎙️ Voice-over Brief")
        col1, col2 = st.columns(2)
        with col1:
            params["topic"] = st.text_input("Topic *", placeholder="e.g. Announcing our new savings feature")
            params["audience"] = st.text_input("Target Audience", value="General audience")
            params["platform"] = st.selectbox("Platform", PLATFORM_OPTIONS, index=4)
            params["duration"] = st.text_input("Duration *", value="30 seconds")
        with col2:
            params["tone"] = st.selectbox("Tone", ["Warm", "Confident", "Calm", "Urgent", "Playful", "Authoritative"])
            params["desired_emotion"] = st.text_input("Desired Emotion (optional)", placeholder="e.g. Reassured, excited")
            params["cta"] = st.text_input("CTA (optional)", placeholder="e.g. Download the app today")
        params["key_message"] = st.text_input("Key Message (optional)")
        params["additional_instructions"] = st.text_area("Additional Instructions (optional)", height=70)

    elif selection == "social_video":
        st.subheader("📱 Social Media Video Brief")
        col1, col2 = st.columns(2)
        with col1:
            params["topic"] = st.text_input("Topic *", placeholder="e.g. 3 mistakes people make with home coffee brewing")
            params["platform"] = st.selectbox("Platform", ["Instagram Reels", "TikTok", "YouTube Shorts", "LinkedIn short-form video"])
            params["audience"] = st.text_input("Target Audience", value="General audience")
        with col2:
            params["duration"] = st.text_input("Duration *", value="15 seconds", placeholder="e.g. 15 seconds, 30 seconds")
            params["tone"] = st.selectbox("Tone", ["Energetic", "Funny", "Relatable", "Bold", "Calm"])
            params["cta"] = st.text_input("CTA (optional)", placeholder="e.g. Follow for more tips")
        params["key_message"] = st.text_input("Key Message (optional)")
        params["additional_instructions"] = st.text_area("Additional Instructions (optional)", height=70)

    submitted = st.form_submit_button("🎬 Generate", use_container_width=True)


# ── Generation logic ──────────────────────────────────────────────────────────
if submitted:
    missing = False
    if selection in ("video_script", "voiceover", "social_video") and not params.get("topic"):
        st.error("Please enter a topic.")
        missing = True
    elif selection in ("storyboard", "shot_list") and not params.get("concept_or_script"):
        st.error("Please enter a concept or script.")
        missing = True
    elif not params.get("duration"):
        st.error("Please enter a duration.")
        missing = True

    if not missing:
        progress_placeholder = st.empty()
        progress_messages = []

        def on_progress(msg: str):
            progress_messages.append(msg)
            log_html = "<br>".join(f"&gt; {m}" for m in progress_messages)
            progress_placeholder.markdown(
                f'<div style="background:#0f172a;border-radius:10px;padding:1rem 1.25rem;'
                f'font-family:\'Courier New\',monospace;font-size:0.85rem;color:#4ade80;'
                f'border:1px solid #1e3a5f;min-height:60px;">{log_html}</div>',
                unsafe_allow_html=True,
            )

        try:
            with st.spinner("Working…"):
                result = agent.generate(content_type=selection, params=params, on_progress=on_progress)

            st.success("Generation complete!")

            st.markdown("---")
            st.subheader("📄 Results")

            tab_labels = ["✅ Final Output"]
            if selection == "video_script":
                tab_labels += ["📋 Scene Plan", "📝 Draft", "⏱️ Timing"]
            elif selection == "storyboard":
                tab_labels += ["🎨 Visual Plan", "⏱️ Timing"]
                if result.get("image"):
                    tab_labels.append("🖼️ Reference Image")
            elif selection == "shot_list":
                tab_labels += ["📋 Production Plan", "⏱️ Timing"]
            elif selection == "voiceover":
                tab_labels += ["🎭 Delivery Plan", "📝 Draft", "⏱️ Timing"]
            elif selection == "social_video":
                tab_labels += ["🪝 Hook Plan", "📝 Draft", "⏱️ Timing"]

            tabs = st.tabs(tab_labels)

            with tabs[0]:
                st.markdown(result["final"])
                st.download_button(
                    "⬇️ Download Output",
                    result["final"],
                    file_name=f"{selection}.md",
                    mime="text/markdown",
                )
                if result.get("revised_for_timing"):
                    st.caption("ℹ️ This output was automatically revised once to better fit the requested duration.")

            tab_idx = 1
            if selection == "video_script":
                with tabs[tab_idx]:
                    st.markdown(result.get("plan", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("draft", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("timing_report", ""))
            elif selection == "storyboard":
                with tabs[tab_idx]:
                    st.markdown(result.get("visual_plan", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("timing_report", ""))
                tab_idx += 1
                if result.get("image"):
                    with tabs[tab_idx]:
                        img = result["image"]
                        if img.get("success"):
                            st.image(img["image_bytes"], caption=img.get("prompt_used", ""), use_container_width=True)
                            st.success("Reference image generated successfully.")
                        else:
                            st.warning("Image generation was unavailable — the text storyboard is still complete.")
                            st.markdown(f"**Fallback:** {img.get('fallback', '')}")
                            if img.get("error"):
                                st.caption(f"Details: {img['error']}")
            elif selection == "shot_list":
                with tabs[tab_idx]:
                    st.markdown(result.get("production_plan", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("timing_report", ""))
            elif selection == "voiceover":
                with tabs[tab_idx]:
                    st.markdown(result.get("delivery_plan", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("draft", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("timing_report", ""))
            elif selection == "social_video":
                with tabs[tab_idx]:
                    st.markdown(result.get("hook_plan", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("draft", ""))
                tab_idx += 1
                with tabs[tab_idx]:
                    st.markdown(result.get("timing_report", ""))

            st.markdown("---")
            st.caption(
                f"Generated by {result.get('provider', 'Gemini')} · "
                f"Model: `{result.get('model', '–')}` · Multi-step workflow"
            )

        except EnvironmentError as e:
            st.error(f"**Configuration Error**\n\n{e}")
        except (ValueError, RuntimeError) as e:
            st.error(f"**Generation Error**\n\n{e}")
        except Exception as e:
            st.error(f"**Unexpected Error**\n\n{e}")

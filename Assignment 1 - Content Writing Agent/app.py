"""
Content Writing Agent — Streamlit UI
=====================================
A clean, professional interface for the Content Writing Agent.

Run with:  streamlit run app.py
"""

import sys
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Content Writing Agent",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #cbd5e1 !important;
        font-size: 0.95rem;
    }

    /* Header */
    .agent-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .agent-header h1 {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .agent-header p {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    .badge {
        display: inline-block;
        background: #1d4ed8;
        color: #eff6ff !important;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        margin-top: 0.75rem;
        letter-spacing: 0.5px;
    }

    /* Section labels */
    .section-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.25rem;
    }

    /* Result area */
    .result-container {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.75rem 2rem;
        margin-top: 1rem;
    }

    /* Progress log */
    .progress-log {
        background: #0f172a;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #4ade80;
        border: 1px solid #1e3a5f;
        min-height: 80px;
    }

    /* Generate button */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 2.5rem;
        border: none;
        border-radius: 10px;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        opacity: 0.92;
    }

    /* Tabs */
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

    /* Input labels */
    label {
        font-weight: 500;
        color: #374151;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✍️ Content Writing Agent")
    st.markdown("---")

    st.markdown("**Select Content Type**")
    content_type = st.radio(
        label="content_type_radio",
        options=["Blog Post", "Website Content", "E-book", "SEO Article"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### About This Agent")
    st.markdown(
        """
        This agent uses a **multi-step workflow** for each content type.
        Each workflow makes real LLM calls for planning, drafting, and refinement.

        **Current LLM**  
        Gemini 3.5 Flash-Lite

        **Assignment**  
        Technians AI Engineer  
        Agent 1 — Content Writing
        """
    )

    st.markdown("---")
    # Live model info
    try:
        import os
        model = os.getenv("GEMINI_MODEL", "Not configured")
        st.caption(f"Model: `{model}`")
    except Exception:
        pass


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="agent-header">
        <h1>✍️ Content Writing Agent</h1>
        <p>Generate high-quality blog posts, website copy, e-books, and SEO articles
           using a multi-step intelligent workflow.</p>
        <span class="badge">Gemini 3.5 Flash-Lite · Multi-Step Workflow</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Dynamic input form ────────────────────────────────────────────────────────
with st.form(key="content_form"):
    if content_type == "Blog Post":
        st.subheader("📝 Blog Post Brief")
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Topic *",
                placeholder="e.g. How AI is transforming remote work",
                key="blog_topic",
            )
            audience = st.text_input(
                "Target Audience",
                value="General readers",
                key="blog_audience",
            )
            tone = st.selectbox(
                "Tone",
                ["Informative", "Conversational", "Professional", "Authoritative",
                 "Inspirational", "Witty", "Empathetic"],
                key="blog_tone",
            )
        with col2:
            purpose = st.text_input(
                "Purpose",
                value="Inform and educate",
                placeholder="e.g. Drive newsletter sign-ups",
                key="blog_purpose",
            )
            desired_length = st.selectbox(
                "Desired Length",
                ["500–800 words", "800–1200 words", "1000–1500 words",
                 "1500–2000 words", "2000+ words"],
                index=2,
                key="blog_length",
            )
        additional = st.text_area(
            "Additional Instructions (optional)",
            placeholder="e.g. Include a section on practical tips. Avoid technical jargon.",
            height=80,
            key="blog_additional",
        )
        params = {
            "topic": topic,
            "audience": audience,
            "tone": tone,
            "purpose": purpose,
            "desired_length": desired_length,
            "additional_instructions": additional,
        }
        ct_key = "blog"

    elif content_type == "Website Content":
        st.subheader("🌐 Website Content Brief")
        col1, col2 = st.columns(2)
        with col1:
            page_type = st.selectbox(
                "Page Type *",
                ["Homepage", "Product Page", "Service Page", "About Page", "Landing Page"],
                key="web_page_type",
            )
            business_name = st.text_input(
                "Business / Brand Name *",
                placeholder="e.g. BrightStack Solutions",
                key="web_business",
            )
            product_or_service = st.text_input(
                "Product or Service *",
                placeholder="e.g. AI-powered project management platform",
                key="web_product",
            )
            target_audience = st.text_input(
                "Target Audience *",
                placeholder="e.g. Startup founders and product managers",
                key="web_audience",
            )
        with col2:
            value_proposition = st.text_area(
                "Core Value Proposition *",
                placeholder="e.g. We reduce project delivery time by 40% through automated task coordination",
                height=100,
                key="web_vp",
            )
            tone = st.selectbox(
                "Brand Tone",
                ["Professional", "Friendly", "Bold", "Authoritative",
                 "Conversational", "Innovative", "Trustworthy"],
                key="web_tone",
            )
            conversion_goal = st.text_input(
                "Primary Conversion Goal *",
                placeholder="e.g. Start free trial, Book a demo, Contact us",
                key="web_cta",
            )
        additional = st.text_area(
            "Additional Instructions (optional)",
            height=70,
            key="web_additional",
        )
        params = {
            "page_type": page_type,
            "business_name": business_name,
            "product_or_service": product_or_service,
            "target_audience": target_audience,
            "value_proposition": value_proposition,
            "tone": tone,
            "conversion_goal": conversion_goal,
            "additional_instructions": additional,
        }
        ct_key = "website"

    elif content_type == "E-book":
        st.subheader("📚 E-book Brief")
        col1, col2 = st.columns(2)
        with col1:
            ebook_title = st.text_input(
                "E-book Title *",
                placeholder="e.g. The Complete Guide to Personal Finance in Your 20s",
                key="ebook_title",
            )
            overall_topic = st.text_input(
                "Overall Topic *",
                placeholder="e.g. Personal finance for young professionals",
                key="ebook_topic",
            )
            target_reader = st.text_input(
                "Target Reader *",
                placeholder="e.g. Young professionals aged 22–30",
                key="ebook_reader",
            )
            book_objective = st.text_area(
                "Book Objective *",
                placeholder="e.g. Teach readers to budget, save, invest, and build an emergency fund",
                height=90,
                key="ebook_objective",
            )
        with col2:
            num_chapters = st.slider("Number of Chapters", 3, 10, 5, key="ebook_chapters")
            depth_level = st.selectbox(
                "Depth Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=1,
                key="ebook_depth",
            )
            tone = st.selectbox(
                "Tone",
                ["Educational", "Conversational", "Motivational",
                 "Academic", "Practical", "Inspiring"],
                key="ebook_tone",
            )
        additional = st.text_area(
            "Additional Instructions (optional)",
            height=70,
            key="ebook_additional",
        )
        params = {
            "title": ebook_title,
            "overall_topic": overall_topic,
            "target_reader": target_reader,
            "book_objective": book_objective,
            "num_chapters": num_chapters,
            "depth_level": depth_level,
            "tone": tone,
            "additional_instructions": additional,
        }
        ct_key = "ebook"

    elif content_type == "SEO Article":
        st.subheader("🔍 SEO Article Brief")
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Article Topic *",
                placeholder="e.g. How to build a morning routine that boosts productivity",
                key="seo_topic",
            )
            primary_keyword = st.text_input(
                "Primary Keyword *",
                placeholder="e.g. morning routine for productivity",
                key="seo_primary",
            )
            secondary_keywords = st.text_input(
                "Secondary Keywords (comma-separated)",
                placeholder="e.g. morning habits, daily routine, productivity tips",
                key="seo_secondary",
            )
            target_audience = st.text_input(
                "Target Audience",
                value="Working professionals",
                key="seo_audience",
            )
        with col2:
            search_intent = st.selectbox(
                "Search Intent",
                ["Informational", "Commercial", "Transactional", "Navigational"],
                key="seo_intent",
            )
            desired_length = st.selectbox(
                "Desired Length",
                ["800–1200 words", "1200–1800 words", "1800–2500 words", "2500+ words"],
                index=1,
                key="seo_length",
            )
        additional = st.text_area(
            "Additional Instructions (optional)",
            placeholder="e.g. Target the UK market. Include actionable steps.",
            height=70,
            key="seo_additional",
        )
        params = {
            "topic": topic,
            "primary_keyword": primary_keyword,
            "secondary_keywords": secondary_keywords,
            "target_audience": target_audience,
            "search_intent": search_intent,
            "desired_length": desired_length,
            "additional_instructions": additional,
        }
        ct_key = "seo"

    submitted = st.form_submit_button("✨ Generate Content", use_container_width=True)


# ── Generation logic ──────────────────────────────────────────────────────────
if submitted:
    # Basic validation
    missing = False
    if ct_key == "blog" and not params.get("topic"):
        st.error("Please enter a topic for your blog post.")
        missing = True
    elif ct_key == "website" and not params.get("business_name"):
        st.error("Please enter the business name.")
        missing = True
    elif ct_key == "ebook" and not params.get("title"):
        st.error("Please enter the e-book title.")
        missing = True
    elif ct_key == "seo" and not params.get("primary_keyword"):
        st.error("Please enter the primary keyword.")
        missing = True

    if not missing:
        # Progress display
        progress_placeholder = st.empty()
        progress_messages = []

        def on_progress(msg: str):
            progress_messages.append(msg)
            log_html = "<br>".join(f"&gt; {m}" for m in progress_messages)
            progress_placeholder.markdown(
                f'<div class="progress-log">{log_html}</div>',
                unsafe_allow_html=True,
            )

        try:
            from content_writing_agent import ContentWritingAgent
            agent = ContentWritingAgent()

            with st.spinner("Working…"):
                result = agent.generate(
                    content_type=ct_key,
                    params=params,
                    on_progress=on_progress,
                )

            st.success("Content generation complete!")

            # ── Result tabs ───────────────────────────────────────────────────
            st.markdown("---")
            st.subheader("📄 Results")

            if ct_key == "blog":
                tab1, tab2, tab3 = st.tabs(
                    ["✅ Final Post", "📋 Outline", "📝 Raw Draft"]
                )
                with tab1:
                    st.markdown(result["final"])
                    st.download_button(
                        "⬇️ Download Final Post",
                        result["final"],
                        file_name="blog_post.md",
                        mime="text/markdown",
                    )
                with tab2:
                    st.markdown(result.get("outline", ""))
                with tab3:
                    st.markdown(result.get("draft", ""))

            elif ct_key == "website":
                tab1, tab2 = st.tabs(["✅ Page Copy", "📐 Content Strategy"])
                with tab1:
                    st.markdown(result["final"])
                    st.download_button(
                        "⬇️ Download Page Copy",
                        result["final"],
                        file_name="website_content.md",
                        mime="text/markdown",
                    )
                with tab2:
                    st.markdown(result.get("content_strategy", ""))

            elif ct_key == "ebook":
                tab1, tab2, tab3 = st.tabs(
                    ["✅ Complete E-book", "📚 Chapter Plan", "📖 Chapters Draft"]
                )
                with tab1:
                    st.markdown(result["final"])
                    st.download_button(
                        "⬇️ Download E-book",
                        result["final"],
                        file_name="ebook.md",
                        mime="text/markdown",
                    )
                with tab2:
                    st.markdown(result.get("chapter_plan", ""))
                with tab3:
                    st.markdown(result.get("chapters", ""))

            elif ct_key == "seo":
                tab1, tab2, tab3 = st.tabs(
                    ["✅ Final Article", "🔍 Keyword Strategy", "📝 Draft"]
                )
                with tab1:
                    st.markdown(result["final"])
                    st.download_button(
                        "⬇️ Download SEO Article",
                        result["final"],
                        file_name="seo_article.md",
                        mime="text/markdown",
                    )
                with tab2:
                    st.markdown(result.get("keyword_strategy", ""))
                with tab3:
                    st.markdown(result.get("draft", ""))

            # Model info footer
            st.markdown("---")
            st.caption(
                f"Generated by {result.get('provider', 'Gemini')} · "
                f"Model: `{result.get('model', '–')}` · "
                f"Multi-step workflow"
            )

        except EnvironmentError as e:
            st.error(f"**Configuration Error**\n\n{e}")
            st.info(
                "Create a `.env` file in the project directory with:\n"
                "```\nGEMINI_API_KEY=your_api_key_here\n"
                "GEMINI_MODEL=gemini-3.5-flash-lite\n```"
            )
        except RuntimeError as e:
            st.error(f"**Generation Error**\n\n{e}")
        except Exception as e:
            st.error(f"**Unexpected Error**\n\n{e}")

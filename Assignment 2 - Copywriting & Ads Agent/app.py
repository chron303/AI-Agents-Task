"""
Copywriting & Ads Agent — Streamlit UI
======================================
Provides an intuitive UI for the 6 marketing workflows.
Includes optional Image Generation for Facebook Ads.

Run with: streamlit run app.py
"""

import sys
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# We need to import our local agent. We add the parent dir to path if needed.
sys.path.insert(0, str(Path(__file__).parent))

from copywriting_ads_agent import CopywritingAdsAgent

# ==========================================
# UI Configuration
# ==========================================

st.set_page_config(
    page_title="Agent 2 — Copywriting & Ads",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for dark/clean theme matching Agent 1
st.markdown("""
<style>
    .main-header {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .main-header p {
        margin: 5px 0 0 0;
        opacity: 0.8;
    }
    .stButton>button {
        background-color: #0078D4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
    }
    .stButton>button:hover {
        background-color: #005A9E;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Initialization
# ==========================================

@st.cache_resource
def get_agent():
    try:
        return CopywritingAdsAgent()
    except EnvironmentError as e:
        st.error(f"Configuration Error: {e}")
        st.stop()

agent = get_agent()
info = agent.get_provider_info()


# ==========================================
# Sidebar Navigation
# ==========================================

st.sidebar.title("🎯 Capabilities")

content_type_labels = {
    "facebook": "📱 Facebook Ads",
    "google": "🔍 Google Ads",
    "linkedin": "💼 LinkedIn Ads",
    "product": "🛒 Product Description",
    "email": "✉️ Email Copy",
    "cta": "🎯 CTA Variations"
}

selection = st.sidebar.radio(
    "Select Workflow:",
    options=list(content_type_labels.keys()),
    format_func=lambda x: content_type_labels[x]
)

st.sidebar.markdown("---")
st.sidebar.caption(f"**Provider:** {info['provider']}")
st.sidebar.caption(f"**Model:** {info['model']}")


# ==========================================
# Main Content Area
# ==========================================

st.markdown(f"""
<div class="main-header">
    <h1>{content_type_labels[selection].split(' ', 1)[1]} Agent</h1>
    <p>Generate highly persuasive, platform-optimized marketing copy.</p>
</div>
""", unsafe_allow_html=True)

# Form Fields based on selection
with st.form("brief_form"):
    st.subheader("Marketing Brief")
    
    params = {}
    
    col1, col2 = st.columns(2)
    
    if selection == "facebook":
        with col1:
            params['product_or_service'] = st.text_input("Product/Service", placeholder="e.g. Acme Ergonomic Chair")
            params['target_audience'] = st.text_input("Target Audience", placeholder="e.g. Remote workers with back pain")
            params['campaign_objective'] = st.text_input("Campaign Objective", placeholder="e.g. Direct sales")
        with col2:
            params['key_benefit'] = st.text_input("Key Benefit", placeholder="e.g. Fixes posture in 7 days")
            params['pain_point'] = st.text_input("Pain Point", placeholder="e.g. Lower back pain after 4 hours")
            params['offer'] = st.text_input("Offer (Optional)", placeholder="e.g. 15% off with code POSTURE")
            
        params['brand_tone'] = st.text_input("Brand Tone", placeholder="e.g. Empathetic, direct, modern")
        params['generate_image'] = st.checkbox("Generate Image Creative (Uses Imagen API if configured)", value=False)
            
    elif selection == "google":
        with col1:
            params['product_or_service'] = st.text_input("Product/Service", placeholder="e.g. Enterprise Cloud Backup")
            params['target_keywords'] = st.text_input("Target Keywords", placeholder="e.g. cloud backup solutions, enterprise data recovery")
            params['search_intent'] = st.text_input("Search Intent", placeholder="e.g. Seeking enterprise-grade security and reliability")
        with col2:
            params['target_audience'] = st.text_input("Target Audience", placeholder="e.g. IT Directors, CIOs")
            params['key_benefits'] = st.text_input("Key Benefits", placeholder="e.g. 99.999% uptime, ransomware protection")
            params['offer'] = st.text_input("Offer/CTA", placeholder="e.g. Book a Demo")

    elif selection == "linkedin":
        with col1:
            params['product_or_service'] = st.text_input("Product/Service", placeholder="e.g. AI HR Software")
            params['target_audience'] = st.text_input("Target Professional Audience", placeholder="e.g. HR Directors, CHROs at companies 500+ employees")
        with col2:
            params['pain_point'] = st.text_input("Business Pain Point", placeholder="e.g. Spending 20 hours a week screening resumes")
            params['key_benefit'] = st.text_input("Business Value/ROI", placeholder="e.g. Reduce time-to-hire by 40%")
            params['offer'] = st.text_input("Offer/CTA", placeholder="e.g. Download Case Study")
            
    elif selection == "product":
        with col1:
            params['product_name'] = st.text_input("Product Name", placeholder="e.g. Lumina Pro Desk Lamp")
            params['product_category'] = st.text_input("Category", placeholder="e.g. Home Office Accessories")
            params['features'] = st.text_area("Features", placeholder="e.g. 5 color temperatures, auto-dimming, Qi charger base")
        with col2:
            params['target_customer'] = st.text_input("Target Customer", placeholder="e.g. Designers, late-night workers")
            params['brand_tone'] = st.text_input("Brand Tone", placeholder="e.g. Premium, minimalist, Apple-like")

    elif selection == "email":
        with col1:
            params['objective'] = st.text_input("Email Objective", placeholder="e.g. Product Launch Announcement")
            params['product_or_service'] = st.text_input("Product/Service", placeholder="e.g. New Summer Apparel Collection")
            params['target_audience'] = st.text_input("Target Audience", placeholder="e.g. Existing past customers")
        with col2:
            params['offer'] = st.text_input("Offer", placeholder="e.g. Early access 24hrs before public")
            params['brand_tone'] = st.text_input("Brand Tone", placeholder="e.g. Excited, exclusive")

    elif selection == "cta":
        with col1:
            params['product_or_service'] = st.text_input("Product/Service", placeholder="e.g. Financial Planning App")
            params['desired_action'] = st.text_input("Desired Action", placeholder="e.g. Sign up for 14-day trial")
            params['target_audience'] = st.text_input("Target Audience", placeholder="e.g. Millennials wanting to invest")
        with col2:
            params['context'] = st.text_input("Context/Placement", placeholder="e.g. Bottom of a long-form landing page")
            params['brand_tone'] = st.text_input("Brand Tone", placeholder="e.g. Trustworthy, friendly, simple")

    submitted = st.form_submit_button("Generate Copy")


# ==========================================
# Generation Logic
# ==========================================

if submitted:
    # Basic validation
    if not any(params.values()):
        st.error("Please fill in at least some details of the brief.")
        st.stop()

    progress_placeholder = st.empty()
    
    def on_progress(msg: str):
        progress_placeholder.info(f"⏳ {msg}")
        # Small delay so the user can actually read the stages
        time.sleep(0.5)

    with st.spinner("Initializing workflow..."):
        try:
            result = agent.generate(selection, params, on_progress)
            progress_placeholder.success("✨ Generation Complete!")
            time.sleep(1)
            progress_placeholder.empty()
        except RuntimeError as e:
            st.error(f"Generation Error: {e}")
            st.stop()

    # Display Results
    st.subheader("Result")
    
    # We display analysis and final output in tabs
    tab_labels = ["Final Output", "Strategic Analysis"]
    has_image = "image" in result and result["image"] is not None
    if has_image:
        tab_labels.append("Ad Creative (Image)")

    tabs = st.tabs(tab_labels)
    
    with tabs[0]:
        st.markdown(result["final"])
        st.download_button(
            label="Download Copy",
            data=result["final"],
            file_name=f"{selection}_copy.md",
            mime="text/markdown"
        )
        
    with tabs[1]:
        st.info("The agent performed this strategic analysis before writing the copy:")
        st.markdown(result["analysis"])
        
    if has_image:
        with tabs[2]:
            img_data = result["image"]
            if img_data["success"]:
                st.image(img_data["image_bytes"], caption=img_data["prompt_used"], use_container_width=True)
                st.success("Image generated successfully.")
            else:
                st.warning("Image API Generation Failed. Using graceful fallback.")
                st.markdown(f"**Fallback visual recommendation:** {img_data['fallback']}")
                st.error(f"Error details: {img_data['error']}")

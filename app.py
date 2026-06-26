import streamlit as st
import asyncio
import os
import time
from dotenv import load_dotenv
from main import run_marketing_workflow, save_results

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Page configuration – MUST be the first Streamlit command
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Marketing Strategy | Multi-Agent System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* ---------- Google Fonts ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ---------- CSS Variables ---------- */
        :root {
            --primary: #4F46E5;
            --primary-light: #818CF8;
            --primary-dark: #3730A3;
            --accent: #F59E0B;
            --success: #10B981;
            --danger: #EF4444;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text: #1E293B;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
            --shadow-lg: 0 10px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.05);
            --radius: 16px;
            --radius-sm: 10px;
            --phase1: #6366F1;
            --phase2: #8B5CF6;
            --phase3: #06B6D4;
        }

        /* ---------- Global Resets ---------- */
        .stApp {
            background: var(--bg);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        header[data-testid="stHeader"] { background: transparent; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* ================================================================
           SIDEBAR
           ================================================================ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        }
        [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 { color: #F8FAFC !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1); }

        .sidebar-step {
            display: flex; align-items: flex-start; gap: 12px;
            padding: 14px 16px; margin: 8px 0;
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            border-left: 3px solid var(--primary-light);
            transition: all 0.2s ease;
        }
        .sidebar-step:hover { background: rgba(255,255,255,0.1); }
        .sidebar-step .step-number {
            width: 30px; height: 30px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
            background: linear-gradient(135deg, #4F46E5, #818CF8);
        }
        .sidebar-step .step-content { font-size: 0.84rem; line-height: 1.5; }
        .sidebar-step .step-content strong { color: #F8FAFC; }
        .sidebar-step .step-content .model-tag {
            display: inline-block; font-size: 0.7rem;
            padding: 2px 8px; border-radius: 10px;
            background: rgba(129,140,248,0.2); color: #A5B4FC;
            margin: 3px 0;
        }

        /* ================================================================
           HERO SECTION
           ================================================================ */
        .hero-container {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 30%, #312E81 60%, #4F46E5 100%);
            border-radius: var(--radius);
            padding: 3rem 2.8rem 2.4rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px -10px rgba(79,70,229,0.25);
        }
        .hero-container::before {
            content: '';
            position: absolute; top: -40%; right: -15%;
            width: 450px; height: 450px;
            background: radial-gradient(circle, rgba(129,140,248,0.18) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-container::after {
            content: '';
            position: absolute; bottom: -35%; left: -5%;
            width: 350px; height: 350px;
            background: radial-gradient(circle, rgba(6,182,212,0.10) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-grid {
            position: absolute; inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
        }
        .hero-title {
            font-size: 2.5rem; font-weight: 800;
            color: #F8FAFC; margin: 0 0 0.6rem 0;
            position: relative; z-index: 1;
            letter-spacing: -0.5px; line-height: 1.25;
        }
        .hero-title .highlight { color: #A5B4FC; }
        .hero-subtitle {
            font-size: 1.05rem; color: #94A3B8;
            margin: 0 0 1.6rem 0;
            position: relative; z-index: 1;
            font-weight: 400; max-width: 600px; line-height: 1.6;
        }
        .hero-agents-bar {
            display: flex; gap: 10px; flex-wrap: wrap;
            position: relative; z-index: 1;
            padding: 14px 18px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 14px;
            backdrop-filter: blur(8px);
            max-width: fit-content;
        }
        .hero-agents-bar .agent-item {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 16px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 22px;
            font-size: 0.84rem; color: #E2E8F0;
            transition: all 0.2s ease;
        }
        .hero-agents-bar .agent-item:hover {
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.25);
        }
        .hero-agents-bar .agent-dot {
            width: 8px; height: 8px; border-radius: 50%;
        }
        .hero-agents-bar .dot1 { background: #818CF8; box-shadow: 0 0 6px #818CF8; }
        .hero-agents-bar .dot2 { background: #A78BFA; box-shadow: 0 0 6px #A78BFA; }
        .hero-agents-bar .dot3 { background: #22D3EE; box-shadow: 0 0 6px #22D3EE; }

        /* ================================================================
           INPUT CARD
           ================================================================ */
        .input-card {
            background: var(--card-bg);
            border-radius: var(--radius);
            padding: 2rem 2.2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }
        .input-card .section-label {
            font-weight: 700; font-size: 1rem;
            color: var(--text); margin-bottom: 1rem;
            display: flex; align-items: center; gap: 8px;
        }
        .chip-row {
            display: flex; gap: 10px; flex-wrap: wrap;
            align-items: center;
            padding: 12px 0 4px;
        }
        .chip-row .chip-label {
            font-size: 0.8rem; color: var(--text-muted);
            font-weight: 500; white-space: nowrap;
        }

        /* ================================================================
           PRIMARY BUTTON
           ================================================================ */
        div.stButton > button {
            background: linear-gradient(135deg, var(--primary) 0%, #6366F1 100%) !important;
            color: #FFFFFF !important; border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2.4rem !important;
            font-weight: 600 !important; font-size: 1rem !important;
            letter-spacing: 0.2px;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 14px rgba(79,70,229,0.35) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(79,70,229,0.45) !important;
        }
        div.stButton > button:active { transform: translateY(0); }

        /* Chip-style buttons */
        .stButton.chip-btn > button {
            background: #F1F5F9 !important; color: #475569 !important;
            border: 1px solid #E2E8F0 !important; border-radius: 22px !important;
            padding: 0.3rem 1rem !important; font-size: 0.8rem !important;
            font-weight: 500 !important; letter-spacing: 0 !important;
            box-shadow: none !important;
        }
        .stButton.chip-btn > button:hover {
            background: #EEF2FF !important; color: var(--primary) !important;
            border-color: #C7D2FE !important; transform: none !important;
            box-shadow: 0 2px 6px rgba(79,70,229,0.12) !important;
        }

        /* ================================================================
           PROGRESS SECTION
           ================================================================ */
        .progress-wrapper {
            text-align: center; padding: 1.5rem 0;
        }
        .progress-wrapper h3 {
            font-size: 1.1rem; font-weight: 700; color: var(--text);
            margin-bottom: 1rem;
        }
        .progress-steps {
            display: flex; gap: 0; justify-content: center;
            align-items: center; flex-wrap: wrap;
            margin: 1rem 0;
        }
        .pstep {
            display: flex; align-items: center; gap: 8px;
            padding: 12px 22px;
            background: #fff; border: 2px solid var(--border);
            border-radius: 30px; font-weight: 600; font-size: 0.88rem;
            color: var(--text-muted); transition: all 0.4s ease;
            position: relative;
        }
        .pstep.active {
            border-color: var(--phase1); color: var(--phase1);
            background: #EEF2FF;
            box-shadow: 0 0 0 4px rgba(99,102,241,0.08);
            animation: pulse-step 2s ease-in-out infinite;
        }
        .pstep.done {
            border-color: var(--success); color: var(--success);
            background: #ECFDF5;
        }
        .pstep-arrow {
            font-size: 1.2rem; color: #CBD5E1; margin: 0 6px;
            font-weight: 700; user-select: none;
        }
        .pstep-arrow.active-arrow { color: var(--phase1); animation: arrow-blink 1.2s ease-in-out infinite; }
        @keyframes pulse-step {
            0%, 100% { box-shadow: 0 0 0 4px rgba(99,102,241,0.08); }
            50% { box-shadow: 0 0 0 10px rgba(99,102,241,0.03); }
        }
        @keyframes arrow-blink {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
        }
        .progress-bar-track {
            width: 100%; max-width: 500px; height: 5px;
            background: #E2E8F0; border-radius: 6px;
            margin: 0.5rem auto 0; overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%; border-radius: 6px;
            background: linear-gradient(90deg, var(--phase1), var(--phase2));
            transition: width 0.4s ease;
        }

        /* ================================================================
           RESULTS SECTION
           ================================================================ */
        .section-divider {
            height: 1px; background: linear-gradient(90deg, transparent, #CBD5E1, transparent);
            margin: 2rem 0;
        }

        .metric-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 16px; margin-bottom: 2rem;
        }
        .metric-card {
            background: var(--card-bg); border-radius: var(--radius-sm);
            padding: 1.4rem 1.5rem; box-shadow: var(--shadow-sm);
            border: 1px solid var(--border); border-left: 4px solid var(--primary);
            display: flex; flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
        .metric-card.mc-1 { border-left-color: var(--phase1); }
        .metric-card.mc-2 { border-left-color: var(--phase2); }
        .metric-card.mc-3 { border-left-color: var(--phase3); }
        .metric-card.mc-4 { border-left-color: var(--accent); }
        .metric-card .metric-icon { font-size: 1.3rem; margin-bottom: 6px; }
        .metric-card .metric-value {
            font-size: 2rem; font-weight: 800; color: var(--text);
            line-height: 1.2;
        }
        .metric-card .metric-label {
            font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;
        }

        /* ================================================================
           EXPANDERS
           ================================================================ */
        [data-testid="stExpander"] {
            background: var(--card-bg);
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1rem; overflow: hidden;
            border-left: 4px solid var(--border) !important;
            transition: border-color 0.3s ease;
        }
        .expander-research { border-left-color: var(--phase1) !important; }
        .expander-strategy { border-left-color: var(--phase2) !important; }
        .expander-content  { border-left-color: var(--phase3) !important; }
        [data-testid="stExpander"] summary {
            font-weight: 700; font-size: 1rem;
            color: var(--text); padding: 1.1rem 1.5rem !important;
            background: #FAFBFC; border-bottom: 1px solid var(--border);
            transition: color 0.2s ease, background 0.2s ease;
        }
        [data-testid="stExpander"] summary:hover {
            color: var(--primary); background: #F8FAFC;
        }
        .expander-badge {
            display: inline-block; font-size: 0.7rem; font-weight: 600;
            padding: 3px 10px; border-radius: 12px;
            margin-left: 10px; vertical-align: middle;
        }
        .badge-research { background: #EEF2FF; color: var(--phase1); }
        .badge-strategy { background: #F3F0FF; color: var(--phase2); }
        .badge-content  { background: #ECFEFF; color: #0891B2; }

        /* ================================================================
           RESULT CONTENT
           ================================================================ */
        .result-card {
            background: #FAFBFC;
            border-radius: var(--radius-sm);
            padding: 1.5rem 2rem; line-height: 1.8;
        }

        /* ================================================================
           DOWNLOAD SECTION
           ================================================================ */
        .download-section {
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            border-radius: var(--radius); padding: 1.2rem 1.8rem;
            margin-top: 1.5rem; border: 1px solid #C7D2FE;
            display: flex; align-items: center;
            justify-content: space-between; flex-wrap: wrap; gap: 1rem;
        }
        .download-info .dl-title {
            font-weight: 700; color: var(--primary-dark); font-size: 0.95rem;
        }
        .download-info .dl-path {
            font-size: 0.78rem; color: #64748B; margin-top: 2px;
        }
        .download-info .dl-path code {
            background: #fff; padding: 1px 8px; border-radius: 4px;
            font-size: 0.75rem;
        }

        /* ================================================================
           MISC
           ================================================================ */
        .stSpinner > div { border-top-color: var(--primary) !important; }
        div[data-testid="stSuccess"] {
            background: #ECFDF5; border: 1px solid #A7F3D0;
            border-radius: var(--radius-sm);
        }
        div[data-testid="stError"] {
            background: #FEF2F2; border: 1px solid #FECACA;
            border-radius: var(--radius-sm);
        }
        div[data-testid="stTextInput"] input {
            border-radius: 10px !important; border: 2px solid var(--border) !important;
            padding: 0.75rem 1rem !important; font-size: 1rem !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
            background: #fff !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 4px rgba(79,70,229,0.08) !important;
        }
        .stMarkdown h1 { font-size: 1.5rem; font-weight: 700; color: var(--text); }
        .stMarkdown h2 {
            font-size: 1.25rem; font-weight: 700; color: var(--text);
            border-bottom: 2px solid #EEF2FF; padding-bottom: 0.5rem; margin-bottom: 1rem;
        }
        .stMarkdown h3 { font-size: 1.05rem; font-weight: 600; color: var(--text); }

        /* ================================================================
           RESPONSIVE
           ================================================================ */
        @media (max-width: 768px) {
            .hero-title { font-size: 1.5rem; }
            .hero-container { padding: 1.8rem 1.2rem; }
            .hero-agents-bar { flex-direction: column; max-width: 100%; }
            .metric-row { grid-template-columns: 1fr 1fr; }
            .progress-steps { flex-direction: column; gap: 6px; }
            .pstep-arrow { display: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🚀 Marketing AI")
        st.markdown("*Multi-Agent Strategy Engine*")
        st.markdown("---")

        st.markdown("### ⚡ How It Works")

        steps = [
            ("1", "🔍", "Market Research", "GLM-4 Plus",
             "Analyzes trends, competitors & target audience"),
            ("2", "🎯", "Strategy", "GLM-5.1",
             "Crafts positioning & channel strategy"),
            ("3", "✍️", "Content Creator", "Qwen3.7-Max",
             "Writes ads, emails, posts & more"),
        ]
        for num, icon, title, model, desc in steps:
            st.markdown(
                f"""<div class="sidebar-step">
                    <div class="step-number">{num}</div>
                    <div class="step-content">
                        <strong>{icon} {title}</strong><br>
                        <span class="model-tag">{model}</span><br>
                        <span style="color:#94A3B8;font-size:0.78rem;">{desc}</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown("")

        st.markdown("---")
        st.markdown("### 💡 Tips for Best Results")
        st.markdown("- Be specific about your product")
        st.markdown("- Mention your target audience")
        st.markdown("- Describe unique selling points")
        st.markdown("- Name competitors if known")

        st.markdown("---")
        st.markdown(
            "<small style='color:#64748B;'>Built with LangGraph + Streamlit<br>"
            "Models: Zhipu AI · Alibaba Cloud</small>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Helper: estimate stats from results
# ---------------------------------------------------------------------------
def compute_stats(research: str, strategy: str, content: str) -> dict:
    return {
        "research_words": len(research.split()) if research else 0,
        "strategy_words": len(strategy.split()) if strategy else 0,
        "content_words": len(content.split()) if content else 0,
        "research_sections": research.count("##") if research else 0,
        "strategy_sections": strategy.count("##") if strategy else 0,
        "content_sections": content.count("##") if content else 0,
    }


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
def main():
    inject_custom_css()
    render_sidebar()

    # =========================================================================
    # HERO SECTION
    # =========================================================================
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-grid"></div>
            <h1 class="hero-title">
                🚀 Marketing Strategy<br>
                <span class="highlight">Multi-Agent System</span>
            </h1>
            <p class="hero-subtitle">
                Three specialized AI agents collaborate to research your market,
                formulate a winning strategy, and produce ready-to-use creative
                content — all in one seamless workflow.
            </p>
            <div class="hero-agents-bar">
                <span class="agent-item">
                    <span class="agent-dot dot1"></span> Research Agent
                </span>
                <span class="agent-item">
                    <span class="agent-dot dot2"></span> Strategy Agent
                </span>
                <span class="agent-item">
                    <span class="agent-dot dot3"></span> Content Agent
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # INPUT SECTION
    # =========================================================================
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-label">📝 What product or service would you like to market?</div>',
        unsafe_allow_html=True,
    )

    # --- Row: examples chips (before text_input to avoid widget-key conflict) ---
    examples = [
        ("🌱", "Eco-friendly reusable water bottle"),
        ("📱", "AI-powered language learning app"),
        ("✨", "Premium organic skincare line"),
        ("⚡", "Smart home energy monitor"),
    ]
    st.markdown('<div class="chip-row">', unsafe_allow_html=True)
    st.markdown('<span class="chip-label">💡 Try an example →</span>', unsafe_allow_html=True)
    chip_cols = st.columns(len(examples))
    for i, (icon, example) in enumerate(examples):
        with chip_cols[i]:
            if st.button(f"{icon} {example}", key=f"ex_{i}", use_container_width=True):
                st.session_state["product_input_widget"] = example
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Row: input + generate button ---
    col1, col2 = st.columns([5, 1])
    with col1:
        product_input = st.text_input(
            "Product name",
            placeholder="Describe your product or service here...",
            label_visibility="collapsed",
            key="product_input_widget",
        )
    with col2:
        generate_clicked = st.button("🚀 Generate", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close input-card

    # =========================================================================
    # PROCESSING
    # =========================================================================
    if generate_clicked:
        if not product_input.strip():
            st.error("⚠️ Please enter a product or service name to continue.")
        else:
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                st.markdown(
                    '<div class="progress-wrapper">'
                    '<h3>⚙️ Generating Your Marketing Plan...</h3>'
                    '<div class="progress-steps">'
                    '  <span class="pstep active">🔍<br>Market Research</span>'
                    '  <span class="pstep-arrow active-arrow">→</span>'
                    '  <span class="pstep">🎯<br>Strategy</span>'
                    '  <span class="pstep-arrow">→</span>'
                    '  <span class="pstep">✍️<br>Content</span>'
                    '</div>'
                    '<div class="progress-bar-track">'
                    '  <div class="progress-bar-fill" style="width:10%;"></div>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            try:
                start_time = time.time()
                result = asyncio.run(run_marketing_workflow(product_input))
                elapsed = time.time() - start_time

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                return

            # --- Done ---
            progress_placeholder.empty()
            with progress_placeholder.container():
                st.markdown(
                    '<div class="progress-wrapper">'
                    '<h3>✅ Marketing Plan Complete!</h3>'
                    '<div class="progress-steps">'
                    '  <span class="pstep done">✅ Market Research</span>'
                    '  <span class="pstep-arrow" style="color:#10B981;">→</span>'
                    '  <span class="pstep done">✅ Strategy</span>'
                    '  <span class="pstep-arrow" style="color:#10B981;">→</span>'
                    '  <span class="pstep done">✅ Content</span>'
                    '</div>'
                    f'<p style="text-align:center;color:#64748B;font-size:0.85rem;">⏱️ Completed in {elapsed:.1f}s</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            # --- Save ---
            file_path = save_results(
                result["product"],
                result["research_report"],
                result["strategy"],
                result["content"],
            )

            # =========================================================================
            # RESULTS
            # =========================================================================
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("## 📊 Results Overview")

            stats = compute_stats(
                result["research_report"],
                result["strategy"],
                result["content"],
            )
            total_words = stats['research_words'] + stats['strategy_words'] + stats['content_words']
            total_sections = stats['research_sections'] + stats['strategy_sections'] + stats['content_sections']

            st.markdown(
                f"""
                <div class="metric-row">
                    <div class="metric-card mc-1">
                        <div class="metric-icon">📝</div>
                        <div class="metric-value">{total_words:,}</div>
                        <div class="metric-label">Total Words Generated</div>
                    </div>
                    <div class="metric-card mc-2">
                        <div class="metric-icon">📑</div>
                        <div class="metric-value">{total_sections}</div>
                        <div class="metric-label">Content Sections</div>
                    </div>
                    <div class="metric-card mc-3">
                        <div class="metric-icon">🤖</div>
                        <div class="metric-value">3</div>
                        <div class="metric-label">AI Agents Deployed</div>
                    </div>
                    <div class="metric-card mc-4">
                        <div class="metric-icon">⏱️</div>
                        <div class="metric-value">{elapsed:.1f}s</div>
                        <div class="metric-label">Generation Time</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Expanders with phase-colored left borders ---
            st.markdown(
                '<div data-testid="stExpander" class="expander-research" style="border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow-sm);margin-bottom:1rem;overflow:hidden;">'
                '<details open>'
                '<summary>🔍 Market Research Report '
                '<span class="expander-badge badge-research">Phase 1</span></summary>'
                f'<div style="padding:1.5rem 2rem;line-height:1.8;">{result["research_report"]}</div>'
                '</details>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div data-testid="stExpander" class="expander-strategy" style="border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow-sm);margin-bottom:1rem;overflow:hidden;">'
                '<details open>'
                '<summary>🎯 Marketing Strategy '
                '<span class="expander-badge badge-strategy">Phase 2</span></summary>'
                f'<div style="padding:1.5rem 2rem;line-height:1.8;">{result["strategy"]}</div>'
                '</details>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div data-testid="stExpander" class="expander-content" style="border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow-sm);margin-bottom:1rem;overflow:hidden;">'
                '<details open>'
                '<summary>✍️ Creative Content '
                '<span class="expander-badge badge-content">Phase 3</span></summary>'
                f'<div style="padding:1.5rem 2rem;line-height:1.8;">{result["content"]}</div>'
                '</details>'
                '</div>',
                unsafe_allow_html=True,
            )

            # =========================================================================
            # DOWNLOAD
            # =========================================================================
            markdown_content = f"""# Market Research Report for {result["product"]}

{result["research_report"]}

---

# Marketing Strategy

{result["strategy"]}

---

# Created Content

{result["content"]}
"""
            st.markdown(
                f"""
                <div class="download-section">
                    <div class="download-info">
                        <div class="dl-title">📥 Your marketing plan is ready!</div>
                        <div class="dl-path">Saved to <code>{file_path}</code></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                label="📥 Download Full Marketing Plan (.md)",
                data=markdown_content,
                file_name=os.path.basename(file_path),
                mime="text/markdown",
                use_container_width=True,
            )

            st.success("✅ Marketing plan generated successfully!")


if __name__ == "__main__":
    main()

"""
Offline Indian Patent AI Novelty Analyzer — Main Streamlit Application Entry Point.
Real-Time Patent Similarity & Novelty Assessment using Stella Embeddings, FAISS, and Official IPO Records.

Provides end-to-end patent intelligence, official Indian metadata preservation,
candidate field pre-filtering, weighted AI Novelty Index calculation,
real-time Search Statistics Panel, IP India verification workflows, and downloadable 12-section PDF reports.
"""

import sys
import os
import time
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root directory to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from search.semantic_search import PatentSearchEngine
from llm.novelty_report import NoveltyReportGenerator
from history.search_history import SearchHistoryManager
from ui.components import (
    apply_saas_dark_theme,
    render_hero_banner,
    render_dataset_overview_card,
    render_search_stats_panel,
)
from ui.dashboard import render_dashboard
from ui.report_view import render_report_view

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Novelty Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom SaaS Dark Theme
apply_saas_dark_theme()

@st.cache_resource
def get_search_engine():
    """Cached singleton loader for Stella Embedding Generator & FAISS search controller."""
    engine = PatentSearchEngine(project_root=PROJECT_ROOT)
    return engine

@st.cache_resource
def get_report_generator():
    """Cached AI Novelty Report Generator."""
    return NoveltyReportGenerator()

@st.cache_resource
def get_history_manager():
    """Cached Search History Manager."""
    return SearchHistoryManager(history_file=os.path.join(PROJECT_ROOT, "data", "search_history.json"))

def init_session_state():
    """Initialize persistent session state flags."""
    if "current_report" not in st.session_state:
        st.session_state.current_report = None
    if "search_stats" not in st.session_state:
        st.session_state.search_stats = None
    if "invention_title" not in st.session_state:
        st.session_state.invention_title = ""
    if "invention_description" not in st.session_state:
        st.session_state.invention_description = ""

def render_sidebar():
    """Renders clean sidebar navigation with product branding."""
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🧠 AI Novelty Analyzer</div>', unsafe_allow_html=True)

        nav_choice = st.radio(
            "Navigation",
            options=["Patent Search", "Analytics Dashboard", "Search History", "About"],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding-top: 10px; line-height: 1.7;">
            <b style="color: #F8FAFC; font-size: 0.9rem;">AI Novelty Analyzer</b><br/>
            <span style="color: #94A3B8; font-size: 0.8rem; font-style: italic;">Intelligent Prior-Art Assessment<br/>for Indian Patents</span>
        </div>
        """, unsafe_allow_html=True)

        return nav_choice

def render_header():
    """Renders clean, minimal hero banner displaying only '🧠 AI Novelty Analyzer'."""
    render_hero_banner()


def execute_search_pipeline(user_query: str, engine, report_gen, history_mgr):
    """
    Executes offline search retrieval flow with automatic technical-domain detection:
    User Input -> Stella Vectorization -> Automatic Domain Classification -> FAISS (k=200) -> Dynamic Feature Matrix -> 12-Section PDF Report
    """
    with st.spinner("Screening official Indian patent corpus (~458k records with k=200 candidates)..."):
        try:
            top_5_patents, all_scores, stats_dict, exec_time = engine.search_offline_indian_patents(
                query_idea=user_query,
                top_k=5,
                candidate_pool_size=200,
                field_filter=None
            )
            st.session_state.search_stats = stats_dict
        except Exception as general_err:
            st.error(f"Error during offline search execution: {general_err}")
            return None

    if not top_5_patents:
        st.warning("No matching patent records found for the given description. Try broadening your keywords.")
        return None

    with st.spinner("Generating 12-Section AI Novelty Report, Concept Enhancement & Feature Analysis..."):
        detected_domain = stats_dict.get("detected_field") if stats_dict else None
        report_data = report_gen.generate_report(
            user_idea=user_query,
            retrieved_patents=top_5_patents,
            all_retrieved_scores=all_scores,
            search_time_sec=exec_time,
            invention_title=st.session_state.get("invention_title", ""),
            invention_description=st.session_state.get("invention_description", ""),
            detected_field=detected_domain,
        )
        if detected_domain and "detected_field" not in report_data:
            report_data["detected_field"] = detected_domain

    # Save to history manager
    history_mgr.add_entry(report_data)
    st.session_state.current_report = report_data
    return report_data

def main():
    init_session_state()
    nav_choice = render_sidebar()

    # Load Engine Singleton
    try:
        engine = get_search_engine()
        report_gen = get_report_generator()
        history_mgr = get_history_manager()
    except Exception as e:
        st.error(f"Error initializing system resources: {e}")
        st.stop()

    if nav_choice == "Patent Search":
        render_header()
        render_dataset_overview_card(
            total_patents=getattr(engine, 'total_patents', 458724),
            fields_count=16
        )

        st.markdown("""
        <div style="background: #1A2436; border: 1px solid #334155; border-left: 4px solid #2563EB; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);">
            <div style="font-size: 1.22rem; font-weight: 700; color: #38BDF8; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
                💡 Describe Your Proposed Invention
            </div>
            <div style="font-size: 0.9rem; color: #94A3B8; margin-bottom: 16px;">
                Provide a title and detailed description of your invention below to evaluate patent novelty.
            </div>
        """, unsafe_allow_html=True)

        st.text_input(
            label="Invention Title",
            key="invention_title",
            placeholder="Enter your invention title (e.g., AI Disaster Communication Network)",
            max_chars=150,
            help="Single-line title summarizing your invention (max 150 characters)."
        )

        st.text_area(
            label="Invention Description",
            key="invention_description",
            placeholder="Describe your invention, including its purpose, key technical features, working mechanism, and intended application.",
            height=200,
            help="Detailed technical description of the invention (supports long text 2000+ characters)."
        )

        with st.expander("💡 What makes a good invention description?", expanded=False):
            st.markdown("""
            **To get the most accurate AI patent novelty assessment, include:**
            - **The Problem:** What specific technical problem or limitation does your invention solve?
            - **Key Technical Features:** What are the primary hardware components, algorithms, or physical structures?
            - **Working Mechanism:** How do the components interact and operate step-by-step?
            - **Differentiation:** What makes your approach novel or unique compared to existing prior art?
            """)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            analyze_button = st.button("🚀 Analyze Patent Novelty", use_container_width=True, type="primary")

        st.markdown("</div>", unsafe_allow_html=True)

        if analyze_button:
            title_text = st.session_state.invention_title.strip()
            desc_text = st.session_state.invention_description.strip()

            if not title_text:
                st.warning("⚠️ Please enter an invention title before starting the patent analysis.")
            elif len(desc_text) < 30:
                st.warning("⚠️ Please provide a more detailed description of your invention (at least 30 characters) before starting the patent analysis.")
            else:
                combined_query = f"Title: {title_text}\nDescription: {desc_text}"
                report_data = execute_search_pipeline(
                    combined_query, engine, report_gen, history_mgr
                )

        if st.session_state.search_stats:
            render_search_stats_panel(st.session_state.search_stats)

        if st.session_state.current_report:
            render_report_view(st.session_state.current_report)

    elif nav_choice == "Analytics Dashboard":
        render_dashboard(engine)

    elif nav_choice == "Search History":
        st.markdown("""
        <div class="header-card">
            <div class="header-title">📜 Persistent Search History</div>
            <div class="header-subtitle">Log of Previously Analyzed Invention Reports</div>
        </div>
        """, unsafe_allow_html=True)

        history_items = history_mgr.load_history()

        if not history_items:
            st.info("No search analyses recorded in history yet. Execute a search under 'Patent Search'!")
        else:
            for item in history_items:
                report_data = item.get("report_data", {})
                novelty_score = item.get("novelty_index", 0.0)
                status = item.get("novelty_status", "N/A")

                with st.expander(f"Report #{item.get('report_id')} | {item.get('timestamp')} | AI Novelty Index: {novelty_score}/100 ({status})"):
                    st.write(f"**Invention Description:** {item.get('query')}")
                    st.write(f"**Novelty Classification:** {status}")

                    if st.button(f"📖 Load Active Report View", key=f"reopen_{item.get('report_id')}"):
                        st.session_state.current_report = report_data
                        st.success("Report loaded into active view! Switch to 'Patent Search' tab to inspect.")

                    st.markdown("---")
                    for p in report_data.get("retrieved_patents", []):
                        st.write(f"**[Official ID: {p.get('application_number')}]** {p.get('title')} — Journal Issue: {p.get('publication_number')} | Location: {p.get('ipo_location')}")

    elif nav_choice == "About":
        st.markdown("""
        <div class="header-card">
            <div class="header-title">ℹ️ About AI Novelty Analyzer</div>
            <div class="header-subtitle">Intelligent Prior-Art Assessment for Indian Patents</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### How It Works
        The **AI Novelty Analyzer** evaluates your invention description against official Indian Patent Office (IPO) records to assess novelty and identify similar prior art.

        ### Key Capabilities
        1. **Patent Corpus:** ~458,724 official Indian patent publication records.
        2. **Automatic Domain Detection:** Semantic field classification across 16 technical domains.
        3. **AI Novelty Index:** Scores your invention's originality from 0–100 with qualitative labels.
        4. **Dynamic Feature Matrix:** Compares proposed features against closest prior art.
        5. **Professional PDF Reports:** Downloadable 12-section assessment reports.
        6. **Innovation Assistant:** AI-generated technology focus and opportunity insights.
        """)

if __name__ == "__main__":
    main()


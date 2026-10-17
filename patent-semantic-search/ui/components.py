"""
Reusable UI Components and Enterprise Midnight Blue Theme CSS styling for Streamlit.
Includes official Indian patent badges, dataset overview cards, search statistics metrics,
and clean professional patent cards displaying only official metadata.
"""

from typing import Any
import streamlit as st
from search.similarity import NOVELTY_INDEX_DISCLAIMER
from preprocessing.clean_text import format_application_number

def apply_saas_dark_theme():
    """
    Injects Enterprise Midnight Blue theme CSS (#0B1220 background, #1A2436 cards,
    #2563EB primary, #38BDF8 cyan accent, #334155 border, Inter typography).
    """
    st.markdown("""
    <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* Global Theme */
        html, body, [class*="css"], .stApp {
            background-color: #0B1220 !important;
            color: #F8FAFC !important;
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #334155 !important;
        }
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {
            color: #CBD5E1 !important;
        }
        .sidebar-brand {
            font-size: 1.2rem;
            font-weight: 800;
            color: #38BDF8 !important;
            padding: 10px 0 16px 0;
            border-bottom: 1px solid #334155;
            margin-bottom: 16px;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1A2436 0%, #111827 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 26px 32px;
            margin-bottom: 22px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .hero-icon {
            font-size: 2.2rem;
            line-height: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        }
        .hero-title {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.15 !important;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .hero-title .brand-ai {
            color: #F8FAFC !important;
            font-weight: 800;
        }
        .hero-title .brand-name {
            color: #F8FAFC !important;
            font-weight: 800;
        }

        /* Header Card */
        .header-card {
            background: linear-gradient(135deg, #1A2436 0%, #111827 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 22px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        }
        .header-title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #F8FAFC !important;
            margin-bottom: 4px;
        }
        .header-subtitle {
            color: #38BDF8 !important;
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .header-desc {
            color: #CBD5E1 !important;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        /* Metric Cards & Stat Containers */
        div[data-testid="stMetric"] {
            background-color: #1A2436 !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        }
        div[data-testid="stMetric"] label {
            color: #94A3B8 !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: #F8FAFC !important;
            font-size: 1.35rem !important;
            font-weight: 800 !important;
        }

        /* Section Titles */
        .section-title {
            color: #38BDF8 !important;
            font-size: 1.25rem;
            font-weight: 700;
            margin-top: 22px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.01em;
        }

        /* AI Novelty Card */
        .novelty-card {
            background: linear-gradient(135deg, #1A2436 0%, #111827 100%);
            border: 1px solid #334155;
            border-left: 5px solid #2563EB;
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        }
        .novelty-score-large {
            font-size: 3.2rem;
            font-weight: 900;
            line-height: 1.0;
            margin-bottom: 6px;
        }
        .novelty-label {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        /* Executive Summary Callout Card */
        .exec-summary-card {
            background: #1A2436;
            border: 1px solid #334155;
            border-left: 4px solid #38BDF8;
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 20px;
            color: #F8FAFC;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Patent Result Cards */
        .patent-card {
            background: #1A2436;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 18px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            transition: border-color 0.2s ease, transform 0.15s ease;
        }
        .patent-card:hover {
            border-color: #38BDF8;
        }
        .patent-title {
            font-size: 1.18rem;
            font-weight: 700;
            color: #F8FAFC !important;
            margin: 8px 0 10px 0;
            line-height: 1.4;
        }
        .patent-id-row {
            margin-bottom: 14px;
            font-size: 0.92rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .patent-id-code {
            color: #38BDF8 !important;
            font-family: 'Consolas', 'Roboto Mono', monospace;
            font-size: 1.05rem;
            font-weight: 700;
            background: #111827;
            padding: 3px 10px;
            border-radius: 6px;
            border: 1px solid #334155;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px 20px;
            font-size: 0.88rem;
            color: #CBD5E1;
            padding-top: 10px;
            border-top: 1px solid #253347;
        }
        .meta-item b {
            color: #94A3B8;
            font-weight: 600;
            display: block;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 2px;
        }
        .meta-item span {
            color: #F8FAFC;
            font-weight: 600;
        }

        /* Badges */
        .badge-verified-ipo {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(16, 185, 129, 0.12);
            color: #34D399 !important;
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 6px;
            padding: 3px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 8px;
            letter-spacing: 0.02em;
        }
        .badge-match-strength {
            display: inline-block;
            font-weight: 700;
            font-size: 0.8rem;
            padding: 3px 10px;
            border-radius: 6px;
            color: #FFFFFF !important;
            letter-spacing: 0.02em;
        }

        /* AI Innovation Assistant Card */
        .assistant-card {
            background: linear-gradient(135deg, #1A2436 0%, #111827 100%);
            border: 1px solid #334155;
            border-left: 4px solid #38BDF8;
            border-radius: 14px;
            padding: 22px 26px;
            margin-top: 24px;
            margin-bottom: 20px;
        }
        .assistant-item {
            margin-bottom: 14px;
        }
        .assistant-label {
            font-size: 0.78rem;
            font-weight: 800;
            color: #38BDF8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 4px;
        }
        .assistant-value {
            font-size: 0.95rem;
            color: #F8FAFC;
            line-height: 1.5;
        }
        .assistant-footer-note {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 16px;
            color: #CBD5E1;
            font-size: 0.86rem;
            font-style: italic;
            margin-top: 14px;
            line-height: 1.5;
        }

        /* Table Styling */
        table {
            background-color: #1A2436 !important;
            color: #F8FAFC !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            width: 100% !important;
        }
        th {
            background-color: #111827 !important;
            color: #38BDF8 !important;
            font-weight: 700 !important;
            font-size: 0.84rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            border-bottom: 1px solid #334155 !important;
            padding: 10px 14px !important;
        }
        td {
            color: #CBD5E1 !important;
            border-bottom: 1px solid #253347 !important;
            padding: 10px 14px !important;
            font-size: 0.88rem !important;
        }

        /* Disclaimer Footer Box */
        .disclaimer-box {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 0.82rem;
            color: #94A3B8;
            line-height: 1.5;
            margin-top: 24px;
            margin-bottom: 16px;
        }

        /* Expander / Accordion Styling */
        details[data-testid="stExpander"] {
            background-color: #1A2436 !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
            margin-bottom: 12px !important;
        }
        details[data-testid="stExpander"] summary {
            color: #F8FAFC !important;
            font-weight: 600 !important;
        }
        details[data-testid="stExpander"] svg {
            color: #38BDF8 !important;
        }

        /* Landscape Narrative Block */
        .landscape-block {
            background: #1A2436;
            border: 1px solid #334155;
            border-left: 4px solid #2563EB;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 14px;
            color: #F8FAFC;
            font-size: 0.92rem;
            line-height: 1.6;
        }
        .landscape-block-label {
            font-size: 0.76rem;
            font-weight: 700;
            color: #38BDF8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }

        /* Inputs & Textareas */
        .stTextInput input, .stTextArea textarea {
            background-color: #111827 !important;
            border: 1px solid #334155 !important;
            color: #F8FAFC !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #38BDF8 !important;
            box-shadow: 0 0 0 1px #38BDF8 !important;
        }

        /* Primary Button */
        button[kind="primary"] {
            background-color: #2563EB !important;
            border-color: #2563EB !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
            transition: all 0.15s ease !important;
        }
        button[kind="primary"]:hover {
            background-color: #1D4ED8 !important;
            border-color: #1D4ED8 !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5) !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            background-color: #111827;
            border-radius: 10px;
            padding: 4px;
            border: 1px solid #334155;
        }
        .stTabs [data-baseweb="tab"] {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1A2436 !important;
            color: #38BDF8 !important;
            border-bottom: 2px solid #2563EB !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def clean_app_number(val: Any) -> str:
    """Removes any IN, IN-, IN/ prefix from application number."""
    formatted = format_application_number(val)
    if formatted.upper().startswith("IN-") or formatted.upper().startswith("IN/"):
        return formatted[3:].strip()
    elif formatted.upper().startswith("IN") and len(formatted) > 2 and formatted[2].isdigit():
        return formatted[2:].strip()
    return formatted


def render_patent_card_html(patent: dict, rank: int = 1) -> str:
    """
    Renders clean professional HTML card with ONLY official metadata.
    Removes explanation box, search context, and IN prefix.
    """
    match_label = patent.get("match_strength_label", "Match")
    match_color = patent.get("match_strength_color", "#2563EB")

    app_num = clean_app_number(patent.get('application_number', 'N/A'))
    title = patent.get('title', 'N/A')
    pub_num = patent.get('publication_number', 'N/A')
    pub_date = patent.get('publication_date', 'N/A')
    ipo_loc = patent.get('ipo_location', 'N/A')
    field = patent.get('field_of_invention', 'N/A')
    app_type = patent.get('application_type', 'N/A')
    claims = patent.get('no_of_claims', 'N/A')
    pages = patent.get('no_of_pages', 'N/A')

    return f"""<div class="patent-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span class="badge-verified-ipo">Official Indian Patent</span>
        <span class="badge-match-strength" style="background: {match_color};">{match_label}</span>
    </div>

    <div class="patent-title">
        Patent {rank}: {title}
    </div>

    <div class="patent-id-row">
        <span style="color: #94A3B8; font-weight: 600;">Application Number (Official ID):</span>
        <span class="patent-id-code">{app_num}</span>
    </div>

    <div class="meta-grid">
        <div class="meta-item">
            <b>IPO Jurisdiction</b>
            <span>{ipo_loc}</span>
        </div>
        <div class="meta-item">
            <b>Patent Journal Issue</b>
            <span>{pub_num}</span>
        </div>
        <div class="meta-item">
            <b>Publication Date</b>
            <span>{pub_date}</span>
        </div>
        <div class="meta-item">
            <b>Application Type</b>
            <span>{app_type}</span>
        </div>
        <div class="meta-item">
            <b>Field of Invention</b>
            <span>{field}</span>
        </div>
        <div class="meta-item">
            <b>Number of Claims</b>
            <span>{claims}</span>
        </div>
        <div class="meta-item">
            <b>Number of Pages</b>
            <span>{pages}</span>
        </div>
    </div>
</div>"""


def render_native_patent_card(patent: dict, rank: int = 1):
    """
    Renders a patent card using pure native Streamlit components.
    Zero raw HTML, zero code-blocks, rounded border, dark enterprise theme,
    right-aligned match badge, and a clean two-column metadata grid.
    """
    match_label = patent.get("match_strength_label", "Moderate Match")
    app_num = clean_app_number(patent.get('application_number', 'N/A'))
    title = patent.get('title', 'N/A')
    pub_num = patent.get('publication_number', 'N/A')
    pub_date = patent.get('publication_date', 'N/A')
    ipo_loc = patent.get('ipo_location', 'N/A')
    field = patent.get('field_of_invention', 'N/A')
    app_type = patent.get('application_type', 'N/A')
    claims = patent.get('no_of_claims', 'N/A')
    pages = patent.get('no_of_pages', 'N/A')

    with st.container(border=True):
        col_title, col_badge = st.columns([4, 1])
        with col_title:
            st.subheader(f"Patent {rank}: {title}")
            st.markdown(f"**Application Number (Official ID):** `{app_num}`")
        with col_badge:
            st.caption("Official Indian Patent")
            badge_color = "green" if "High" in match_label else ("blue" if "Moderate" in match_label else "gray")
            if hasattr(st, "badge"):
                st.badge(match_label, color=badge_color)
            else:
                st.markdown(f":{badge_color}-background[ **{match_label}** ]")

        st.divider()

        grid_col1, grid_col2 = st.columns(2)
        with grid_col1:
            st.markdown(f"**IPO Jurisdiction:** {ipo_loc}")
            st.markdown(f"**Patent Journal Issue:** {pub_num}")
            st.markdown(f"**Publication Date:** {pub_date}")
            st.markdown(f"**Application Type:** {app_type}")
        with grid_col2:
            st.markdown(f"**Field of Invention:** {field}")
            st.markdown(f"**Number of Claims:** {claims}")
            st.markdown(f"**Number of Pages:** {pages}")


def render_hero_banner():
    """
    Renders clean, minimal hero banner displaying only '🧠 AI Novelty Analyzer'.
    Matches Enterprise Midnight Blue theme with cyan accent and Inter typography.
    """
    st.markdown("""
    <div class="hero-banner">
        <span class="hero-icon">🧠</span>
        <div class="hero-title">
            <span class="brand-ai" style="color: #F8FAFC;">AI</span> <span class="brand-name" style="color: #F8FAFC;">Novelty Analyzer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_dataset_overview_card(total_patents: int = 458724, fields_count: int = 16):
    """Renders dataset overview panel at top of UI."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Patent Database", f"{total_patents:,}")
    with c2:
        st.metric("Technical Fields", f"{fields_count}")
    with c3:
        st.metric("IPO Jurisdictions", "Mumbai, Delhi, Chennai, Kolkata")
    with c4:
        st.metric("Search Source", "Official Indian Patent Office")


def render_search_stats_panel(stats_dict: dict):
    """
    Renders real-time Search Statistics Panel with 4 metrics:
    - Patent Database
    - Detected Technical Domain
    - Top Candidates Retrieved (200)
    - Search Runtime
    """
    if not stats_dict:
        return
    st.markdown('<div class="section-title">📊 Search Statistics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Patent Database", "458,724")
    with c2:
        st.metric("Detected Technical Domain", stats_dict.get("detected_field", "Applied Engineering & Automation"))
    with c3:
        st.metric("Top Candidates Retrieved (200)", "200")
    with c4:
        st.metric("Search Runtime", f"{stats_dict.get('search_time_sec', 0.0):.2f} s")


def render_disclaimer_box():
    """Renders mandatory project disclaimer box."""
    st.markdown(f"""
    <div class="disclaimer-box">
        <b>Disclaimer:</b> {NOVELTY_INDEX_DISCLAIMER}
    </div>
    """, unsafe_allow_html=True)

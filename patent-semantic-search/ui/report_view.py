"""
Report View Component — SaaS Dashboard with Horizontal Tabs.
Renders AI analysis results across 6 dashboard tabs:
  Overview | Patent Matches | Feature Matrix | Landscape | Innovation | Methodology
The PDF retains formal 12-section structure independently.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    render_native_patent_card,
    render_patent_card_html,
    render_disclaimer_box
)
from reports.pdf_generator import PDFReportGenerator


def render_report_view(report_data: dict):
    """
    Renders the SaaS dashboard with horizontal tab navigation.
    Tabs: Overview, Patent Matches, Feature Matrix, Landscape, Innovation, Methodology.
    """
    pdf_gen = PDFReportGenerator()
    _ensure_concept_enhancement(report_data)

    idx_data = report_data.get("novelty_index_data", {})
    novelty_score = idx_data.get("novelty_index", 0.0)
    potential_label = idx_data.get("potential_label", "N/A")
    status_color = idx_data.get("status_color", "#2563EB")

    patents = report_data.get("retrieved_patents", [])

    st.markdown("---")

    # ==========================================
    # HORIZONTAL DASHBOARD TABS
    # ==========================================
    tab_overview, tab_patents, tab_matrix, tab_landscape, tab_innovation, tab_methodology = st.tabs([
        "📊 Overview",
        "Patent Matches",
        "🧩 Feature Matrix",
        "🌐 Landscape",
        "💡 Innovation",
        "📄 Methodology"
    ])

    # ==========================================
    # TAB 1: OVERVIEW
    # ==========================================
    with tab_overview:
        # AI Novelty Index Card
        st.markdown(f"""
        <div class="novelty-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="color: #94A3B8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;">
                        AI Novelty Index
                    </div>
                    <div class="novelty-score-large" style="color: {status_color};">
                        {novelty_score}<span style="font-size: 1.8rem; font-weight: 700; color: #94A3B8;">/100</span>
                    </div>
                    <div class="novelty-label" style="color: {status_color};">
                        {potential_label}
                    </div>
                </div>
                <div style="text-align: right; color: #94A3B8; font-size: 0.85rem; line-height: 1.6;">
                    <span style="color: #CBD5E1; font-weight: 600;">Dataset:</span> Official Indian Patent Office<br/>
                    <span style="color: #CBD5E1; font-weight: 600;">Screened Records:</span> {report_data.get('total_screened', len(patents)):,}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Executive Summary
        from llm.novelty_report import polish_executive_summary_flow
        raw_exec_summary = report_data.get("executive_summary", "Assessment summary generated based on official Indian patent prior art records.")
        exec_summary_text = polish_executive_summary_flow(raw_exec_summary)
        st.markdown(f"""
        <div class="exec-summary-card">
            <div style="font-weight: 700; color: #38BDF8; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                Executive Summary
            </div>
            <div>{exec_summary_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # Download PDF Button
        try:
            pdf_bytes = pdf_gen.generate_pdf_bytes(report_data)
            col_btn, _ = st.columns([1, 2])
            with col_btn:
                st.download_button(
                    label="📥 Download Professional PDF Report",
                    data=pdf_bytes,
                    file_name="Patent_Novelty_Assessment_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
        except Exception as e:
            st.warning(f"PDF compilation notice: {e}")

    # ==========================================
    # TAB 2: PATENT MATCHES
    # ==========================================
    with tab_patents:
        st.caption("Closest prior art records from the official Indian Patent Office dataset.")
        for idx, p in enumerate(patents[:5], start=1):
            render_native_patent_card(p, rank=idx)

    # ==========================================
    # TAB 3: FEATURE MATRIX
    # ==========================================
    with tab_matrix:
        st.markdown("Proposed invention features evaluated against closest retrieved prior art.")

        rubric_rows = report_data.get("feature_rubric", [])
        if rubric_rows:
            matrix_data = []
            for r in rubric_rows:
                status = r.get("prior_art_status") or ("Shared" if str(r.get("exists_in_prior_art", "")).lower() == "yes" else "Strong Difference")
                matrix_data.append({
                    "Feature": r.get("feature", "Technical Feature"),
                    "Prior-Art Status": status,
                    "Observation": r.get("observation", "")
                })
            st.table(pd.DataFrame(matrix_data))
        else:
            st.info("Feature rubric data unavailable for this query.")

    # ==========================================
    # TAB 4: LANDSCAPE (Qualitative Assessment, No Repeated Metrics)
    # ==========================================
    with tab_landscape:
        stats_dict = st.session_state.get("search_stats") or {}
        detected_domain = report_data.get("detected_field") or stats_dict.get("detected_field") or "Applied Engineering & Automation"

        # Technology Maturity
        tech_maturity = report_data.get("technology_maturity") or (
            f"The official patent landscape within {detected_domain} demonstrates an established foundation of baseline operational mechanisms, "
            f"with growing patent velocity toward integrated, intelligent automation and edge-compute architectures."
        )
        st.markdown(f"""
        <div class="landscape-block">
            <div class="landscape-block-label">Technology Maturity</div>
            {tech_maturity}
        </div>
        """, unsafe_allow_html=True)

        # Competition Overview
        competition_text = report_data.get("competition_overview") or (
            f"Prior art distribution in {detected_domain} exhibits moderate clustering around standard mechanical and electronic interfaces. "
            f"The top 5 retrieved patents represent the closest semantic prior art, indicating that competing solutions focus on modular sub-assemblies."
        )
        st.markdown(f"""
        <div class="landscape-block">
            <div class="landscape-block-label">Competition Overview</div>
            {competition_text}
        </div>
        """, unsafe_allow_html=True)

        # White-Space Opportunity
        white_space_text = report_data.get("white_space_opportunity") or (
            f"Strategic analysis identifies actionable white-space opportunities within {detected_domain}. "
            f"Features classified under Strong Difference in the comparative matrix represent "
            f"defensible technological positions where the proposed invention diverges meaningfully from existing prior art."
        )
        st.markdown(f"""
        <div class="landscape-block">
            <div class="landscape-block-label">White-Space Opportunity</div>
            {white_space_text}
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # TAB 5: INNOVATION
    # ==========================================
    with tab_innovation:
        concept_data = report_data.get("concept_enhancement") or {}
        tech_concept = concept_data.get("technical_concept") or {}
        detected_domain_inn = report_data.get("detected_field") or (st.session_state.get("search_stats") or {}).get("detected_field") or "Applied Engineering & Automation"

        # Extract Technology Focus
        core_principles = tech_concept.get("core_principle") or []
        if isinstance(core_principles, list) and core_principles:
            tech_focus = core_principles[0]
        elif isinstance(core_principles, str) and core_principles.strip():
            tech_focus = core_principles.strip().split("\n\n")[0]
        else:
            tech_focus = f"Edge-native execution and deterministic signal conditioning tailored for {detected_domain_inn} applications."

        # Extract Recommended Hardware
        key_modules = tech_concept.get("key_modules") or concept_data.get("hardware_components") or []
        if key_modules and isinstance(key_modules, list):
            hw_items = [f"**{m.get('module') or m.get('component', 'Module')}:** {m.get('purpose', '')}" for m in key_modules[:3]]
            hw_display = " · ".join(hw_items)
        else:
            hw_display = "Microcontroller processing unit, high-precision acquisition transceivers, and dedicated power management ICs."

        # Extract One Innovation Opportunity
        expansions = concept_data.get("innovation_expansion") or []
        if expansions and isinstance(expansions, list):
            first_opp = expansions[0]
            opp_title = first_opp.get("enhancement", "Advanced Synergistic Subsystem")
            opp_desc = first_opp.get("technical_implementation", "")
            opp_display = f"**{opp_title}:** {opp_desc}"
        else:
            opp_raw = report_data.get("innovation_opportunities", "")
            opp_display = opp_raw.split("\n")[0] if opp_raw else "Implement adaptive calibration algorithms for deterministic edge latency reduction."

        st.markdown(f"""
        <div class="assistant-card">
            <div class="assistant-item">
                <div class="assistant-label">Technology Focus</div>
                <div class="assistant-value">{tech_focus}</div>
            </div>
            <div class="assistant-item">
                <div class="assistant-label">Recommended Hardware</div>
                <div class="assistant-value">{hw_display}</div>
            </div>
            <div class="assistant-item" style="margin-bottom: 0;">
                <div class="assistant-label">Innovation Opportunity</div>
                <div class="assistant-value">{opp_display}</div>
            </div>
            <div class="assistant-footer-note">
                Detailed implementation guidance, system architecture, recommended technologies, innovation opportunities, and commercialization analysis are available in the Professional PDF Report.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # TAB 6: METHODOLOGY
    # ==========================================
    with tab_methodology:
        st.markdown("""
        **Analytical Methodology**

        The AI Novelty Analyzer uses a multi-stage assessment pipeline:

        1. **Dense Vector Representation** — Continuous dense semantic vectors are generated locally using the Stella-en-400M-v5 model.
        2. **FAISS Candidate Retrieval** — Global IndexFlatIP retrieves the top 200 candidates using inner-product cosine similarity over official IPO records.
        3. **Dynamic Technical Differentiation** — Comparative rubric evaluates proposed functional features directly against closest retrieved prior art.
        4. **AI Novelty Assessment** — The internal novelty calculation synthesizes multiple dimensions to produce the AI Novelty Index score.
        """)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        render_disclaimer_box()


def _ensure_concept_enhancement(report_data: dict) -> None:
    """Ensures concept enhancement payload is populated for PDF rendering and UI assistant."""
    existing = report_data.get("concept_enhancement") or {}
    if existing.get("technical_concept") and existing.get("system_architecture"):
        return
    from llm.novelty_report import NoveltyReportGenerator
    from llm.concept_enhancement import ConceptEnhancementGenerator

    title, description = NoveltyReportGenerator._resolve_title_description(
        report_data.get("user_idea", ""),
        report_data.get("invention_title", ""),
        report_data.get("invention_description", ""),
    )
    report_data["invention_title"] = title
    report_data["invention_description"] = description
    report_data["concept_enhancement"] = ConceptEnhancementGenerator().generate(
        invention_title=title,
        invention_description=description,
        retrieved_patents=report_data.get("retrieved_patents") or [],
    )

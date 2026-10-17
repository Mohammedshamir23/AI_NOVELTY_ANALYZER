"""
Dashboard View module for AI Novelty Analyzer.
Displays real-time performance metrics, vector dimensions, search statistics, and Indian Patent Office architecture.
"""

import streamlit as st

def render_dashboard(search_engine):
    """
    Renders system analytics dashboard.
    """
    total_patents = getattr(search_engine, 'total_patents', 458724)
    vector_dim = search_engine.generator.vector_dim if search_engine and hasattr(search_engine, 'generator') else 1024
    index_loaded = False
    if search_engine:
        if hasattr(search_engine, 'index') and search_engine.index is not None:
            index_loaded = True
        elif hasattr(search_engine, 'faiss_manager') and search_engine.faiss_manager and search_engine.faiss_manager.index is not None:
            index_loaded = True

    st.markdown("""
    <div class="header-card">
        <div class="header-title">📊 System Analytics & Metrics</div>
        <div class="header-subtitle">Real-Time Patent Corpus & Vector Search Infrastructure</div>
    </div>
    """, unsafe_allow_html=True)


    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Master Corpus Patents", f"{total_patents:,}")
    with c2:
        st.metric("Vector Dimensions", f"{vector_dim}D")
    with c3:
        st.metric("FAISS Index Status", "Active" if index_loaded else "Pending Build")
    with c4:
        st.metric("Candidate Fields", "16 Fields")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Pipeline Architecture Specs</div>', unsafe_allow_html=True)

    st.markdown("""
    The **AI Novelty Analyzer** executes high-performance semantic retrieval:

    * **Patent Corpus Dataset:** Master publication records (~458,724 records) preprocessed for semantic search.
    * **Candidate Pre-Filtering:** Keyword-based classification mapping across 16 technical fields.
    * **Dense Vector Backbone:** `dunzhang/stella_en_400M_v5` continuous 1024-dimensional dense vector space model.
    * **Global Vector Index:** Global FAISS `IndexFlatIP` (Inner-Product L2 Normalized Cosine Search).
    * **Novelty Evaluation Engine:** AI Novelty Index combining Weighted Top-5 Semantic Uniqueness (50%), Feature Uniqueness Rubric (30%), and Prior-Art Density (20%).
    * **LLM Synthesis:** Gemini API / Deterministic Domain Engine generating executive summaries, feature matrices, innovation opportunities, and filing recommendations.
    """)


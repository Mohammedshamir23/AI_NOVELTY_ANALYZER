# AI Novelty Analyzer 🧠

> **Tagline:** Intelligent Patent Similarity Detection and Innovation Analysis

A complete, production-ready patent-analysis platform that combines dense vector semantic search, live patent API retrieval, claim-by-claim LLM comparison, feature extraction, downloadable PDF reports, and actionable innovation suggestions.

---

## 🌟 Architecture & Key Features

1. **Phase 1 – Core Retrieval (Preserved)**
   - **Stella-en-400M-v5** embedding backbone model.
   - **FAISS IndexFlatIP** vector index (inner product on normalized vectors for exact Cosine Similarity).
   - Interactive patent cards with expandable claim viewers.

2. **Phase 2 – Real-Time Patent Search**
   - Live **USPTO Open Data API** integration.
   - Sidebar Search Source selector: `Local Dataset`, `USPTO Live`, or `Hybrid`.
   - In-memory temporary FAISS search indexes for live patent retrieval.
   - Intelligent response caching.

3. **Phase 3 – AI Novelty Report**
   - Powered by **Gemini 2.5 Flash** (with fallback synthesis).
   - Generates Executive Summary, Overall Novelty Status, Filing Recommendation, and Match Scores.

4. **Phase 4 – Claim-by-Claim Comparison**
   - Expandable alignment matrix matching user invention features against prior art claims (`✅ Match` / `❌ Different`).

5. **Phase 5 – Intelligent Feature Extraction**
   - Automatic extraction of shared **Common Features** and **Potentially Unique Features**.
   - Displayed as modern, color-coded tag badges.

6. **Phase 6 – Global Patent Search**
   - Architecture supporting USPTO, WIPO, EPO, and Google Patents imports.
   - Global search filters: Jurisdiction/Country, CPC Classification, and Inventor/Assignee.

7. **Phase 7 – Downloadable PDF Report**
   - Built with **ReportLab**.
   - Professional PDF exports including metrics, novelty analysis, claim comparison tables, and top prior art patents.

8. **Phase 8 – Innovation Suggestion Engine**
   - Actionable technical suggestions to enhance novelty (e.g. *Consider integrating adaptive muscle prediction or energy-efficient sensing to improve novelty*).
   - Strictly engineered to provide technical guidance without claiming legal patent approval.

---

## 📁 Project Folder Structure

```
AI-Novelty-Analyzer/
│
├── app.py                      # Main Streamlit entry point
├── ui/
│   ├── app.py                  # Backward-compatible UI entry point
│   ├── dashboard.py            # Analytics & performance dashboard
│   ├── report_view.py          # AI Novelty Report rendering view
│   └── components.py           # Custom SaaS Dark Theme & tag components
│
├── preprocessing/
│   ├── clean_text.py           # Text normalization utilities
│   └── parser.py               # Dataset parsing & loading
│
├── embeddings/
│   ├── generate_embeddings.py  # Core vector embedding generator
│   ├── stella_model.py         # Stella-en-400M-v5 model wrapper
│   └── embedding_cache.py      # Persistence manager (.npy / .pkl)
│
├── search/
│   ├── faiss_index.py          # Persistent FAISS IndexFlatIP manager
│   ├── faiss_search.py         # Temporary in-memory FAISS builder
│   ├── semantic_search.py      # Core search coordinator
│   └── similarity.py           # Cosine Similarity & Match Score logic
│
├── services/
│   ├── uspto_api.py            # USPTO Open Data API client
│   ├── patent_formatter.py     # Standard patent record schema
│   └── cache.py                # JSON response cache
│
├── llm/
│   ├── novelty_report.py       # AI Novelty Report generator
│   ├── claim_comparison.py     # LLM Claim alignment module
│   └── feature_extractor.py    # Common & Unique feature tagger
│
├── reports/
│   └── pdf_generator.py        # ReportLab PDF report builder
│
├── history/
│   └── search_history.py       # JSON search history manager
│
├── data/                       # Cached embeddings & search history
├── .env                        # Environment variables & API keys
├── requirements.txt            # System dependencies
└── README.md                   # Project documentation
```

---

## 📐 Match Score & Novelty Classification

### Match Score Formula
$$\text{Match Score} = \text{Cosine Similarity} \times 100$$

### Score Color Matrix
| Match Score Range | Badge Color | Interpretation |
|---|---|---|
| **90 – 100** | 🔴 Red | Very High Similarity (Close Prior Art) |
| **75 – 89** | 🟠 Orange | High Similarity (Overlapping Concepts) |
| **60 – 74** | 🟡 Yellow | Moderate Similarity (Domain Overlap) |
| **Below 60** | 🟢 Green | High Novelty Potential |

### Novelty Classification
| Highest Match Score | Novelty Status |
|---|---|
| **90 – 100** | Very High Similarity |
| **75 – 89** | High Similarity |
| **60 – 74** | Moderate Similarity |
| **Below 60** | High Novelty Potential |

---

## 🚀 Installation & Setup

1. **Clone Repository & Navigate to Directory**
   ```bash
   git clone <repository_url>
   cd patent-semantic-search
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```env
   USPTO_API_KEY=your_uspto_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Launch Streamlit Web Application**
   ```bash
   streamlit run app.py
   ```

---

## 🔮 Future Scalability
- Integration with official WIPO and EPO REST APIs.
- Automated claim tree extraction and dependency graphing.
- Distributed FAISS vector search across millions of patent records.

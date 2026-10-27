# 🧠 AI Novelty Analyzer

### AI-Powered Patent Search, Similarity Analysis & Preliminary Novelty Assessment

AI Novelty Analyzer is an AI-powered application designed to help researchers, students, and innovators evaluate proposed inventions by identifying semantically similar patents, comparing technical features, and generating structured patent assessment reports.

The system combines **Natural Language Processing (NLP), semantic embeddings, FAISS vector search, and Generative AI** to analyze invention descriptions against an Indian patent dataset and produce an AI Novelty Index with supporting technical analysis.

> **Disclaimer:** The AI Novelty Index is a project-defined analytical metric for preliminary prior-art assessment. It is not an official patentability score or a legal determination issued by the Indian Patent Office.

---

## 🚀 Key Features

- **Semantic Patent Search:** Retrieves relevant patents based on the meaning and technical context of an invention description, rather than relying only on exact keyword matches.
- **AI Novelty Assessment:** Generates a project-defined novelty score out of 100 with a qualitative classification.
- **Comparative Feature Matrix:** Compares technical features of the proposed invention with retrieved prior art.
- **Top 5 Similar Patents:** Displays relevant patent records with available metadata, including application number, publication date, patent journal issue, application type, field of invention, claims, and pages.
- **Technical Domain Detection:** Identifies a relevant technical domain based on the submitted invention.
- **Patent Landscape Analysis:** Provides a qualitative overview of technology maturity, competition, and potential innovation opportunities.
- **AI-Generated Executive Summary:** Summarizes the invention, related prior art, and potential technical differences.
- **Innovation Recommendations:** Generates potential technical improvements and development suggestions relevant to the proposed invention.
- **Professional PDF Reports:** Exports structured assessment reports containing patent matches, technical comparisons, methodology, innovation opportunities, and disclaimers.
- **Interactive Dashboard:** Provides a streamlined interface for submitting inventions and reviewing assessment results.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive web interface |
| Stella Embeddings (`stella-en-400M-v5`) | Semantic representation of patent and invention text |
| FAISS | Efficient vector similarity search |
| Google Gemini API | Generative AI analysis and report synthesis |
| Pandas | Patent dataset processing and manipulation |
| NumPy | Numerical and vector operations |
| ReportLab | PDF report generation |

## 🏗️ System Architecture

The application follows a semantic retrieval and AI-assisted analysis pipeline.

```text
              User Input
                  |
                  v
       Invention Title & Description
                  |
                  v
        Text Processing / Preparation
                  |
                  v
       Stella Semantic Embeddings
                  |
                  v
          FAISS Vector Search
                  |
                  v
       Retrieve Relevant Patents
                  |
                  v
      Technical Feature Comparison
                  |
                  v
       Gemini AI Content Generation
                  |
                  v
         AI Novelty Assessment
                  |
                  v
       Interactive Results Dashboard
                  |
                  v
       Professional PDF Report
```

### Workflow

1. **Input:** The user submits an invention title and technical description.
2. **Text Representation:** The application converts the invention text into semantic vectors using the Stella embedding model.
3. **Patent Retrieval:** FAISS searches the patent vector index to retrieve relevant candidate records.
4. **Technical Comparison:** The system compares the submitted invention with retrieved patents and generates a comparative feature matrix.
5. **AI Analysis:** Gemini generates the executive summary, qualitative assessment, patent landscape observations, and innovation recommendations.
6. **Report Generation:** The application presents the results in the dashboard and generates a downloadable PDF report.

## 📊 AI Novelty Index

The application produces an AI Novelty Index on a scale of 0–100.

| Score Range | Classification |
|---|---|
| 80–100 | Strong Originality |
| 60–79.99 | Moderate Originality |
| 40–59.99 | Limited Originality |
| Below 40 | Significant Prior Art Overlap |

The index is a project-defined analytical metric. It should be interpreted alongside the retrieved patents and technical comparisons, not as a guarantee that an invention is patentable.

## 🧩 Comparative Feature Matrix

The feature matrix presents a structured comparison between the proposed invention and relevant prior art.

| Component | Description |
|---|---|
| Feature | Technical concept identified in the invention |
| Prior-Art Status | Indicates the assessed relationship with retrieved prior art |
| Observation | Explains the similarities, differences, or available evidence |

Feature extraction and observations should be grounded in the submitted invention and retrieved patent records. AI-generated differences do not, by themselves, establish legal novelty or inventiveness.

## 📄 Generated PDF Report

The professional report is organized into the following sections:

1. AI Novelty Assessment
2. Executive Summary
3. Proposed Invention
4. Search Summary
5. Why This Score Was Given
6. Top Similar Patents
7. Comparative Technical Analysis
8. Patent Landscape Analysis
9. Innovation Opportunities and Technical Specifications
10. Filing Recommendation
11. Analytical Methodology
12. Regulatory Disclaimer

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the project's dependencies
- Git
- A Google Gemini API key
- Access to the project's patent dataset and compatible FAISS index

### 1. Clone the Repository

```bash
git clone https://github.com/Mohammedshamir23/Novelty-Analyzer.git
cd Novelty-Analyzer
```

### 2. Create a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

If the repository contains `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

If it does not, install the dependencies specified by the project configuration before proceeding.

### 4. Configure API Credentials

Set up your Gemini API key using the environment variable expected by your application.

For example, if the code reads `GEMINI_API_KEY`:

**PowerShell:**

```powershell
$env:GEMINI_API_KEY = "your_api_key_here"
```

Alternatively, use the environment configuration mechanism supported by the project. Never commit API keys or other secrets to GitHub.

### 5. Prepare the Patent Dataset and Index

Ensure the required patent dataset, embedding model, and FAISS index are available at the locations configured by the application.

Large datasets and index files may need to be downloaded or generated separately if they are not included in the repository.

### 6. Run the Application

If `app.py` is the Streamlit entry point:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal to access the application.

*Note: Verify the actual dependency versions, API variable names, dataset paths, and startup instructions against the repository before following these steps.*

## 📁 Project Structure

The project is organized into modules for search, AI analysis, interface rendering, preprocessing, and report generation.

```text
Novelty-Analyzer/
├── app.py
├── search/
│   ├── semantic_search.py
│   └── similarity.py
├── preprocessing/
│   └── clean_text.py
├── llm/
│   ├── feature_extractor.py
│   └── novelty_report.py
├── ui/
│   ├── components.py
│   └── report_view.py
├── reports/
│   └── pdf_generator.py
├── requirements.txt
├── README.md
└── .gitignore
```

*This is a representative structure based on the project's modules; retain the actual filenames and folders present in your repository.*

## 🔍 Example Use Case

**Input invention:** AI-Based Smart Water Leakage Detection and Pipeline Monitoring System

**Description:** A pipeline monitoring system that uses pressure sensors, acoustic sensors, edge AI, Raspberry Pi processing, IoT alerts, and GPS-based mapping to detect and locate water leaks.

The application can use this input to:

- Retrieve patents related to pipeline leakage and water monitoring.
- Compare the invention's stated technical components against retrieved patent records.
- Generate an AI Novelty Index and qualitative assessment.
- Summarize similarities and potential technical differences.
- Suggest further development opportunities within the invention's technical scope.
- Generate a structured PDF assessment report.

Results depend on the dataset, retrieval quality, and AI-generated analysis. They require independent verification.

## 🔐 Security and Data Handling

- Store API keys in environment variables or an appropriate secrets manager.
- Never upload credentials, private keys, or `.env` files to a public repository.
- Follow the dataset's licensing and usage conditions.
- Avoid committing unnecessary large datasets, generated reports, model weights, or vector index files.
- Review `.gitignore` before publishing the repository.

## ⚠️ Limitations

- Retrieval quality depends on the completeness and quality of the available patent dataset and vector index.
- Semantic similarity does not establish that two inventions are legally equivalent.
- AI-generated feature comparisons and recommendations may contain errors and require human verification.
- The AI Novelty Index is not an official patentability determination.
- Patentability depends on applicable law, prior-art examination, claim scope, and other factors that this tool does not conclusively determine.

## 🔮 Future Enhancements

- Improved evidence-grounded technical feature extraction.
- More reliable technical domain classification.
- Patent citation and source verification.
- Enhanced prior-art comparison and claim-level analysis.
- Expanded visualization of patent relationships and technology trends.
- Automated evaluation of generated report accuracy.
- Deployment as a cloud-hosted application.

## 🎓 Project Information

**Project Name:** AI Novelty Analyzer

**Category:** Artificial Intelligence, Natural Language Processing, Semantic Search, and Generative AI

**Repository:** [Mohammedshamir23/Novelty-Analyzer](https://github.com/Mohammedshamir23/Novelty-Analyzer)

## 📜 Disclaimer

AI Novelty Analyzer is intended for educational, research, and preliminary patent-search assistance. It does not replace a professional patent search, legal advice, or an examination by the relevant patent office. Users should independently verify patent records and consult a qualified patent professional before making filing decisions.

---

**Built to explore how semantic search and generative AI can support preliminary patent research and technical innovation assessment.**

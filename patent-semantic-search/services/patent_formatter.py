"""
Standardized Patent Record Formatter for Local, USPTO, and External APIs.
"""

from typing import Dict, Any

def format_patent_record(
    patent_id: str,
    title: str,
    abstract: str,
    claims: str = "",
    cpc_code: str = "N/A",
    issue_date: str = "N/A",
    assignee: str = "N/A",
    inventor: str = "N/A",
    country: str = "US",
    source: str = "Local Dataset"
) -> Dict[str, Any]:
    """
    Normalizes patent record key names across all sources.
    """
    return {
        "patent_id": str(patent_id).strip(),
        "title": str(title).strip() or "Untitled Patent",
        "abstract": str(abstract).strip() or "Abstract unavailable.",
        "claims": str(claims).strip() or "Claims unavailable.",
        "cpc_code": str(cpc_code).strip() or "N/A",
        "issue_date": str(issue_date).strip() or "N/A",
        "assignee": str(assignee).strip() or "N/A",
        "inventor": str(inventor).strip() or "N/A",
        "country": str(country).strip().upper() or "US",
        "source": str(source).strip()
    }

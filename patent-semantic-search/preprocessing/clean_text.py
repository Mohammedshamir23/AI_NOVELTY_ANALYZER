"""
Text cleaning and normalization utilities for official Indian patent analysis.
Strictly preserves technical terms, hyphens, alphanumeric symbols, and abbreviations.
"""

import re

def clean_patent_text(text: str) -> str:
    """
    Clean raw patent text by normalizing whitespaces, stripping corrupted replacement chars,
    and removing HTML tags while preserving technical terms, hyphens, and abbreviations.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace common corrupted Windows-1252 / UTF-8 encoding replacement symbols
    # e.g., unicode replacement char \ufffd or weird byte sequences
    text = text.replace('\ufffd', '')
    text = re.sub(r'[â€œâ€â€˜â€™â€•]', ' ', text)
    
    # Remove non-printable control characters except standard punctuation and whitespace
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Collapse multiple spaces while preserving hyphens and technical symbols
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def preprocess_search_text(title: str, field: str, app_type: str, location: str) -> str:
    """
    Formats official Indian patent metadata into an enriched, cohesive sentence for Stella embedding generation.
    Combines TITLE_OF_INVENTION, FIELD_OF_INVENTION, APPLICATION_TYPE_DESC, and IPO_LOCATION.
    """
    c_title = clean_patent_text(title)
    c_field = clean_patent_text(field) or "General Technology"
    c_app_type = clean_patent_text(app_type) or "Ordinary Application"
    c_location = clean_patent_text(location) or "Indian Patent Office"
    
    if c_title and not c_title.endswith("."):
        c_title += "."
        
    return (
        f"Invention Title: {c_title} "
        f"Technical Field: {c_field}. "
        f"Patent Application Type: {c_app_type}. "
        f"Registered at Patent Office: {c_location}."
    )

def format_application_number(value) -> str:
    """
    Ensures Application Number is stored and rendered as a full, clean integer string.
    Converts scientific notation (e.g., '2.02E+11', '2.03E+11') back to full integer string.
    Never returns floats or scientific notation strings.
    """
    if value is None:
        return "N/A"
    val_str = str(value).strip()
    if not val_str or val_str.upper() in ["NAN", "NONE", "N/A"]:
        return "N/A"
    
    if "E+" in val_str.upper() or "E-" in val_str.upper():
        try:
            return f"{int(float(val_str))}"
        except (ValueError, OverflowError):
            return val_str
            
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
        
    # Remove leading IN prefix (e.g., IN-, IN/, IN , or IN followed by digits)
    if val_str.upper().startswith("IN-") or val_str.upper().startswith("IN/") or val_str.upper().startswith("IN "):
        val_str = val_str[3:].strip()
    elif val_str.upper().startswith("IN") and len(val_str) > 2 and (val_str[2].isdigit() or val_str[2] in ["-", "/", "_"]):
        val_str = val_str[2:].lstrip("-_/ ")
        
    return val_str



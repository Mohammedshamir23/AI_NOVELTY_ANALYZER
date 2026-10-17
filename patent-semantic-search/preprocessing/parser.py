"""
Official Indian Patent Dataset Loader and Parser Module.
Loads data/processed/indian_patents_master.csv and preserves official Indian patent metadata.
"""

import os
import pandas as pd
from typing import Optional
from preprocessing.clean_text import clean_patent_text, format_application_number

DEFAULT_MASTER_PATH = "data/processed/indian_patents_master.csv"

def load_patent_csv(csv_path: str = DEFAULT_MASTER_PATH) -> pd.DataFrame:
    """
    Safely loads official Indian patent master CSV dataset into a standardized pandas DataFrame.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Master Indian patent dataset not found at: {csv_path}. Run preprocessing/merge_indian_patents.py first.")
        
    df = pd.read_csv(
        csv_path,
        dtype={
            "APPLICATION_NUMBER": str,
            "PUBLICATION_NUMBER": str,
            "NO_OF_PAGES": str,
            "NO_OF_CLAIMS": str
        },
        encoding_errors="replace"
    )
    
    # Required official Indian patent columns
    required_cols = [
        'TITLE_OF_INVENTION',
        'APPLICATION_NUMBER',
        'PUBLICATION_NUMBER',
        'PUBLICATION_DATE',
        'IPO_LOCATION',
        'APPLICATION_TYPE_DESC',
        'FIELD_OF_INVENTION',
        'NO_OF_PAGES',
        'NO_OF_CLAIMS',
        'SEARCH_TEXT'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = "N/A"

    # Fill NaNs and ensure string dtypes
    for col in required_cols:
        df[col] = df[col].fillna("N/A").astype(str).apply(clean_patent_text)

    if "APPLICATION_NUMBER" in df.columns:
        df["APPLICATION_NUMBER"] = df["APPLICATION_NUMBER"].apply(format_application_number)

    return df[required_cols]

class PatentParser:
    """
    Parser wrapper class for Indian patent metadata loading.
    """
    def load_patents_from_csv(self, csv_path: str = DEFAULT_MASTER_PATH) -> pd.DataFrame:
        return load_patent_csv(csv_path)


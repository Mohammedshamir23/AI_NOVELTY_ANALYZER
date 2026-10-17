"""
Preprocessing pipeline module to load, merge, clean, and deduplicate official Indian Patent Office (IPO) CSV files.
Generates data/processed/indian_patents_master.csv and data/processed/preprocessing_log.json.
"""

import os
import glob
import json
import datetime
import pandas as pd
from typing import Dict, Any
from preprocessing.clean_text import clean_patent_text, format_application_number

def clean_inline_text(val: str) -> str:
    """Basic inline text cleanup helper for string columns."""
    if not isinstance(val, str) or pd.isna(val):
        return "N/A"
    cleaned = val.strip()
    return cleaned if cleaned else "N/A"

def merge_indian_patents(
    raw_dir: str = "data/raw",
    output_csv_path: str = "data/processed/indian_patents_master.csv",
    log_json_path: str = "data/processed/preprocessing_log.json"
) -> Dict[str, Any]:
    """
    Loads all CSV files from raw_dir, merges them incrementally, cleans formatting,
    deduplicates on APPLICATION_NUMBER + TITLE_OF_INVENTION, constructs SEARCH_TEXT,
    and exports master CSV and preprocessing log.
    """
    print("=" * 60)
    print("Starting Official Indian Patent Office Data Preprocessing Pipeline")
    print("=" * 60)

    # 1. Locate all CSV files in raw_dir
    csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No raw CSV files found in directory '{raw_dir}'.")

    print(f"Found {len(csv_files)} CSV files in '{raw_dir}'. Loading incrementally...")

    processed_dfs = []
    total_rows_before = 0

    # 2. Process each CSV file incrementally for memory efficiency
    for file_idx, csv_path in enumerate(csv_files, start=1):
        filename = os.path.basename(csv_path)
        print(f"[{file_idx}/{len(csv_files)}] Reading file: {filename}...")
        
        # Read with string dtypes for patent numbers and safe encoding replacement
        df_chunk = pd.read_csv(
            csv_path,
            dtype={
                "APPLICATION_NUMBER": str,
                "PUBLICATION_NUMBER": str,
                "NO_OF_PAGES": str,
                "NO_OF_CLAIMS": str
            },
            encoding_errors="replace"
        )
        
        rows_in_chunk = len(df_chunk)
        total_rows_before += rows_in_chunk
        print(f"   -> Loaded {rows_in_chunk:,} rows from {filename}")
        
        processed_dfs.append(df_chunk)

    # Combine dataframes
    merged_df = pd.concat(processed_dfs, ignore_index=True)
    # 3. Clean string columns & handle missing values
    string_cols = [
        "PUBLICATION_NUMBER", "PUBLICATION_DATE", "IPO_LOCATION",
        "APPLICATION_TYPE_DESC", "APPLICATION_NUMBER", "DATE_OF_FILING",
        "TITLE_OF_INVENTION", "FIELD_OF_INVENTION", "NO_OF_PAGES", "NO_OF_CLAIMS"
    ]

    for col in string_cols:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].astype(str).apply(clean_inline_text)
        else:
            merged_df[col] = "N/A"

    if "APPLICATION_NUMBER" in merged_df.columns:
        merged_df["APPLICATION_NUMBER"] = merged_df["APPLICATION_NUMBER"].apply(format_application_number)

    # 4. Deduplicate using APPLICATION_NUMBER + TITLE_OF_INVENTION
    print("Deduplicating dataset using subset ['APPLICATION_NUMBER', 'TITLE_OF_INVENTION']...")
    dedup_df = merged_df.drop_duplicates(subset=["APPLICATION_NUMBER", "TITLE_OF_INVENTION"]).copy()
    
    total_rows_after = len(dedup_df)
    duplicates_removed = total_rows_before - total_rows_after
    print(f"Rows before cleaning : {total_rows_before:,}")
    print(f"Rows after cleaning  : {total_rows_after:,}")
    print(f"Duplicates removed   : {duplicates_removed:,}")

    # 5. Construct enriched SEARCH_TEXT column
    # Format: TITLE_OF_INVENTION. FIELD: FIELD_OF_INVENTION. APPLICATION TYPE: APPLICATION_TYPE_DESC. IPO LOCATION: IPO_LOCATION.
    print("\nConstructing enriched SEARCH_TEXT column for Stella embeddings...")
    
    def build_search_text(row):
        title = row["TITLE_OF_INVENTION"]
        field = row["FIELD_OF_INVENTION"]
        app_type = row["APPLICATION_TYPE_DESC"]
        location = row["IPO_LOCATION"]
        
        # Ensure title ends with period
        title_str = title.strip()
        if not title_str.endswith("."):
            title_str += "."
            
        return f"{title_str} FIELD: {field}. APPLICATION TYPE: {app_type}. IPO LOCATION: {location}."

    dedup_df["SEARCH_TEXT"] = dedup_df.apply(build_search_text, axis=1)

    # 6. Ensure output directory exists and save master CSV
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    
    print(f"Exporting master dataset to '{output_csv_path}'...")
    dedup_df.to_csv(output_csv_path, index=False, encoding="utf-8")
    print(f"Master CSV successfully exported! Size: {os.path.getsize(output_csv_path) / (1024*1024):.2f} MB")

    # 7. Generate and save preprocessing log JSON
    log_data = {
        "csv_files_loaded": len(csv_files),
        "file_names": [os.path.basename(f) for f in csv_files],
        "rows_before_cleaning": total_rows_before,
        "rows_after_cleaning": total_rows_after,
        "duplicates_removed": duplicates_removed,
        "generated_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    os.makedirs(os.path.dirname(os.path.abspath(log_json_path)), exist_ok=True)
    with open(log_json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)
        
    print(f"Saved preprocessing log to '{log_json_path}'.")
    print("=" * 60)
    print("Preprocessing completed successfully!")
    print("=" * 60)

    return log_data

if __name__ == "__main__":
    merge_indian_patents()

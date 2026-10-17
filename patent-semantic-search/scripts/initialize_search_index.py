"""
Standalone script to build initial FAISS index and patent metadata pickle.
Extracts representative patents from indian_patents_master.csv, generates Stella embeddings,
and builds data/processed/faiss_index.bin and data/processed/patent_metadata.pkl.
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from embeddings.generate_embeddings import StellaEmbeddingGenerator
from search.faiss_index import FAISSIndexManager

MASTER_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "indian_patents_master.csv")
INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "faiss_index.bin")
META_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "patent_metadata.pkl")

def initialize_index(sample_size: int = 5000):
    print(f"Loading master CSV from '{MASTER_CSV_PATH}'...")
    df = pd.read_csv(
        MASTER_CSV_PATH,
        dtype={
            "APPLICATION_NUMBER": str,
            "PUBLICATION_NUMBER": str,
            "NO_OF_PAGES": str,
            "NO_OF_CLAIMS": str
        },
        encoding_errors="replace"
    ).fillna("N/A")

    print(f"Total rows in master CSV: {len(df):,}")
    
    # Save full metadata pickle
    metadata_records = df.to_dict(orient="records")
    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata_records, f)
    print(f"Saved full metadata pickle to '{META_PATH}' ({len(metadata_records):,} records).")

    # Select representative subset for FAISS index build
    if len(df) > sample_size:
        # Sample across different FIELD_OF_INVENTION values for balanced coverage
        df_sample = df.groupby("FIELD_OF_INVENTION", group_keys=False).apply(
            lambda x: x.sample(min(len(x), sample_size // 16), random_state=42)
        )
        if len(df_sample) < sample_size:
            remaining = df.drop(df_sample.index).sample(sample_size - len(df_sample), random_state=42)
            df_sample = pd.concat([df_sample, remaining])
    else:
        df_sample = df

    df_sample = df_sample.reset_index(drop=True)
    print(f"Selected {len(df_sample):,} representative patents for vector index build.")

    search_texts = df_sample["SEARCH_TEXT"].tolist()
    
    print("Initializing Stella embedding generator...")
    generator = StellaEmbeddingGenerator()

    print(f"Encoding {len(search_texts):,} patent texts...")
    embeddings = generator.encode_texts(search_texts, batch_size=64, show_progress=True)
    print(f"Embeddings shape: {embeddings.shape}")

    # Build and save FAISS index
    manager = FAISSIndexManager(dimension=generator.vector_dim, index_file_path=INDEX_PATH)
    manager.build_index(embeddings)
    manager.save_index()

    # Save metadata pickle for indexed subset if needed or save indices mapping
    sample_records = df_sample.to_dict(orient="records")
    with open(META_PATH, "wb") as f:
        pickle.dump(sample_records, f)

    print("Index initialization complete! FAISS index and metadata are ready.")

if __name__ == "__main__":
    initialize_index()

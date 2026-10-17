"""
FAISS Index Manager for Fast Vector Similarity Search.

Features:
- Single global FAISS IndexFlatIP index across all ~458k normalized Stella embeddings.
- Saves binary index to data/processed/faiss_index.bin.
- Saves metadata dictionary/DataFrame to data/processed/patent_metadata.pkl.
"""

import os
import pickle
import faiss
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any

DEFAULT_INDEX_PATH = "data/processed/faiss_index.bin"
DEFAULT_META_PATH = "data/processed/patent_metadata.pkl"
EMBEDDINGS_PATH = "data/processed/embeddings.npy"
MASTER_CSV_PATH = "data/processed/indian_patents_master.csv"

class FAISSIndexManager:
    """
    Manages building, saving, loading, and searching the global FAISS vector index.
    """

    def __init__(self, dimension: int = 1024, index_file_path: str = DEFAULT_INDEX_PATH):
        self.dimension = dimension
        self.index_file_path = index_file_path
        # IndexFlatIP calculates inner product (cosine similarity on L2 normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)

    def normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """
        L2-normalizes vectors in-place / returns float32 matrix.
        """
        vecs = vectors.astype(np.float32).copy()
        faiss.normalize_L2(vecs)
        return vecs

    def build_index(self, embeddings: np.ndarray) -> None:
        """
        Builds FAISS IndexFlatIP index from document embedding matrix.
        """
        norm_vectors = self.normalize_vectors(embeddings)
        self.dimension = norm_vectors.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(norm_vectors)
        print(f"[FAISSIndexManager] Built FAISS IndexFlatIP with {self.index.ntotal:,} vectors of dim {self.dimension}.")

    def save_index(self, custom_path: str = None) -> None:
        """
        Saves binary FAISS index to disk.
        """
        save_path = custom_path or self.index_file_path
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        faiss.write_index(self.index, save_path)
        print(f"[FAISSIndexManager] Saved FAISS index to '{save_path}' ({os.path.getsize(save_path)/(1024*1024):.2f} MB).")

    def load_index(self, custom_path: str = None) -> bool:
        """
        Loads binary FAISS index from disk.
        """
        load_path = custom_path or self.index_file_path
        if not os.path.exists(load_path):
            return False
        try:
            self.index = faiss.read_index(load_path)
            self.dimension = self.index.d
            print(f"[FAISSIndexManager] Loaded FAISS index from '{load_path}' ({self.index.ntotal:,} vectors).")
            return True
        except Exception as e:
            print(f"[FAISSIndexManager] Failed to load index from '{load_path}': {e}")
            return False

    def search(self, query_vector: np.ndarray, top_k: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Searches global index for Top-K candidate nearest neighbors.
        """
        if self.index.ntotal == 0:
            raise ValueError("FAISS index is empty. Please build or load the index first.")

        norm_query = self.normalize_vectors(query_vector)
        effective_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(norm_query, effective_k)
        
        return scores[0], indices[0]


def build_faiss_from_processed_data(
    embeddings_path: str = EMBEDDINGS_PATH,
    master_csv_path: str = MASTER_CSV_PATH,
    index_output_path: str = DEFAULT_INDEX_PATH,
    meta_output_path: str = DEFAULT_META_PATH
):
    """
    Builds and persists FAISS index and metadata pickle file from generated embeddings & master CSV.
    """
    if not os.path.exists(embeddings_path):
        raise FileNotFoundError(f"Embeddings file not found at '{embeddings_path}'. Run generate_embeddings.py first.")
    if not os.path.exists(master_csv_path):
        raise FileNotFoundError(f"Master CSV not found at '{master_csv_path}'. Run merge_indian_patents.py first.")

    print(f"Loading embeddings from '{embeddings_path}'...")
    embeddings = np.load(embeddings_path)
    print(f"Loaded embeddings matrix shape: {embeddings.shape}")

    print(f"Loading metadata from '{master_csv_path}'...")
    df_meta = pd.read_csv(
        master_csv_path,
        dtype={
            "APPLICATION_NUMBER": str,
            "PUBLICATION_NUMBER": str,
            "NO_OF_PAGES": str,
            "NO_OF_CLAIMS": str
        },
        encoding_errors="replace"
    ).fillna("N/A")

    if len(df_meta) != len(embeddings):
        print(f"Warning: Row count mismatch! CSV rows: {len(df_meta):,}, Embeddings: {len(embeddings):,}")

    # Build FAISS index
    dim = embeddings.shape[1]
    manager = FAISSIndexManager(dimension=dim, index_file_path=index_output_path)
    manager.build_index(embeddings)
    manager.save_index()

    # Save metadata records as pickle
    records = df_meta.to_dict(orient="records")
    os.makedirs(os.path.dirname(os.path.abspath(meta_output_path)), exist_ok=True)
    with open(meta_output_path, "wb") as f:
        pickle.dump(records, f)

    print(f"Successfully saved patent metadata pickle to '{meta_output_path}' ({len(records):,} records)!")
    return manager, records

if __name__ == "__main__":
    build_faiss_from_processed_data()

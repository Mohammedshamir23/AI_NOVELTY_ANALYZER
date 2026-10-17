"""
Embedding Cache Manager for Storing and Loading Embeddings.

Follows Step 3 Requirements:
- Save embeddings locally using pickle or NumPy (.npy / .pkl).
- Ensure embeddings are generated only once to maximize system efficiency.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict, Any

class EmbeddingCacheManager:
    """
    Handles local persistence of generated patent embeddings and associated metadata.
    """

    def __init__(self, cache_dir: str):
        """
        Args:
            cache_dir (str): Directory where cache artifacts (.npy, .pkl) are stored.
        """
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.embeddings_path = os.path.join(self.cache_dir, "patent_embeddings.npy")
        self.metadata_path = os.path.join(self.cache_dir, "patent_metadata.pkl")

    def is_cache_valid(self, patent_df: pd.DataFrame) -> bool:
        """
        Checks if valid cached embeddings exist matching the current dataset length.
        
        Args:
            patent_df (pd.DataFrame): Current DataFrame of patent records.
            
        Returns:
            bool: True if valid cache exists, False otherwise.
        """
        if not (os.path.exists(self.embeddings_path) and os.path.exists(self.metadata_path)):
            return False

        try:
            embeddings = np.load(self.embeddings_path)
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)

            if len(embeddings) != len(patent_df):
                print(f"[CacheManager] Cache count mismatch ({len(embeddings)} vs {len(patent_df)}). Will regenerate.")
                return False

            cached_ids = [m['patent_id'] for m in metadata]
            current_ids = patent_df['patent_id'].tolist()

            if cached_ids != current_ids:
                print("[CacheManager] Cache patent ID mismatch. Will regenerate.")
                return False

            return True
        except Exception as e:
            print(f"[CacheManager] Error validating cache ({e}). Will regenerate.")
            return False

    def save_cache(self, embeddings: np.ndarray, patent_df: pd.DataFrame) -> None:
        """
        Saves vector matrix to .npy and patent metadata list to .pkl.
        
        Args:
            embeddings (np.ndarray): Dense embedding matrix.
            patent_df (pd.DataFrame): Patent DataFrame.
        """
        np.save(self.embeddings_path, embeddings)
        
        metadata = patent_df.to_dict(orient='records')
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
            
        print(f"[CacheManager] Saved {len(embeddings)} vectors to cache at '{self.cache_dir}'.")

    def load_cache(self) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Loads vector matrix and metadata DataFrame from cache files.
        
        Returns:
            Tuple[np.ndarray, pd.DataFrame]: Cached embedding matrix and DataFrame.
        """
        embeddings = np.load(self.embeddings_path)
        with open(self.metadata_path, 'rb') as f:
            metadata = pickle.load(f)
            
        patent_df = pd.DataFrame(metadata)
        print(f"[CacheManager] Loaded {len(embeddings)} cached vectors from '{self.cache_dir}'.")
        return embeddings, patent_df


if __name__ == "__main__":
    cache_mgr = EmbeddingCacheManager("./data")
    print("Cache valid check:", cache_mgr.is_cache_valid(pd.DataFrame({'patent_id': ['US1']})))

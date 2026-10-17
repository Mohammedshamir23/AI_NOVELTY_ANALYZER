"""
FAISS Search module for AI Novelty Analyzer.
Preserves FAISS IndexFlatIP vector retrieval.
"""

import numpy as np
import faiss
from typing import Tuple
from search.faiss_index import FAISSIndexManager

class FAISSSearch(FAISSIndexManager):
    """
    Modular wrapper for FAISS IndexFlatIP vector search.
    """
    pass

def build_temporary_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Builds a temporary, in-memory FAISS IndexFlatIP index for live/hybrid search without persisting to disk.
    """
    if len(embeddings) == 0:
        raise ValueError("Cannot build FAISS index with empty embeddings.")
        
    dim = embeddings.shape[1]
    norm_embeddings = embeddings.astype(np.float32).copy()
    faiss.normalize_L2(norm_embeddings)
    
    index = faiss.IndexFlatIP(dim)
    index.add(norm_embeddings)
    return index

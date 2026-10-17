"""
Embedding Generator Module using Stella-en-400M-v5 for Official Indian Patent Retrieval.

Features:
- Loads 'dunzhang/stella_en_400M_v5' model (GPU if available, CPU otherwise).
- Encodes SEARCH_TEXT into continuous dense vector space.
- Batch processing with tqdm progress bar.
- L2 normalization for inner product FAISS cosine similarity.
- Batch chunk checkpointing under data/processed/checkpoints/ to allow exact resumption if interrupted.
- Final output saved to data/processed/embeddings.npy.
"""

import os
import glob
import json
import torch
import numpy as np
import pandas as pd
from typing import List, Union, Optional
from tqdm import tqdm

DEFAULT_MODEL_NAME = "dunzhang/stella_en_400M_v5"
MASTER_CSV_PATH = "data/processed/indian_patents_master.csv"
CHECKPOINT_DIR = "data/processed/checkpoints"
CHECKPOINT_META_PATH = os.path.join(CHECKPOINT_DIR, "checkpoint_meta.json")
FINAL_EMBEDDINGS_PATH = "data/processed/embeddings.npy"

class StellaEmbeddingGenerator:
    """
    Generates dense vector embeddings using the Stella-en-400M-v5 model.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, use_gpu: bool = True):
        self.model_name = model_name
        self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"
        self.model = None
        self.vector_dim = 1024  # Default Stella dimension
        self._load_model()

    def _load_model(self):
        """
        Loads the Stella SentenceTransformer model.
        Handles xformers requirement gracefully by overriding memory_efficient_attention if needed.
        """
        print(f"[StellaEmbeddingGenerator] Loading model '{self.model_name}' on device '{self.device}'...")
        from sentence_transformers import SentenceTransformer

        # Attempt 1: Standard load with trust_remote_code=True
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                trust_remote_code=True
            )
        except Exception as e1:
            print(f"[StellaEmbeddingGenerator] Initial load attempt note: {e1}. Retrying without xformers requirement...")
            try:
                # Attempt 2: Disable memory_efficient_attention / unpad_inputs custom flags
                self.model = SentenceTransformer(
                    self.model_name,
                    device=self.device,
                    trust_remote_code=True,
                    model_kwargs={
                        "use_memory_efficient_attention": False,
                        "unpad_inputs": False
                    }
                )
            except Exception as e2:
                print(f"[StellaEmbeddingGenerator] Secondary attempt note: {e2}. Trying fallback SentenceTransformer model...")
                try:
                    # Attempt 3: Standard sentence transformer fallback if custom stella script fails on host
                    self.model = SentenceTransformer(
                        "sentence-transformers/all-mpnet-base-v2",
                        device=self.device
                    )
                except Exception as e3:
                    err_msg = f"CRITICAL ERROR: Failed to load embedding model: {e3}"
                    print(f"[StellaEmbeddingGenerator] {err_msg}")
                    raise RuntimeError(err_msg) from e3

        # Test encoding to get vector dimension
        dummy_emb = self.model.encode("Indian Patent Test", normalize_embeddings=True, convert_to_numpy=True)
        self.vector_dim = int(dummy_emb.shape[0])
        print(f"[StellaEmbeddingGenerator] Model loaded successfully! Vector Dimension: {self.vector_dim}")


    def encode_texts(self, texts: List[str], batch_size: int = 64, show_progress: bool = True) -> np.ndarray:
        """
        Encodes a list of text strings into L2-normalized float32 embeddings.
        """
        if not texts:
            return np.empty((0, self.vector_dim), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.astype(np.float32)


def generate_master_embeddings(
    master_csv_path: str = MASTER_CSV_PATH,
    checkpoint_dir: str = CHECKPOINT_DIR,
    final_output_path: str = FINAL_EMBEDDINGS_PATH,
    batch_chunk_size: int = 5000,
    batch_size: int = 64
) -> np.ndarray:
    """
    Generates embeddings for the complete Indian patent master dataset with batch chunk checkpointing.
    """
    if not os.path.exists(master_csv_path):
        raise FileNotFoundError(f"Master dataset not found at '{master_csv_path}'. Please run preprocessing/merge_indian_patents.py first.")

    print(f"Loading SEARCH_TEXT from '{master_csv_path}'...")
    df = pd.read_csv(master_csv_path, usecols=["SEARCH_TEXT"], dtype=str, encoding_errors="replace")
    search_texts = df["SEARCH_TEXT"].fillna("N/A").tolist()
    total_rows = len(search_texts)
    print(f"Total patent records to embed: {total_rows:,}")

    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)

    # 1. Check existing checkpoints
    processed_rows = 0
    last_batch = -1

    if os.path.exists(CHECKPOINT_META_PATH):
        try:
            with open(CHECKPOINT_META_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
                processed_rows = meta.get("processed_rows", 0)
                last_batch = meta.get("last_batch", -1)
            print(f"[Checkpoint] Resuming from checkpoint: {processed_rows:,} / {total_rows:,} records (last batch index: {last_batch})")
        except Exception as e:
            print(f"[Checkpoint] Warning reading checkpoint metadata: {e}. Starting fresh.")

    # Instantiate Stella Generator
    generator = StellaEmbeddingGenerator()

    # 2. Process in chunks of batch_chunk_size (5,000 patents)
    num_chunks = int(np.ceil(total_rows / batch_chunk_size))

    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * batch_chunk_size
        end_idx = min(start_idx + batch_chunk_size, total_rows)
        chunk_file = os.path.join(checkpoint_dir, f"batch_{chunk_idx:04d}.npy")

        # Skip if chunk file already exists and was registered
        if start_idx < processed_rows and os.path.exists(chunk_file):
            print(f"  [Chunk {chunk_idx + 1}/{num_chunks}] Already cached: {chunk_file} ({start_idx:,} to {end_idx:,})")
            continue

        print(f"\n[Chunk {chunk_idx + 1}/{num_chunks}] Embedding records {start_idx:,} to {end_idx:,}...")
        chunk_texts = search_texts[start_idx:end_idx]
        
        # Generate embeddings for chunk
        chunk_vecs = generator.encode_texts(chunk_texts, batch_size=batch_size, show_progress=True)

        # Save chunk .npy file
        np.save(chunk_file, chunk_vecs)

        # Update metadata
        processed_rows = end_idx
        last_batch = chunk_idx

        meta_data = {
            "processed_rows": processed_rows,
            "last_batch": last_batch,
            "total_rows": total_rows,
            "chunk_size": batch_chunk_size,
            "vector_dim": generator.vector_dim,
            "model_name": generator.model_name
        }
        with open(CHECKPOINT_META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)

        print(f"  -> Saved checkpoint: {chunk_file} ({processed_rows:,}/{total_rows:,} completed)")

    # 3. Concatenate all chunk files into final embeddings.npy
    print("\nConcatenating all batch checkpoint files into final embeddings array...")
    chunk_files = sorted(glob.glob(os.path.join(checkpoint_dir, "batch_*.npy")))
    
    if len(chunk_files) != num_chunks:
        print(f"Warning: Expected {num_chunks} chunk files, found {len(chunk_files)}.")

    all_embeddings = []
    for f_path in chunk_files:
        vecs = np.load(f_path)
        all_embeddings.append(vecs)

    final_embeddings = np.vstack(all_embeddings).astype(np.float32)
    print(f"Final combined matrix shape: {final_embeddings.shape}")

    np.save(final_output_path, final_embeddings)
    print(f"Successfully saved final embeddings to '{final_output_path}'! Size: {os.path.getsize(final_output_path)/(1024*1024):.2f} MB")

    return final_embeddings

if __name__ == "__main__":
    generate_master_embeddings()

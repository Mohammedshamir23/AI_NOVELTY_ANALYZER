"""
Stella Embedding Model wrapper for AI Novelty Analyzer.
Preserves Stella-en-400M-v5 model loading and feature extraction.
"""

from embeddings.generate_embeddings import StellaEmbeddingGenerator

class StellaModel(StellaEmbeddingGenerator):
    """
    Modular Stella-en-400M-v5 embedding generator class.
    """
    def __init__(self, model_name: str = "dunzhang/stella_en_400M_v5", use_gpu: bool = False):
        super().__init__(model_name=model_name, use_gpu=use_gpu)

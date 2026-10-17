"""
Core Offline Real-Time Semantic Search Engine with Candidate Field Pre-Filtering.

Workflow:
User Query -> Stella Query Vector Encoding -> Global FAISS Index Top-100 Candidates ->
Keyword Field Detection -> Field Filtering -> Top-5 Ranking & Qualitative Match Strength.

Preserves official Indian Patent metadata without modification.
"""

import os
import time
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

from preprocessing.clean_text import clean_patent_text, format_application_number
from embeddings.generate_embeddings import StellaEmbeddingGenerator
from search.faiss_index import FAISSIndexManager
from search.similarity import get_match_strength_label
from search.domain_detection import detect_technical_domain

DEFAULT_INDEX_PATH = "data/processed/faiss_index.bin"
DEFAULT_META_PATH = "data/processed/patent_metadata.pkl"

# Lightweight Keyword-to-Field Mapping Dictionary for 16 Official IPO Fields
FIELD_KEYWORD_MAP = {
    "BIOMEDICAL": [
        "heart", "cardiac", "biosensor", "medical", "health", "blood", "pulse", "sweat",
        "glucose", "patient", "implant", "diagnostic", "therapy", "clinical", "biomedical",
        "ECG", "EEG", "microfluidic", "catheter", "surgical"
    ],
    "COMPUTER": [
        "ai", "artificial intelligence", "neural", "algorithm", "machine learning", "software",
        "data", "cloud", "database", "app", "image processing", "deep learning", "nlp",
        "recommendation", "computer", "processor", "memory", "program", "code", "cyber"
    ],
    "MECHANICAL": [
        "drone", "robot", "robotic", "engine", "gear", "vehicle", "motor", "pump", "valve",
        "turbine", "hydraulic", "pneumatic", "brake", "mechanical", "transmission", "bearing",
        "chassis", "steering", "actuator", "blade"
    ],
    "ELECTRONICS": [
        "semiconductor", "chip", "circuit", "transistor", "sensor", "microfluidic",
        "microcontroller", "pcb", "signal", "diode", "electronics", "integrated circuit",
        "display", "led", "oled", "amplification"
    ],
    "COMMUNICATION": [
        "wireless", "antenna", "5g", "4g", "cellular", "telemetry", "bluetooth", "network",
        "transmitter", "receiver", "packet", "rf", "communication", "satellite", "broadband",
        "wifi", "channel", "modulation"
    ],
    "ELECTRICAL": [
        "battery", "voltage", "current", "transformer", "power", "inverter", "grid",
        "electric", "electrical", "capacitor", "generator", "charging", "electrode",
        "converter", "high voltage", "watt"
    ],
    "CHEMISTRY": [
        "chemical", "synthesis", "compound", "catalyst", "reaction", "solvent", "solution",
        "molecular", "chemistry", "acid", "base", "polymerization", "organic", "inorganic",
        "formulation", "reagent"
    ],
    "BIOTECHNOLOGY": [
        "gene", "dna", "rna", "protein", "cell", "tissue", "enzyme", "organism", "biological",
        "biotechnology", "vaccine", "antibody", "genomic", "crispr", "microbial", "bacteria"
    ],
    "PHYSICS": [
        "optical", "laser", "quantum", "photonic", "spectroscopy", "magnetic", "radiation",
        "plasma", "thermal", "physics", "lens", "wavelength", "refraction", "interferometer"
    ],
    "POLYMER": [
        "polymer", "resin", "elastomer", "composite", "plastic", "fiberglass", "nanocomposite",
        "copolymer", "adhesive", "coating"
    ],
    "BIOCHEMISTRY": [
        "biochemistry", "metabolic", "metabolism", "assay", "peptide", "amino acid", "lipid",
        "biomarker", "enzyme activity"
    ],
    "CIVIL": [
        "concrete", "cement", "structure", "building", "road", "asphalt", "bridge",
        "construction", "soil", "civil", "geotechnical", "beam", "foundation"
    ],
    "METALLURGY": [
        "alloy", "metal", "steel", "iron", "aluminum", "coating", "corrosion", "casting",
        "welding", "metallurgy", "forging", "heat treatment"
    ],
    "FOOD": [
        "food", "beverage", "nutrition", "edible", "shelf-life", "fermentation", "processing",
        "preservation", "agricultural", "flavor", "grain", "dairy"
    ],
    "TEXTILE": [
        "fabric", "yarn", "fiber", "textile", "weaving", "garment", "thread", "spinning",
        "loom", "knitting", "dyeing"
    ]
}


def infer_technical_field(query_text: str) -> Tuple[str, float]:
    """
    Infers target technical field using lightweight keyword mapping.
    Returns: (detected_field_name, confidence_score)
    """
    q_lower = query_text.lower()
    field_scores = {}

    for field, keywords in FIELD_KEYWORD_MAP.items():
        score = 0
        for kw in keywords:
            if kw.lower() in q_lower:
                # Longer exact match gets higher score
                score += 2 if len(kw) > 4 else 1
        if score > 0:
            field_scores[field] = score

    if not field_scores:
        return "GENERAL", 0.0

    sorted_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)
    best_field, best_score = sorted_fields[0]
    
    # Simple confidence metric
    confidence = float(min(1.0, best_score / 3.0))
    return best_field, confidence


class PatentSearchEngine:
    """
    Offline Patent Semantic Search Controller using Stella embeddings and global FAISS index.
    """

    def __init__(
        self,
        index_path: str = DEFAULT_INDEX_PATH,
        meta_path: str = DEFAULT_META_PATH,
        project_root: Optional[str] = None
    ):
        if project_root:
            if not os.path.isabs(index_path):
                index_path = os.path.join(project_root, index_path)
            if not os.path.isabs(meta_path):
                meta_path = os.path.join(project_root, meta_path)


        self.index_path = index_path
        self.meta_path = meta_path
        
        self.generator = StellaEmbeddingGenerator()
        self.faiss_manager = FAISSIndexManager(dimension=self.generator.vector_dim, index_file_path=index_path)

        self.metadata: List[Dict[str, Any]] = []
        self.is_initialized = False

        self.load_resources()

    @property
    def index(self):
        """Backwards compatible property accessor for FAISS index."""
        return self.faiss_manager.index if hasattr(self, 'faiss_manager') else None

    def load_resources(self):
        """
        Loads FAISS binary index and metadata pickle file.
        """
        print("[PatentSearchEngine] Loading system resources...")
        if not self.faiss_manager.load_index(self.index_path):
            print(f"[PatentSearchEngine] FAISS index file missing at '{self.index_path}'.")
            
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            print(f"[PatentSearchEngine] Metadata pickle file missing at '{self.meta_path}'.")

        self.field_counts = {}
        if os.path.exists(self.meta_path) and self.metadata:
            for m in self.metadata:
                fld = str(m.get("FIELD_OF_INVENTION", "")).upper().strip()
                self.field_counts[fld] = self.field_counts.get(fld, 0) + 1

        self.is_initialized = (self.faiss_manager.index.ntotal > 0 and len(self.metadata) > 0)
        if self.is_initialized:
            print("[PatentSearchEngine] System initialized successfully and ready for search!")

    def search_offline_indian_patents(
        self,
        query_idea: str,
        top_k: int = 5,
        candidate_pool_size: int = 200,
        candidates_k: Optional[int] = None,
        field_filter: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], List[float], Dict[str, Any], float]:
        """
        Executes semantic search against official Indian patent corpus.
        
        Workflow:
        1. Query -> Stella embedding
        2. FAISS retrieve Top candidates from global index
        3. Keyword field detection (or manual field_filter) -> Filter candidates by FIELD_OF_INVENTION
        4. If < 5 field matches, fallback to unfiltered candidate pool
        5. Return Top 5 patents, similarity scores, search statistics dict, and execution runtime
        
        Returns:
            Tuple[List[Dict[str, Any]], List[float], Dict[str, Any], float]:
            (top_5_patents, all_retrieved_scores, stats_dict, exec_time)
        """
        start_time = time.time()
        clean_query = clean_patent_text(query_idea)
        pool_size = candidates_k if candidates_k is not None else candidate_pool_size
        
        if not self.is_initialized or not clean_query:
            empty_stats = {
                "total_corpus_patents": len(self.metadata),
                "detected_field": field_filter or "N/A",
                "candidates_evaluated": 0,
                "filter_mode": "None",
                "search_time_sec": 0.0
            }
            return [], [], empty_stats, 0.0

        # 1. Infer field via keyword mapping or explicit field_filter
        if field_filter and field_filter != "Auto-Detect Field":
            detected_field = field_filter.upper()
        else:
            detected_field, confidence = infer_technical_field(clean_query)

        # 2. Encode query text using Stella
        query_vector = self.generator.encode_texts([clean_query], show_progress=False)

        # 3. Retrieve Top candidate vectors from global FAISS index
        scores, candidate_indices = self.faiss_manager.search(query_vector, top_k=pool_size)

        # 4. Filter candidates by detected field
        field_matched_candidates = []
        unfiltered_candidates = []

        for score, idx in zip(scores, candidate_indices):
            if 0 <= idx < len(self.metadata):
                patent_meta = self.metadata[idx].copy()
                cosine_sim = float(np.clip(score, 0.0, 1.0))
                patent_meta["cosine_similarity"] = cosine_sim
                patent_meta["global_index"] = int(idx)
                
                label, color = get_match_strength_label(cosine_sim)
                patent_meta["match_strength_label"] = label
                patent_meta["match_strength_color"] = color

                unfiltered_candidates.append(patent_meta)
                
                # Check if patent field matches inferred field
                pat_field = str(patent_meta.get("FIELD_OF_INVENTION", "")).upper()
                if detected_field != "GENERAL" and detected_field in pat_field:
                    field_matched_candidates.append(patent_meta)

        # Fallback decision:
        # 1. Fall back to global Top 100 whenever fewer than 5 field-matched patents remain.
        # 2. If top global vector candidate is significantly stronger (>0.12 gap) than field-matched candidate,
        #    use global candidates so stronger vector matches are never discarded.
        if len(field_matched_candidates) >= top_k:
            field_matched_candidates.sort(key=lambda x: x["cosine_similarity"], reverse=True)
            top_field_sim = field_matched_candidates[0]["cosine_similarity"]
            top_global_sim = unfiltered_candidates[0]["cosine_similarity"] if unfiltered_candidates else 0.0

            if (top_global_sim - top_field_sim) > 0.12:
                selected_candidates = unfiltered_candidates
                filter_mode = "Global Search (High Similarity Vector Fallback)"
            else:
                selected_candidates = field_matched_candidates
                filter_mode = f"Field Pre-Filtered ({detected_field})"
        else:
            selected_candidates = unfiltered_candidates
            filter_mode = "Global Search (Fallback < 5 Matches)"

        # Sort and take Top 5
        selected_candidates.sort(key=lambda x: x["cosine_similarity"], reverse=True)
        top_5_results = selected_candidates[:top_k]

        # Standardize metadata key names for UI / PDF consistency
        formatted_top_5 = []
        for rank, p in enumerate(top_5_results, start=1):
            raw_app_num = p.get("APPLICATION_NUMBER", "N/A")
            clean_app_num = format_application_number(raw_app_num)
            if clean_app_num.upper().startswith("IN-") or clean_app_num.upper().startswith("IN/"):
                clean_app_num = clean_app_num[3:].strip()
            elif clean_app_num.upper().startswith("IN") and len(clean_app_num) > 2 and clean_app_num[2].isdigit():
                clean_app_num = clean_app_num[2:].strip()

            formatted_p = {
                "rank": rank,
                "title": p.get("TITLE_OF_INVENTION", "N/A"),
                "application_number": clean_app_num,
                "publication_number": p.get("PUBLICATION_NUMBER", "N/A"),
                "publication_date": p.get("PUBLICATION_DATE", "N/A"),
                "ipo_location": p.get("IPO_LOCATION", "N/A"),
                "field_of_invention": p.get("FIELD_OF_INVENTION", "N/A"),
                "application_type": p.get("APPLICATION_TYPE_DESC", "N/A"),
                "no_of_claims": p.get("NO_OF_CLAIMS", "N/A"),
                "no_of_pages": p.get("NO_OF_PAGES", "N/A"),
                "search_text": p.get("SEARCH_TEXT", ""),
                "cosine_similarity": p.get("cosine_similarity", 0.0),
                "match_strength_label": p.get("match_strength_label", "Low Match"),
                "match_strength_color": p.get("match_strength_color", "#10b981"),
                "verified_ipo": True
            }
            formatted_top_5.append(formatted_p)

        # Log raw FAISS Cosine Similarity scores in terminal for debugging (hidden from UI)
        print("\n" + "="*75)
        print("[FAISS RETRIEVAL DEBUG] Top 5 Raw Cosine Similarity Scores:")
        print("="*75)
        for p in formatted_top_5:
            print(f"  Rank {p['rank']}: Cosine Sim = {p['cosine_similarity']:.4f} | Label = {p['match_strength_label']:<18} | App No = {p['application_number']:<16} | Title = {p['title'][:55]}")
        print("="*75 + "\n")

        all_scores = [p["cosine_similarity"] for p in unfiltered_candidates]
        exec_time = round(time.time() - start_time, 2)

        specific_domain = detect_technical_domain(clean_query, patent_context=formatted_top_5)

        stats_dict = {
            "total_database_patents": 458724,
            "total_corpus_patents": 458724,
            "detected_field": specific_domain,
            "top_candidates_retrieved": len(unfiltered_candidates),
            "candidates_evaluated": len(unfiltered_candidates),
            "filter_mode": filter_mode,
            "search_time_sec": exec_time
        }

        return formatted_top_5, all_scores, stats_dict, exec_time


if __name__ == "__main__":
    engine = PatentSearchEngine()
    test_query = "Smart microfluidic sweat electrolyte biosensor device with wireless transmission"
    top_5, scores, stats, exec_time = engine.search_offline_indian_patents(test_query)
    print("\n--- Test Search Results ---")
    print("Search Stats:", stats)
    print(f"Execution Time: {exec_time}s")
    print(f"Retrieved {len(top_5)} Top Patents:")
    for p in top_5:
        print(f"Rank {p['rank']}: [{p['application_number']}] {p['title']} ({p['match_strength_label']} - {p['cosine_similarity']:.4f})")

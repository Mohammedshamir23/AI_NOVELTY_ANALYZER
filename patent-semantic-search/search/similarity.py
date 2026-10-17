"""
Similarity & Match Scoring utilities for AI Novelty Analyzer.
Implements Qualitative Match Strength Labels, Weighted Top-5 Semantic Uniqueness,
Prior-Art Density Scoring, and Combined AI Novelty Index Calculation.
"""

import numpy as np
from typing import List, Dict, Any, Tuple

# Mandatory Project Disclaimer
NOVELTY_INDEX_DISCLAIMER = (
    "The AI Novelty Index is a project-defined analytical metric for preliminary prior-art assessment. "
    "It is not an official patentability score issued by a patent office."
)

def get_match_strength_label(cosine_sim: float) -> Tuple[str, str]:
    """
    Returns External Qualitative Match Strength Label & Badge Hex Color based on Cosine Similarity.
    
    Updated Thresholds:
    - Cosine Sim >= 0.80 -> Very High Match (#ef4444 Red)
    - 0.65 <= Cosine Sim < 0.80 -> High Match (#f97316 Orange)
    - 0.50 <= Cosine Sim < 0.65 -> Moderate Match (#eab308 Yellow)
    - Cosine Sim < 0.50 -> Low Match (#10b981 Green)
    """
    clipped = float(np.clip(cosine_sim, 0.0, 1.0))
    if clipped >= 0.80:
        return "Very High Match", "#ef4444"
    elif clipped >= 0.65:
        return "High Match", "#f97316"
    elif clipped >= 0.50:
        return "Moderate Match", "#eab308"
    else:
        return "Low Match", "#10b981"

def calculate_weighted_semantic_uniqueness(top_5_cosine_scores: List[float]) -> Tuple[float, float]:
    """
    Calculates Weighted Similarity across Top-5 FAISS retrieval scores:
    Weighted Similarity = (5*S1 + 4*S2 + 3*S3 + 2*S4 + 1*S5) / 15
    Semantic Uniqueness = (1 - Weighted Similarity) * 100
    
    Returns:
        Tuple[float, float]: (weighted_similarity_percentage, semantic_uniqueness_score)
    """
    scores = [float(np.clip(s, 0.0, 1.0)) for s in top_5_cosine_scores]
    while len(scores) < 5:
        scores.append(scores[-1] if scores else 0.0)

    weights = [5, 4, 3, 2, 1]
    weighted_sim = sum(w * s for w, s in zip(weights, scores[:5])) / 15.0
    semantic_uniqueness = round((1.0 - weighted_sim) * 100.0, 2)
    return round(weighted_sim * 100.0, 2), semantic_uniqueness

def calculate_prior_art_density(all_retrieved_scores: List[float]) -> Tuple[float, Dict[str, int]]:
    """
    Calculates Prior-Art Density score and category counts across screened patents.
    Categories:
    - Very High Match (sim >= 0.80)
    - High Match (0.65 <= sim < 0.80)
    - Moderate Match (0.50 <= sim < 0.65)
    - Low Match (sim < 0.50)
    
    Returns:
        Tuple[float, Dict[str, int]]: (prior_art_density_score, counts_dict)
    """
    counts = {"Very High": 0, "High": 0, "Moderate": 0, "Low": 0}
    for score in all_retrieved_scores:
        s = float(np.clip(score, 0.0, 1.0))
        if s >= 0.80:
            counts["Very High"] += 1
        elif s >= 0.65:
            counts["High"] += 1
        elif s >= 0.50:
            counts["Moderate"] += 1
        else:
            counts["Low"] += 1

    # Density Penalty Calculation
    penalty = (counts["Very High"] * 15) + (counts["High"] * 8) + (counts["Moderate"] * 3) + (counts["Low"] * 1)
    density_score = round(max(0.0, min(100.0, 100.0 - penalty)), 2)
    return density_score, counts

def calculate_ai_novelty_index(
    top_5_cosine_scores: List[float],
    feature_uniqueness_score: float,
    all_retrieved_scores: List[float]
) -> Dict[str, Any]:
    """
    Calculates the combined project-defined AI Novelty Index score.
    The internal novelty calculation is preserved for system evaluation and ranking, but calculation formulas are intentionally hidden from the user interface and PDF report.
    """
    weighted_sim_pct, semantic_uniqueness = calculate_weighted_semantic_uniqueness(top_5_cosine_scores)
    prior_art_score, density_counts = calculate_prior_art_density(all_retrieved_scores)
    
    feat_score = round(float(np.clip(feature_uniqueness_score, 0.0, 100.0)), 2)
    
    final_novelty_index = round(
        (0.50 * semantic_uniqueness) +
        (0.30 * feat_score) +
        (0.20 * prior_art_score),
        2
    )

    if final_novelty_index >= 80.0:
        potential_label = "Strong Originality"
        status_color = "#10b981"
    elif final_novelty_index >= 60.0:
        potential_label = "Moderate Originality"
        status_color = "#38bdf8"
    elif final_novelty_index >= 40.0:
        potential_label = "Limited Originality"
        status_color = "#f59e0b"
    else:
        potential_label = "Significant Prior Art Overlap"
        status_color = "#ef4444"

    return {
        "novelty_index": final_novelty_index,
        "potential_label": potential_label,
        "status_color": status_color,
        "semantic_uniqueness": semantic_uniqueness,
        "weighted_similarity_pct": weighted_sim_pct,
        "feature_uniqueness": feat_score,
        "prior_art_density": prior_art_score,
        "density_counts": density_counts,
        "disclaimer": NOVELTY_INDEX_DISCLAIMER
    }

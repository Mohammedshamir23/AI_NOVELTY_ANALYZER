"""
Verification script for Universal Delta Update – Strict AI Content Grounding.
"""

import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from search.domain_detection import detect_technical_domain
from llm.feature_extractor import FeatureExtractor, is_feature_grounded
from llm.novelty_report import NoveltyReportGenerator, sanitize_hallucinated_terms

def run_tests():
    print("=== TEST 1: Dynamic Technical Domain Classification ===")
    d1 = detect_technical_domain(
        title="Smart Water Pipeline Monitoring System",
        description="Acoustic leak detection sensors placed along municipal water distribution pipelines."
    )
    print(f"Domain 1 (Water Pipeline): {d1}")
    assert d1 == "Smart Water Pipeline Monitoring", f"Expected 'Smart Water Pipeline Monitoring', got '{d1}'"

    d2 = detect_technical_domain(
        title="Microfluidic Sweat Electrolyte Biosensor",
        description="A wearable sensor measuring sweat sodium and potassium levels in real-time."
    )
    print(f"Domain 2 (Biosensor): {d2}")
    assert d2 == "Medical Diagnostic Devices", f"Expected 'Medical Diagnostic Devices', got '{d2}'"

    d3 = detect_technical_domain(
        title="Computer Vision Automated Defect Sorter",
        description="Camera-based optical inspection unit using convolutional neural networks for component triage."
    )
    print(f"Domain 3 (Vision): {d3}")
    assert d3 == "Computer Vision Classification", f"Expected 'Computer Vision Classification', got '{d3}'"

    print("Domain detection passed!\n")

    print("=== TEST 2: Universal Dynamic Feature Extraction & Evidence-Based Validation ===")
    fe = FeatureExtractor()

    # Test with water pipeline invention
    water_title = "Smart Water Pipeline Monitoring System"
    water_desc = "Integrates acoustic leak detection sensors, pressure sensor network, and GPS mapping on pipelines."
    mock_patents = [{
        "application_number": "202411012345",
        "title": "Pipeline monitoring and acoustic inspection apparatus",
        "publication_number": "12/2024",
        "field_of_invention": "MECHANICAL",
        "search_text": "acoustic sensor for monitoring fluid pipeline networks and detecting pressure drops."
    }]

    res = fe.evaluate_feature_rubric(
        user_idea=f"Title: {water_title}\nDescription: {water_desc}",
        retrieved_patents=mock_patents,
        invention_title=water_title,
        invention_description=water_desc
    )

    print(f"Extracted {len(res['feature_rubric'])} features:")
    for f in res["feature_rubric"]:
        print(f"  - [{f['prior_art_status']}] {f['feature']} (Score: {f['score']}) | Obs: {f['observation']}")

    # Verify no hallucinated technologies appear
    hallucinated = ["blockchain", "cryptographic", "lora mesh", "zero-trust", "vision"]
    for f in res["feature_rubric"]:
        name_lower = f["feature"].lower()
        for h in hallucinated:
            assert h not in name_lower, f"Hallucinated technology '{h}' found in feature '{f['feature']}'!"

    print("Feature extraction grounding passed!\n")

    print("=== TEST 3: Grounded Report Generation & Hallucination Prevention Pass ===")
    rg = NoveltyReportGenerator()
    report = rg.generate_report(
        user_idea=f"Title: {water_title}\nDescription: {water_desc}",
        retrieved_patents=mock_patents,
        all_retrieved_scores=[0.82, 0.75, 0.71, 0.65, 0.60],
        invention_title=water_title,
        invention_description=water_desc
    )

    print("--- Executive Summary ---")
    print(report["executive_summary"])

    print("\n--- Innovation Opportunities ---")
    print(report["innovation_opportunities"])

    print("\n--- Filing Recommendation ---")
    print(report["filing_recommendation"])

    print(f"\n--- Technical Domain: {report['detected_field']} ---")
    assert report["detected_field"] == "Smart Water Pipeline Monitoring"

    # Verify absence of hallucinated technologies across all generated text
    full_narrative = (
        report["executive_summary"] + " " +
        report["innovation_opportunities"] + " " +
        report["filing_recommendation"]
    ).lower()

    for h in ["blockchain", "zero-trust", "cryptographic routing", "cryogenic"]:
        assert h not in full_narrative, f"Found ungrounded buzzword '{h}' in narrative output!"

    print("\nAll Strict AI Content Grounding tests PASSED successfully!")

if __name__ == "__main__":
    run_tests()

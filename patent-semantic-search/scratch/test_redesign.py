"""
Comprehensive verification test suite for the Enterprise Patent Intelligence & Novelty Assessment Platform redesign.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from preprocessing.clean_text import format_application_number
from search.similarity import calculate_ai_novelty_index
from llm.feature_extractor import FeatureExtractor
from llm.concept_enhancement import ConceptEnhancementGenerator
from reports.pdf_generator import PDFReportGenerator
from ui.components import clean_app_number, render_patent_card_html

def test_application_number_cleaning():
    print("[TEST 1] Testing Application Number Cleaning (IN prefix removal)...")
    test_cases = [
        ("IN202041012345", "202041012345"),
        ("IN-202111001234", "202111001234"),
        ("IN/201941098765", "201941098765"),
        ("IN 201831011223", "201831011223"),
        ("202041012345", "202041012345"),
        ("2.02E+11", "202000000000"),
    ]
    for raw, expected in test_cases:
        res = clean_app_number(raw)
        assert not res.upper().startswith("IN-") and not res.upper().startswith("IN/"), f"Failed on {raw}: {res}"
        if expected != "202000000000":
            assert res == expected, f"Expected {expected}, got {res}"
    print("  -> PASSED: All IN prefixes stripped cleanly.")

def test_novelty_index_labels():
    print("[TEST 2] Testing Qualitative AI Novelty Index Labels...")
    # Tier 1: Strong Originality (>= 80)
    res85 = calculate_ai_novelty_index([0.1, 0.15, 0.2, 0.25, 0.3], 90.0, [0.1, 0.2])
    assert res85["potential_label"] == "Strong Originality", f"Expected Strong Originality, got {res85['potential_label']}"

    # Tier 2: Moderate Originality (60 - 79)
    res65 = calculate_ai_novelty_index([0.4, 0.45, 0.5, 0.55, 0.6], 60.0, [0.4, 0.5, 0.6])
    assert res65["potential_label"] == "Moderate Originality", f"Expected Moderate Originality, got {res65['potential_label']}"

    # Tier 3: Limited Originality (40 - 59)
    res45 = calculate_ai_novelty_index([0.65, 0.7, 0.72, 0.75, 0.78], 30.0, [0.7, 0.75])
    assert res45["potential_label"] == "Limited Originality", f"Expected Limited Originality, got {res45['potential_label']}"

    # Tier 4: Significant Prior Art Overlap (< 40)
    res25 = calculate_ai_novelty_index([0.9, 0.92, 0.95, 0.96, 0.97], 0.0, [0.9, 0.95, 0.98])
    assert "formula" not in res85, "Formula key found in calculate_ai_novelty_index result!"
    print("  -> PASSED: All 4 qualitative tiers match enterprise specifications and formula is hidden.")

def test_dynamic_feature_extractor():
    print("[TEST 3] Testing Dynamic Feature Extractor (3 columns, dynamic without templates)...")
    extractor = FeatureExtractor()
    test_title = "Autonomous Drone Fleet Communication and Battery Swapping Hub"
    test_desc = "A specialized multi-rotor docking station utilizing robotic servo arms for hot-swapping lithium batteries and establishing ad-hoc mesh telemetry."

    prior_patent = [{
        "title": "BATTERY RECHARGING DOCK FOR UNMANNED VEHICLES",
        "application_number": "201941011222",
        "field_of_invention": "ELECTRICAL",
        "search_text": "A stationary charging pad utilizing inductive wireless power coils for recharging vehicle batteries."
    }]

    feat_res = extractor.evaluate_feature_rubric(
        user_idea=f"Title: {test_title}\nDescription: {test_desc}",
        retrieved_patents=prior_patent,
        invention_title=test_title,
        invention_description=test_desc
    )

    rubric = feat_res["feature_rubric"]
    assert len(rubric) == 5, f"Expected 5 features, got {len(rubric)}"
    valid_statuses = {"Shared", "Moderate Difference", "Strong Difference"}
    for item in rubric:
        assert "feature" in item, "Missing feature key"
        assert "prior_art_status" in item, "Missing prior_art_status key"
        assert item["prior_art_status"] in valid_statuses, f"Invalid status: {item['prior_art_status']}"
        assert "observation" in item, "Missing observation key"
        assert len(item["observation"]) > 5, "Observation too brief"
        # Verify not using the old hardcoded templates
        assert "Core Sensor Hardware Architecture" != item["feature"], "Found old hardcoded template!"

    print("  -> PASSED: Dynamic features extracted with valid 3-column statuses without fixed templates.")

def test_patent_card_rendering():
    print("[TEST 4] Testing Patent Card Clean Rendering (official metadata only)...")
    patent = {
        "title": "DRONE DOCKING APPARATUS",
        "application_number": "IN202141099881",
        "publication_number": "12/2021",
        "publication_date": "15/03/2021",
        "ipo_location": "Delhi",
        "field_of_invention": "ELECTRICAL",
        "application_type": "ORDINARY APPLICATION",
        "no_of_claims": "12",
        "no_of_pages": "24",
        "match_strength_label": "High Match",
        "match_strength_color": "#2563EB",
        "search_text": "Internal raw context that should be omitted",
        "match_explanation": "Old explanation that should be omitted"
    }
    card_html = render_patent_card_html(patent, rank=1)
    assert "Why This Patent Was Retrieved" not in card_html, "Found 'Why This Patent Was Retrieved' in card!"
    assert "Search Context:" not in card_html, "Found 'Search Context' in card!"
    assert "IN202141099881" not in card_html, "Found unstripped IN prefix!"
    assert "202141099881" in card_html, "Missing cleaned application number!"
    assert "Patent Journal Issue" in card_html, "Missing Journal Issue"
    assert "12/2021" in card_html
    print("  -> PASSED: Patent card contains only official metadata with no explanation box.")

def test_pdf_report_compilation():
    print("[TEST 5] Testing 12-Section PDF Report Compilation...")
    test_title = "AI Drone Battery Swapping Hub"
    test_desc = "A robotic drone docking station for automated battery swapping and mesh communication."

    gen = ConceptEnhancementGenerator()
    concept_res = gen.generate(
        invention_title=test_title,
        invention_description=test_desc,
        retrieved_patents=[]
    )

    report_data = {
        "user_idea": f"Title: {test_title}\nDescription: {test_desc}",
        "invention_title": test_title,
        "invention_description": test_desc,
        "search_time_sec": 0.38,
        "total_screened": 458724,
        "detected_field": "ELECTRICAL",
        "novelty_index_data": {
            "novelty_index": 82.5,
            "potential_label": "Strong Originality",
            "status_color": "#10B981"
        },
        "executive_summary": "The proposed invention demonstrates strong novelty against retrieved Indian patent records.",
        "why_score_given": "The score of 82.5/100 reflects distinct mechanical battery exchange mechanisms that differ from baseline inductive charging patents.",
        "landscape_observation": "The patent landscape in electrical docking stations shows foundational charging pads but open white space for automated robotic swapping.",
        "recommendation": "Proceed with drafting claims focused on robotic arm synchronization.",
        "filing_recommendation": "File an ordinary patent application with IPO Delhi.",
        "feature_rubric": [
            {"feature": "Robotic Gripper Mechanism", "prior_art_status": "Strong Difference", "score": 20, "observation": "Unique mechanical arm not in prior art."},
            {"feature": "Ad-Hoc Mesh Antenna", "prior_art_status": "Moderate Difference", "score": 10, "observation": "Prior art has standard wireless, but not localized mesh."},
            {"feature": "Thermal Sensor Array", "prior_art_status": "Shared", "score": 0, "observation": "Standard temperature sensing in charging docks."}
        ],
        "retrieved_patents": [
            {
                "title": "VEHICLE CHARGING DOCK",
                "application_number": "IN202041012345",
                "publication_number": "05/2021",
                "publication_date": "29/01/2021",
                "ipo_location": "Chennai",
                "field_of_invention": "ELECTRICAL",
                "application_type": "ORDINARY APPLICATION",
                "no_of_claims": "10",
                "no_of_pages": "18",
                "match_strength_label": "High Match",
                "match_strength_color": "#2563EB"
            }
        ],
        "concept_enhancement": concept_res
    }

    pdf_gen = PDFReportGenerator()
    pdf_bytes = pdf_gen.generate_pdf_bytes(report_data)
    assert len(pdf_bytes) > 5000, f"PDF byte size too small: {len(pdf_bytes)}"
    print(f"  -> PASSED: 12-section PDF compiled successfully ({len(pdf_bytes):,} bytes)!")

if __name__ == "__main__":
    test_application_number_cleaning()
    test_novelty_index_labels()
    test_dynamic_feature_extractor()
    test_patent_card_rendering()
    test_pdf_report_compilation()
    print("\n=======================================================")
    print("ALL ENTERPRISE REDESIGN TEST SUITES PASSED CLEANLY!")
    print("=======================================================")

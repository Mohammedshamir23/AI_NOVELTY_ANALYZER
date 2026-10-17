"""
Verification test for Hero Banner Branding Update (AI Novelty Analyzer).
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.components import render_hero_banner
import app

def test_hero_banner():
    print("[TEST] Verifying Hero Banner delta update...")
    import inspect
    src = inspect.getsource(render_hero_banner)
    
    # Must contain
    assert "🧠" in src, "Brain icon missing from hero banner!"
    assert "#F8FAFC" in src, "White color missing for AI / Novelty Analyzer!"
    assert "Novelty Analyzer" in src, "Novelty Analyzer title missing!"
    assert "AI" in src, "'AI' prefix missing!"
    
    # Must NOT contain removed text
    forbidden_terms = [
        "Patent Intelligence & Novelty Assessment Platform",
        "Real-Time Indian Patent Office (IPO) Vector Search & Novelty Analysis",
        "High-performance semantic vector search",
        "Stella embeddings",
        "FAISS indexing",
        "Dynamic feature analysis"
    ]
    for term in forbidden_terms:
        assert term not in src, f"Forbidden term '{term}' found in hero banner!"
        
    print("  -> PASSED: Hero banner displays only [brain] AI Novelty Analyzer with proper branding colors.")

if __name__ == "__main__":
    test_hero_banner()

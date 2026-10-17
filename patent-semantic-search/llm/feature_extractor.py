"""
Universal Dynamic Feature Extraction and Feature Uniqueness Scoring Module for Official Indian Patent Analysis.
Strictly grounded in:
1. Submitted Invention Title
2. Submitted Technical Description
3. Closest Retrieved Prior-Art Patent

Extracts 5 complete engineering concepts, validates every feature against source text,
and compares them against the closest retrieved prior art patent.
Statuses: 'Shared' (0 pts), 'Moderate Difference' (10 pts), 'Strong Difference' (20 pts).
Total Feature Uniqueness Score = 0 to 100.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of", "from",
    "is", "are", "was", "were", "it", "this", "that", "these", "those", "system", "method", "device",
    "apparatus", "using", "used", "based", "which", "into", "as", "be", "can", "will", "uses",
    "comprising", "configured", "wherein", "providing", "via", "such", "an", "all", "any"
}

UNSUPPORTED_BUZZWORDS = [
    "blockchain", "smart contract", "cryptographic routing", "zero-trust", "lora mesh",
    "cryogenic", "quantum key", "facial recognition"
]


def is_feature_grounded(feature_name: str, source_texts: List[str]) -> bool:
    """
    Evidence-based feature validation:
    Verifies that the feature appears in or is directly traceable to at least one of:
    1. Submitted Title
    2. Submitted Description
    3. Retrieved Prior-Art Patent
    """
    if not feature_name or not source_texts:
        return False
    combined_source = " ".join(source_texts).lower()
    feat_words = [w.lower() for w in re.findall(r'[A-Za-z0-9]+', feature_name) if w.lower() not in STOPWORDS]
    if not feat_words:
        return False

    # Block completely unmentioned buzzwords
    for bw in UNSUPPORTED_BUZZWORDS:
        if bw in feature_name.lower() and bw not in combined_source:
            return False

    # Check if at least one meaningful component word appears in the combined source
    match_count = sum(1 for w in feat_words if w in combined_source)
    return match_count >= 1


class FeatureExtractor:
    """
    Dynamically extracts 5 complete engineering concepts from user's invention title and description,
    with priority:
    1. Submitted Invention Title
    2. Submitted Technical Description
    3. Closest Retrieved Prior-Art Patent
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def evaluate_feature_rubric(
        self,
        user_idea: str,
        retrieved_patents: List[Dict[str, Any]],
        invention_title: str = "",
        invention_description: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates 5 dynamic technical features against the closest retrieved prior art patent.
        Returns:
            Dict containing feature_score (0-100), feature_rubric (list of dicts), common_features, unique_features.
        """
        title = invention_title.strip()
        description = invention_description.strip()

        if not title or not description:
            # Parse from user_idea if not passed explicitly
            title_match = re.search(r"Title:\s*(.+?)(?:\n|Description:)", user_idea, re.IGNORECASE | re.DOTALL)
            desc_match = re.search(r"Description:\s*(.*)", user_idea, re.IGNORECASE | re.DOTALL)
            if title_match and not title:
                title = title_match.group(1).strip()
            if desc_match and not description:
                description = desc_match.group(1).strip()
            if not title and not description:
                description = user_idea.strip()

        closest_patent = retrieved_patents[0] if retrieved_patents else {}
        closest_summary = (
            f"Title: {closest_patent.get('title', 'N/A')}\n"
            f"Application Number: {closest_patent.get('application_number', 'N/A')}\n"
            f"Field of Invention: {closest_patent.get('field_of_invention', 'N/A')}\n"
            f"Technical Context: {closest_patent.get('search_text', 'N/A')[:600]}"
        )

        source_texts = [
            title,
            description,
            closest_patent.get('title', ''),
            closest_patent.get('field_of_invention', ''),
            closest_patent.get('search_text', '')
        ]

        # Attempt Gemini analysis if API key present
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = f"""
                You are a senior patent examiner evaluating a proposed invention against official Indian Patent prior art.

                Proposed Invention:
                - Title: {title or 'N/A'}
                - Description: {description}

                Closest Retrieved Prior Art Patent:
                {closest_summary}

                STRICT AI CONTENT GROUNDING MANDATES:
                1. Extraction Priority:
                   - Priority 1: Submitted Invention Title
                   - Priority 2: Submitted Technical Description
                   - Priority 3: Closest Retrieved Prior-Art Patent
                2. Extract exactly 5 complete, professional engineering concepts (2-4 words each, e.g., 'Pressure Sensor Network', 'Acoustic Leak Detection', 'Edge AI Processing', 'Computer Vision Classification', 'Raspberry Pi Control Module', 'IoT Monitoring Module', 'Microfluidic Channel Architecture').
                3. EVIDENCE-BASED VALIDATION: Every extracted feature MUST be explicitly traceable to the submitted invention or retrieved prior art.
                   DO NOT invent or introduce unmentioned hardware, software, or technologies (such as blockchain, cryptographic routing, LoRa mesh, zero-trust identity, or computer vision unless explicitly stated in the input texts).
                4. For each feature, evaluate its technical differentiation against the closest prior art patent:
                   - "Shared": The mechanism or concept is substantially disclosed in the closest prior art (Score: 0).
                   - "Moderate Difference": Closest prior art contains an equivalent or related approach, but this invention incorporates specific modifications or alternative engineering parameters (Score: 10).
                   - "Strong Difference": The mechanism is structurally or methodologically absent from the closest prior art (Score: 20).
                5. Observation requirement: The observation MUST explain:
                   (a) how the feature appears in the proposed invention,
                   (b) whether it exists in prior art, and
                   (c) how the implementation differs.

                Respond strictly in valid JSON format:
                {{
                  "features": [
                    {{
                      "feature": "Dynamic engineering concept",
                      "prior_art_status": "Strong Difference",
                      "score": 20,
                      "observation": "Implemented in the invention as ...; prior art lacks this mechanism, resulting in ..."
                    }}
                  ]
                }}
                """

                response = model.generate_content(prompt)
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    res = json.loads(json_match.group(0))
                    feats = res.get("features", [])
                    if len(feats) == 5:
                        # Validation pass
                        validated_feats = []
                        for f in feats:
                            feat_name = str(f.get("feature", "")).strip()
                            if is_feature_grounded(feat_name, source_texts):
                                status = str(f.get("prior_art_status", "")).strip().title()
                                if "Strong" in status:
                                    status = "Strong Difference"
                                    score = 20
                                elif "Moderate" in status:
                                    status = "Moderate Difference"
                                    score = 10
                                else:
                                    status = "Shared"
                                    score = 0
                                f["feature"] = feat_name
                                f["prior_art_status"] = status
                                f["score"] = score
                                f["exists_in_prior_art"] = "Yes" if status == "Shared" else "No"
                                validated_feats.append(f)

                        if len(validated_feats) == 5:
                            total_score = sum(f["score"] for f in validated_feats)
                            common = [f["feature"] for f in validated_feats if f["prior_art_status"] == "Shared"]
                            unique = [f["feature"] for f in validated_feats if f["prior_art_status"] in ["Moderate Difference", "Strong Difference"]]
                            return {
                                "feature_score": float(total_score),
                                "feature_rubric": validated_feats,
                                "common_features": common,
                                "unique_features": unique
                            }
            except Exception as e:
                print(f"[FeatureExtractor] Gemini API fallback: {e}")

        # Deterministic dynamic grounded rubric fallback
        return self._dynamic_fallback_rubric(title, description, retrieved_patents)

    def _dynamic_fallback_rubric(
        self,
        title: str,
        description: str,
        retrieved_patents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Dynamically extracts complete engineering concepts strictly from the actual title,
        description, and closest prior art text. Never introduces unsupported buzzwords.
        """
        closest_patent = retrieved_patents[0] if retrieved_patents else {}
        closest_text = (
            str(closest_patent.get("title", "")) + " " +
            str(closest_patent.get("field_of_invention", "")) + " " +
            str(closest_patent.get("search_text", ""))
        ).lower()

        full_text = f"{title}. {description}".strip()
        full_lower = full_text.lower()
        source_texts = [title, description, closest_text]

        dynamic_features: List[str] = []

        # 1. Regex candidate extraction for technical noun compounds (Priority 1: Title, Priority 2: Description)
        # Match multi-word technical phrases like "Acoustic Leak Detection", "Pressure Sensor Network", etc.
        candidates = []
        for text_source in [title, description]:
            # Look for 2-4 word capitalized or technical noun combinations
            matches = re.findall(r'\b(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+\b', text_source)
            for m in matches:
                clean_m = m.strip()
                words = clean_m.split()
                if len(words) >= 2 and not any(w.lower() in STOPWORDS for w in words):
                    if clean_m not in candidates:
                        candidates.append(clean_m)

        # 2. Targeted engineering concept patterns only if keywords explicitly exist in user's text
        grounded_patterns = [
            (["acoustic", "leak", "pipeline", "water"], "Acoustic Leak Detection"),
            (["pressure", "sensor", "hydrostatic", "pipe"], "Pressure Sensor Network"),
            (["flow", "meter", "fluid", "hydraulic"], "Fluid Flow Monitoring Subsystem"),
            (["camera", "vision", "optical", "image", "visual", "inspection"], "Computer Vision Inspection"),
            (["edge", "ai", "inference", "embedded model"], "Edge AI Processing Unit"),
            (["microcontroller", "raspberry", "arduino", "mcu", "embedded"], "Embedded Controller Module"),
            (["servo", "actuator", "motor", "mechanical", "sorting"], "Servo-Based Actuation Mechanism"),
            (["iot", "telemetry", "wireless", "rf", "bluetooth", "wifi", "cellular"], "IoT Telemetry & Sensing Module"),
            (["biosensor", "sweat", "electrolyte", "microfluidic"], "Microfluidic Biosensing Module"),
            (["battery", "solar", "energy", "power management"], "Power Management & Energy Subsystem"),
            (["gps", "mapping", "coordinate", "location", "gis"], "GPS Mapping & Localization Module"),
            (["predictive", "maintenance", "fault", "diagnostic"], "Predictive Fault Diagnostic Module"),
        ]

        for keywords, concept_name in grounded_patterns:
            if any(k in full_lower for k in keywords):
                if concept_name not in dynamic_features:
                    dynamic_features.append(concept_name)
            if len(dynamic_features) >= 5:
                break

        # Incorporate extracted direct phrase candidates
        for c in candidates:
            if len(dynamic_features) >= 5:
                break
            if c not in dynamic_features and is_feature_grounded(c, source_texts):
                dynamic_features.append(c)

        # If still fewer than 5, build grounded modules strictly from words present in user input
        if len(dynamic_features) < 5:
            user_words = [
                w.title() for w in re.findall(r'[A-Za-z]{4,}', full_text)
                if w.lower() not in STOPWORDS
            ]
            suffixes = [
                "Control Architecture",
                "Sensing Network",
                "Processing Subsystem",
                "Interface Module",
                "Monitoring Mechanism"
            ]
            s_idx = 0
            for uw in user_words:
                cand = f"{uw} {suffixes[s_idx % len(suffixes)]}"
                if cand not in dynamic_features and is_feature_grounded(cand, source_texts):
                    dynamic_features.append(cand)
                    s_idx += 1
                if len(dynamic_features) >= 5:
                    break

        # Priority 3: Extract from closest retrieved prior art patent if still under 5
        if len(dynamic_features) < 5 and closest_patent:
            pat_words = [
                w.title() for w in re.findall(r'[A-Za-z]{4,}', closest_patent.get("title", ""))
                if w.lower() not in STOPWORDS
            ]
            for pw in pat_words:
                cand = f"{pw} Prior-Art Subsystem"
                if cand not in dynamic_features and is_feature_grounded(cand, source_texts):
                    dynamic_features.append(cand)
                if len(dynamic_features) >= 5:
                    break

        # Strict evidence-based validation: filter out any ungrounded feature
        validated_features = [f for f in dynamic_features if is_feature_grounded(f, source_texts)]

        rubric = []
        common = []
        unique = []
        total_score = 0

        for feat_name in validated_features[:5]:
            feat_lower_words = [w.lower() for w in feat_name.split() if w.lower() not in STOPWORDS]
            matches = sum(1 for w in feat_lower_words if w in closest_text)

            if matches >= 2:
                status = "Shared"
                score = 0
                obs = f"Implemented in the invention as {feat_name}; substantially disclosed in closest prior art."
                common.append(feat_name)
            elif matches == 1:
                status = "Moderate Difference"
                score = 10
                obs = f"Present in the invention as {feat_name}; prior art shares baseline principles but differs in implementation parameters."
                unique.append(feat_name)
            else:
                status = "Strong Difference"
                score = 20
                obs = f"Distinct technical configuration in the invention; structurally and methodologically absent from closest prior art."
                unique.append(feat_name)

            rubric.append({
                "feature": feat_name,
                "prior_art_status": status,
                "score": score,
                "observation": obs,
                "exists_in_prior_art": "Yes" if status == "Shared" else "No"
            })
            total_score += score

        return {
            "feature_score": float(total_score),
            "feature_rubric": rubric,
            "common_features": common,
            "unique_features": unique
        }

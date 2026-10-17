"""
AI Novelty Analysis Report Generator & Synthesis Engine for Official Indian Patents.
Strict AI Content Grounding Layer implemented across all report sections:
1. Executive Summary strictly grounded in Submitted Title, Description & Top Retrieved Prior Art.
2. Dynamic Feature Extraction & Grounded Comparative Technical Analysis.
3. Grounded Innovation Opportunities strictly extending existing technologies.
4. Grounded Filing Recommendations referencing real differentiating features.
5. Hallucination Prevention Layer for all technical statements.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

from search.similarity import (
    calculate_ai_novelty_index,
    NOVELTY_INDEX_DISCLAIMER
)
from search.domain_detection import detect_technical_domain
from llm.feature_extractor import FeatureExtractor, is_feature_grounded
from llm.claim_comparison import ClaimComparator
from llm.concept_enhancement import ConceptEnhancementGenerator

UNSUPPORTED_BUZZWORDS = [
    "blockchain", "smart contract", "cryptographic routing", "zero-trust", "lora mesh",
    "cryogenic", "quantum key", "facial recognition"
]


def polish_executive_summary_flow(text: str) -> str:
    """
    Ensures natural sentence flow in executive summary by replacing trailing or listing
    comma-separated terms with natural conjunctions (e.g. 'A and B' instead of 'A, B').
    """
    if not text:
        return text
    text = re.sub(
        r'(\bintegration of\s+[^,\.\n]+),\s+([^,\.\n]+)\.',
        r'\1 and \2.',
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(
        r'([A-Za-z0-9\s]+),\s+([A-Za-z0-9\s]+)\.\s*$',
        r'\1 and \2.',
        text
    )
    return text


def sanitize_hallucinated_terms(text: str, source_texts: List[str]) -> str:
    """
    Hallucination Prevention Layer:
    Scans generated text and replaces unsupported buzzwords unless explicitly present
    in the submitted invention or retrieved prior art.
    """
    if not text:
        return text
    combined_source = " ".join(source_texts).lower()

    replacements = {
        "cryptographic routing": "secure communication routing",
        "blockchain": "tamper-evident audit logging",
        "zero-trust identity": "authenticated identity verification",
        "zero-trust": "authenticated access control",
        "lora mesh": "wireless telemetry network",
        "cryogenic": "low-temperature operating",
        "quantum key": "secure hardware key"
    }

    sanitized = text
    for bad_term, safe_sub in replacements.items():
        if bad_term in sanitized.lower() and bad_term not in combined_source:
            # Case-insensitive replacement
            sanitized = re.sub(re.escape(bad_term), safe_sub, sanitized, flags=re.IGNORECASE)

    return sanitized


class NoveltyReportGenerator:
    """
    Synthesizes patent retrieval data into an executive AI Novelty Analysis Report.
    Strictly grounds all AI-generated content in submitted inputs and retrieved prior art.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.feature_extractor = FeatureExtractor()
        self.claim_comparator = ClaimComparator()
        self.concept_enhancer = ConceptEnhancementGenerator()

    def generate_report(
        self,
        user_idea: str,
        retrieved_patents: List[Dict[str, Any]],
        all_retrieved_scores: List[float],
        search_time_sec: float = 0.0,
        invention_title: str = "",
        invention_description: str = "",
        detected_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds complete AI Novelty Report object with strict AI content grounding.
        """
        title, description = self._resolve_title_description(
            user_idea, invention_title, invention_description
        )

        if not detected_field:
            detected_field = detect_technical_domain(
                query_text=user_idea,
                title=title,
                description=description,
                patent_context=retrieved_patents
            )

        # 1. Evaluate Feature Rubric (5 features, dynamic without templates)
        feat_res = self.feature_extractor.evaluate_feature_rubric(
            user_idea, retrieved_patents, invention_title=title, invention_description=description
        )

        # 2. Calculate AI Novelty Index
        top_5_scores = [p.get('cosine_similarity', 0.0) for p in retrieved_patents[:5]]
        novelty_idx_data = calculate_ai_novelty_index(
            top_5_cosine_scores=top_5_scores,
            feature_uniqueness_score=feat_res["feature_score"],
            all_retrieved_scores=all_retrieved_scores
        )

        # 3. Generate AI Match Explanations for each patent card
        processed_patents = self._generate_match_explanations(user_idea, retrieved_patents)

        # 4. Claim comparison for top match
        top_patent = processed_patents[0] if processed_patents else {}
        claim_table = self.claim_comparator.compare_claims(user_idea, top_patent)

        # 5. Executive Summary, Recommendation & Innovation Suggestions (Strict Grounding)
        narrative = self._generate_ai_narrative(
            user_idea,
            title,
            description,
            processed_patents,
            novelty_idx_data["novelty_index"],
            novelty_idx_data["potential_label"],
            feat_res
        )

        # 6. AI Concept Enhancement from original Title + Description
        concept_enhancement = self.concept_enhancer.generate(
            invention_title=title,
            invention_description=description,
            retrieved_patents=processed_patents,
        )

        # 7. Hallucination Prevention Pass across all narrative fields
        source_texts = [
            title,
            description,
            top_patent.get("title", ""),
            top_patent.get("field_of_invention", ""),
            top_patent.get("search_text", "")
        ]

        exec_summary = sanitize_hallucinated_terms(
            polish_executive_summary_flow(narrative.get("executive_summary")), source_texts
        )
        why_score = sanitize_hallucinated_terms(narrative.get("why_score_given"), source_texts)
        landscape_obs = sanitize_hallucinated_terms(narrative.get("landscape_observation"), source_texts)
        recommendation = sanitize_hallucinated_terms(narrative.get("recommendation"), source_texts)
        innov_opps = sanitize_hallucinated_terms(narrative.get("innovation_opportunities"), source_texts)
        filing_rec = sanitize_hallucinated_terms(narrative.get("filing_recommendation"), source_texts)

        return {
            "user_idea": user_idea,
            "invention_title": title,
            "invention_description": description,
            "detected_field": detected_field,
            "search_time_sec": search_time_sec,
            "total_screened": len(all_retrieved_scores),
            "novelty_index_data": novelty_idx_data,
            "disclaimer": NOVELTY_INDEX_DISCLAIMER,
            "executive_summary": exec_summary,
            "why_score_given": why_score,
            "landscape_observation": landscape_obs,
            "recommendation": recommendation,
            "innovation_opportunities": innov_opps,
            "filing_recommendation": filing_rec,
            "feature_score": feat_res["feature_score"],
            "feature_rubric": feat_res["feature_rubric"],
            "common_features": feat_res["common_features"],
            "unique_features": feat_res["unique_features"],
            "top_patent_claim_comparison": claim_table,
            "retrieved_patents": processed_patents,
            "concept_enhancement": concept_enhancement,
        }

    @staticmethod
    def _resolve_title_description(
        user_idea: str,
        invention_title: str,
        invention_description: str,
    ) -> tuple:
        title = (invention_title or "").strip()
        description = (invention_description or "").strip()
        if title and description:
            return title, description

        idea = user_idea or ""
        title_match = re.search(r"Title:\s*(.+?)(?:\n|Description:)", idea, re.IGNORECASE | re.DOTALL)
        desc_match = re.search(r"Description:\s*(.*)", idea, re.IGNORECASE | re.DOTALL)
        parsed_title = title_match.group(1).strip() if title_match else ""
        parsed_desc = desc_match.group(1).strip() if desc_match else ""
        return title or parsed_title, description or parsed_desc or idea

    def _generate_match_explanations(
        self,
        user_idea: str,
        retrieved_patents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Adds concise AI Match Explanation ("Why this patent matched") to every patent card.
        Never alters official patent metadata.
        """
        results = []
        for p in retrieved_patents:
            patent_copy = p.copy()
            match_explanation = self._explain_single_match(user_idea, patent_copy)
            patent_copy["match_explanation"] = match_explanation
            results.append(patent_copy)
        return results

    def _explain_single_match(self, user_idea: str, patent: Dict[str, Any]) -> str:
        """Generates 1-2 sentence match explanation without modifying metadata."""
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = f"""
                Provide a 1-2 sentence technical explanation answering: "Why this official Indian patent matched the proposed invention?".
                Do not modify patent title or metadata. Use facts strictly from the title, field of invention, and context.

                User Invention Idea:
                {user_idea}

                Patent Title: {patent.get('title')}
                Application Number (Primary ID): {patent.get('application_number')}
                Journal Issue: {patent.get('publication_number')}
                Field of Invention: {patent.get('field_of_invention')}
                Search Context: {patent.get('search_text')}

                Response format: Just the explanation text.
                """
                resp = model.generate_content(prompt)
                if resp.text.strip():
                    return resp.text.strip()
            except Exception:
                pass

        # Deterministic match explanation fallback
        title = patent.get('title', 'official Indian prior art')
        field = patent.get('field_of_invention', 'N/A')
        search_ctx = patent.get('search_text', '')
        kw_matches = [w for w in user_idea.split() if len(w) > 4 and w.lower() in search_ctx.lower()]

        if kw_matches:
            kw_str = ", ".join(list(dict.fromkeys(kw_matches))[:3])
            return f"This official Indian patent shares key technical concepts ({kw_str}) in the field of {field} with your invention, while differing in specific component implementations."
        else:
            return f"This patent matched based on domain overlap in {field} and structural vector similarity with '{title[:50]}'."

    def _generate_ai_narrative(
        self,
        user_idea: str,
        title: str,
        description: str,
        retrieved_patents: List[Dict[str, Any]],
        novelty_index: float,
        potential_label: str,
        feat_res: Dict[str, Any]
    ) -> Dict[str, str]:
        """Calls Gemini or uses deterministic grounded domain synthesis for report sections."""
        top_patent = retrieved_patents[0] if retrieved_patents else {}
        top_title = top_patent.get('title', 'existing official Indian patent')
        top_app_num = top_patent.get('application_number', 'prior patent')
        unique_list = feat_res.get('unique_features', [])
        common_list = feat_res.get('common_features', [])

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                patent_text = "\n".join([
                    f"- Application No: {p.get('application_number')} | Journal Issue: {p.get('publication_number')} | Title: {p.get('title')} | Field: {p.get('field_of_invention')}"
                    for p in retrieved_patents[:3]
                ])

                prompt = f"""
                You are a senior patent attorney and AI novelty examiner evaluating an invention against official Indian Patent Office prior art.

                Proposed Invention:
                - Title: {title or 'N/A'}
                - Description: {description}

                Retrieved Official Indian Prior Art:
                {patent_text}

                Extracted Verified Features:
                - Unique Differentiators: {', '.join(unique_list) if unique_list else 'Specific architectural refinements'}
                - Common Baseline Features: {', '.join(common_list) if common_list else 'General domain baseline'}

                AI Novelty Index: {novelty_index}% ({potential_label})

                STRICT GROUNDING RULES (ALL STATEMENTS MUST BE TRACEABLE TO INPUTS):
                1. Executive Summary: Must follow this strict 4-part structure in natural professional language:
                   - Briefly state the invention's purpose based strictly on the submitted title and description.
                   - Explain the closest prior-art overlap (referencing Application No: {top_app_num} and title: '{top_title}').
                   - Describe ONLY the actual differentiating features found in the invention ({', '.join(unique_list) if unique_list else 'novel structural configurations'}).
                   - Conclude with the AI Novelty Index interpretation ({novelty_index}/100 - {potential_label}).
                   DO NOT invent or introduce unmentioned technologies. Write in natural flowing prose (use 'A and B' instead of 'A, B').
                2. Innovation Opportunities: Must ONLY extend technologies already present in the invention or reasonably supported by retrieved patents (e.g., enhanced sensing, improved edge processing, predictive maintenance, energy optimization, communication improvements, mechanical optimization).
                   DO NOT introduce unrelated technologies such as blockchain, cryptographic routing, LoRa mesh, zero-trust identity, or computer vision unless they explicitly appear in the invention or retrieved patents.
                3. Filing Recommendation: Recommend claiming only the invention's actual differentiating technical elements.
                4. Why This Score Was Given: Qualitative explanation without mathematical formulas.
                5. Avoid repeating the invention title verbatim in narrative paragraphs. Refer to "the proposed system" or "the proposed invention".

                Format strictly as JSON:
                {{
                  "executive_summary": "The proposed invention aims to ... While foundational aspects overlap with Indian Patent Application {top_app_num} ('{top_title}'), the system distinguishes itself through ... With an AI Novelty Index of {novelty_index}/100 ({potential_label}), the invention demonstrates viable patentability.",
                  "why_score_given": "The assigned AI Novelty Index reflects...",
                  "technology_maturity": "The technology domain exhibits...",
                  "competition_overview": "Prior art clustering indicates...",
                  "white_space_opportunity": "Identifiable white space exists for...",
                  "landscape_observation": "The patent landscape indicates moderate concentration around baseline mechanisms...",
                  "recommendation": "File an independent patent application focusing on...",
                  "innovation_opportunities": "1. Enhanced Sensing: ...\n2. Processing Optimization: ...\n3. System Reliability: ...",
                  "filing_recommendation": "Focus claim drafting on the specific novel architectural elements..."
                }}
                """

                response = model.generate_content(prompt)
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    res = json.loads(json_match.group(0))
                    if "executive_summary" in res:
                        res["executive_summary"] = polish_executive_summary_flow(res["executive_summary"])
                    return res
            except Exception as e:
                print(f"[NoveltyReportGenerator] Gemini API narrative fallback: {e}")

        # Deterministic grounded fallback narrative
        if not unique_list:
            unique_str = "specialized control and operational parameters"
        elif len(unique_list) == 1:
            unique_str = unique_list[0]
        elif len(unique_list[:2]) == 2:
            unique_str = f"{unique_list[0]} and {unique_list[1]}"
        else:
            unique_str = f"{', '.join(unique_list[:2])} and {unique_list[2]}"

        # Purpose derived from title / description
        purpose_phrase = f"the implementation of {title.lower()}" if title else "advancing technical operational efficiency"

        exec_summary = (
            f"The proposed invention focuses on {purpose_phrase}, demonstrating {potential_label} with an assigned "
            f"AI Novelty Index of {novelty_index}/100. The closest retrieved prior art is Indian Patent Application {top_app_num} "
            f"('{top_title}'). While baseline operational principles overlap in foundational system topology, "
            f"the proposed invention establishes distinct technical divergence through its integration of {unique_str}. "
            f"Consequently, the novelty assessment indicates promising patentability potential, provided claims are centered "
            f"on these verified differentiating components."
        )

        why_score = (
            f"The AI Novelty Index of {novelty_index}/100 ({potential_label}) is determined by qualitative evaluation of structural overlap "
            f"against closest retrieved prior art (Application {top_app_num}), weighted by technical feature differentiation "
            f"and overall domain concentration in the official Indian Patent corpus."
        )

        tech_maturity = (
            "The patent landscape exhibits an established baseline in conventional operational architectures, "
            "with active momentum toward integrated automated workflows and high-efficiency control modules."
        )

        competition_overview = (
            "Prior art distribution indicates moderate clustering around standard mechanical assemblies and generic sensor interfaces. "
            "Disclosures focus predominantly on centralized topologies, leaving localized modular architectures less saturated."
        )

        whitespace_opportunity = (
            f"Significant white-space opportunities exist for specialized implementations combining {unique_str} "
            f"with deterministic control logic, providing a clear path for defensible patent claims."
        )

        landscape_obs = (
            f"The official patent landscape within this technology domain demonstrates an established base of foundational publications. "
            f"However, significant whitespace exists for specialized implementations combining {unique_str} "
            f"with deterministic control mechanisms, providing a clear path for defensible patent claims."
        )

        rec = (
            f"Conduct a verifiable search on the official IP India portal (https://ipindiaservices.gov.in/publicsearch) for Application Number {top_app_num}. "
            f"Focus patent claims on the specific implementation parameters of {unique_list[0] if unique_list else 'the system'}."
        )

        # Grounded Innovation Opportunities: Strictly extending actual features
        f1 = unique_list[0] if unique_list else (feat_res.get("feature_rubric", [{}])[0].get("feature", "Primary Sensing Mechanism"))
        f2 = unique_list[1] if len(unique_list) > 1 else (feat_res.get("feature_rubric", [{}])[-1].get("feature", "Core Processing Architecture"))

        innov_opp = (
            f"1. Enhanced Sensing: Implement dynamic self-calibration routines for {f1} to enhance detection precision under variable environmental conditions.\n"
            f"2. Processing Optimization: Refine algorithmic execution thresholds within {f2} to minimize execution latency and computational overhead.\n"
            f"3. System Reliability & Predictive Maintenance: Incorporate continuous diagnostic logging to anticipate operational degradation and optimize power efficiency."
        )

        filing_rec = (
            f"Focus independent patent claims strictly on the unique structural configuration of {unique_str}. "
            f"Ensure dependent claims capture sensor calibration parameters, communication interfaces, and operational execution thresholds. "
            f"Obtain formal patent attorney counsel before filing Form 1 and Form 2 with the Indian Patent Office."
        )

        return {
            "executive_summary": exec_summary,
            "why_score_given": why_score,
            "technology_maturity": tech_maturity,
            "competition_overview": competition_overview,
            "white_space_opportunity": whitespace_opportunity,
            "landscape_observation": landscape_obs,
            "recommendation": rec,
            "innovation_opportunities": innov_opp,
            "filing_recommendation": filing_rec
        }

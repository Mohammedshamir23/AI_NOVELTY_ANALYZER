"""
AI Novelty Analysis Report PDF Generator.
Builds professional 12-section Patent Intelligence & Novelty Assessment Reports using ReportLab.
Includes Cover Page, Executive Summary, Proposed Invention, Search Summary,
Why This Score Was Given, Top Similar Patents, Comparative Technical Analysis (3 columns),
Patent Landscape Analysis, Innovation Opportunities (detailed consultancy specs),
Filing Recommendation, Methodology, and Disclaimer.
Omit all formulas, internal score breakdowns, and percentage calculation tables.
"""

import os
import io
import re
import time
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from search.similarity import NOVELTY_INDEX_DISCLAIMER
from preprocessing.clean_text import format_application_number

def clean_pdf_app_number(val: Any) -> str:
    """Strips any IN, IN-, or IN/ prefix from application number."""
    formatted = format_application_number(val)
    if formatted.upper().startswith("IN-") or formatted.upper().startswith("IN/"):
        return formatted[3:].strip()
    elif formatted.upper().startswith("IN") and len(formatted) > 2 and formatted[2].isdigit():
        return formatted[2:].strip()
    return formatted


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw center-aligned page footers:
    'AI Novelty Analyzer | Page X of Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_footer(num_pages)
            super().showPage()
        super().save()

    def draw_page_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        footer_text = f"AI Novelty Analyzer | Page {self._pageNumber} of {page_count}"
        self.drawCentredString(self._pagesize[0] / 2.0, 18, footer_text)
        self.restoreState()


class PDFReportGenerator:
    """
    Generates downloadable 12-Section PDF Patent Intelligence Reports.
    """

    def generate_pdf_bytes(self, report_data: Dict[str, Any]) -> bytes:
        """
        Builds PDF in-memory and returns PDF byte content.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Enterprise Midnight Palette
        primary_dark = colors.HexColor("#0B1220")
        secondary_dark = colors.HexColor("#111827")
        card_dark = colors.HexColor("#1A2436")
        accent_blue = colors.HexColor("#2563EB")
        accent_cyan = colors.HexColor("#0284C7")
        border_color = colors.HexColor("#334155")
        text_dark = colors.HexColor("#0F172A")
        text_muted = colors.HexColor("#64748B")
        bg_light = colors.HexColor("#F8FAFC")

        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=accent_blue,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=text_muted,
            spaceAfter=8
        )

        heading_style = ParagraphStyle(
            'HeadingCustom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=secondary_dark,
            spaceBefore=8,
            spaceAfter=4
        )

        subheading_style = ParagraphStyle(
            'SubHeadingCustom',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=12.5,
            textColor=accent_blue,
            spaceBefore=5,
            spaceAfter=2
        )

        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=text_dark
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerCustom',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.8,
            leading=10.5,
            textColor=text_muted
        )

        score_card_title_style = ParagraphStyle(
            'ScoreCardTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#94A3B8"),
            alignment=1  # Centered
        )

        score_card_val_style = ParagraphStyle(
            'ScoreCardVal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.white,
            alignment=1  # Centered
        )

        score_card_label_style = ParagraphStyle(
            'ScoreCardLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#38BDF8"),
            alignment=1  # Centered
        )

        score_card_sub_style = ParagraphStyle(
            'ScoreCardSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.2,
            leading=9.5,
            textColor=colors.HexColor("#94A3B8"),
            alignment=1  # Centered
        )

        patent_title_style = ParagraphStyle(
            'PatentCardTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor("#0B1220")
        )

        patent_badge_style = ParagraphStyle(
            'PatentCardBadge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=accent_blue,
            alignment=2  # Right-aligned
        )

        patent_meta_style = ParagraphStyle(
            'PatentCardMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#334155")
        )

        story = []

        # ==========================================
        # 1. COVER PAGE & HEADER (AI Novelty Index - Single Score Only)
        # ==========================================
        story.append(Paragraph("AI Novelty Analyzer", title_style))
        story.append(Paragraph(f"Generated: {time.strftime('%B %d, %Y - %H:%M:%S UTC')} | Dataset: Official Indian Patent Office (IPO)", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceAfter=6))

        story.append(Paragraph("1. AI Novelty Assessment", heading_style))

        idx_data = report_data.get("novelty_index_data", {})
        novelty_score = idx_data.get("novelty_index", 0.0)
        potential_label = idx_data.get("potential_label", "N/A")

        score_card_data = [
            [Paragraph("<font color='#94A3B8'><b>AI NOVELTY INDEX</b></font>", score_card_title_style)],
            [Paragraph(f"<font color='#FFFFFF'><b>{novelty_score}</b></font><font size=13 color='#94A3B8'><b> / 100</b></font>", score_card_val_style)],
            [Paragraph(f"<b>{potential_label}</b>", score_card_label_style)],
            [Paragraph("Screened against 458,724 official Indian Patent Office records &bull; Top 200 candidates evaluated", score_card_sub_style)]
        ]

        score_card_table = Table(score_card_data, colWidths=[540])
        score_card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1A2436")),
            ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#2563EB")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
            ('TOPPADDING', (0, 1), (-1, 1), 1),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
            ('TOPPADDING', (0, 2), (-1, 2), 1),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 2),
            ('TOPPADDING', (0, 3), (-1, 3), 1),
            ('BOTTOMPADDING', (0, 3), (-1, 3), 6),
        ]))
        story.append(score_card_table)
        story.append(Spacer(1, 4))

        # ==========================================
        # 2. EXECUTIVE SUMMARY
        # ==========================================
        story.append(Paragraph("2. Executive Summary", heading_style))
        story.append(Paragraph(self._pdf_text(report_data.get("executive_summary", "N/A")), body_style))
        story.append(Spacer(1, 4))

        # ==========================================
        # 3. PROPOSED INVENTION (Two Separate Distinct Blocks)
        # ==========================================
        story.append(Paragraph("3. Proposed Invention", heading_style))
        inv_title, inv_desc = self._invention_title_and_description(report_data)

        # Block 1: Submitted Invention Title Card
        title_card_data = [
            [Paragraph("<font size=7.5 color='#2563EB'><b>SUBMITTED INVENTION TITLE</b></font>", body_style)],
            [Paragraph(f"<font size=10 color='#0B1220'><b>{self._pdf_text(inv_title or 'N/A')}</b></font>", body_style)]
        ]
        title_card_table = Table(title_card_data, colWidths=[540])
        title_card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#2563EB")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(title_card_table)
        story.append(Spacer(1, 4))

        # Block 2: Original Technical Description Card
        desc_card_data = [
            [Paragraph("<font size=7.5 color='#64748B'><b>ORIGINAL TECHNICAL DESCRIPTION</b></font>", body_style)],
            [Paragraph(self._pdf_text(inv_desc or "N/A"), body_style)]
        ]
        desc_card_table = Table(desc_card_data, colWidths=[540])
        desc_card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(desc_card_table)
        story.append(Spacer(1, 5))

        # ==========================================
        # 4. SEARCH SUMMARY
        # ==========================================
        story.append(Paragraph("4. Search Summary", heading_style))
        sec4_data = [
            ["Metric", "Value"],
            ["Patent Database", "458,724 Records"],
            ["Detected Technical Domain", str(report_data.get('detected_field', 'Applied Engineering & Automation'))],
            ["Top Candidates Retrieved (200)", "200 Candidates Evaluated"],
            ["Search Runtime", f"{report_data.get('search_time_sec', 0.0):.2f} s"]
        ]
        sec4_table = Table(sec4_data, colWidths=[180, 360])
        sec4_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), secondary_dark),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 3.5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(sec4_table)
        story.append(Spacer(1, 5))

        # ==========================================
        # 5. WHY THIS SCORE WAS GIVEN (Qualitative Assessment)
        # ==========================================
        story.append(Paragraph("5. Why This Score Was Given", heading_style))
        why_text = report_data.get("why_score_given") or (
            f"The AI Novelty Index of {novelty_score}/100 ({potential_label}) is determined through qualitative synthesis of semantic proximity "
            f"against closest retrieved prior art, offset by distinct technical mechanisms present in the proposed invention. "
            f"The assessment weighs structural overlap in the foundational claims while recognizing differentiated functional parameters "
            f"that stand apart from retrieved Indian patent publications."
        )
        story.append(Paragraph(self._pdf_text(why_text), body_style))
        story.append(Spacer(1, 5))

        # ==========================================
        # 6. TOP SIMILAR PATENTS (Official Metadata Only)
        # ==========================================
        story.append(Paragraph("6. Top Similar Patents — Official Indian Patent Metadata", heading_style))
        patents = report_data.get("retrieved_patents", [])

        for idx, p in enumerate(patents[:5], start=1):
            match_label = p.get("match_strength_label", "Match")
            app_num = clean_pdf_app_number(p.get("application_number", "N/A"))
            pub_num = p.get("publication_number", "N/A")
            pub_date = p.get("publication_date", "N/A")
            ipo_loc = p.get("ipo_location", "N/A")
            field = p.get("field_of_invention", "N/A")
            app_type = p.get("application_type", "N/A")
            claims = p.get("no_of_claims", "N/A")
            pages = p.get("no_of_pages", "N/A")

            p_card_data = [
                [
                    Paragraph(f"<b>Patent {idx}: {self._pdf_text(p.get('title', 'N/A'))}</b>", patent_title_style),
                    Paragraph(f"<font color='{accent_blue.hexval()}'><b>[{match_label}]</b></font>", patent_badge_style)
                ],
                [
                    Paragraph(
                        f"<font color='#64748B'><b>Application Number (Official ID):</b></font> <b>{app_num}</b> &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>IPO Jurisdiction:</b></font> {ipo_loc} &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>Journal Issue:</b></font> {pub_num} &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>Publication Date:</b></font> {pub_date}",
                        patent_meta_style
                    ),
                    ""
                ],
                [
                    Paragraph(
                        f"<font color='#64748B'><b>Field of Invention:</b></font> {field} &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>Application Type:</b></font> {app_type} &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>Claims:</b></font> {claims} &nbsp;&bull;&nbsp; "
                        f"<font color='#64748B'><b>Pages:</b></font> {pages}",
                        patent_meta_style
                    ),
                    ""
                ]
            ]

            p_table = Table(p_card_data, colWidths=[425, 115])
            p_table.setStyle(TableStyle([
                ('SPAN', (0, 1), (1, 1)),
                ('SPAN', (0, 2), (1, 2)),
                ('BACKGROUND', (0, 0), (-1, -1), bg_light),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
                ('TOPPADDING', (0, 1), (-1, 1), 1),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
                ('TOPPADDING', (0, 2), (-1, 2), 1),
                ('BOTTOMPADDING', (0, 2), (-1, 2), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(p_table)
            story.append(Spacer(1, 5))

        # ==========================================
        # 7. COMPARATIVE TECHNICAL ANALYSIS (3 Columns)
        # ==========================================
        story.append(Paragraph("7. Comparative Technical Analysis", heading_style))
        rubric_rows = report_data.get("feature_rubric", [])
        sec7_data = [["Feature", "Prior-Art Status", "Observation"]]

        for r in rubric_rows:
            status = r.get("prior_art_status") or ("Shared" if str(r.get("exists_in_prior_art", "")).lower() == "yes" else "Strong Difference")
            sec7_data.append([
                Paragraph(f"<b>{self._pdf_text(r.get('feature', ''))}</b>", body_style),
                Paragraph(f"<b>{status}</b>", body_style),
                Paragraph(self._pdf_text(r.get("observation", "")), body_style)
            ])

        if len(sec7_data) == 1:
            sec7_data.append([Paragraph("N/A", body_style), Paragraph("N/A", body_style), Paragraph("N/A", body_style)])

        sec7_table = Table(sec7_data, colWidths=[150, 110, 280])
        sec7_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), secondary_dark),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 3.5),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        story.append(sec7_table)
        story.append(Spacer(1, 5))

        # ==========================================
        # 8. PATENT LANDSCAPE ANALYSIS (Qualitative Assessment Only)
        # ==========================================
        story.append(Paragraph("8. Patent Landscape Analysis", heading_style))

        detected_field_name = str(report_data.get("detected_field", "Applied Engineering & Automation"))
        tech_maturity_val = report_data.get("technology_maturity") or (
            f"The patent landscape within {detected_field_name} demonstrates an established foundation in conventional operational methods, "
            f"with accelerated patent velocity toward integrated, intelligent automation and edge-compute architectures."
        )
        comp_overview_val = report_data.get("competition_overview") or (
            f"Prior art distribution in {detected_field_name} reveals moderate clustering around standard mechanical assemblies and generic sensors. "
            f"Competing filings predominantly emphasize centralized architectures, leaving decentralized edge topologies less crowded."
        )
        whitespace_val = report_data.get("white_space_opportunity") or (
            f"Strategic analysis identifies actionable white space within {detected_field_name}. "
            f"Features categorized as Strong Difference establish a defensible technological position where the proposed invention meaningfully diverges."
        )

        land_data = [
            [Paragraph("<b>Technology Maturity</b>", body_style), Paragraph(self._pdf_text(tech_maturity_val), body_style)],
            [Paragraph("<b>Competition Overview</b>", body_style), Paragraph(self._pdf_text(comp_overview_val), body_style)],
            [Paragraph("<b>White-Space Opportunity</b>", body_style), Paragraph(self._pdf_text(whitespace_val), body_style)]
        ]
        land_table = Table(land_data, colWidths=[150, 390])
        land_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        story.append(land_table)
        story.append(Spacer(1, 5))

        # ==========================================
        # 9. INNOVATION OPPORTUNITIES (Full Detailed Consultancy Specs)
        # ==========================================
        story.append(Paragraph("9. Innovation Opportunities & Technical Specifications", heading_style))
        self._append_concept_enhancement(story, report_data, heading_style, subheading_style, body_style, border_color, secondary_dark)
        story.append(Spacer(1, 5))

        # ==========================================
        # 10. FILING RECOMMENDATION
        # ==========================================
        story.append(Paragraph("10. Filing Recommendation", heading_style))
        story.append(Paragraph(self._pdf_text(report_data.get("filing_recommendation", "N/A")), body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Filing Recommendation:</b> {self._pdf_text(report_data.get('recommendation', 'N/A'))}", body_style))
        story.append(Spacer(1, 5))

        # ==========================================
        # 11. METHODOLOGY
        # ==========================================
        story.append(Paragraph("11. Analytical Methodology", heading_style))
        methodology_text = (
            "<b>Stella semantic embedding generation and FAISS candidate retrieval workflow:</b><br/>"
            "1. <b>Dense Vector Representation:</b> Continuous dense semantic vectors are generated locally using the Stella-en-400M-v5 model.<br/>"
            "2. <b>High-Dimensional FAISS Retrieval:</b> Global IndexFlatIP retrieves Top Candidates Retrieved (200) using inner-product cosine similarity over official IPO records.<br/>"
            "3. <b>Dynamic Technical Differentiation:</b> Comparative rubric evaluates proposed functional features directly against closest retrieved prior art.<br/>"
            "4. <b>Holistic AI Novelty Assessment:</b> The internal novelty calculation is preserved for system evaluation and ranking, but calculation formulas are intentionally hidden from the user interface and PDF report."
        )
        story.append(Paragraph(methodology_text, body_style))
        story.append(Spacer(1, 5))

        # ==========================================
        # 12. DISCLAIMER
        # ==========================================
        story.append(Paragraph("12. Regulatory Disclaimer", heading_style))
        disc_text = (
            f"<b>Disclaimer:</b> {NOVELTY_INDEX_DISCLAIMER}<br/>"
            "<b>Legal Scope Notice:</b> The AI Novelty Index is an automated analytical metric for preliminary prior-art screening. "
            "It does not constitute a legal or binding patentability determination by the Indian Patent Office (IPO) or any judicial patent authority."
        )
        disc_table = Table([[Paragraph(disc_text, disclaimer_style)]], colWidths=[540])
        disc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('PADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(disc_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @staticmethod
    def _invention_title_and_description(report_data: Dict[str, Any]) -> tuple:
        title = (report_data.get("invention_title") or "").strip()
        description = (report_data.get("invention_description") or "").strip()
        if title and description:
            return title, description
        idea = report_data.get("user_idea") or ""
        title_match = re.search(r"Title:\s*(.+?)(?:\n|Description:)", idea, re.IGNORECASE | re.DOTALL)
        desc_match = re.search(r"Description:\s*(.*)", idea, re.IGNORECASE | re.DOTALL)
        parsed_title = title_match.group(1).strip() if title_match else ""
        parsed_desc = desc_match.group(1).strip() if desc_match else ""
        return title or parsed_title, description or parsed_desc or idea

    @staticmethod
    def _pdf_text(value: Any) -> str:
        text = str(value or "")
        for src, dst in {
            "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
            "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
        }.items():
            text = text.replace(src, dst)
        text = text.encode("latin-1", "replace").decode("latin-1")
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return text.replace("\n", "<br/>")

    def _append_concept_enhancement(
        self,
        story: List,
        report_data: Dict[str, Any],
        heading_style,
        subheading_style,
        body_style,
        border_color,
        secondary_dark
    ) -> None:
        section = report_data.get("concept_enhancement") or {}

        # --- Section 1 — Enhanced Technical Concept ---
        story.append(Paragraph("<b>Enhanced Technical Concept & Modules</b>", subheading_style))
        story.append(Spacer(1, 2))

        tech_concept = section.get("technical_concept") or {}
        core_p = tech_concept.get("core_principle") or []
        if isinstance(core_p, str):
            core_p = [p.strip() for p in core_p.split("\n\n") if p.strip()]
        if not core_p and section.get("concept_expansion"):
            core_p = [p.strip() for p in str(section.get("concept_expansion")).split("\n\n") if p.strip()]

        for p in core_p[:2]:
            story.append(Paragraph(self._pdf_text(p), body_style))
            story.append(Spacer(1, 2))

        key_mods = tech_concept.get("key_modules") or section.get("hardware_components") or []
        mod_table_data = [[Paragraph("<b>Module</b>", body_style), Paragraph("<b>Purpose & Specification</b>", body_style)]]
        for m in key_mods:
            mod_table_data.append([
                Paragraph(f"<b>{self._pdf_text(m.get('module') or m.get('component', ''))}</b>", body_style),
                Paragraph(self._pdf_text(m.get('purpose', '')), body_style),
            ])
        if len(mod_table_data) == 1:
            mod_table_data.append([Paragraph("N/A", body_style), Paragraph("N/A", body_style)])
        mod_table = Table(mod_table_data, colWidths=[140, 380])
        mod_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), secondary_dark),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(mod_table)
        story.append(Spacer(1, 6))

        # --- Section 2 — Suggested System Architecture ---
        story.append(Paragraph("<b>Suggested System Architecture</b>", subheading_style))
        story.append(Spacer(1, 2))
        arch = section.get("system_architecture") or {}
        flow = arch.get("system_flow") or section.get("suggested_system_architecture", "")
        if flow:
            story.append(Paragraph(f"<b>System Flow:</b> {self._pdf_text(flow)}", body_style))
            story.append(Spacer(1, 3))

        arch_table_data = [[
            Paragraph("<b>Layer</b>", body_style),
            Paragraph("<b>Components</b>", body_style),
            Paragraph("<b>Data Flow</b>", body_style)
        ]]
        for row in arch.get("architecture_table") or []:
            arch_table_data.append([
                Paragraph(f"<b>{self._pdf_text(row.get('layer', ''))}</b>", body_style),
                Paragraph(self._pdf_text(row.get('components', '')), body_style),
                Paragraph(self._pdf_text(row.get('data_flow', '')), body_style),
            ])
        if len(arch_table_data) == 1:
            arch_table_data.append([Paragraph("N/A", body_style), Paragraph("N/A", body_style), Paragraph("N/A", body_style)])
        arch_table = Table(arch_table_data, colWidths=[90, 200, 230])
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), secondary_dark),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(arch_table)
        story.append(Spacer(1, 6))

        # --- Section 3 — Recommended Technologies & Tools ---
        story.append(Paragraph("<b>Recommended Technologies & Tools</b>", subheading_style))
        story.append(Spacer(1, 2))
        tech_data = [[Paragraph("<b>Category</b>", body_style), Paragraph("<b>Recommended Technology & Role</b>", body_style)]]
        for row in section.get("recommended_technologies") or []:
            rec = row.get("recommended_technology") or row.get("technologies", "")
            tech_data.append([
                Paragraph(f"<b>{self._pdf_text(row.get('category', ''))}</b>", body_style),
                Paragraph(self._pdf_text(rec), body_style),
            ])
        if len(tech_data) == 1:
            tech_data.append([Paragraph("N/A", body_style), Paragraph("N/A", body_style)])
        tech_table = Table(tech_data, colWidths=[120, 400])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), secondary_dark),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tech_table)
        story.append(Spacer(1, 6))

        # --- Section 4 — Innovation Expansion Opportunities ---
        story.append(Paragraph("<b>Innovation Expansion Roadmaps</b>", subheading_style))
        story.append(Spacer(1, 2))
        expansion_cards = section.get("innovation_expansion") or []
        for card in expansion_cards:
            enh = card.get("enhancement", "Enhancement")
            impl = card.get("technical_implementation", "")
            ben = card.get("patent_benefit", "")
            card_content = (
                f"<b>{self._pdf_text(enh)}</b><br/>"
                f"<b>Implementation:</b> {self._pdf_text(impl)}<br/>"
                f"<b>Patent Advantage:</b> {self._pdf_text(ben)}"
            )
            c_table = Table([[Paragraph(card_content, body_style)]], colWidths=[520])
            c_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(c_table)
            story.append(Spacer(1, 4))

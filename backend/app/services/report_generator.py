"""
Service: Report Generator
Responsibility:
    Synthesizes claims, evidence levels, and verification verdicts into a
    cohesive structured report with overall citation reliability scoring.

Formula:
    Reliability Score = (
        1.0 * count(SUPPORTED) +
        0.7 * count(PARTLY_SUPPORTED) +
        0.5 * count(POTENTIALLY_OUTDATED) +
        0.3 * count(UNVERIFIED) +
        0.0 * count(UNSUPPORTED) -
        0.2 * count(CONTRADICTORY)
    ) / total_claims * 100.0, clamped to [0.0, 100.0].
"""
import io
from datetime import datetime, timezone
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from app.schemas.document import Document
from app.schemas.claim import Claim
from app.schemas.report import VerificationReport
from app.schemas.enums import VerificationVerdict, EvidenceLevel


def calculate_reliability_score(claims: List[Claim]) -> float:
    """
    Computes weighted reliability score on a 0.0 - 100.0 scale.
    """
    if not claims:
        return 100.0

    score_weights = {
        VerificationVerdict.SUPPORTED: 1.0,
        VerificationVerdict.PARTLY_SUPPORTED: 0.7,
        VerificationVerdict.POTENTIALLY_OUTDATED: 0.5,
        VerificationVerdict.UNSUPPORTED: 0.0,
        VerificationVerdict.CONTRADICTORY: -0.2,
    }

    total_weight = 0.0
    for claim in claims:
        if claim.verdict and claim.verdict in score_weights:
            total_weight += score_weights[claim.verdict]
        else:
            # Unverified / unable to verify / null
            total_weight += 0.3

    raw_percentage = (total_weight / len(claims)) * 100.0
    return round(max(0.0, min(100.0, raw_percentage)), 1)


def generate_verification_report(
    document: Document,
    claims: List[Claim],
) -> VerificationReport:
    """
    Synthesizes metrics, aggregate counts, and compiles the final VerificationReport.
    """
    now = datetime.now(timezone.utc)
    total_claims = len(claims)

    verdict_counts: Dict[str, int] = {v.value: 0 for v in VerificationVerdict}
    verdict_counts["UNVERIFIED"] = 0

    evidence_level_counts: Dict[str, int] = {
        EvidenceLevel.FULL_TEXT.value: 0,
        EvidenceLevel.ABSTRACT_ONLY.value: 0,
        EvidenceLevel.METADATA_ONLY.value: 0,
        EvidenceLevel.NONE.value: 0,
    }

    human_review_count = 0

    for claim in claims:
        if claim.verdict:
            verdict_counts[claim.verdict.value] += 1
        else:
            verdict_counts["UNVERIFIED"] += 1

        if claim.needs_human_review:
            human_review_count += 1

        if claim.evidence:
            for ev in claim.evidence:
                lvl = ev.evidence_level.value
                evidence_level_counts[lvl] = evidence_level_counts.get(lvl, 0) + 1
        else:
            evidence_level_counts[EvidenceLevel.NONE.value] += 1

    reliability = calculate_reliability_score(claims)

    return VerificationReport(
        document_id=document.id,
        filename=document.filename,
        generated_at=now,
        total_claims=total_claims,
        reliability_score=reliability,
        verdict_counts=verdict_counts,
        evidence_level_counts=evidence_level_counts,
        human_review_required_count=human_review_count,
        claims=claims,
    )


def generate_pdf_report(report: VerificationReport) -> bytes:
    """
    Generates a professional academic PDF audit report from a VerificationReport.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("CiteVerify AI — Verification Audit Report", title_style))
    story.append(
        Paragraph(
            f"Document: <b>{report.filename}</b> &nbsp;|&nbsp; ID: {report.document_id} &nbsp;|&nbsp; Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            subtitle_style,
        )
    )
    story.append(Spacer(1, 10))

    # Executive Summary Card
    score_color = colors.HexColor("#16a34a") if report.reliability_score >= 70 else (
        colors.HexColor("#d97706") if report.reliability_score >= 40 else colors.HexColor("#dc2626")
    )
    summary_data = [
        [
            Paragraph("<b>Overall Citation Reliability Score</b>", body_style),
            Paragraph(f"<b><font size=16 color='{score_color.hexval()}'>{report.reliability_score}%</font></b>", body_style),
        ],
        [
            Paragraph("<b>Total Extracted Claims</b>", body_style),
            Paragraph(str(report.total_claims), body_style),
        ],
        [
            Paragraph("<b>Human Review Required</b>", body_style),
            Paragraph(f"<font color='#dc2626'><b>{report.human_review_required_count}</b></font>", body_style),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[240, 290])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Verdict Distributions Table
    story.append(Paragraph("Verification Verdicts Breakdown", h2_style))
    verdict_rows = [["Verdict", "Count", "Percentage"]]
    for k, v in report.verdict_counts.items():
        pct = f"{(v / report.total_claims * 100):.1f}%" if report.total_claims > 0 else "0%"
        verdict_rows.append([k, str(v), pct])

    v_table = Table(verdict_rows, colWidths=[200, 150, 180])
    v_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(v_table)
    story.append(Spacer(1, 15))

    # Detailed Claims Breakdown
    story.append(Paragraph(f"Detailed Claims Analysis ({len(report.claims)} Claims)", h2_style))

    for idx, claim in enumerate(report.claims, start=1):
        v_str = claim.verdict.value if claim.verdict else "UNVERIFIED"
        v_col = "#16a34a" if v_str == "SUPPORTED" else (
            "#d97706" if v_str == "PARTLY_SUPPORTED" else (
                "#7c3aed" if v_str == "POTENTIALLY_OUTDATED" else "#dc2626"
            )
        )
        review_flag = " [REQUIRES HUMAN REVIEW]" if claim.needs_human_review else ""

        claim_card_data = [
            [
                Paragraph(
                    f"<b>Claim #{idx} (Page {claim.page_number})</b>: {claim.claim_text}",
                    body_style,
                )
            ],
            [
                Paragraph(
                    f"<b>Verdict:</b> <font color='{v_col}'><b>{v_str}</b></font> (Confidence: {claim.confidence:.2f}){review_flag}<br/>"
                    f"<b>Rationale:</b> {claim.rationale or 'N/A'}",
                    body_style,
                )
            ],
        ]

        if claim.evidence:
            ev_summary_lines = []
            for ev in claim.evidence[:3]:
                score_str = f"relevance: {ev.similarity_score:.2f}" if ev.similarity_score is not None else ""
                ev_summary_lines.append(
                    f"&bull; <i>[{ev.source_provider.upper()} | {ev.evidence_level.value} {score_str}]</i>: {ev.passage[:200]}..."
                )
            claim_card_data.append(
                [
                    Paragraph(
                        "<b>Top Evidence Passages:</b><br/>" + "<br/>".join(ev_summary_lines),
                        body_style,
                    )
                ]
            )

        card_table = Table(claim_card_data, colWidths=[530])
        card_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(KeepTogether([card_table, Spacer(1, 8)]))

    doc.build(story)
    return buf.getvalue()


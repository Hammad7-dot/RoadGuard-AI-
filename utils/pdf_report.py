"""
RoadGuard AI
PDF Inspection Report
-----------------------

Builds a shareable PDF summary of everything logged in the detections
database: headline stats, damage-type breakdown, and the full record
table. Meant to be handed to a road-maintenance team or filed as an
inspection record, rather than requiring them to open the app/DB.
"""

from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def build_report(
    stats: Dict,
    distribution: Dict[str, int],
    rows: List[dict],
    geotagged: Optional[List[dict]] = None,
) -> bytes:
    """
    Returns the PDF as raw bytes, ready to hand to
    st.download_button(..., mime="application/pdf").
    """

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=50, bottomMargin=50, leftMargin=50, rightMargin=50
    )
    styles = getSampleStyleSheet()
    story = []

    # ---- Title ----
    story.append(Paragraph("RoadGuard AI - Inspection Report", styles["Title"]))
    story.append(Paragraph(
        datetime.now().strftime("Generated on %A, %d %B %Y at %H:%M"),
        styles["Normal"]
    ))
    story.append(Spacer(1, 20))

    # ---- Headline stats ----
    story.append(Paragraph("Summary", styles["Heading2"]))

    avg_conf = stats.get("avg_confidence")
    avg_conf_text = f"{avg_conf * 100:.1f}%" if avg_conf is not None else "N/A"

    summary_table_data = [
        ["Images Analyzed", str(stats.get("images_analyzed", 0))],
        ["Videos Analyzed", str(stats.get("videos_analyzed", 0))],
        ["Total Detections", str(stats.get("total_detections", 0))],
        ["Average Confidence", avg_conf_text],
        ["Geotagged Detections", str(len(geotagged) if geotagged else 0)],
    ]
    summary_table = Table(summary_table_data, colWidths=[220, 220])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#8B5CF6")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # ---- Damage distribution ----
    story.append(Paragraph("Damage Type Breakdown", styles["Heading2"]))

    if distribution:
        dist_data = [["Damage Type", "Count"]] + [
            [k, str(v)] for k, v in distribution.items()
        ]
        dist_table = Table(dist_data, colWidths=[300, 140])
        dist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ]))
        story.append(dist_table)
    else:
        story.append(Paragraph("No detections recorded yet.", styles["Normal"]))

    story.append(PageBreak())

    # ---- Full record table ----
    story.append(Paragraph("Detection Records", styles["Heading2"]))
    story.append(Spacer(1, 10))

    if rows:
        header = ["ID", "Filename", "Damage Type", "Confidence", "Created At"]
        table_data = [header]
        for r in rows[:200]:  # cap so the PDF doesn't balloon on huge histories
            conf = r.get("confidence")
            conf_text = f"{conf * 100:.0f}%" if conf is not None else "-"
            table_data.append([
                str(r.get("id", "")),
                str(r.get("filename", ""))[:30],
                str(r.get("damage_type", "")),
                conf_text,
                str(r.get("created_at", ""))[:19],
            ])

        record_table = Table(
            table_data, colWidths=[35, 150, 130, 70, 105], repeatRows=1
        )
        record_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ]))
        story.append(record_table)

        if len(rows) > 200:
            story.append(Spacer(1, 10))
            story.append(Paragraph(
                f"...and {len(rows) - 200} more records not shown here. "
                "Export the full CSV from the Reports page for the complete history.",
                styles["Italic"]
            ))
    else:
        story.append(Paragraph("No detections recorded yet.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

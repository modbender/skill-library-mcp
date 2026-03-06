"""
PDF Report Generation Module
Professional, physician-shareable genetic analysis reports

Uses ReportLab for PDF generation.

Features:
- Executive summary section
- Detailed findings by category
- Actionable recommendations
- Clinical-grade formatting
- Disclaimers and limitations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import io

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, KeepTogether, ListFlowable, ListItem, HRFlowable
    )
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Color scheme
COLORS = {
    "primary": colors.HexColor("#1a365d"),  # Dark blue
    "secondary": colors.HexColor("#2b6cb0"),  # Medium blue
    "accent": colors.HexColor("#38a169"),  # Green
    "warning": colors.HexColor("#dd6b20"),  # Orange
    "critical": colors.HexColor("#c53030"),  # Red
    "light_bg": colors.HexColor("#f7fafc"),  # Light gray
    "border": colors.HexColor("#e2e8f0"),  # Gray border
}


def create_styles() -> Dict[str, ParagraphStyle]:
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=COLORS["primary"],
            spaceAfter=20,
            alignment=TA_CENTER,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=30,
        ),
        "SectionHeader": ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=COLORS["primary"],
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5,
        ),
        "SubsectionHeader": ParagraphStyle(
            "SubsectionHeader",
            parent=styles["Heading3"],
            fontSize=12,
            textColor=COLORS["secondary"],
            spaceBefore=12,
            spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
        ),
        "Finding": ParagraphStyle(
            "Finding",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            leftIndent=10,
        ),
        "Critical": ParagraphStyle(
            "Critical",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COLORS["critical"],
            fontName="Helvetica-Bold",
        ),
        "Warning": ParagraphStyle(
            "Warning",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COLORS["warning"],
        ),
        "Recommendation": ParagraphStyle(
            "Recommendation",
            parent=styles["Normal"],
            fontSize=10,
            leftIndent=15,
            bulletIndent=5,
        ),
        "Disclaimer": ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
            leading=10,
        ),
        "Footer": ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
        ),
    }
    
    return custom_styles


def generate_pdf_report(
    analysis_results: Dict[str, Any],
    output_path: str = None,
    include_raw_data: bool = False
) -> Optional[str]:
    """
    Generate a professional PDF report from genetic analysis results.
    
    Args:
        analysis_results: Dict containing all analysis results
        output_path: Path for output PDF (default: ~/dna-analysis/reports/report.pdf)
        include_raw_data: Whether to include detailed variant tables
        
    Returns:
        Path to generated PDF or None if generation failed
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    # Set output path
    if output_path is None:
        output_dir = Path.home() / "dna-analysis" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "genetic_report.pdf")
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    styles = create_styles()
    story = []
    
    # Title page
    story.extend(_build_title_page(analysis_results, styles))
    story.append(PageBreak())
    
    # Executive summary
    story.extend(_build_executive_summary(analysis_results, styles))
    story.append(PageBreak())
    
    # Critical findings
    if analysis_results.get("critical_alerts") or analysis_results.get("high_priority"):
        story.extend(_build_critical_findings(analysis_results, styles))
        story.append(PageBreak())
    
    # Pharmacogenomics
    if analysis_results.get("pharmacogenomics"):
        story.extend(_build_pharmacogenomics_section(analysis_results, styles))
        story.append(PageBreak())
    
    # Health risks
    story.extend(_build_health_risks_section(analysis_results, styles))
    story.append(PageBreak())
    
    # Ancestry (if available)
    if analysis_results.get("ancestry") or analysis_results.get("haplogroups"):
        story.extend(_build_ancestry_section(analysis_results, styles))
        story.append(PageBreak())
    
    # Traits
    if analysis_results.get("traits"):
        story.extend(_build_traits_section(analysis_results, styles))
        story.append(PageBreak())
    
    # Recommendations
    story.extend(_build_recommendations_section(analysis_results, styles))
    story.append(PageBreak())
    
    # Disclaimers
    story.extend(_build_disclaimers(styles))
    
    # Build PDF
    try:
        doc.build(story)
        return output_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def _build_title_page(results: Dict, styles: Dict) -> List:
    """Build title page elements."""
    elements = []
    
    elements.append(Spacer(1, 2*inch))
    
    elements.append(Paragraph("Comprehensive Genetic Analysis Report", styles["Title"]))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Date and metadata
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Generated: {date_str}", styles["Subtitle"]))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Summary statistics box
    total_snps = results.get("total_snps", "N/A")
    platform = results.get("format", "Unknown")
    version = results.get("version", "N/A")
    
    summary_data = [
        ["Analysis Summary", ""],
        ["Total SNPs Analyzed", f"{total_snps:,}" if isinstance(total_snps, int) else str(total_snps)],
        ["Data Source", platform],
        ["Analysis Version", f"v{version}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, COLORS["border"]),
        ("BACKGROUND", (0, 1), (-1, -1), COLORS["light_bg"]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(summary_table)
    
    elements.append(Spacer(1, inch))
    
    # Important notice
    notice_text = """
    <b>IMPORTANT:</b> This report is for informational purposes only and is not a medical diagnosis.
    Genetic risk factors are just one component of overall health. Please consult with a qualified
    healthcare provider or genetic counselor before making any medical decisions based on these results.
    """
    elements.append(Paragraph(notice_text, styles["Warning"]))
    
    return elements


def _build_executive_summary(results: Dict, styles: Dict) -> List:
    """Build executive summary section."""
    elements = []
    
    elements.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    # Key findings count
    critical_count = len(results.get("critical_alerts", []))
    high_count = len(results.get("high_priority", []))
    pharma_count = len(results.get("pharmacogenomics_alerts", []))
    
    # APOE status
    apoe = results.get("apoe", {})
    apoe_text = f"APOE Genotype: {apoe.get('genotype', 'Unknown')} ({apoe.get('risk_level', 'N/A')} risk)"
    
    summary_items = [
        f"• Total genetic markers analyzed: {results.get('total_snps', 'N/A'):,}" if isinstance(results.get('total_snps'), int) else f"• Total genetic markers analyzed: {results.get('total_snps', 'N/A')}",
        f"• Critical findings requiring attention: {critical_count}",
        f"• High-priority findings: {high_count}",
        f"• Pharmacogenomic alerts: {pharma_count}",
        f"• {apoe_text}",
    ]
    
    for item in summary_items:
        elements.append(Paragraph(item, styles["Body"]))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Quick interpretation
    elements.append(Paragraph("Quick Interpretation", styles["SubsectionHeader"]))
    
    if critical_count > 0:
        elements.append(Paragraph(
            f"<b>⚠️ {critical_count} critical finding(s)</b> identified that may require immediate "
            "discussion with your healthcare provider.",
            styles["Critical"]
        ))
    elif high_count > 0:
        elements.append(Paragraph(
            f"<b>{high_count} notable finding(s)</b> identified. Consider discussing with your "
            "healthcare provider at your next visit.",
            styles["Warning"]
        ))
    else:
        elements.append(Paragraph(
            "No critical genetic findings identified. Standard preventive care recommendations apply.",
            styles["Body"]
        ))
    
    return elements


def _build_critical_findings(results: Dict, styles: Dict) -> List:
    """Build critical findings section."""
    elements = []
    
    elements.append(Paragraph("Critical and High-Priority Findings", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["critical"]))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(
        "The following findings may have significant health implications and should be "
        "discussed with a healthcare provider or genetic counselor.",
        styles["Body"]
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    # Critical alerts
    critical = results.get("critical_alerts", [])
    if critical:
        elements.append(Paragraph("CRITICAL ALERTS", styles["Critical"]))
        for alert in critical[:5]:  # Limit to top 5
            gene = alert.get("gene", "Unknown")
            rsid = alert.get("rsid", "")
            geno = alert.get("genotype", "")
            
            alert_text = f"<b>{gene}</b> ({rsid}): {geno}"
            elements.append(Paragraph(alert_text, styles["Finding"]))
            
            for rec in alert.get("recommendations", [])[:3]:
                elements.append(Paragraph(f"    → {rec}", styles["Recommendation"]))
            
            elements.append(Spacer(1, 0.1*inch))
    
    # High priority
    high = results.get("high_priority", [])
    if high:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("HIGH PRIORITY FINDINGS", styles["Warning"]))
        for item in high[:5]:
            gene = item.get("gene", "Unknown")
            rsid = item.get("rsid", "")
            geno = item.get("genotype", "")
            
            item_text = f"<b>{gene}</b> ({rsid}): {geno}"
            elements.append(Paragraph(item_text, styles["Finding"]))
            elements.append(Spacer(1, 0.05*inch))
    
    return elements


def _build_pharmacogenomics_section(results: Dict, styles: Dict) -> List:
    """Build pharmacogenomics section."""
    elements = []
    
    elements.append(Paragraph("Pharmacogenomics (Drug-Gene Interactions)", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(
        "These genetic variants may affect how you respond to certain medications. "
        "Share this information with your healthcare provider and pharmacist.",
        styles["Body"]
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    pharma = results.get("pharmacogenomics", {})
    pharma_alerts = results.get("pharmacogenomics_alerts", [])
    
    if pharma_alerts:
        # Create table of pharmacogenomics findings
        table_data = [["Gene", "Genotype", "Clinical Impact"]]
        
        for alert in pharma_alerts[:10]:
            gene = alert.get("gene", "Unknown")
            geno = alert.get("genotype", "")
            action = alert.get("action_type", "Review needed")
            table_data.append([gene, geno, action[:50]])
        
        pharma_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
        pharma_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["secondary"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(pharma_table)
    else:
        elements.append(Paragraph(
            "No significant pharmacogenomic findings detected in the tested markers.",
            styles["Body"]
        ))
    
    return elements


def _build_health_risks_section(results: Dict, styles: Dict) -> List:
    """Build health risks section."""
    elements = []
    
    elements.append(Paragraph("Health Risk Factors", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    # APOE
    apoe = results.get("apoe", {})
    if apoe.get("genotype") != "unknown":
        elements.append(Paragraph("APOE Status (Alzheimer's / Cardiovascular)", styles["SubsectionHeader"]))
        
        apoe_data = [
            ["Genotype", apoe.get("genotype", "Unknown")],
            ["Risk Level", apoe.get("risk_level", "Unknown")],
            ["Interpretation", apoe.get("interpretation", "")[:100]],
        ]
        
        apoe_table = Table(apoe_data, colWidths=[2*inch, 4.5*inch])
        apoe_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("BACKGROUND", (0, 0), (0, -1), COLORS["light_bg"]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(apoe_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # PRS Summary
    prs = results.get("prs", {})
    if prs and not prs.get("error"):
        elements.append(Paragraph("Polygenic Risk Scores", styles["SubsectionHeader"]))
        elements.append(Paragraph(
            "These scores estimate genetic predisposition based on multiple variants. "
            "They are probabilistic, not deterministic.",
            styles["Body"]
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        prs_data = [["Condition", "Percentile", "Confidence"]]
        for condition, scores in list(prs.items())[:8]:
            if scores.get("percentile_estimate"):
                prs_data.append([
                    condition,
                    f"{scores['percentile_estimate']}th",
                    scores.get("confidence", "N/A")
                ])
        
        if len(prs_data) > 1:
            prs_table = Table(prs_data, colWidths=[3*inch, 1.5*inch, 2*inch])
            prs_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["secondary"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(prs_table)
    
    return elements


def _build_ancestry_section(results: Dict, styles: Dict) -> List:
    """Build ancestry section."""
    elements = []
    
    elements.append(Paragraph("Ancestry & Lineage", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    # Haplogroups
    haplogroups = results.get("haplogroups", {})
    if haplogroups:
        mtdna = haplogroups.get("mtDNA", {})
        ydna = haplogroups.get("Y_DNA", {})
        
        if mtdna.get("haplogroup") != "Unknown":
            elements.append(Paragraph(
                f"<b>Maternal Lineage (mtDNA):</b> Haplogroup {mtdna.get('haplogroup')} "
                f"(Confidence: {mtdna.get('confidence', 'N/A')})",
                styles["Body"]
            ))
            if mtdna.get("history"):
                elements.append(Paragraph(
                    f"    Origin: {mtdna['history'].get('origin', 'Unknown')}",
                    styles["Finding"]
                ))
            elements.append(Spacer(1, 0.1*inch))
        
        if ydna.get("haplogroup") not in ["Unknown", "N/A (female)"]:
            elements.append(Paragraph(
                f"<b>Paternal Lineage (Y-DNA):</b> Haplogroup {ydna.get('haplogroup')} "
                f"(Confidence: {ydna.get('confidence', 'N/A')})",
                styles["Body"]
            ))
            if ydna.get("history"):
                elements.append(Paragraph(
                    f"    Origin: {ydna['history'].get('origin', 'Unknown')}",
                    styles["Finding"]
                ))
    
    # Ancestry composition
    ancestry = results.get("ancestry", {})
    composition = ancestry.get("composition", {})
    if composition.get("status") == "success":
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Ancestry Composition Estimate", styles["SubsectionHeader"]))
        
        for pop, pct in composition.get("ancestry_proportions", {}).items():
            if pct >= 5:
                elements.append(Paragraph(f"    {pop}: {pct}%", styles["Body"]))
    
    return elements


def _build_traits_section(results: Dict, styles: Dict) -> List:
    """Build traits section."""
    elements = []
    
    elements.append(Paragraph("Genetic Traits", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    traits = results.get("notable_traits", [])
    if traits:
        for trait in traits[:12]:
            trait_name = trait.get("trait", "Unknown")
            interpretation = trait.get("interpretation", "")
            if isinstance(interpretation, dict):
                interpretation = str(interpretation)
            
            elements.append(Paragraph(
                f"<b>{trait_name}:</b> {interpretation[:80]}",
                styles["Body"]
            ))
            elements.append(Spacer(1, 0.05*inch))
    else:
        elements.append(Paragraph("Trait analysis results not available.", styles["Body"]))
    
    return elements


def _build_recommendations_section(results: Dict, styles: Dict) -> List:
    """Build recommendations section."""
    elements = []
    
    elements.append(Paragraph("Recommendations", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    lifestyle = results.get("lifestyle_recommendations", {})
    
    if lifestyle.get("diet"):
        elements.append(Paragraph("Diet", styles["SubsectionHeader"]))
        for item in lifestyle["diet"][:5]:
            elements.append(Paragraph(f"• {item}", styles["Recommendation"]))
    
    if lifestyle.get("exercise"):
        elements.append(Paragraph("Exercise", styles["SubsectionHeader"]))
        for item in lifestyle["exercise"][:5]:
            elements.append(Paragraph(f"• {item}", styles["Recommendation"]))
    
    if lifestyle.get("supplements"):
        elements.append(Paragraph("Supplements to Consider", styles["SubsectionHeader"]))
        for item in lifestyle["supplements"][:5]:
            elements.append(Paragraph(f"• {item}", styles["Recommendation"]))
    
    if lifestyle.get("screening"):
        elements.append(Paragraph("Recommended Screenings", styles["SubsectionHeader"]))
        for item in lifestyle["screening"][:5]:
            elements.append(Paragraph(f"• {item}", styles["Recommendation"]))
    
    if lifestyle.get("avoid"):
        elements.append(Paragraph("Items to Avoid/Limit", styles["SubsectionHeader"]))
        for item in lifestyle["avoid"][:5]:
            elements.append(Paragraph(f"• {item}", styles["Recommendation"]))
    
    return elements


def _build_disclaimers(styles: Dict) -> List:
    """Build disclaimers section."""
    elements = []
    
    elements.append(Paragraph("Important Disclaimers & Limitations", styles["SectionHeader"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["border"]))
    elements.append(Spacer(1, 0.2*inch))
    
    disclaimers = [
        "<b>Not a Medical Diagnosis:</b> This report provides genetic information only and does not "
        "constitute a medical diagnosis. Genetic variants indicate risk factors, not certainties.",
        
        "<b>Consult Healthcare Providers:</b> Always discuss genetic findings with qualified healthcare "
        "providers before making medical decisions. Genetic counseling is recommended for significant findings.",
        
        "<b>Technical Limitations:</b> Consumer genetic arrays analyze a subset (~0.1%) of the genome. "
        "Rare variants, structural variants, and many clinically relevant variants may not be detected.",
        
        "<b>Probabilistic Results:</b> Polygenic risk scores and disease associations are probabilistic. "
        "Many conditions depend heavily on environmental factors and lifestyle choices.",
        
        "<b>Population Specificity:</b> Some genetic associations are better studied in certain populations. "
        "Risk estimates may be less accurate for underrepresented ancestries.",
        
        "<b>Evolving Science:</b> Genetic research is rapidly advancing. Interpretations may change as "
        "scientific knowledge grows.",
        
        "<b>Privacy:</b> Genetic information is sensitive. Take appropriate measures to protect this report.",
    ]
    
    for disclaimer in disclaimers:
        elements.append(Paragraph(disclaimer, styles["Disclaimer"]))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}",
        styles["Footer"]
    ))
    
    return elements


def is_available() -> bool:
    """Check if PDF generation is available."""
    return REPORTLAB_AVAILABLE

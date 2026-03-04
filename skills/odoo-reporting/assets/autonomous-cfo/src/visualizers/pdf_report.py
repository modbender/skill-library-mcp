"""
PDF Report Generator - Light theme A4 reports
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Script-relative output directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", ".."))
DEFAULT_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output", "pdf_reports")


class PDFReportGenerator:
    """Generates professional PDF reports with light theme"""
    
    COLORS = {
        "primary": "#cd7f32",     # Copper accent
        "secondary": "#1a2a3a",   # Dark text
        "text": "#333333",
        "text_light": "#666666",
        "border": "#e0e0e0",
        "background": "#ffffff",
        "positive": "#2e7d32",
        "negative": "#c62828",
    }
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check available PDF libraries"""
        self.has_weasyprint = self._try_import("weasyprint")
        self.has_reportlab = self._try_import("reportlab")
        self.has_fpdf = self._try_import("fpdf")
    
    def _try_import(self, module: str) -> bool:
        try:
            __import__(module)
            return True
        except ImportError:
            return False
    
    def generate_report(
        self,
        title: str,
        subtitle: str,
        sections: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Generate multi-section PDF report"""
        
        if self.has_weasyprint:
            return self._generate_with_weasyprint(title, subtitle, sections, metadata, filename)
        elif self.has_fpdf:
            return self._generate_with_fpdf(title, subtitle, sections, metadata, filename)
        elif self.has_reportlab:
            return self._generate_with_reportlab(title, subtitle, sections, metadata, filename)
        else:
            return self._generate_html_fallback(title, subtitle, sections, metadata, filename)
    
    def _generate_with_weasyprint(self, title: str, subtitle: str, sections: List, metadata: Dict, filename: str) -> str:
        """Generate PDF using WeasyPrint (best quality)"""
        from weasyprint import HTML, CSS
        
        html_content = self._build_html(title, subtitle, sections, metadata)
        
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        css = CSS(string=self._get_css())
        HTML(string=html_content).write_pdf(filepath, stylesheets=[css])
        
        return filepath
    
    def _generate_with_fpdf(self, title: str, subtitle: str, sections: List, metadata: Dict, filename: str) -> str:
        """Generate PDF using FPDF"""
        from fpdf import FPDF
        
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # Title
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(26, 42, 58)  # Dark
        pdf.cell(0, 15, title, ln=True, align="C")
        
        # Subtitle
        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(102, 102, 102)
        pdf.cell(0, 10, subtitle, ln=True, align="C")
        
        # Divider
        pdf.set_draw_color(205, 127, 50)  # Copper
        pdf.set_line_width(0.5)
        pdf.line(20, pdf.get_y() + 5, 190, pdf.get_y() + 5)
        pdf.ln(15)
        
        # Sections
        for section in sections:
            self._add_section_fpdf(pdf, section)
        
        # Footer
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Confidential", align="C")
        
        pdf.output(filepath)
        return filepath
    
    def _add_section_fpdf(self, pdf, section: Dict):
        """Add a section to FPDF document"""
        # Section title
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(205, 127, 50)  # Copper
        pdf.cell(0, 10, section.get("title", ""), ln=True)
        
        # Section content
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(51, 51, 51)
        
        content = section.get("content", {})
        
        # Handle different content types
        if isinstance(content, dict):
            for key, value in content.items():
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(80, 8, key + ":", ln=False)
                pdf.set_font("Helvetica", "", 10)
                
                # Format value
                if isinstance(value, (int, float)):
                    formatted = f"{value:,.2f}"
                else:
                    formatted = str(value)
                
                pdf.cell(0, 8, formatted, ln=True)
        elif isinstance(content, list):
            for item in content:
                try:
                    # Sanitize text: remove unicode bullets, limit length
                    text = str(item).replace("•", "-").replace("\u2022", "-")
                    # Encode to ASCII to remove any problematic characters
                    text = text.encode("ascii", errors="ignore").decode("ascii")
                    # Truncate long text
                    if len(text) > 100:
                        text = text[:97] + "..."
                    # Reset x position to left margin before multi_cell
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 6, f"- {text}")
                except Exception as e:
                    # Skip problematic items
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 6, "- [Content skipped]")
        else:
            pdf.multi_cell(0, 6, str(content))
        
        pdf.ln(5)
    
    def _generate_with_reportlab(self, title: str, subtitle: str, sections: List, metadata: Dict, filename: str) -> str:
        """Generate PDF using ReportLab"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a2a3a'),
            alignment=1,  # Center
            spaceAfter=10
        )
        
        story = []
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(subtitle, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Sections
        for section in sections:
            story.append(Paragraph(section.get("title", ""), styles['Heading2']))
            content = section.get("content", {})
            
            if isinstance(content, dict):
                data = [[k, str(v)] for k, v in content.items()]
                t = Table(data, colWidths=[200, 200])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(t)
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filepath
    
    def _generate_html_fallback(self, title: str, subtitle: str, sections: List, metadata: Dict, filename: str) -> str:
        """Generate HTML file if no PDF library available - NOTE: returns .html, not .pdf"""
        # Use .html extension for the fallback, not .pdf
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        elif filename.endswith('.pdf'):
            # Convert .pdf to .html extension for the fallback
            filename = filename[:-4] + '.html'
        
        filepath = os.path.join(self.output_dir, filename)
        
        html = self._build_html(title, subtitle, sections, metadata)
        
        with open(filepath, 'w') as f:
            f.write(f"<!DOCTYPE html><html><head><style>{self._get_css()}</style></head><body>{html}</body></html>")
        
        # Return the actual HTML path (caller should convert to PDF externally)
        return filepath
    
    def _build_html(self, title: str, subtitle: str, sections: List, metadata: Dict) -> str:
        """Build HTML content for report"""
        html = f"""
        <div class="header">
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
            <div class="divider"></div>
        </div>
        """
        
        for section in sections:
            html += f'<div class="section"><h2>{section.get("title", "")}</h2>'
            content = section.get("content", {})
            
            if isinstance(content, dict):
                html += '<table class="data-table">'
                for key, value in content.items():
                    formatted = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
                    html += f'<tr><td class="label">{key}</td><td class="value">{formatted}</td></tr>'
                html += '</table>'
            elif isinstance(content, list):
                html += '<ul>'
                for item in content:
                    html += f'<li>{item}</li>'
                html += '</ul>'
            else:
                html += f'<p>{content}</p>'
            
            html += '</div>'
        
        # Methodology footer
        if metadata.get("methodology"):
            html += f'<div class="methodology"><h3>Methodology</h3><p>{metadata["methodology"]}</p></div>'
        
        # Timestamp footer
        html += f'<div class="footer">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Confidential</div>'
        
        return html
    
    def _get_css(self) -> str:
        """Get CSS styles for PDF/HTML"""
        return """
        @page { margin: 2cm; }
        body { font-family: 'Helvetica', sans-serif; color: #333; }
        .header { text-align: center; margin-bottom: 30px; }
        h1 { color: #1a2a3a; font-size: 24pt; margin-bottom: 5px; }
        .subtitle { color: #666; font-size: 12pt; }
        .divider { height: 2px; background: #cd7f32; margin: 20px 0; }
        .section { margin-bottom: 25px; }
        h2 { color: #cd7f32; font-size: 14pt; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px; }
        .data-table { width: 100%; border-collapse: collapse; }
        .data-table td { padding: 8px; border-bottom: 1px solid #f0f0f0; }
        .label { font-weight: bold; width: 50%; }
        .value { text-align: right; }
        .methodology { background: #f5f5f5; padding: 15px; margin-top: 30px; font-size: 9pt; }
        .methodology h3 { margin-top: 0; color: #666; }
        .footer { text-align: center; color: #999; font-size: 8pt; margin-top: 40px; }
        """

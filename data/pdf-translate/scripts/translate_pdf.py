#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translation Script
Translates PDF documents and generates a new PDF with translated content.
"""

import argparse
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import pdfplumber
    except ImportError:
        missing.append("pdfplumber")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except ImportError:
        missing.append("reportlab")

    if missing:
        print(f"Error: Missing required packages: {', '.join(missing)}")
        print("Install with: pip3 install " + " ".join(missing))
        sys.exit(1)


def register_fonts():
    """Register Chinese and English fonts for PDF generation."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Chinese font paths (priority: STHeiti > PingFang > others)
    chinese_font_paths = [
        '/System/Library/Fonts/STHeiti Light.ttc',  # macOS 黑体（推荐）
        '/System/Library/Fonts/PingFang.ttc',       # macOS 苹方
        '/System/Library/Fonts/Helvetica.ttc',      # 后备
        'C:/Windows/Fonts/msyh.ttc',                # Windows 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',              # Windows 黑体
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
    ]

    # Register Chinese font
    chinese_font = None
    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                chinese_font = 'ChineseFont'
                break
            except Exception as e:
                continue

    if not chinese_font:
        chinese_font = 'Helvetica'

    # Register English font (for English keywords and proper nouns)
    try:
        pdfmetrics.registerFont(TTFont('EnglishFont', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=0))
        english_font = 'EnglishFont'
    except:
        english_font = 'Helvetica'

    return chinese_font, english_font


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    import pdfplumber

    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            text_content.append({
                'page_num': i + 1,
                'text': text
            })

    return text_content


def translate_text(text, target_lang='zh'):
    """
    Translate text to target language.
    Note: This is a placeholder. In actual use, Claude will handle translation.
    """
    # Return text as-is - translation will be done by Claude
    return text


def create_pdf_from_text(translated_content, output_path, chinese_font, english_font):
    """Create PDF from translated content with mixed Chinese/English font support."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.colors import HexColor
    import re

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        leading=32
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=18,
        textColor=HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=20,
        leading=24
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=chinese_font,
        fontSize=11,
        textColor=HexColor('#374151'),
        spaceAfter=8,
        leading=16,
        alignment=TA_JUSTIFY
    )

    def apply_mixed_font(text):
        """Apply mixed Chinese/English font to text."""
        # Pattern to match English text (including common abbreviations)
        english_pattern = r'([a-zA-Z0-9_\-\.]+(?:\s+[a-zA-Z0-9_\-\.]+)*)'

        def replace_english(match):
            english_text = match.group(1)
            # Check if it's a common abbreviation or technical term
            common_terms = ['API', 'JSON', 'PDF', 'AI', 'URL', 'HTTP', 'REST', 'SQL', 'HTML', 'CSS']
            if any(term in english_text for term in common_terms):
                return f'<font name="{english_font}">{english_text}</font>'
            # Check if it's a longer English phrase (likely proper noun)
            if len(english_text.split()) > 2 or len(english_text) > 10:
                return f'<font name="{english_font}">{english_text}</font>'
            return english_text

        # Apply font to English text
        result = re.sub(english_pattern, replace_english, text)
        return result

    story = []

    for page_data in translated_content:
        page_num = page_data['page_num']
        text = page_data['text']

        if page_num == 1:
            story.append(Paragraph("翻译文档", title_style))
            story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph(f"第 {page_num} 页", heading1_style))
        story.append(Spacer(1, 12))

        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Apply mixed font to paragraph
                mixed_text = apply_mixed_font(para.strip())
                story.append(Paragraph(mixed_text, body_style))

        story.append(PageBreak())

    doc.build(story)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Translate PDF documents')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output PDF file path (default: input_translated.pdf)')
    parser.add_argument('--font', help='Custom font path for Chinese text')

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.parent / f"{input_path.stem}_translated.pdf")

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    # Extract text
    print("Extracting text from PDF...")
    text_content = extract_text_from_pdf(str(input_path))
    print(f"Extracted {len(text_content)} pages")

    # Note: Translation should be done by Claude before calling create_pdf_from_text
    # This script handles extraction and PDF generation

    # For now, just create PDF with original text as placeholder
    print("Registering fonts...")
    chinese_font, english_font = register_fonts()
    print(f"Using Chinese font: {chinese_font}")
    print(f"Using English font: {english_font}")

    print(f"Creating PDF at: {output_path}")
    create_pdf_from_text(text_content, output_path, chinese_font, english_font)

    print(f"PDF created successfully: {output_path}")


if __name__ == '__main__':
    main()

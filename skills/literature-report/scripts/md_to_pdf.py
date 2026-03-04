#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to PDF converter
"""

from pathlib import Path
import markdown
from weasyprint import HTML, CSS

def md_to_pdf(md_file, pdf_file):
    """Convert Markdown to PDF"""
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Add CSS styling
    html_with_style = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Noto Sans SC', 'SimHei', sans-serif;
                font-size: 12pt;
                line-height: 1.6;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                font-size: 24pt;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                font-size: 18pt;
                color: #34495e;
                margin-top: 30px;
            }}
            h3 {{
                font-size: 14pt;
                color: #7f8c8d;
            }}
            code {{
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #3498db;
                color: white;
            }}
            tr:nth-child(even) {{
                background: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert to PDF
    HTML(string=html_with_style).write_pdf(pdf_file)
    
    print(f"✅ PDF已生成: {pdf_file}")

if __name__ == '__main__':
    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent
    
    md_file = PROJECT_ROOT / 'TECH_FLOW.md'
    pdf_file = PROJECT_ROOT / 'TECH_FLOW.pdf'
    
    md_to_pdf(md_file, pdf_file)
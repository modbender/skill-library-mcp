#!/usr/bin/env python3
"""
Generate PDF report from video performance data
Usage: python generate_report.py <excel_path> [output_path]

Requirements: pip install fpdf2 pandas openpyxl
"""

import sys
import os
from datetime import datetime

try:
    from fpdf import FPDF
    import pandas as pd
except ImportError:
    print("Error: Missing required packages.")
    print("Install with: pip install fpdf2 pandas openpyxl")
    sys.exit(1)


class ReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Video Ad Performance Analysis | Memories.ai', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def section(self, title, color=(41, 128, 185)):
        self.set_font('Helvetica', 'B', 13)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 9, f'  {title}', fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(4)


def generate_report(excel_path: str, output_path: str = None):
    # Load data
    df = pd.read_excel(excel_path)
    df.columns = [c.lower().replace('sum of ', '').replace(' ', '_') for c in df.columns]
    
    if output_path is None:
        output_path = excel_path.replace('.xlsx', '_report.pdf').replace('.xls', '_report.pdf')
    
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.set_font('Helvetica', 'B', 22)
    pdf.cell(0, 15, 'Creator Video Performance Report', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%B %d, %Y")}', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # Key metrics
    pdf.section('Dataset Overview')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, f"Total Videos: {len(df)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Creators: {df['creator'].nunique()}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Spend: ${df['ad_spend'].sum():,.0f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Earnings: ${df['earnings'].sum():,.0f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Average ROI: {df['roi'].mean():.0%}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Key finding
    pdf.section('Key Finding', (231, 76, 60))
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 6, """High-performing videos: <100 words, ~5s per product, visual-first + background music
Low-performing videos: >150 words, >15s per product, too much explaining

Core problem: Creators spend too much time "selling" instead of "showing".""")
    pdf.ln(5)
    
    # Thresholds table
    pdf.section('Quantitative Thresholds')
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(60, 7, 'Metric', border=1)
    pdf.cell(60, 7, 'GOOD', border=1, align='C')
    pdf.cell(60, 7, 'BAD', border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    
    thresholds = [
        ('Word Count', '<100 words', '>150 words'),
        ('Time per Product', '~5 seconds', '>15 seconds'),
        ('Shows All Products First', 'YES', 'NO'),
        ('Format', 'Visual + Music', 'Talking'),
    ]
    pdf.set_font('Helvetica', '', 9)
    for metric, good, bad in thresholds:
        pdf.cell(60, 6, metric, border=1)
        pdf.cell(60, 6, good, border=1, align='C')
        pdf.cell(60, 6, bad, border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Creator ranking
    pdf.add_page()
    pdf.section('Creator Performance Ranking')
    
    creator_stats = df.groupby('creator').agg({
        'ad_spend': 'sum',
        'earnings': 'sum',
        'row_labels': 'count'
    }).rename(columns={'row_labels': 'videos'})
    creator_stats['roi'] = creator_stats['earnings'] / creator_stats['ad_spend']
    creator_stats = creator_stats.sort_values('roi', ascending=False)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(45, 7, 'Creator', border=1)
    pdf.cell(20, 7, 'Videos', border=1, align='C')
    pdf.cell(35, 7, 'Spend', border=1, align='C')
    pdf.cell(35, 7, 'Earnings', border=1, align='C')
    pdf.cell(25, 7, 'ROI', border=1, align='C')
    pdf.cell(30, 7, 'Action', border=1, align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', '', 9)
    for creator, row in creator_stats.iterrows():
        roi = row['roi']
        status = 'SCALE UP' if roi >= 1.2 else 'OPTIMIZE' if roi >= 1.0 else 'REVIEW'
        color = (232, 245, 233) if roi >= 1.2 else (255, 249, 196) if roi >= 1.0 else (253, 237, 236)
        
        pdf.set_fill_color(*color)
        pdf.cell(45, 6, str(creator)[:20], border=1, fill=True)
        pdf.cell(20, 6, str(int(row['videos'])), border=1, align='C', fill=True)
        pdf.cell(35, 6, f"${row['ad_spend']:,.0f}", border=1, align='C', fill=True)
        pdf.cell(35, 6, f"${row['earnings']:,.0f}", border=1, align='C', fill=True)
        pdf.cell(25, 6, f"{roi:.0%}", border=1, align='C', fill=True)
        pdf.cell(30, 6, status, border=1, align='C', fill=True, new_x="LMARGIN", new_y="NEXT")
    
    # Feedback guide
    pdf.add_page()
    pdf.section('Creator Feedback Guide', (155, 89, 182))
    pdf.set_font('Helvetica', '', 10)
    
    feedback_text = """
1. PACING
   Problem: Video spends ~30 seconds per product
   Solution: Show each item in ~5 seconds with quick cuts

2. WORD COUNT  
   Problem: Too much talking (>150 words)
   Solution: Use <100 words, replace verbal with visual demos

3. OPENING
   Problem: Products revealed one by one
   Solution: Show ALL products in first 2-3 seconds

4. AUDIENCE
   Problem: Talking to existing followers
   Solution: Remember ads reach non-followers - hook them in 3 seconds

5. EXCEPTION (Kirstin Approach)
   Detailed reviews work IF you show all products first
   and use low-pressure language
"""
    pdf.multi_cell(0, 5.5, feedback_text)
    
    # Reference videos
    pdf.ln(5)
    pdf.section('Reference Videos', (52, 152, 219))
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, """GOOD Examples:
- instagram.com/reel/Cy1zs4gLGFG (46 words, 15s/3 outfits)
- instagram.com/reel/DEybxPbNeOl (56 words, quick showcase)
- instagram.com/reel/DHHr5o2s1LG (91 words, fast cuts)

BAD Example:
- instagram.com/reel/DRCdjLlDcla (168 words, 30s/outfit)""")
    
    # Save
    pdf.output(output_path)
    print(f"Report saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <excel_path> [output_path]")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_report(excel_path, output_path)

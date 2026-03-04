#!/usr/bin/env python3
"""
WeChat Image Generator
Generate beautiful images for WeChat articles with auto-screenshot
"""

import sys
import os
import argparse
import json
import html
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

def load_template(name):
    """Load HTML template"""
    template_path = ASSETS_DIR / f"{name}.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_cover(title, subtitle, output):
    """Generate cover image"""
    template = load_template("cover")
    html_content = template.replace("{{TITLE}}", html.escape(title))
    html_content = html_content.replace("{{SUBTITLE}}", html.escape(subtitle))
    
    # Save HTML to temp file
    html_path = output.replace('.png', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated HTML: {html_path}")
    print(f"✓ Now taking screenshot...")
    
    # Use OpenClaw browser tool to screenshot
    # Output screenshot command for user to run
    file_url = f"file://{os.path.abspath(html_path)}"
    print(f"\n📸 Run this command to take screenshot:")
    print(f'browser open --url "{file_url}" && sleep 2 && browser screenshot --type png --outputPath "{output}"')
    print(f"\nOr manually open in browser and screenshot:\nopen {html_path}")

def generate_compare(left, right, label, output):
    """Generate comparison image"""
    template = load_template("compare")
    
    # Escape HTML but preserve newlines
    left_escaped = html.escape(left).replace('\\n', '\n')
    right_escaped = html.escape(right).replace('\\n', '\n')
    
    html_content = template.replace("{{LEFT_CONTENT}}", left_escaped)
    html_content = html_content.replace("{{RIGHT_CONTENT}}", right_escaped)
    html_content = html_content.replace("{{LABEL}}", html.escape(label))
    
    # Save HTML
    html_path = output.replace('.png', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated HTML: {html_path}")
    print(f"✓ Now taking screenshot...")
    
    file_url = f"file://{os.path.abspath(html_path)}"
    print(f"\n📸 Run this command to take screenshot:")
    print(f'browser open --url "{file_url}" && sleep 2 && browser screenshot --type png --outputPath "{output}"')
    print(f"\nOr manually open in browser and screenshot:\nopen {html_path}")

def generate_chart(data_str, labels_str, output):
    """Generate chart image
    
    Args:
        data_str: "Title1:val1,val2|Title2:val3,val4"
        labels_str: "Label1,Label2"
    """
    template = load_template("chart")
    
    # Parse data
    groups = data_str.split('|')
    labels = labels_str.split(',')
    
    chart_groups_html = ""
    
    for group in groups:
        parts = group.split(':')
        if len(parts) != 2:
            continue
        
        group_title = parts[0]
        values = [float(v) for v in parts[1].split(',')]
        
        if len(values) != len(labels):
            print(f"⚠️  Warning: {len(values)} values but {len(labels)} labels")
            continue
        
        # Calculate max value for scaling
        max_val = max(values)
        
        # Use logarithmic scale for better visualization when values differ greatly
        import math
        log_values = [math.log10(v + 1) for v in values]  # +1 to handle zero
        max_log = max(log_values)
        
        # Generate bars HTML
        bars_html = ""
        for i, (val, label, log_val) in enumerate(zip(values, labels, log_values)):
            # Use log scale for height, but show original value
            height_pct = (log_val / max_log * 100) if max_log > 0 else 0
            # Ensure minimum visible height (at least 30% for better visual)
            height_pct = max(height_pct, 30)
            bars_html += f'''
            <div class="bar-container">
                <div class="bar" style="height: {height_pct}%;">
                    <div class="bar-value">{val:,.0f}</div>
                </div>
                <div class="bar-label">{html.escape(label)}</div>
            </div>
            '''
        
        chart_groups_html += f'''
        <div class="chart-group">
            <div class="chart-title">{html.escape(group_title)}</div>
            <div class="bars">
                {bars_html}
            </div>
        </div>
        '''
    
    html_content = template.replace("{{CHART_GROUPS}}", chart_groups_html)
    
    # Save HTML
    html_path = output.replace('.png', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated HTML: {html_path}")
    print(f"✓ Now taking screenshot...")
    
    file_url = f"file://{os.path.abspath(html_path)}"
    print(f"\n📸 Run this command to take screenshot:")
    print(f'browser open --url "{file_url}" && sleep 2 && browser screenshot --type png --outputPath "{output}"')
    print(f"\nOr manually open in browser and screenshot:\nopen {html_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate WeChat article images")
    subparsers = parser.add_subparsers(dest='command', help='Image type')
    
    # Cover command
    cover_parser = subparsers.add_parser('cover', help='Generate cover image')
    cover_parser.add_argument('--title', required=True, help='Main title')
    cover_parser.add_argument('--subtitle', required=True, help='Subtitle')
    cover_parser.add_argument('--output', required=True, help='Output PNG path')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Generate comparison image')
    compare_parser.add_argument('--left', required=True, help='Left content')
    compare_parser.add_argument('--right', required=True, help='Right content')
    compare_parser.add_argument('--label', default='→', help='Arrow label')
    compare_parser.add_argument('--output', required=True, help='Output PNG path')
    
    # Chart command
    chart_parser = subparsers.add_parser('chart', help='Generate chart image')
    chart_parser.add_argument('--data', required=True, help='Data: "Title1:v1,v2|Title2:v3,v4"')
    chart_parser.add_argument('--labels', required=True, help='Labels: "Label1,Label2"')
    chart_parser.add_argument('--output', required=True, help='Output PNG path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.command == 'cover':
        generate_cover(args.title, args.subtitle, args.output)
    elif args.command == 'compare':
        generate_compare(args.left, args.right, args.label, args.output)
    elif args.command == 'chart':
        generate_chart(args.data, args.labels, args.output)

if __name__ == '__main__':
    main()

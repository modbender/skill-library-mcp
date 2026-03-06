#!/usr/bin/env python3
"""
Report Generator Script
Based on a clean, minimal business report template.

This script takes content, refines it, generates an HTML report, and converts it to an image.
"""

import sys
import os
import argparse
import json
import subprocess
from datetime import datetime

# HTML Template based on the provided file
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {
            /* Light & Concise Theme (Default) */
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-primary: #1f2937;
            --text-secondary: #4b5563;
            
            /* Theme Colors - Light Blue/Teal for cleaner look */
            --accent-color: #3b82f6;        /* Primary Blue */
            --accent-dark: #1d4ed8;         /* Darker Blue */
            --accent-light: #dbeafe;        /* Very Light Blue */
            --accent-border: #bfdbfe;       /* Border Blue */
            
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 2vh 3vw;
            overflow: hidden; 
        }

        /* Top Section: Goal */
        .header {
            flex: 0 0 auto;
            text-align: center;
            margin-bottom: 2vh;
            padding: 2vh 2vw;
            background: #ffffff;
            color: var(--text-primary);
            border-radius: 12px;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-left: 6px solid var(--accent-color);
        }

        .header-label {
            font-size: 0.85rem;
            color: var(--accent-color);
            font-weight: 600;
            margin-bottom: 0.5vh;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        .header-title {
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.3;
            color: var(--text-primary);
        }

        /* Middle Section: 4 Quadrants */
        .content {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 2vh 2vw;
            margin-bottom: 2vh;
        }

        .quadrant {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2.5vh 2vw;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
            border: 1px solid rgba(0,0,0,0.03);
            position: relative;
            overflow: hidden;
        }

        .quadrant:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08);
            border-color: var(--accent-border);
        }

        .q-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5vh;
            padding-bottom: 1vh;
            border-bottom: 1px solid var(--bg-color);
        }

        .q-number {
            font-size: 3rem;
            font-weight: 900;
            opacity: 0.06;
            position: absolute;
            right: 1.5rem;
            top: 0.5rem;
            font-family: Arial, sans-serif;
            color: var(--text-primary);
        }

        .q-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-right: 1rem;
            color: var(--text-primary);
        }

        .q-subtitle {
            font-size: 0.9rem;
            color: var(--text-secondary);
            background: var(--bg-color);
            padding: 2px 10px;
            border-radius: 20px;
        }

        .q-slogan {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 1.5vh;
            padding-left: 12px;
            border-left: 3px solid var(--accent-color);
            color: var(--accent-color);
        }
        
        .q-list {
            list-style: none;
            flex: 1;
        }

        .q-list li {
            position: relative;
            padding-left: 1.2rem;
            margin-bottom: 0.8vh;
            line-height: 1.5;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .q-list li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--accent-border);
            font-weight: bold;
            font-size: 1.2em;
        }


        /* Bottom Section: Summary */
        .footer {
            flex: 0 0 auto;
            background: #ffffff;
            color: var(--text-secondary);
            padding: 1.5vh 2vw;
            border-radius: 12px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            border-top: 1px solid rgba(0,0,0,0.03);
        }
        
        .footer-content {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            font-size: 1rem;
            font-weight: 500;
        }

        .arrow {
            color: var(--accent-border);
            font-size: 0.9em;
        }

        /* Responsive adjustment for small screens */
        @media (max-width: 768px) {
            body {
                height: auto;
                overflow: auto;
            }
            .content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <!-- Top: Goal -->
    <header class="header">
        <div class="header-label">一句话总目标</div>
        <div class="header-title">{goal}</div>
    </header>

    <!-- Middle: 4 Quadrants -->
    <main class="content">
        <!-- Q1 -->
        <article class="quadrant q1">
            <div class="q-number">01</div>
            <div class="q-header">
                <h2 class="q-title">{q1_title}</h2>
                <span class="q-subtitle">{q1_subtitle}</span>
            </div>
            <div class="q-slogan">{q1_slogan}</div>
            <ul class="q-list">
                {q1_items}
            </ul>
        </article>

        <!-- Q2 -->
        <article class="quadrant q2">
            <div class="q-number">02</div>
            <div class="q-header">
                <h2 class="q-title">{q2_title}</h2>
                <span class="q-subtitle">{q2_subtitle}</span>
            </div>
            <div class="q-slogan">{q2_slogan}</div>
            <ul class="q-list">
                {q2_items}
            </ul>
        </article>

        <!-- Q3 -->
        <article class="quadrant q3">
            <div class="q-number">03</div>
            <div class="q-header">
                <h2 class="q-title">{q3_title}</h2>
                <span class="q-subtitle">{q3_subtitle}</span>
            </div>
            <div class="q-slogan">{q3_slogan}</div>
            <ul class="q-list">
                {q3_items}
            </ul>
        </article>

        <!-- Q4 -->
        <article class="quadrant q4">
            <div class="q-number">04</div>
            <div class="q-header">
                <h2 class="q-title">{q4_title}</h2>
                <span class="q-subtitle">{q4_subtitle}</span>
            </div>
            <div class="q-slogan">{q4_slogan}</div>
            <ul class="q-list">
                {q4_items}
            </ul>
        </article>
    </main>

    <!-- Bottom: Summary -->
    <footer class="footer">
        <div class="footer-content">
            <span>方法论总结</span>
            <span>|</span>
            <span>{summary_1}</span> <span class="arrow">→</span>
            <span>{summary_2}</span> <span class="arrow">→</span>
            <span>{summary_3}</span> <span class="arrow">→</span>
            <span>{summary_4}</span>
        </div>
    </footer>

</body>
</html>
"""

def generate_html(data, output_path):
    """Generates HTML file from data."""
    
    # Helper to format list items
    def format_list(items):
        return "\n".join([f"<li>{item}</li>" for item in items])

    # Prepare context for template
    context = {
        "title": data.get("title", "述职报告"),
        "goal": data.get("goal", ""),
        
        "q1_title": data.get("q1", {}).get("title", ""),
        "q1_subtitle": data.get("q1", {}).get("subtitle", ""),
        "q1_slogan": data.get("q1", {}).get("slogan", ""),
        "q1_items": format_list(data.get("q1", {}).get("items", [])),
        
        "q2_title": data.get("q2", {}).get("title", ""),
        "q2_subtitle": data.get("q2", {}).get("subtitle", ""),
        "q2_slogan": data.get("q2", {}).get("slogan", ""),
        "q2_items": format_list(data.get("q2", {}).get("items", [])),
        
        "q3_title": data.get("q3", {}).get("title", ""),
        "q3_subtitle": data.get("q3", {}).get("subtitle", ""),
        "q3_slogan": data.get("q3", {}).get("slogan", ""),
        "q3_items": format_list(data.get("q3", {}).get("items", [])),
        
        "q4_title": data.get("q4", {}).get("title", ""),
        "q4_subtitle": data.get("q4", {}).get("subtitle", ""),
        "q4_slogan": data.get("q4", {}).get("slogan", ""),
        "q4_items": format_list(data.get("q4", {}).get("items", [])),
        
        "summary_1": data.get("summary", ["", "", "", ""])[0],
        "summary_2": data.get("summary", ["", "", "", ""])[1],
        "summary_3": data.get("summary", ["", "", "", ""])[2],
        "summary_4": data.get("summary", ["", "", "", ""])[3],
    }
    
    html_content = HTML_TEMPLATE.format(**context)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path

def convert_to_image(html_path, output_image_path):
    """Converts HTML to Image using openclaw browser tool (simulated here via cli or instructions).
    Since this script runs inside the skill environment, we might not have direct access to 'browser' tool in python.
    However, we can instruct the user/agent to do it, or use a headless browser if available.
    
    For this skill, we will output the instruction to use the 'browser' tool to capture the screenshot.
    """
    # Note: Real conversion would require playwright, selenium, or wkhtmltoimage.
    # Given the environment, we will use the `browser` tool capability of OpenClaw if possible, 
    # but since this is a python script, we might just print the command for the agent to execute.
    pass

def main():
    parser = argparse.ArgumentParser(description="Generate Report HTML")
    parser.add_argument("--data", required=True, help="JSON string of report data")
    parser.add_argument("--output", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"report_{timestamp}.html"
    html_path = os.path.join(args.output, html_filename)
    
    generate_html(data, html_path)
    
    print(json.dumps({
        "html_path": html_path,
        "message": "HTML generated successfully"
    }))

if __name__ == "__main__":
    main()

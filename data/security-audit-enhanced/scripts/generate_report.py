#!/usr/bin/env python3
"""
Report generator for security audit.
Generates HTML and Markdown reports from JSON audit results.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report</title>
    <style>
        :root {{
            --critical: #dc2626;
            --high: #ea580c;
            --medium: #ca8a04;
            --low: #2563eb;
            --passed: #16a34a;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8fafc;
        }}
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        .score-container {{
            text-align: center;
            margin: 2rem 0;
        }}
        .score {{
            font-size: 4rem;
            font-weight: bold;
            color: {score_color};
        }}
        .rating {{
            font-size: 1.5rem;
            color: {score_color};
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }}
        .summary-item {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .summary-item .count {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .summary-item .label {{
            color: #64748b;
            font-size: 0.875rem;
        }}
        .critical .count {{ color: var(--critical); }}
        .high .count {{ color: var(--high); }}
        .medium .count {{ color: var(--medium); }}
        .low .count {{ color: var(--low); }}
        .passed .count {{ color: var(--passed); }}
        .findings {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .finding {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .finding:last-child {{
            border-bottom: none;
        }}
        .finding-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        .severity-badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            color: white;
        }}
        .severity-critical {{ background: var(--critical); }}
        .severity-high {{ background: var(--high); }}
        .severity-medium {{ background: var(--medium); }}
        .severity-low {{ background: var(--low); }}
        .finding-domain {{
            font-weight: 600;
        }}
        .finding-text {{
            color: #475569;
            margin: 0.5rem 0;
        }}
        .recommendation {{
            background: #f1f5f9;
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 0.875rem;
        }}
        .meta {{
            color: #64748b;
            font-size: 0.875rem;
            margin-top: 2rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Security Audit Report</h1>
        <p>Generated: {timestamp}</p>
        <p>Platform: {platform}</p>
    </div>

    <div class="score-container">
        <div class="score">{score}</div>
        <div class="rating">{rating}</div>
    </div>

    <div class="summary">
        <div class="summary-item critical">
            <div class="count">{critical}</div>
            <div class="label">Critical</div>
        </div>
        <div class="summary-item high">
            <div class="count">{high}</div>
            <div class="label">High</div>
        </div>
        <div class="summary-item medium">
            <div class="count">{medium}</div>
            <div class="label">Medium</div>
        </div>
        <div class="summary-item low">
            <div class="count">{low}</div>
            <div class="label">Low</div>
        </div>
        <div class="summary-item passed">
            <div class="count">{passed}</div>
            <div class="label">Passed</div>
        </div>
    </div>

    <div class="findings">
        {findings_html}
    </div>

    <div class="meta">
        <p>This audit was performed by Security Audit Enhanced.</p>
        <p>No changes were made to your configuration.</p>
    </div>
</body>
</html>
'''


def get_score_color(score: int) -> str:
    """Get color based on score."""
    if score >= 90:
        return "#16a34a"  # green
    elif score >= 70:
        return "#ca8a04"  # yellow
    elif score >= 50:
        return "#ea580c"  # orange
    else:
        return "#dc2626"  # red


def generate_finding_html(finding: Dict[str, Any]) -> str:
    """Generate HTML for a single finding."""
    severity = finding.get("severity", "low")
    return f'''
    <div class="finding">
        <div class="finding-header">
            <span class="severity-badge severity-{severity}">{severity}</span>
            <span class="finding-domain">{finding.get("domain", "unknown")}</span>
        </div>
        <p class="finding-text">{finding.get("finding", "")}</p>
        <div class="recommendation">
            <strong>Fix:</strong> {finding.get("recommendation", "")}
        </div>
    </div>
    '''


def generate_html_report(report: Dict[str, Any]) -> str:
    """Generate HTML report from audit results."""
    findings_html = ""
    for finding in report.get("findings", []):
        findings_html += generate_finding_html(finding)

    return HTML_TEMPLATE.format(
        score=report.get("score", 0),
        rating=report.get("rating", "Unknown"),
        score_color=get_score_color(report.get("score", 0)),
        critical=report.get("summary", {}).get("critical", 0),
        high=report.get("summary", {}).get("high", 0),
        medium=report.get("summary", {}).get("medium", 0),
        low=report.get("summary", {}).get("low", 0),
        passed=report.get("summary", {}).get("passed", 0),
        timestamp=report.get("timestamp", ""),
        platform=report.get("platform", ""),
        findings_html=findings_html,
    )


def generate_markdown_report(report: Dict[str, Any]) -> str:
    """Generate Markdown report from audit results."""
    lines = [
        "# 🔒 Security Audit Report\n",
        f"**Timestamp:** {report.get('timestamp', '')}",
        f"**Platform:** {report.get('platform', '')}",
        f"**Config:** {report.get('config_path', 'Not found')}\n",
        f"## Score: {report.get('score', 0)}/100 ({report.get('rating', 'Unknown')})\n",
        "## Summary\n",
        "| Severity | Count |",
        "|----------|-------|",
        f"| 🔴 Critical | {report.get('summary', {}).get('critical', 0)} |",
        f"| 🟠 High | {report.get('summary', {}).get('high', 0)} |",
        f"| 🟡 Medium | {report.get('summary', {}).get('medium', 0)} |",
        f"| 🔵 Low | {report.get('summary', {}).get('low', 0)} |",
        f"| ✅ Passed | {report.get('summary', {}).get('passed', 0)} |\n",
    ]

    if report.get("findings"):
        lines.append("## Findings\n")
        for finding in report["findings"]:
            severity = finding.get("severity", "low").upper()
            domain = finding.get("domain", "unknown")
            lines.append(f"### {severity}: {domain}\n")
            lines.append(f"- **Finding:** {finding.get('finding', '')}")
            lines.append(f"- **Recommendation:** {finding.get('recommendation', '')}\n")

    lines.extend([
        "---\n",
        "*This audit was performed by Security Audit Enhanced.*",
        "*No changes were made to your configuration.*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate security audit reports")
    parser.add_argument("--input", type=Path, required=True, help="Input JSON file")
    parser.add_argument("--format", choices=["html", "markdown"], default="html", help="Output format")
    parser.add_argument("--output", type=Path, required=True, help="Output file")

    args = parser.parse_args()

    # Load input
    with open(args.input) as f:
        report = json.load(f)

    # Generate output
    if args.format == "html":
        content = generate_html_report(report)
    else:
        content = generate_markdown_report(report)

    # Write output
    args.output.write_text(content)
    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()

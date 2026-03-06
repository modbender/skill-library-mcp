#!/usr/bin/env python3
"""
Security Audit Report Generator
Pro-tier feature - Generate professional audit reports

Creates detailed security audit reports in multiple formats (markdown, HTML, JSON)
from scan results. Ideal for delivering to clients or for compliance documentation.

Usage:
    python3 generate_report.py --scan-dir /path/to/project --output report.md
    python3 generate_report.py --input scan_results.json --format html
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from .threat_scan import scan_directory
from .secret_scan import scan_files


class AuditReportGenerator:
    """Generates professional security audit reports"""

    def __init__(self, config=None):
        self.config = config or {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_from_scan(self, scan_dir, output_file=None, format='markdown'):
        """
        Generate report by running a fresh scan

        Args:
            scan_dir: Directory to scan
            output_file: Output file path (optional)
            format: Output format (markdown, html, json)

        Returns:
            Report content as string
        """
        # Run scans
        print(f"🔍 Scanning {scan_dir}...")

        threat_results = scan_directory(
            scan_dir,
            severity=self.config.get('severity', 'all')
        )

        secret_results = scan_files(
            scan_dir,
            patterns_file=self.config.get('patterns_file')
        )

        # Generate report
        report_data = self._compile_report_data(scan_dir, threat_results, secret_results)
        report_content = self._format_report(report_data, format)

        # Save to file if specified
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"✅ Report saved to: {output_file}")

        return report_content, report_data

    def generate_from_results(self, input_file, output_file=None, format='markdown'):
        """
        Generate report from existing scan results

        Args:
            input_file: JSON file with scan results
            output_file: Output file path (optional)
            format: Output format (markdown, html, json)

        Returns:
            Report content as string
        """
        with open(input_file, 'r') as f:
            scan_data = json.load(f)

        report_data = self._compile_report_data(
            scan_data.get('scan_path', 'Unknown'),
            scan_data.get('threat_results'),
            scan_data.get('secret_results')
        )

        report_content = self._format_report(report_data, format)

        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"✅ Report saved to: {output_file}")

        return report_content, report_data

    def _compile_report_data(self, scan_path, threat_results, secret_results):
        """Compile scan results into report data structure"""
        total_issues = 0
        severity_counts = threat_results.get('severity_counts', {}) if threat_results else {}

        for severity in ['critical', 'high', 'medium', 'low']:
            total_issues += severity_counts.get(severity, 0)

        if secret_results:
            total_issues += len(secret_results)

        return {
            'metadata': {
                'scan_path': str(scan_path),
                'timestamp': self.timestamp,
                'scanner': 'ObekT Security Pro',
                'version': '1.1.0'
            },
            'summary': {
                'total_issues': total_issues,
                'severity_breakdown': severity_counts,
                'secrets_found': len(secret_results) if secret_results else 0,
                'overall_severity': self._calculate_overall_severity(severity_counts, secret_results)
            },
            'threats': threat_results.get('findings', []) if threat_results else [],
            'secrets': secret_results or [],
            'recommendations': self._generate_recommendations(severity_counts, secret_results)
        }

    def _calculate_overall_severity(self, severity_counts, secret_results):
        """Calculate overall severity level"""
        if severity_counts.get('critical', 0) > 0:
            return 'CRITICAL'
        if severity_counts.get('high', 0) > 0:
            return 'HIGH'
        if secret_results and len(secret_results) > 0:
            return 'HIGH'
        if severity_counts.get('medium', 0) > 0:
            return 'MEDIUM'
        if severity_counts.get('low', 0) > 0:
            return 'LOW'
        return 'CLEAR'

    def _generate_recommendations(self, severity_counts, secret_results):
        """Generate contextual recommendations"""
        recommendations = []

        if severity_counts.get('critical', 0) > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'issue': 'Critical security vulnerabilities detected',
                'action': 'Immediately address all critical findings before deployment'
            })

        if severity_counts.get('high', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'{severity_counts.get("high", 0)} high-severity issues found',
                'action': 'Review and fix high-severity vulnerabilities in next sprint'
            })

        if secret_results and len(secret_results) > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'issue': f'{len(secret_results)} potential secrets exposed',
                'action': 'Rotate all exposed credentials and remove from code. Use environment variables or secret management.'
            })

        if severity_counts.get('medium', 0) > 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': 'Multiple medium-severity issues',
                'action': 'Create a technical debt backlog to address medium-severity items'
            })

        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'issue': 'No significant issues found',
                'action': 'Continue following secure coding best practices'
            })

        return recommendations

    def _format_report(self, report_data, format):
        """Format report in specified format"""
        if format == 'json':
            return json.dumps(report_data, indent=2)
        elif format == 'html':
            return self._format_html_report(report_data)
        else:  # markdown
            return self._format_markdown_report(report_data)

    def _format_markdown_report(self, data):
        """Generate markdown report"""
        lines = []

        # Header
        lines.append(f"# Security Audit Report")
        lines.append("")
        lines.append(f"**Generated:** {data['metadata']['timestamp']}")
        lines.append(f"**Scanner:** {data['metadata']['scanner']} v{data['metadata']['version']}")
        lines.append(f"**Target:** `{data['metadata']['scan_path']}`")
        lines.append("")

        # Summary
        lines.append("## Executive Summary")
        lines.append("")
        severity_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'CLEAR': '✅'
        }
        overall = data['summary']['overall_severity']
        lines.append(f"**Overall Severity:** {severity_emoji.get(overall, '')} {overall}")
        lines.append("")
        lines.append(f"- **Total Issues:** {data['summary']['total_issues']}")
        lines.append(f"- **Secrets Found:** {data['summary']['secrets_found']}")
        lines.append("")

        # Severity breakdown
        lines.append("### Severity Breakdown")
        lines.append("")
        breakdown = data['summary']['severity_breakdown']
        for severity in ['critical', 'high', 'medium', 'low']:
            count = breakdown.get(severity, 0)
            emoji = severity_emoji.get(severity.upper(), '')
            lines.append(f"- {emoji} **{severity.upper()}:** {count}")
        lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        for rec in data['recommendations']:
            lines.append(f"### {rec['priority']}")
            lines.append(f"- **Issue:** {rec['issue']}")
            lines.append(f"- **Action:** {rec['action']}")
            lines.append("")

        # Threat details
        if data['threats']:
            lines.append("## Threat Findings")
            lines.append("")
            for i, threat in enumerate(data['threats'], 1):
                lines.append(f"### {i}. [{threat.get('severity', 'unknown').upper()}] {threat.get('file', 'unknown')}")
                lines.append(f"**Line:** {threat.get('line', 'unknown')}")
                lines.append(f"**Pattern:** {threat.get('pattern', 'unknown')}")
                lines.append("")
                lines.append(f"```")
                lines.append(threat.get('code_snippet', 'N/A'))
                lines.append(f"```")
                lines.append("")
                lines.append(f"**Description:** {threat.get('description', 'N/A')}")
                lines.append("")

        # Secret details
        if data['secrets']:
            lines.append("## Secret Findings")
            lines.append("")
            lines.append(f"⚠️ **{len(data['secrets'])} potential secrets found**")
            lines.append("")
            for i, secret in enumerate(data['secrets'], 1):
                lines.append(f"### {i}. {secret.get('file', 'unknown')}")
                lines.append(f"**Line:** {secret.get('line', 'unknown')}")
                lines.append(f"**Type:** {secret.get('type', 'unknown')}")
                lines.append(f"**Match:** `{secret.get('match', 'N/A')[:50]}...`")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by ObekT Security Pro - Professional security audit toolkit*")

        return '\n'.join(lines)

    def _format_html_report(self, data):
        """Generate HTML report"""
        severity_colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#ca8a04',
            'low': '#16a34a',
            'clear': '#15803d'
        }

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Audit Report - {data['metadata']['timestamp']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        h3 {{ color: #4b5563; }}
        .summary {{ background: #f3f4f6; padding: 20px; border-radius: 6px; margin: 20px 0; }}
        .severity-banner {{ padding: 15px; border-radius: 6px; margin: 20px 0; color: white; text-align: center; font-weight: bold; }}
        .finding {{ border-left: 4px solid #ddd; padding-left: 15px; margin: 15px 0; }}
        .code {{ background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Security Audit Report</h1>

        <p><strong>Generated:</strong> {data['metadata']['timestamp']}<br>
        <strong>Scanner:</strong> {data['metadata']['scanner']} v{data['metadata']['version']}<br>
        <strong>Target:</strong> <code>{data['metadata']['scan_path']}</code></p>

        <h2>Executive Summary</h2>
        <div class="summary">
            <p><strong>Overall Severity:</strong></p>
            <div class="severity-banner" style="background: {severity_colors.get(data['summary']['overall_severity'].lower(), '#6b7280')}">
                {data['summary']['overall_severity']}
            </div>
            <p><strong>Total Issues:</strong> {data['summary']['total_issues']}<br>
            <strong>Secrets Found:</strong> {data['summary']['secrets_found']}</p>
        </div>

        <h2>Severity Breakdown</h2>
        <ul>
            <li><span class="tag" style="background: {severity_colors['critical']}">CRITICAL</span> {data['summary']['severity_breakdown'].get('critical', 0)}</li>
            <li><span class="tag" style="background: {severity_colors['high']}">HIGH</span> {data['summary']['severity_breakdown'].get('high', 0)}</li>
            <li><span class="tag" style="background: {severity_colors['medium']}">MEDIUM</span> {data['summary']['severity_breakdown'].get('medium', 0)}</li>
            <li><span class="tag" style="background: {severity_colors['low']}">LOW</span> {data['summary']['severity_breakdown'].get('low', 0)}</li>
        </ul>

        <h2>Recommendations</h2>
"""

        for rec in data['recommendations']:
            html += f"""        <div class="finding">
            <h3><span class="tag" style="background: {severity_colors.get(rec['priority'].lower(), '#6b7280')}">{rec['priority']}</span></h3>
            <p><strong>Issue:</strong> {rec['issue']}<br>
            <strong>Action:</strong> {rec['action']}</p>
        </div>
"""

        html += """    </div>
</body>
</html>"""

        return html


def main():
    parser = argparse.ArgumentParser(description='Generate security audit reports')
    parser.add_argument('--scan-dir', '-d', type=str,
                        help='Directory to scan (if not using --input)')
    parser.add_argument('--input', '-i', type=str,
                        help='Input JSON file with scan results')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file path')
    parser.add_argument('--format', '-f', type=str, choices=['markdown', 'html', 'json'],
                        default='markdown', help='Output format (default: markdown)')
    parser.add_argument('--severity', '-s', type=str, default='all',
                        help='Severity levels to include in scan (default: all)')

    args = parser.parse_args()

    config = {
        'severity': args.severity
    }

    generator = AuditReportGenerator(config)

    if args.input:
        # Generate from existing results
        content, data = generator.generate_from_results(
            args.input,
            args.output,
            args.format
        )
    elif args.scan_dir:
        # Run new scan and generate report
        content, data = generator.generate_from_scan(
            args.scan_dir,
            args.output,
            args.format
        )
    else:
        print("❌ Error: Must specify either --scan-dir or --input")
        sys.exit(1)

    print(f"✅ Report generated successfully")
    print(f"   Overall Severity: {data['summary']['overall_severity']}")
    print(f"   Total Issues: {data['summary']['total_issues']}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Skill Auditor - Security audit for agent skills
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import json

@dataclass
class AuditFindings:
    """Security audit findings for a skill"""
    skill_path: str
    total_issues: int
    critical_issues: List[str]
    high_issues: List[str]
    medium_issues: List[str]
    low_issues: List[str]
    recommendations: List[str]

# Skill-specific security checks
SKILL_SECURITY_CHECKS = {
    "critical": [
        ("exec() or eval() usage", r'(?:exec|eval)\s*\(', "Direct code execution with potentially unsafe input"),
        ("unsafe subprocess call", r'subprocess\.(?:call|Popen)(?!\s*\[)', "subprocess without args list - injection risk"),
        ("os.system() usage", r'os\.system\s*\(', "Shell command execution - potential command injection"),
        ("hardcoded crypto key", r'(?:mnemonic|private.*key|seed.*phrase|wallet.*secret)', "Hardcoded wallet/crypto secrets"),
        ("credential in code", r'(?:api[_-]?key|secret|password|token)\s*=\s*["\']', "Hardcoded credentials"),
    ],
    "high": [
        ("file upload without validation", r'(?:upload|save|download).*(?:file)[^\n]*(?![\w\s]*validate)', "File operations without validation checks"),
        ("path traversal risk", r'\.join.*\.\.|path.*\.\.', "Potential path traversal via .."),
        ("unsafe file operation", r'open\s*\([^)]*\.\.\.', "File open with potentially unsafe path"),
        ("network request without validation", r'(?:requests|http|fetch).*\{(?:request|input)', "Network request with unsanitized input"),
        ("unsafe shell command", r'(?i)shell\s*=\s*[Tt]rue', "Shell execution enabled - high risk"),
        ("weak random", r'import random[^#\n]*\n(?:?!.*secrets)', "Using random module instead of secrets for crypto"),
    ],
    "medium": [
        ("logging sensitive data", r'log\.(?:debug|info|warning).*(?:password|token|key|api)', "Logging potentially sensitive data"),
        ("unsafe redirect", r'redirect.*request\.', "Open redirect using request data"),
        ("missing error handling", r'except\s*:[^#\n]*(?!.*log|print)', "Bare except without logging - security issues swallowed"),
        ("hardcoded path", r'[\'"]/home/\w+|C:\\\\Users\\\\', "Hardcoded user-specific paths"),
        ("unsafe URL handling", r'url.*\+.*request', "URL construction with user input"),
    ],
    "low": [
        ("commented code", r'^\s*#[^#\n]*(?:password|api.*key|secret)', "Sensitive data in comments"),
        ("debug prints", r'print\s*\([^)]*(?:debug|test)', "Leftover debug output"),
        ("TODO/FIXME comments", r'(?:TODO|FIXME|HACK).*security', "Security-related TODOs need attention"),
    ],
}

def check_file_safety(skill_path: Path) -> List[Dict]:
    """Check for dangerous file operations in scripts"""
    issues = []

    scripts_dir = skill_path / 'scripts'
    if not scripts_dir.exists():
        return issues

    for script_file in scripts_dir.glob('*.py'):
        with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Check for file operations
        dangerous_patterns = [
            (r'open\s*\([^)]*\.\.\.', "CRITICAL", "Path traversal risk"),
            (r'os\.remove\s*\(', "HIGH", "Destructive file operation"),
            (r'shutil\.rmtree', "CRITICAL", "Recursive directory deletion"),
            (r'os\.system\s*\(\s*.*rm', "CRITICAL", "System command with rm"),
        ]

        for pattern, severity, description in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'file': str(script_file.relative_to(skill_path)),
                    'severity': severity,
                    'issue': description,
                    'line': 'check entire file'
                })

    return issues

def check_external_dependencies(skill_path: Path) -> List[Dict]:
    """Check for external dependencies and network calls"""
    issues = []

    for script_file in skill_path.rglob('*.py'):
        try:
            with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for network calls without validation
            network_issues = [
                (r'requests\.(?:get|post|put|delete).*url\s*\+=', "HIGH", "URL constructed from variable"),
                (r'subprocess\.call.*http', "HIGH", "Network command via subprocess"),
            ]

            for pattern, severity, description in network_issues:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        'file': str(script_file.relative_to(skill_path)),
                        'severity': severity,
                        'issue': description,
                        'line': 'check file'
                    })
        except Exception:
            continue

    return issues

def check_skill_structure(skill_path: Path) -> List[Dict]:
    """Check skill structure and best practices"""
    issues = []

    # Check for SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        issues.append({
            'file': 'skill structure',
            'severity': 'HIGH',
            'issue': 'Missing SKILL.md - skills must include SKILL.md',
            'line': 'N/A'
        })
    else:
        # Validate SKILL.md frontmatter
        with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if not re.search(r'^---\s*$', content[:100], re.MULTILINE):
            issues.append({
                'file': 'SKILL.md',
                'severity': 'MEDIUM',
                'issue': 'Invalid frontmatter - should start with ---',
                'line': 'line 1'
            })

        if 'name:' not in content[:500]:
            issues.append({
                'file': 'SKILL.md',
                'severity': 'HIGH',
                'issue': 'Missing required field: name',
                'line': 'frontmatter'
            })

        if 'description:' not in content[:500]:
            issues.append({
                'file': 'SKILL.md',
                'severity': 'HIGH',
                'issue': 'Missing required field: description',
                'line': 'frontmatter'
            })

    # Check unsafe files
    dangerous_files = ['token.txt', 'secrets.yaml', '.env', 'credentials.json']
    for filename in dangerous_files:
        if (skill_path / filename).exists():
            issues.append({
                'file': filename,
                'severity': 'CRITICAL',
                'issue': f'Secrets file committed: {filename}',
                'line': 'N/A'
            })

    return issues

def check_code_patterns(skill_path: Path) -> List[Dict]:
    """Run pattern-based security checks on all files"""
    issues = []

    for file_path in skill_path.rglob('*'):
        if not file_path.is_file():
            continue

        extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}
        if file_path.suffix not in extensions:
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            for severity, checks in SKILL_SECURITY_CHECKS.items():
                for pattern_name, pattern, description in checks:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Filter out false positives (comments, examples)
                            if '#' in line or 'example' in line.lower():
                                continue

                            issues.append({
                                'file': str(file_path.relative_to(skill_path)),
                                'severity': severity.upper(),
                                'issue': f'{pattern_name}: {description}',
                                'line': line_num
                            })
                            break
        except Exception:
            continue

    return issues

def generate_recommendations(issues: List[Dict]) -> List[str]:
    """Generate actionable recommendations based on findings"""
    recommendations = []

    severity_counts = {}
    for issue in issues:
        severity = issue['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    if severity_counts.get('CRITICAL', 0) > 0:
        recommendations.append("🚨 CRITICAL: Immediate action required. Review and fix all critical issues before deploying.")

    if severity_counts.get('HIGH', 0) > 0:
        recommendations.append("⚠️  HIGH: Multiple high-severity issues found. Prioritize fixes before public release.")

    # Check for specific issue types
    issue_types = [issue['issue'].lower() for issue in issues]
    if any('credential' in it or 'secret' in it or 'key' in it for it in issue_types):
        recommendations.append("🔑 Remove all hardcoded credentials. Use environment variables or secret management.")

    if any('eval' in it or 'exec' in it or 'system' in it for it in issue_types):
        recommendations.append("⚡ Avoid dynamic code execution. Use safer alternatives or validate all inputs thoroughly.")

    if any('file' in it and ('upload' in it or 'download' in it) for it in issue_types):
        recommendations.append("📁 Validate all file operations. Restrict file types, check file sizes, and sanitize paths.")

    if any('network' in it or 'url' in it or 'request' in it for it in issue_types):
        recommendations.append("🌐 Validate all network inputs. Use allowlists, sanitize URLs, and implement rate limiting.")

    if 'SKILL.md' in str(issue_types):
        recommendations.append("📝 Ensure SKILL.md is complete with proper frontmatter (name and description fields).")

    return recommendations

def audit_skill(skill_path: Path, quick: bool = False) -> AuditFindings:
    """Perform security audit on a skill"""
    print(f"\nAuditing skill: {skill_path}\n")

    issues = []

    if quick:
        # Quick audit: structure checks only
        issues.extend(check_skill_structure(skill_path))
    else:
        # Full audit
        issues.extend(check_skill_structure(skill_path))
        issues.extend(check_file_safety(skill_path))
        issues.extend(check_external_dependencies(skill_path))
        issues.extend(check_code_patterns(skill_path))

    # Categorize by severity
    critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
    high_issues = [i for i in issues if i['severity'] == 'HIGH']
    medium_issues = [i for i in issues if i['severity'] == 'MEDIUM']
    low_issues = [i for i in issues if i['severity'] == 'LOW']

    # Generate recommendations
    recommendations = generate_recommendations(issues)

    return AuditFindings(
        skill_path=str(skill_path),
        total_issues=len(issues),
        critical_issues=[f"{i['file']}:{i['line']} - {i['issue']}" for i in critical_issues],
        high_issues=[f"{i['file']}:{i['line']} - {i['issue']}" for i in high_issues],
        medium_issues=[f"{i['file']}:{i['line']} - {i['issue']}" for i in medium_issues],
        low_issues=[f"{i['file']}:{i['line']} - {i['issue']}" for i in low_issues],
        recommendations=recommendations
    )

def format_audit_report(findings: AuditFindings, output_format: str = 'text'):
    """Format audit findings as report"""
    if output_format == 'json':
        return json.dumps({
            'skill_path': findings.skill_path,
            'total_issues': findings.total_issues,
            'critical_issues': findings.critical_issues,
            'high_issues': findings.high_issues,
            'medium_issues': findings.medium_issues,
            'low_issues': findings.low_issues,
            'recommendations': findings.recommendations
        }, indent=2)

    if output_format == 'markdown':
        md = f"# Security Audit Report\n\n"
        md += f"**Skill:** `{findings.skill_path}`\n"
        md += f"**Total Issues:** {findings.total_issues}\n\n"

        # Severity summary
        md += "## Severity Summary\n\n"
        md += f"- 🚨 **CRITICAL:** {len(findings.critical_issues)}\n"
        md += f"- ⚠️  **HIGH:** {len(findings.high_issues)}\n"
        md += f"- ⚡ **MEDIUM:** {len(findings.medium_issues)}\n"
        md += f"- ℹ️  **LOW:** {len(findings.low_issues)}\n\n"

        # Findings by severity
        if findings.critical_issues:
            md += "## CRITICAL Issues\n\n"
            for issue in findings.critical_issues:
                md += f"- {issue}\n"
            md += "\n"

        if findings.high_issues:
            md += "## HIGH Issues\n\n"
            for issue in findings.high_issues:
                md += f"- {issue}\n"
            md += "\n"

        if findings.medium_issues:
            md += "## MEDIUM Issues\n\n"
            for issue in findings.medium_issues:
                md += f"- {issue}\n"
            md += "\n"

        if findings.low_issues:
            md += "## LOW Issues\n\n"
            for issue in findings.low_issues:
                md += f"- {issue}\n"
            md += "\n"

        # Recommendations
        if findings.recommendations:
            md += "## Recommendations\n\n"
            for rec in findings.recommendations:
                md += f"- {rec}\n"
            md += "\n"

        return md

    # Default text format
    text = "="*60 + "\n"
    text += "SECURITY AUDIT REPORT\n"
    text += "="*60 + "\n\n"
    text += f"Skill: {findings.skill_path}\n"
    text += f"Total Issues: {findings.total_issues}\n\n"

    text += "-"*60 + "\n"
    text += "SEVERITY SUMMARY\n"
    text += "-"*60 + "\n"
    text += f"🚨 CRITICAL: {len(findings.critical_issues)}\n"
    text += f"⚠️  HIGH:     {len(findings.high_issues)}\n"
    text += f"⚡ MEDIUM:   {len(findings.medium_issues)}\n"
    text += f"ℹ️  LOW:      {len(findings.low_issues)}\n\n"

    if findings.critical_issues:
        text += "-"*60 + "\n"
        text += "CRITICAL ISSUES\n"
        text += "-"*60 + "\n"
        for issue in findings.critical_issues:
            text += f"  [CRITICAL] {issue}\n"
        text += "\n"

    if findings.high_issues:
        text += "-"*60 + "\n"
        text += "HIGH ISSUES\n"
        text += "-"*60 + "\n"
        for issue in findings.high_issues:
            text += f"  [HIGH] {issue}\n"
        text += "\n"

    if findings.medium_issues:
        text += "-"*60 + "\n"
        text += "MEDIUM ISSUES\n"
        text += "-"*60 + "\n"
        for issue in findings.medium_issues:
            text += f"  [MEDIUM] {issue}\n"
        text += "\n"

    if findings.low_issues:
        text += "-"*60 + "\n"
        text += "LOW ISSUES\n"
        text += "-"*60 + "\n"
        for issue in findings.low_issues:
            text += f"  [LOW] {issue}\n"
        text += "\n"

    if findings.recommendations:
        text += "-"*60 + "\n"
        text += "RECOMMENDATIONS\n"
        text += "-"*60 + "\n"
        for rec in findings.recommendations:
            text += f"  {rec}\n"
        text += "\n"

    return text

def main():
    parser = argparse.ArgumentParser(description='Skill Auditor - Security audit for agent skills')
    parser.add_argument('skill_path', help='Path to the skill directory')
    parser.add_argument('--quick', action='store_true', help='Quick audit (structure only)')
    parser.add_argument('--output', default='text', choices=['text', 'json', 'markdown'], help='Output format')

    args = parser.parse_args()

    skill_path = Path(args.skill_path)

    if not skill_path.exists():
        print(f"Error: Skill path not found: {args.skill_path}")
        return 1

    if not skill_path.is_dir():
        print(f"Error: Skill path must be a directory: {args.skill_path}")
        return 1

    # Perform audit
    findings = audit_skill(skill_path, quick=args.quick)

    # Format and output
    report = format_audit_report(findings, args.output)
    print(report)

    # Exit code based on findings
    if len(findings.critical_issues) > 0:
        return 2
    elif len(findings.high_issues) > 0:
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(main())

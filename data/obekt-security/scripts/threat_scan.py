#!/usr/bin/env python3
"""
Threat Scanner - Pattern-based vulnerability detection
Scans code files for common security issues
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ThreatMatch:
    """Represents a matched security threat"""
    severity: str
    category: str
    pattern: str
    file: str
    line: int
    snippet: str
    recommendation: str

# Vulnerability patterns organized by severity and category
PATTERNS = {
    "critical": {
        "command_injection": [
            (r'exec\s*\(\s*["\'].*f["\'].*["\']', "String formatting in exec() - command injection risk"),
            (r'eval\s*\(\s*["\'].*f["\'].*["\']', "String formatting in eval() - eval injection risk"),
            (r'os\.system\s*\(\s*["\'].*\{.*\}', "User input in os.system() - command injection"),
            (r'subprocess\.call\s*\([^)]*shell=True', "shell=True with user input - command injection"),
            (r'popen\s*\(\s*["\'].*\{.*\}', "User input in popen() - command injection"),
        ],
        "sql_injection": [
            (r'execute\s*\([^)]*["\']\s*["\'].*\+[^)]*\)', "SQL query with concatenation - SQL injection"),
            (r'query\s*\([^)]*["\']\s*["\'].*\+[^)]*\)', "SQL query with concatenation - SQL injection"),
            (r'cursor\.execute\s*\([^)]*["\']\s*["\'].*\+[^)]*\)', "SQL execute with concatenation - injection"),
        ],
        "crypto_drain": [
            (r'mnemonic|private.*key|seed.*phrase\s*=.*["\'][\w\s]{50,}', "Hardcoded crypto seed/mnemonic - wallet drain risk"),
            (r'secret.*key|priv.*key\s*=.*["\'][a-fA-F0-9]{64}', "Hardcoded private key - wallet drain risk"),
        ],
    },
    "high": {
        "hardcoded_secrets": [
            (r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded API key found"),
            (r'secret[_-]?key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded secret key found"),
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded password found"),
            (r'access[_-]?token\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded access token found"),
        ],
        "weak_crypto": [
            (r'hashlib\.md5\s*\(', "MD5 hash - cryptographically weak"),
            (r'hashlib\.sha1\s*\(', "SHA1 hash - cryptographically weak"),
            (r'Crypto\.Cipher\.DES\s*\(', "DES cipher - broken and insecure"),
            (r'Crypto\.Cipher\.RC4\s*\(', "RC4 cipher - broken and insecure"),
        ],
        "file_traversal": [
            (r'open\s*\([^)]*\.\.\.', "Path traversal pattern with .. - directory traversal risk"),
            (r'Path\s*\([^)]*\.\.\.', "Path traversal pattern with .. - directory traversal risk"),
            (r'os\.path\.join.*os\.path\.abspath', "Potential path manipulation - verify input"),
        ],
        "weak_random": [
            (r'random\.random\s*\(', "random.random() - not cryptographically secure"),
            (r'random\.randint\s*\(', "random.randint() - not cryptographically secure"),
            (r'math\.random', "math.random() - predictable numbers"),
        ],
    },
    "medium": {
        "info_leakage": [
            (r'print\s*\([^)]*password', "Password in print statement - info leakage"),
            (r'print\s*\([^)]*token', "Token in print statement - info leakage"),
            (r'print\s*\([^)]*key', "Key in print statement - info leakage"),
            (r'log\.(debug|info|warning)\s*\([^)]*password', "Sensitive data in logs"),
        ],
        "unsafe_redirect": [
            (r'redirect\s*\([^)]*request\.', "Open redirect - potential phishing via request data"),
            (r'Response\.redirect\s*\([^)]*request\.', "Open redirect - potential phishing via request data"),
        ],
        "missing_validation": [
            (r'request\.(GET|POST|json|form)\[["\']\w+["\']\](?!\s*or)', "Request data without validation"),
            (r'input\s*\(\s*\)(?!\s*\.strip|\.lower|\s*int', "User input without validation"),
        ],
    },
    "low": {
        "deprecated": [
            (r'subprocess\.call\s*\(\s*\[', "subprocess.call - prefer subprocess.run with check=True"),
        ],
        "hardcoded_paths": [
            (r"[\"'](?:/home/\w+|C:\\\\Users\\\\)[^\"'\)]+[\"']", "Hardcoded user path - may not be portable"),
        ],
    },
}

RECOMMENDATIONS = {
    "command_injection": "Use parameterized commands or subprocess.run with args list, never shell=True with user input",
    "sql_injection": "Use parameterized queries (cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,)))",
    "crypto_drain": "Remove hardcoded secrets. Use environment variables or secure key management (AWS Secrets Manager, HashiCorp Vault)",
    "hardcoded_secrets": "Use environment variables or secret management services. Never commit secrets to version control",
    "weak_crypto": "Use strong alternatives: SHA-256+ for hashing, AES-256-GCM for encryption",
    "file_traversal": "Validate and sanitize file paths. Use os.path.basename() or whitelist allowed directories",
    "weak_random": "Use secrets module for cryptographic operations: secrets.randbelow(), secrets.token_hex()",
    "info_leakage": "Remove sensitive data from logs and debug output. Use proper logging levels and filtering",
    "unsafe_redirect": "Validate redirect URLs against a whitelist. Use Django's safe_url_validator or similar",
    "missing_validation": "Always validate and sanitize user input. Use schemas, validators, or pydantic models",
}

def get_context_snippet(line_content, context_lines=2):
    """Get a snippet around the matched line"""
    lines = line_content.strip()
    return lines[:100].strip()

def scan_file(file_path: Path, severities: List[str]) -> List[ThreatMatch]:
    """Scan a single file for threats"""
    matches = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        for severity in severities:
            if severity not in PATTERNS:
                continue

            for category, patterns in PATTERNS[severity].items():
                for pattern, description in patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            matches.append(ThreatMatch(
                                severity=severity.upper(),
                                category=category,
                                pattern=description,
                                file=str(file_path),
                                line=line_num,
                                snippet=get_context_snippet(line),
                                recommendation=RECOMMENDATIONS.get(category, "Review security implications")
                            ))

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return matches

def scan_directory(directory: Path, severities: List[str], recursive: bool = True) -> Dict[str, List[ThreatMatch]]:
    """Scan a directory for threats"""
    results = {}
    extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.rb', '.php', '.sh', '.sql'}

    if recursive:
        files = [f for f in directory.rglob('*') if f.suffix in extensions and f.is_file()]
    else:
        files = [f for f in directory.glob('*') if f.suffix in extensions and f.is_file()]

    print(f"Scanning {len(files)} files...")

    for file_path in files:
        matches = scan_file(file_path, severities)
        if matches:
            results[str(file_path)] = matches

    return results

def format_results(results: Dict[str, List[ThreatMatch]], output_format: str = 'text'):
    """Format scan results for output"""
    all_matches = []
    for file_path, matches in results.items():
        all_matches.extend(matches)

    # Sort by severity (critical > high > medium > low)
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    all_matches.sort(key=lambda x: severity_order.get(x.severity, 99))

    if output_format == 'json':
        return json.dumps([asdict(m) for m in all_matches], indent=2, default=str)

    if output_format == 'markdown':
        md = "# Security Scan Results\n\n"
        md += f"**Total findings:** {len(all_matches)}\n\n"

        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            severity_matches = [m for m in all_matches if m.severity == severity]
            if not severity_matches:
                continue

            md += f"## {severity} ({len(severity_matches)})\n\n"

            for match in severity_matches:
                md += f"### {match.category}\n"
                md += f"- **File:** `{match.file}:{match.line}`\n"
                md += f"- **Pattern:** {match.pattern}\n"
                md += f"- **Snippet:** `{match.snippet}`\n"
                md += f"- **Recommendation:** {match.recommendation}\n\n"

            md += "---\n\n"

        return md

    # Default text format
    text = f"SECURITY SCAN RESULTS\n{'='*50}\n"
    text += f"Total findings: {len(all_matches)}\n\n"

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        severity_matches = [m for m in all_matches if m.severity == severity]
        if not severity_matches:
            continue

        text += f"\n{severity} ({len(severity_matches)} issues)\n"
        text += "-" * len(severity) + "\n\n"

        for match in severity_matches:
            text += f"  {match.category}\n"
            text += f"  File: {match.file}:{match.line}\n"
            text += f"  Issue: {match.pattern}\n"
            text += f"  Snippet: {match.snippet}\n"
            text += f"  Fix: {match.recommendation}\n\n"

    return text

def main():
    parser = argparse.ArgumentParser(description='Threat Scanner - Pattern-based vulnerability detection')
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--severity', default='all', help='Filter by severity (critical,high,medium,low,all)')
    parser.add_argument('--output', default='text', choices=['text', 'json', 'markdown'], help='Output format')
    parser.add_argument('--no-recursive', action='store_true', help='Do not scan recursively')

    args = parser.parse_args()

    # Determine severities to scan
    if args.severity == 'all':
        severities = ['critical', 'high', 'medium', 'low']
    else:
        severities = [s.lower() for s in args.severity.split(',')]

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {args.path}")
        return 1

    # Scan
    if path.is_file():
        matches = scan_file(path, severities)
        results = {str(path): matches} if matches else {}
    else:
        results = scan_directory(path, severities, recursive=not args.no_recursive)

    # Format and output
    output = format_results(results, args.output)
    print(output)

    return 0 if not results else 1

if __name__ == '__main__':
    exit(main())

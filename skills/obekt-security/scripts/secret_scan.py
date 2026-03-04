#!/usr/bin/env python3
"""
Secret Scanner - Detect hardcoded credentials and secrets
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import json

@dataclass
class SecretMatch:
    """Represents a matched secret"""
    secret_type: str
    severity: str
    file: str
    line: int
    value_preview: str
    context: str

# Secret detection patterns
SECRET_PATTERNS = [
    # AWS keys
    {
        "type": "AWS Access Key",
        "severity": "critical",
        "pattern": r'AKIA[0-9A-Z]{16}',
        "description": "AWS access key ID"
    },
    {
        "type": "AWS Secret Key",
        "severity": "critical",
        "pattern": r'(?i)aws.*secret.*["\']?[:=]\s*["\']([a-zA-Z0-9/+]{40})["\']',
        "description": "AWS secret access key"
    },
    # Generic API keys
    {
        "type": "API Key",
        "severity": "high",
        "pattern": r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "description": "Generic API key"
    },
    {
        "type": "API Secret",
        "severity": "high",
        "pattern": r'(?i)api[_-]?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "description": "Generic API secret"
    },
    {
        "type": "API Token",
        "severity": "high",
        "pattern": r'(?i)api[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        "description": "Generic API token"
    },
    # Service-specific keys
    {
        "type": "GitHub Token",
        "severity": "critical",
        "pattern": r'ghp_[a-zA-Z0-9]{36}',
        "description": "GitHub personal access token"
    },
    {
        "type": "GitHub OAuth",
        "severity": "high",
        "pattern": r'gho_[a-zA-Z0-9]{36}',
        "description": "GitHub OAuth token"
    },
    {
        "type": "GitHub App Secret",
        "severity": "critical",
        "pattern": r'gh[us]_[a-zA-Z0-9]{36}',
        "description": "GitHub server-to-server token"
    },
    {
        "type": "Slack Token",
        "severity": "high",
        "pattern": r'xox[baprs]-[a-zA-Z0-9-]{10,}',
        "description": "Slack bot/user token"
    },
    {
        "type": "Stripe API Key",
        "severity": "critical",
        "pattern": r'sk_live_[a-zA-Z0-9]{24}',
        "description": "Stripe live API key"
    },
    {
        "type": "Stripe Publishable Key",
        "severity": "medium",
        "pattern": r'pk_live_[a-zA-Z0-9]{24}',
        "description": "Stripe publishable key"
    },
    # Private keys
    {
        "type": "Private Key (PEM)",
        "severity": "critical",
        "pattern": r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
        "description": "PEM private key block"
    },
    {
        "type": "SSH Private Key",
        "severity": "critical",
        "pattern": r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
        "description": "OpenSSH private key block"
    },
    {
        "type": "EC Private Key",
        "severity": "critical",
        "pattern": r'-----BEGIN\s+EC\s+PRIVATE\s+KEY-----',
        "description": "Elliptic curve private key block"
    },
    # Database keys
    {
        "type": "Database URL",
        "severity": "critical",
        "pattern": r'(?:postgres|mysql|sqlite|mongodb)://(?:[a-zA-Z0-9_\-]+):([^@\s]{8,})@',
        "description": "Database connection string with password"
    },
    # Crypto secrets
    {
        "type": "Ethereum Private Key",
        "severity": "critical",
        "pattern": r'0x[a-fA-F0-9]{64}',
        "description": "Ethereum/Wallet private key (64 hex chars)"
    },
    {
        "type": "Mnemonic/Seed Phrase",
        "severity": "critical",
        "pattern": r'\b(?:[a-z]{4,}\s+){11}[a-z]{4,}\b',
        "description": "Potential BIP39 mnemonic phrase (12+ words)"
    },
    # JWT tokens
    {
        "type": "JWT Token",
        "severity": "high",
        "pattern": r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
        "description": "JSON Web Token"
    },
    # OAuth tokens
    {
        "type": "OAuth Bearer Token",
        "severity": "high",
        "pattern": r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}',
        "description": "OAuth bearer token"
    },
    # Cloud tokens
    {
        "type": "GCP Service Account",
        "severity": "critical",
        "pattern": r'"type":\s*"service_account"[^}]*"private_key":\s*"-----BEGIN'  # Simplified - normally would parse JSON
    }
]

EXCLUDED_PATTERNS = [
    # False positives
    r'example\.com',
    r'example\.org',
    r'test[_-]?api[_-]?key',
    r'your[_-]?key',
    r'replace[_-]?with',
    r'<Your>',
    r'YOUR_API_KEY',
    r'xxx',
    r'redacted',
]

EXCLUDED_DIRS = {
    '.git', '.idea', '.vscode', 'node_modules', 'venv', 'env',
    '__pycache__', '.pytest_cache', 'dist', 'build',
}

def should_scan_file(file_path: Path) -> bool:
    """Check if file should be scanned"""
    extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
        '.env', '.config', '.ini', '.conf', '.toml', '.xml',
        '.java', '.go', '.rs', '.rb', '.php', '.sh', '.sql',
        '.md', '.txt', '.html', '.css'
    }
    return file_path.suffix in extensions and file_path.is_file()

def should_scan_dir(dir_path: Path) -> bool:
    """Check if directory should be scanned"""
    return dir_path.name not in EXCLUDED_DIRS and dir_path.is_dir()

def scan_file(file_path: Path) -> List[SecretMatch]:
    """Scan a single file for secrets"""
    matches = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Check against false positive patterns first
            if any(re.search(exc, line, re.IGNORECASE) for exc in EXCLUDED_PATTERNS):
                continue

            for pattern_info in SECRET_PATTERNS:
                pattern = pattern_info['pattern']
                matches_iter = re.finditer(pattern, line, re.IGNORECASE)

                for match in matches_iter:
                    value = match.group(1) if match.groups() else match.group(0)
                    preview = f"{value[:16]}{'...' if len(value) > 16 else ''}"

                    # Get context (2 lines before and after)
                    start_ctx = max(0, line_num - 3)
                    end_ctx = min(len(lines), line_num + 2)
                    context = '\n'.join(lines[start_ctx:end_ctx]).strip()

                    matches.append(SecretMatch(
                        secret_type=pattern_info['type'],
                        severity=pattern_info['severity'].upper(),
                        file=str(file_path),
                        line=line_num,
                        value_preview=preview,
                        context=context[:200] + ('...' if len(context) > 200 else '')
                    ))

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return matches

def scan_directory(directory: Path, recursive: bool = True) -> Dict[str, List[SecretMatch]]:
    """Scan a directory for secrets"""
    results = {}

    if recursive:
        dirs = [d for d in directory.rglob('*') if should_scan_dir(d)]
        files = [f for d in dirs for f in d.iterdir() if should_scan_file(f)]
        files = list(set(files))  # Remove duplicates
    else:
        files = [f for f in directory.glob('*') if should_scan_file(f)]

    print(f"Scanning {len(files)} files for secrets...")

    for file_path in files:
        matches = scan_file(file_path)
        if matches:
            results[str(file_path)] = matches

    return results

def format_results(results: Dict[str, List[SecretMatch]], output_format: str = 'text'):
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
        md = "# Secret Scan Results\n\n"
        md += f"**Total secrets found:** {len(all_matches)}\n\n"
        md += "⚠️ **WARNING:** Remove these secrets immediately and rotate credentials!\n\n"

        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            severity_matches = [m for m in all_matches if m.severity == severity]
            if not severity_matches:
                continue

            md += f"## {severity} ({len(severity_matches)})\n\n"

            for match in severity_matches[:20]:  # Limit output
                md += f"### {match.secret_type}\n"
                md += f"- **File:** `{match.file}:{match.line}`\n"
                md += f"- **Preview:** `{match.value_preview}`\n"
                md += f"- **Context:**\n```\n{match.context}\n```\n\n"

            if len(severity_matches) > 20:
                md += f"*...and {len(severity_matches) - 20} more {severity.lower()} findings*\n\n"
            md += "---\n\n"

        return md

    # Default text format
    text = "SECRET SCAN RESULTS\n" + "="*50 + "\n"
    text += f"Total secrets found: {len(all_matches)}\n"
    text += "\n⚠️  WARNING: Remove these secrets immediately and rotate credentials!\n\n"

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        severity_matches = [m for m in all_matches if m.severity == severity]
        if not severity_matches:
            continue

        text += f"\n{severity} ({len(severity_matches)} secrets)\n"
        text += "-" * len(severity) + "\n\n"

        for match in severity_matches[:20]:
            text += f"  {match.secret_type}\n"
            text += f"  File: {match.file}:{match.line}\n"
            text += f"  Preview: {match.value_preview}\n"
            text += f"  Context: {match.context}\n\n"

        if len(severity_matches) > 20:
            text += f"  ...and {len(severity_matches) - 20} more\n\n"

    return text

def main():
    parser = argparse.ArgumentParser(description='Secret Scanner - Detect hardcoded credentials')
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--output', default='text', choices=['text', 'json', 'markdown'], help='Output format')
    parser.add_argument('--no-recursive', action='store_true', help='Do not scan recursively')

    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {args.path}")
        return 1

    # Scan
    if path.is_file() and should_scan_file(path):
        matches = scan_file(path)
        results = {str(path): matches} if matches else {}
    elif path.is_dir():
        results = scan_directory(path, recursive=not args.no_recursive)
    else:
        print(f"Error: Cannot scan {args.path}")
        return 1

    # Format and output
    output = format_results(results, args.output)
    print(output)

    return 0 if not results else 1

if __name__ == '__main__':
    exit(main())

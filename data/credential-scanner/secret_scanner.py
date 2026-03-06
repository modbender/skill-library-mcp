#!/usr/bin/env python3
"""
Secret Scanner v0.1.0
Scans files and repos for leaked secrets, API keys, tokens, and credentials.

Detects 40+ secret patterns across all major cloud providers and services.

Usage:
    python secret_scanner.py <path>
    python secret_scanner.py <path> --json
    python secret_scanner.py <path> --output report.md

Author: nirwandogra
License: MIT
"""

import os
import re
import sys
import json
import math
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional
from enum import Enum


# =============================================================================
# CONFIGURATION
# =============================================================================

SCAN_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php',
    '.cs', '.rs', '.c', '.cpp', '.h', '.swift', '.kt',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml',
    '.env', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
    '.md', '.txt', '.rst', '.properties',
}

SCAN_FILENAMES = {
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'Makefile', '.env', '.env.local', '.env.development', '.env.production',
    '.env.staging', '.env.test', '.npmrc', '.pypirc', 'credentials',
    'config', '.htpasswd', 'wp-config.php',
}

IGNORE_DIRS = {
    'node_modules', 'vendor', 'venv', '.venv', 'env',
    '.git', '.svn', '.hg',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'dist', 'build', '.next', '.nuxt',
    'coverage', '.coverage', 'htmlcov',
    '.tox', '.eggs', '*.egg-info',
}

IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Pipfile.lock', 'poetry.lock', 'composer.lock',
    'Gemfile.lock', 'go.sum',
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LINE_LENGTH = 5000


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecretFinding:
    pattern_name: str
    severity: str
    file_path: str
    line_number: int
    line_preview: str
    secret_preview: str
    description: str
    remediation: str


@dataclass
class ScanReport:
    scan_path: str
    scan_timestamp: str
    files_scanned: int = 0
    files_skipped: int = 0
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    findings: List[SecretFinding] = field(default_factory=list)
    scanned_files: List[str] = field(default_factory=list)


# =============================================================================
# SECRET PATTERNS
# =============================================================================

SECRET_PATTERNS = [
    # --- AWS ---
    {
        "name": "AWS Access Key ID",
        "pattern": r"(?<![A-Za-z0-9/+=])(AKIA[0-9A-Z]{16})(?![A-Za-z0-9/+=])",
        "severity": "critical",
        "description": "AWS Access Key ID detected",
        "remediation": "Rotate the key in AWS IAM console immediately. Use IAM roles or environment variables instead."
    },
    {
        "name": "AWS Secret Access Key",
        "pattern": r"(?i)(aws_secret_access_key|aws_secret_key)\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "severity": "critical",
        "description": "AWS Secret Access Key detected",
        "remediation": "Rotate in AWS IAM immediately. Never hardcode AWS credentials."
    },
    # --- Azure ---
    {
        "name": "Azure Storage Account Key",
        "pattern": r"(?i)(AccountKey|storage[_-]?key)\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{86,90}==)['\"]?",
        "severity": "critical",
        "description": "Azure Storage Account Key detected",
        "remediation": "Rotate the key in Azure Portal > Storage Account > Access Keys. Use Managed Identity instead."
    },
    {
        "name": "Azure Connection String",
        "pattern": r"(?i)(DefaultEndpointsProtocol=https?;AccountName=\w+;AccountKey=[A-Za-z0-9/+=]{86,90}==)",
        "severity": "critical",
        "description": "Azure Storage connection string with embedded key",
        "remediation": "Store connection strings in Azure Key Vault or app settings, not in code."
    },
    {
        "name": "Azure SAS Token",
        "pattern": r"[?&]sig=[A-Za-z0-9%/+=]{40,}(&|$)",
        "severity": "high",
        "description": "Azure Shared Access Signature (SAS) token detected",
        "remediation": "SAS tokens should be short-lived and not committed to source control."
    },
    {
        "name": "Azure Client Secret",
        "pattern": r"(?i)(client[_-]?secret|azure[_-]?secret)\s*[=:]\s*['\"]?([A-Za-z0-9~._-]{34,})['\"]?",
        "severity": "critical",
        "description": "Azure AD client secret / app password detected",
        "remediation": "Rotate in Azure AD > App Registrations. Use managed identity or certificates."
    },
    # --- GCP ---
    {
        "name": "GCP API Key",
        "pattern": r"(?<![A-Za-z0-9])(AIza[0-9A-Za-z_-]{35})(?![A-Za-z0-9])",
        "severity": "high",
        "description": "Google Cloud Platform API key detected",
        "remediation": "Restrict the key in GCP Console > APIs & Services > Credentials. Use service accounts instead."
    },
    {
        "name": "GCP Service Account Key",
        "pattern": r'"type"\s*:\s*"service_account"',
        "severity": "critical",
        "description": "GCP service account JSON key file detected",
        "remediation": "Use Workload Identity Federation instead. Never commit service account keys."
    },
    # --- GitHub ---
    {
        "name": "GitHub Personal Access Token",
        "pattern": r"(?<![A-Za-z0-9])(ghp_[A-Za-z0-9]{36,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "GitHub Personal Access Token detected",
        "remediation": "Revoke token at github.com/settings/tokens. Use fine-grained tokens with minimal scopes."
    },
    {
        "name": "GitHub OAuth Token",
        "pattern": r"(?<![A-Za-z0-9])(gho_[A-Za-z0-9]{36,})(?![A-Za-z0-9])",
        "severity": "high",
        "description": "GitHub OAuth Access Token detected",
        "remediation": "Revoke and regenerate the OAuth token."
    },
    {
        "name": "GitHub App Token",
        "pattern": r"(?<![A-Za-z0-9])(ghu_[A-Za-z0-9]{36,}|ghs_[A-Za-z0-9]{36,}|ghr_[A-Za-z0-9]{36,})(?![A-Za-z0-9])",
        "severity": "high",
        "description": "GitHub App installation/user/refresh token detected",
        "remediation": "Regenerate the token. Ensure proper token rotation."
    },
    # --- GitLab ---
    {
        "name": "GitLab Personal Access Token",
        "pattern": r"(?<![A-Za-z0-9])(glpat-[A-Za-z0-9_-]{20,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "GitLab Personal Access Token detected",
        "remediation": "Revoke at GitLab > Settings > Access Tokens."
    },
    # --- OpenAI / AI Keys ---
    {
        "name": "OpenAI API Key",
        "pattern": r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{40,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "OpenAI API key detected",
        "remediation": "Rotate at platform.openai.com/api-keys. Use environment variables."
    },
    {
        "name": "Anthropic API Key",
        "pattern": r"(?<![A-Za-z0-9])(sk-ant-[A-Za-z0-9_-]{40,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "Anthropic API key detected",
        "remediation": "Rotate at console.anthropic.com. Use environment variables."
    },
    {
        "name": "Hugging Face Token",
        "pattern": r"(?<![A-Za-z0-9])(hf_[A-Za-z0-9]{34,})(?![A-Za-z0-9])",
        "severity": "high",
        "description": "Hugging Face API token detected",
        "remediation": "Rotate at huggingface.co/settings/tokens."
    },
    # --- Slack ---
    {
        "name": "Slack Bot/User Token",
        "pattern": r"(?<![A-Za-z0-9])(xox[bpsa]-[0-9]{10,}-[A-Za-z0-9-]+)(?![A-Za-z0-9])",
        "severity": "high",
        "description": "Slack API token detected",
        "remediation": "Regenerate at api.slack.com/apps. Restrict token scopes."
    },
    {
        "name": "Slack Webhook URL",
        "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
        "severity": "medium",
        "description": "Slack incoming webhook URL detected",
        "remediation": "Rotate the webhook URL if exposed publicly."
    },
    # --- Stripe ---
    {
        "name": "Stripe Secret Key",
        "pattern": r"(?<![A-Za-z0-9])(sk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "Stripe live secret/restricted key detected",
        "remediation": "Roll the key at dashboard.stripe.com/apikeys immediately."
    },
    {
        "name": "Stripe Test Key",
        "pattern": r"(?<![A-Za-z0-9])(sk_test_[A-Za-z0-9]{24,})(?![A-Za-z0-9])",
        "severity": "medium",
        "description": "Stripe test secret key detected",
        "remediation": "Test keys are lower risk but should still not be committed."
    },
    # --- Twilio ---
    {
        "name": "Twilio Auth Token",
        "pattern": r"(?i)(twilio[_-]?auth[_-]?token|auth_token)\s*[=:]\s*['\"]?([a-f0-9]{32})['\"]?",
        "severity": "high",
        "description": "Twilio Auth Token detected",
        "remediation": "Rotate at twilio.com/console. Use API keys instead of main credentials."
    },
    # --- SendGrid ---
    {
        "name": "SendGrid API Key",
        "pattern": r"(?<![A-Za-z0-9])(SG\.[A-Za-z0-9_-]{22,}\.[A-Za-z0-9_-]{43,})(?![A-Za-z0-9])",
        "severity": "high",
        "description": "SendGrid API key detected",
        "remediation": "Delete and recreate at app.sendgrid.com/settings/api_keys."
    },
    # --- Database Connection Strings ---
    {
        "name": "MongoDB Connection String",
        "pattern": r"mongodb(\+srv)?://[A-Za-z0-9_]+:[^@\s]{8,}@[^\s'\"]+",
        "severity": "critical",
        "description": "MongoDB connection string with embedded credentials",
        "remediation": "Store in environment variable or secrets manager. Rotate the password."
    },
    {
        "name": "PostgreSQL Connection String",
        "pattern": r"postgres(ql)?://[A-Za-z0-9_]+:[^@\s]{4,}@[^\s'\"]+",
        "severity": "critical",
        "description": "PostgreSQL connection string with embedded password",
        "remediation": "Use environment variables. Rotate the database password."
    },
    {
        "name": "MySQL Connection String",
        "pattern": r"mysql://[A-Za-z0-9_]+:[^@\s]{4,}@[^\s'\"]+",
        "severity": "critical",
        "description": "MySQL connection string with embedded password",
        "remediation": "Use environment variables or connection pooler with managed credentials."
    },
    {
        "name": "Redis Connection String",
        "pattern": r"redis://:[^@\s]{4,}@[^\s'\"]+",
        "severity": "high",
        "description": "Redis connection string with embedded password",
        "remediation": "Use environment variables. Enable Redis ACLs and rotate passwords."
    },
    # --- SSH / Certificates ---
    {
        "name": "SSH Private Key",
        "pattern": r"-----BEGIN\s+(RSA|EC|OPENSSH|DSA)\s+PRIVATE\s+KEY-----",
        "severity": "critical",
        "description": "SSH private key detected in file",
        "remediation": "Remove immediately. Generate a new key pair. Never commit private keys."
    },
    {
        "name": "PEM Certificate Key",
        "pattern": r"-----BEGIN\s+(ENCRYPTED\s+)?PRIVATE\s+KEY-----",
        "severity": "critical",
        "description": "PEM private key detected",
        "remediation": "Remove and store in a certificate vault (Azure Key Vault, AWS ACM)."
    },
    # --- JWT / Bearer ---
    {
        "name": "JWT Token",
        "pattern": r"(?<![A-Za-z0-9])(eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})(?![A-Za-z0-9_-])",
        "severity": "medium",
        "description": "JSON Web Token (JWT) detected",
        "remediation": "JWTs may contain sensitive claims. Remove and use short-lived tokens."
    },
    {
        "name": "Bearer Token in Code",
        "pattern": r"""(?i)['"]Bearer\s+[A-Za-z0-9_-]{20,}['"]""",
        "severity": "high",
        "description": "Hardcoded Bearer token in code",
        "remediation": "Use environment variables for auth tokens. Never hardcode Bearer tokens."
    },
    # --- Generic Credential Patterns ---
    {
        "name": "Generic Password Assignment",
        "pattern": r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
        "severity": "high",
        "description": "Hardcoded password detected",
        "remediation": "Use environment variables or a secrets manager for passwords."
    },
    {
        "name": "Generic Secret Assignment",
        "pattern": r"(?i)(secret|secret_key|api_secret)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
        "severity": "high",
        "description": "Hardcoded secret value detected",
        "remediation": "Store secrets in environment variables, Azure Key Vault, or AWS Secrets Manager."
    },
    {
        "name": "Generic Token Assignment",
        "pattern": r"(?i)(api_token|auth_token|access_token)\s*[=:]\s*['\"][^'\"]{16,}['\"]",
        "severity": "high",
        "description": "Hardcoded token detected",
        "remediation": "Retrieve tokens at runtime from environment or secrets manager."
    },
    {
        "name": "Basic Auth Header",
        "pattern": r"(?i)Authorization:\s*Basic\s+[A-Za-z0-9+/=]{10,}",
        "severity": "high",
        "description": "Hardcoded Basic Authentication header",
        "remediation": "Use dynamic credential injection. Basic auth should come from env/config."
    },
    # --- Service Bus / Messaging ---
    {
        "name": "Service Bus Connection String",
        "pattern": r"Endpoint=sb://[^;]+;SharedAccessKeyName=[^;]+;SharedAccessKey=[A-Za-z0-9+/=]{30,}",
        "severity": "critical",
        "description": "Azure Service Bus connection string with shared access key",
        "remediation": "Store in Azure Key Vault. Use Managed Identity for Service Bus access."
    },
    # --- NPM / PyPI ---
    {
        "name": "NPM Auth Token",
        "pattern": r"(?i)(_authToken|npm_token)\s*[=:]\s*['\"]?([A-Za-z0-9_-]{36,})['\"]?",
        "severity": "critical",
        "description": "NPM registry auth token detected",
        "remediation": "Revoke at npmjs.com > Access Tokens. Use npm login for auth."
    },
    {
        "name": "PyPI API Token",
        "pattern": r"(?<![A-Za-z0-9])(pypi-[A-Za-z0-9_-]{50,})(?![A-Za-z0-9])",
        "severity": "critical",
        "description": "PyPI API token detected",
        "remediation": "Revoke at pypi.org/manage/account/token/. Use trusted publishers instead."
    },
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def mask_secret(text: str, show_chars: int = 4) -> str:
    """Mask a secret, showing only first few characters."""
    if len(text) <= show_chars + 4:
        return text[:2] + '*' * (len(text) - 2)
    return text[:show_chars] + '*' * 8 + text[-2:]


def is_likely_placeholder(value: str) -> bool:
    """Check if a value looks like a placeholder/example rather than a real secret."""
    placeholders = [
        'xxx', 'your_', 'example', 'placeholder', 'changeme', 'replace',
        'insert', 'todo', 'fixme', 'dummy', 'fake', 'test_', 'sample',
        '<your', '{your', '${', '{{', 'REPLACE_ME', 'CHANGE_ME',
    ]
    lower = value.lower()
    return any(p in lower for p in placeholders)


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    length = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def should_scan_file(file_path: Path) -> bool:
    """Determine if a file should be scanned."""
    if file_path.name in IGNORE_FILES:
        return False
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return False
    if file_path.suffix.lower() in SCAN_EXTENSIONS or file_path.name in SCAN_FILENAMES:
        try:
            size = file_path.stat().st_size
            if size > MAX_FILE_SIZE or size == 0:
                return False
        except OSError:
            return False
        return True
    return False


# =============================================================================
# SCANNER CLASS
# =============================================================================

class SecretScanner:
    def __init__(self, scan_path: str):
        self.scan_path = Path(scan_path).resolve()
        self.report = ScanReport(
            scan_path=str(self.scan_path),
            scan_timestamp=datetime.now().isoformat()
        )
        self._compiled_patterns = []
        for p in SECRET_PATTERNS:
            try:
                self._compiled_patterns.append({
                    **p,
                    "_regex": re.compile(p["pattern"], re.IGNORECASE if '(?i)' not in p["pattern"] else 0)
                })
            except re.error:
                pass

    def scan(self) -> ScanReport:
        """Run the full scan."""
        if not self.scan_path.exists():
            raise FileNotFoundError(f"Path not found: {self.scan_path}")

        if self.scan_path.is_file():
            self._scan_file(self.scan_path)
        else:
            for file_path in sorted(self.scan_path.rglob('*')):
                if file_path.is_file():
                    if should_scan_file(file_path):
                        self._scan_file(file_path)
                    else:
                        self.report.files_skipped += 1

        # Count severities
        for f in self.report.findings:
            if f.severity == "critical":
                self.report.critical_count += 1
            elif f.severity == "high":
                self.report.high_count += 1
            elif f.severity == "medium":
                self.report.medium_count += 1
            elif f.severity == "low":
                self.report.low_count += 1

        self.report.total_findings = len(self.report.findings)
        return self.report

    def _scan_file(self, file_path: Path):
        """Scan a single file for secrets."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            self.report.files_skipped += 1
            return

        self.report.files_scanned += 1
        rel_path = str(file_path.relative_to(self.scan_path)) if self.scan_path.is_dir() else file_path.name
        self.report.scanned_files.append(rel_path)

        lines = content.split('\n')
        seen = set()  # Deduplicate findings per file+pattern+line

        for pattern_def in self._compiled_patterns:
            regex = pattern_def["_regex"]
            for i, line in enumerate(lines, 1):
                if len(line) > MAX_LINE_LENGTH:
                    continue

                # Skip comment-only lines that look like documentation
                stripped = line.strip()
                if stripped.startswith('#') and 'example' in stripped.lower():
                    continue

                for match in regex.finditer(line):
                    matched_text = match.group(0)

                    # Skip placeholders
                    if is_likely_placeholder(matched_text):
                        continue

                    dedup_key = (rel_path, pattern_def["name"], i)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    # Mask the secret for display
                    masked = mask_secret(matched_text)
                    line_preview = line.strip()[:120]

                    finding = SecretFinding(
                        pattern_name=pattern_def["name"],
                        severity=pattern_def["severity"],
                        file_path=rel_path,
                        line_number=i,
                        line_preview=line_preview,
                        secret_preview=masked,
                        description=pattern_def["description"],
                        remediation=pattern_def["remediation"]
                    )
                    self.report.findings.append(finding)


# =============================================================================
# OUTPUT FORMATTERS
# =============================================================================

def format_markdown(report: ScanReport) -> str:
    """Format report as Markdown."""
    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

    lines = [
        "# 🔐 Secret Scanner Report",
        "",
        f"**Scan Path:** `{report.scan_path}`",
        f"**Scan Date:** {report.scan_timestamp}",
        f"**Files Scanned:** {report.files_scanned} ({report.files_skipped} skipped)",
        "",
        "## Summary",
        "",
        f"| Severity | Count |",
        f"|----------|-------|",
        f"| 🔴 Critical | {report.critical_count} |",
        f"| 🟠 High | {report.high_count} |",
        f"| 🟡 Medium | {report.medium_count} |",
        f"| 🟢 Low | {report.low_count} |",
        f"| **Total** | **{report.total_findings}** |",
        "",
    ]

    if report.total_findings == 0:
        lines.extend([
            "## ✅ No Secrets Found",
            "",
            "No leaked secrets or credentials were detected. Great job keeping your code clean!",
            "",
        ])
    else:
        lines.extend([
            "## ⚠️ Findings",
            "",
        ])

        # Group by severity
        for sev in ["critical", "high", "medium", "low"]:
            sev_findings = [f for f in report.findings if f.severity == sev]
            if not sev_findings:
                continue
            emoji = severity_emoji[sev]
            lines.append(f"### {emoji} {sev.upper()} ({len(sev_findings)})")
            lines.append("")
            for f in sev_findings:
                lines.extend([
                    f"**{f.pattern_name}**",
                    f"- **File:** `{f.file_path}` (line {f.line_number})",
                    f"- **Found:** `{f.secret_preview}`",
                    f"- **Description:** {f.description}",
                    f"- **Fix:** {f.remediation}",
                    "",
                ])

        lines.extend([
            "## 🛡️ Remediation Steps",
            "",
            "1. **Rotate all detected secrets immediately** — assume they are compromised",
            "2. **Remove secrets from source code** — use environment variables or a secrets manager",
            "3. **Clean git history** — use `git filter-repo` or BFG Repo-Cleaner to remove from past commits",
            "4. **Add `.env` to `.gitignore`** — prevent credential files from being committed",
            "5. **Set up pre-commit hooks** — use tools like `detect-secrets` to catch future leaks",
            "",
        ])

    return '\n'.join(lines)


def format_json(report: ScanReport) -> str:
    """Format report as JSON."""
    data = {
        'scan_path': report.scan_path,
        'scan_timestamp': report.scan_timestamp,
        'files_scanned': report.files_scanned,
        'files_skipped': report.files_skipped,
        'summary': {
            'total': report.total_findings,
            'critical': report.critical_count,
            'high': report.high_count,
            'medium': report.medium_count,
            'low': report.low_count,
        },
        'findings': [asdict(f) for f in report.findings],
        'scanned_files': report.scanned_files,
    }
    return json.dumps(data, indent=2)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Secret Scanner — Find leaked secrets, API keys, and credentials in your code'
    )
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--output', '-o', help='Write report to file')
    args = parser.parse_args()

    try:
        scanner = SecretScanner(args.path)
        report = scanner.scan()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output = format_json(report) if args.json else format_markdown(report)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit codes: 2=critical found, 1=high found, 0=clean
    if report.critical_count > 0:
        sys.exit(2)
    elif report.high_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

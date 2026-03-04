#!/usr/bin/env python3
"""
Security Audit Scanner
Scans files/directories for hardcoded secrets, absolute paths, and sensitive patterns.

Usage:
  python3 audit.py <path> [--json] [--strict]
  python3 audit.py --staged           # Scan git staged files only
  python3 audit.py --last-commit      # Scan files changed in last commit

Exit codes: 0=clean, 1=findings, 2=error
"""

import sys, os, re, json, subprocess, argparse
from pathlib import Path

# ── Pattern definitions ────────────────────────────────────────────────────

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.next'}
SKIP_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.zip', '.tar', '.gz',
                   '.lock', '.map', '.min.js', '.min.css', '.pdf', '.ico', '.ttf', '.woff',
                   '.woff2', '.eot', '.svg'}

PATTERNS = [
    # Real secrets — HIGH severity
    {
        "id": "hardcoded-api-key",
        "severity": "HIGH",
        "description": "Hardcoded API key or token",
        "regex": r'(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token)\s*[=:]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
        "group": 2,
        "min_entropy": 3.5,
    },
    {
        "id": "hardcoded-secret",
        "severity": "HIGH",
        "description": "Hardcoded secret or password",
        "regex": r'(?i)(secret|password|passwd|client_secret|client_key)\s*[=:]\s*["\']([^"\']{8,})["\']',
        "group": 2,
        "exclude_vars": True,  # Skip if value looks like a variable/env ref
    },
    {
        "id": "aws-key",
        "severity": "HIGH",
        "description": "AWS Access Key ID",
        "regex": r'AKIA[0-9A-Z]{16}',
    },
    {
        "id": "aws-secret",
        "severity": "HIGH",
        "description": "AWS Secret Access Key",
        "regex": r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']([A-Za-z0-9+/]{40})["\']',
    },
    {
        "id": "jwt-token",
        "severity": "HIGH",
        "description": "Hardcoded JWT token",
        "regex": r'eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}',
    },
    {
        "id": "woocommerce-key",
        "severity": "HIGH",
        "description": "WooCommerce consumer key/secret",
        "regex": r'(ck|cs)_[a-f0-9]{40}',
    },
    {
        "id": "private-key-block",
        "severity": "HIGH",
        "description": "Private key block",
        "regex": r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    },
    {
        "id": "generic-bearer",
        "severity": "HIGH",
        "description": "Bearer token value",
        "regex": r'Bearer\s+[A-Za-z0-9_\-\.]{40,}',
    },

    # Medium — suspicious patterns
    {
        "id": "absolute-home-path",
        "severity": "MEDIUM",
        "description": "Absolute home directory path hardcoded",
        "regex": r'/home/[a-z_][a-z0-9_\-]*/(?!\.openclaw/workspace/skills)',
        "exclude_comments": False,
    },
    {
        "id": "absolute-root-path",
        "severity": "MEDIUM",
        "description": "Absolute /root/ path hardcoded",
        "regex": r'/root/[^\s"\']+',
    },
    {
        "id": "ip-address",
        "severity": "LOW",
        "description": "Hardcoded IP address (non-localhost)",
        "regex": r'\b(?!127\.0\.0\.1|0\.0\.0\.0|localhost)(\d{1,3}\.){3}\d{1,3}\b',
    },
    {
        "id": "refresh-token",
        "severity": "MEDIUM",
        "description": "Possible refresh/access token value",
        "regex": r'(Atzr|Atza|ATNR)\|[A-Za-z0-9+/\|]{40,}',
    },
    {
        "id": "base64-long",
        "severity": "LOW",
        "description": "Long base64 string (possible encoded secret)",
        "regex": r'["\'][A-Za-z0-9+/]{60,}={0,2}["\']',
    },
    {
        "id": "node-modules-in-skill",
        "severity": "MEDIUM",
        "description": "node_modules committed — should be gitignored",
        "path_pattern": r'node_modules/',
        "file_level": True,
    },
    {
        "id": "env-file-committed",
        "severity": "HIGH",
        "description": ".env file committed",
        "path_pattern": r'(^|/)\.env(\.|$)',
        "file_level": True,
    },
]

# Safe placeholder values — don't flag these
SAFE_VALUES = {
    'your_api_key_here', 'your-api-key', 'YOUR_API_KEY', 'REPLACE_ME',
    'process.env', 'os.environ', 'config.', 'cfg.', '${', 'process.env.',
    'placeholder', 'example', 'changeme', 'todo', 'fixme',
}


def shannon_entropy(s):
    import math
    if not s:
        return 0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    return -sum((f/len(s)) * math.log2(f/len(s)) for f in freq.values())


def is_safe_value(val):
    val_lower = val.lower()
    for safe in SAFE_VALUES:
        if safe.lower() in val_lower:
            return True
    if re.match(r'^[A-Z_]+$', val):  # ALL_CAPS env var reference
        return True
    if val.startswith('$') or val.startswith('{{') or val.startswith('%('):
        return True
    return False


def scan_file_content(filepath, content):
    findings = []
    lines = content.split('\n')

    for pattern in PATTERNS:
        if pattern.get('file_level'):
            continue

        regex = pattern.get('regex')
        if not regex:
            continue

        compiled = re.compile(regex)
        for lineno, line in enumerate(lines, 1):
            # Skip obvious comments for some patterns
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                if pattern.get('exclude_comments', True) and pattern['severity'] in ('LOW',):
                    continue

            for match in compiled.finditer(line):
                value = match.group(pattern.get('group', 0))

                # Check entropy for API key patterns
                if pattern.get('min_entropy') and shannon_entropy(value) < pattern['min_entropy']:
                    continue

                # Skip safe placeholder values
                if pattern.get('exclude_vars') and is_safe_value(value):
                    continue

                findings.append({
                    "id": pattern['id'],
                    "severity": pattern['severity'],
                    "description": pattern['description'],
                    "file": str(filepath),
                    "line": lineno,
                    "match": line.strip()[:120],
                    "value_preview": value[:40] + ('...' if len(value) > 40 else ''),
                })

    return findings


def scan_path_patterns(filepath):
    findings = []
    fstr = str(filepath)
    for pattern in PATTERNS:
        if not pattern.get('file_level') or not pattern.get('path_pattern'):
            continue
        if re.search(pattern['path_pattern'], fstr):
            findings.append({
                "id": pattern['id'],
                "severity": pattern['severity'],
                "description": pattern['description'],
                "file": fstr,
                "line": 0,
                "match": f"Path: {fstr}",
                "value_preview": "",
            })
    return findings


def should_skip(path):
    p = Path(path)
    for part in p.parts:
        if part in SKIP_DIRS:
            return True
    ext = ''.join(p.suffixes)
    return ext in SKIP_EXTENSIONS


def scan_directory(target):
    all_findings = []
    target_path = Path(target)

    if target_path.is_file():
        files = [target_path]
    else:
        files = [f for f in target_path.rglob('*') if f.is_file()]

    for f in files:
        if should_skip(f):
            continue
        all_findings.extend(scan_path_patterns(f))
        try:
            content = f.read_text(errors='ignore')
            all_findings.extend(scan_file_content(f, content))
        except Exception:
            pass

    return all_findings


def scan_git_files(mode='staged'):
    if mode == 'staged':
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    else:
        result = subprocess.run(['git', 'diff', 'HEAD~1', '--name-only'], capture_output=True, text=True)

    files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    all_findings = []
    for f in files:
        if os.path.exists(f):
            all_findings.extend(scan_directory(f))
    return all_findings


def group_by_severity(findings):
    grouped = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
    for f in findings:
        grouped.setdefault(f['severity'], []).append(f)
    return grouped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default='.', help='Path to scan')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--staged', action='store_true', help='Scan git staged files')
    parser.add_argument('--last-commit', action='store_true', help='Scan last commit files')
    parser.add_argument('--strict', action='store_true', help='Exit 1 on any finding including LOW')
    args = parser.parse_args()

    if args.staged:
        findings = scan_git_files('staged')
    elif args.last_commit:
        findings = scan_git_files('last-commit')
    else:
        findings = scan_directory(args.path)

    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        key = (f['file'], f['line'], f['id'])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    grouped = group_by_severity(unique)

    if args.json:
        print(json.dumps({'findings': unique, 'summary': {k: len(v) for k, v in grouped.items()}}, indent=2))
    else:
        total = len(unique)
        if total == 0:
            print('✅ CLEAN — No security findings.')
            sys.exit(0)

        print(f'\n🔍 Security Audit — {total} finding(s)\n')
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            items = grouped.get(severity, [])
            if not items:
                continue
            icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🔵'}[severity]
            print(f'{icon} {severity} ({len(items)})')
            for item in items:
                loc = f"{item['file']}:{item['line']}" if item['line'] else item['file']
                print(f"  [{item['id']}] {item['description']}")
                print(f"   → {loc}")
                if item['value_preview']:
                    print(f"   → Value: {item['value_preview']}")
                print(f"   → {item['match'][:100]}")
                print()

        high = len(grouped.get('HIGH', []))
        medium = len(grouped.get('MEDIUM', []))
        print(f"Summary: {high} HIGH, {medium} MEDIUM, {len(grouped.get('LOW', []))} LOW")

    has_high = bool(grouped.get('HIGH'))
    has_medium = bool(grouped.get('MEDIUM'))
    if has_high or (args.strict and (has_medium or grouped.get('LOW'))):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()

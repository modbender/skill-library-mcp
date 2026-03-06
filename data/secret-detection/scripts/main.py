#!/usr/bin/env python3
"""
Git secret detection hook.
Scans files for common secret patterns (API keys, passwords, tokens).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Common secret patterns (simplified examples)
SECRET_PATTERNS = [
    (r'(?i)aws_access_key_id\s*=\s*["\']?(AKIA[0-9A-Z]{16})', "AWS Access Key ID"),
    (r'(?i)aws_secret_access_key\s*=\s*["\']?([0-9a-zA-Z/+]{40})', "AWS Secret Access Key"),
    (r'(?i)password\s*=\s*["\']?([^\s"\']{8,})', "Password"),
    (r'(?i)secret\s*=\s*["\']?([^\s"\']{8,})', "Secret"),
    (r'(?i)token\s*=\s*["\']?([^\s"\']{8,})', "Token"),
    (r'(?i)api_key\s*=\s*["\']?([^\s"\']{8,})', "API Key"),
    (r'(?i)ghp_[0-9a-zA-Z]{36}', "GitHub Personal Access Token"),
    (r'(?i)github_pat_[0-9a-zA-Z]{40}', "GitHub Fine‑Grained Token"),
    (r'(?i)sk-[0-9a-zA-Z]{48}', "OpenAI API Key"),
    (r'(?i)Bearer\s+([0-9a-zA-Z._-]{20,})', "Bearer Token"),
]

def scan_file(filepath, patterns=SECRET_PATTERNS):
    """Scan a single file for secret patterns."""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (IOError, UnicodeDecodeError):
        # Skip binary or unreadable files
        return findings
    
    for i, line in enumerate(lines, start=1):
        for pattern, label in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                findings.append({
                    'file': str(filepath),
                    'line': i,
                    'content': line.strip(),
                    'secret': match,
                    'label': label,
                })
    return findings

def scan_files(filepaths, patterns=SECRET_PATTERNS):
    """Scan multiple files."""
    all_findings = []
    for fp in filepaths:
        findings = scan_file(fp, patterns)
        all_findings.extend(findings)
    return all_findings

def get_staged_files():
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return []
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        # Resolve relative paths
        return [f for f in files if os.path.exists(f)]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

def install_hook():
    """Install pre‑commit hook in current git repository."""
    hook_path = Path('.git/hooks/pre-commit')
    if not hook_path.parent.exists():
        return {'status': 'error', 'message': 'Not a git repository (no .git directory)'}
    
    script_path = Path(__file__).resolve()
    hook_content = f'''#!/bin/bash
# Git pre‑commit hook for secret detection
python3 "{script_path}" hook-run
'''
    
    try:
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        return {'status': 'success', 'hook_path': str(hook_path)}
    except IOError as e:
        return {'status': 'error', 'message': f'Failed to write hook: {e}'}

def run_scan(args):
    """Run scan based on arguments."""
    if args.staged:
        files = get_staged_files()
        if not files:
            return {'status': 'success', 'findings': [], 'message': 'No staged files'}
    elif args.file:
        files = args.file
    else:
        return {'status': 'error', 'message': 'No files specified'}
    
    findings = scan_files(files)
    return {
        'status': 'success',
        'findings': findings,
        'file_count': len(files),
        'secret_count': len(findings),
    }

def main():
    parser = argparse.ArgumentParser(description='Git secret detection')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # install
    install_parser = subparsers.add_parser('install', help='Install git pre‑commit hook')
    
    # scan
    scan_parser = subparsers.add_parser('scan', help='Scan files for secrets')
    scan_group = scan_parser.add_mutually_exclusive_group(required=True)
    scan_group.add_argument('--staged', action='store_true', help='Scan staged git files')
    scan_group.add_argument('--file', action='append', help='File to scan (can be repeated)')
    
    # hook-run (internal, called by hook)
    subparsers.add_parser('hook-run', help='Internal: run from git hook')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        result = install_hook()
        if result['status'] == 'success':
            print(f"✓ Pre‑commit hook installed at {result['hook_path']}")
        else:
            print(f"✗ {result['message']}")
        print(json.dumps(result, indent=2))
    
    elif args.command == 'scan':
        result = run_scan(args)
        if result['status'] == 'success':
            findings = result['findings']
            if findings:
                print(f"⚠️  Found {len(findings)} secret(s):")
                for f in findings:
                    print(f"  {f['file']}:{f['line']} [{f['label']}] {f['secret'][:20]}...")
                print("✗ Secrets detected")
            else:
                print(f"✓ No secrets found (scanned {result['file_count']} files)")
        else:
            print(f"✗ {result['message']}")
        print(json.dumps(result, indent=2))
        # Exit with appropriate code for hook usage
        if args.staged and findings:
            sys.exit(1)
    
    elif args.command == 'hook-run':
        # Called from git hook: scan staged files and exit with appropriate code
        result = run_scan(argparse.Namespace(staged=True, file=None))
        findings = result.get('findings', [])
        if findings:
            print("⚠️  Secret detection blocked commit:")
            for f in findings:
                print(f"  {f['file']}:{f['line']} [{f['label']}] {f['content'][:60]}...")
            sys.exit(1)
        else:
            sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
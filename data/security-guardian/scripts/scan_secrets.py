#!/usr/bin/env python3
import os
import re
import sys
import argparse

# Common patterns for secrets
PATTERNS = {
    "Generic API Key": r"(?i)(?:key|api|token|secret|auth|password|pwd)(?:[\s|'|\"]*[:|=][\s|'|\"]*)([a-zA-Z0-9_\-]{16,})",
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
    "Firebase Config": r"apiKey:\s*['\"][A-Za-z0-9_\-]{35,45}['\"]",
    "Private Key": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
}

DANGEROUS_PATHS = ["/", "/etc", "/var", "/usr", "/boot", "/dev", "/root"]

def scan_file(file_path):
    findings = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            for line_no, line in enumerate(f, 1):
                for name, pattern in PATTERNS.items():
                    if re.search(pattern, line):
                        findings.append({
                            "type": name,
                            "line": line_no,
                            "file": file_path
                        })
    except Exception:
        pass
    return findings

def main():
    parser = argparse.ArgumentParser(description="Security Guardian: Secret Scanner")
    parser.add_argument("path", help="Target directory or file to scan")
    parser.add_argument("--exclude", nargs='*', help="Exclude patterns", default=[".git", "node_modules", "venv", "__pycache__"])
    parser.add_argument("--force", action="store_true", help="Force scan even if path is considered dangerous")
    args = parser.parse_args()

    abs_path = os.path.abspath(args.path)
    
    if abs_path in DANGEROUS_PATHS and not args.force:
        print(f"CRITICAL: Scanning {abs_path} is blocked for safety. Use --force if you really mean it.")
        sys.exit(1)

    all_findings = []
    if os.path.isfile(args.path):
        all_findings.extend(scan_file(args.path))
    else:
        for root, dirs, files in os.walk(args.path):
            dirs[:] = [d for d in dirs if d not in args.exclude]
            for file in files:
                file_path = os.path.join(root, file)
                all_findings.extend(scan_file(file_path))

    if all_findings:
        print(f"FOUND {len(all_findings)} POTENTIAL SECRETS:")
        for f in all_findings:
            print(f"[{f['type']}] {f['file']}:{f['line']}")
        sys.exit(1)
    else:
        print("No secrets found. Clean as a whistle! ✨")
        sys.exit(0)

if __name__ == "__main__":
    main()

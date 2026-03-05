#!/usr/bin/env python3
"""Skill Differ — Compare two versions of an OpenClaw skill for security changes.

Detects new capabilities added between versions to assess update safety.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# === Capability Detection Patterns ===
# Each category maps to patterns that indicate a specific capability

CAPABILITY_PATTERNS = {
    "network_access": [
        (r'requests\.(get|post|put|delete|patch|head)', "HTTP requests via requests library"),
        (r'urllib\.request\.(urlopen|Request)', "HTTP via urllib"),
        (r'(curl|wget)\s+', "Shell HTTP request"),
        (r'fetch\(', "Fetch API call"),
        (r'http\.client|httplib', "HTTP client library"),
        (r'socket\.(connect|create_connection)', "Raw socket connection"),
    ],
    "credential_access": [
        (r'(OPENAI_API_KEY|ANTHROPIC_API_KEY|OPENROUTER_API_KEY|AWS_SECRET|GITHUB_TOKEN|DISCORD_TOKEN)', "Sensitive API key access"),
        (r'os\.environ\[.*(key|token|secret|password|credential)', "Sensitive env var read"),
        (r'(\.ssh/|id_rsa|id_ed25519)', "SSH key access"),
        (r'(\.aws/credentials|\.npmrc|\.netrc)', "Credential file access"),
        (r'keychain|keyring|credential.store', "System keychain access"),
    ],
    "filesystem_access": [
        (r'open\(.*[\'"]/(etc|var|proc|sys)', "System file access"),
        (r'(shutil\.rmtree|os\.remove|os\.unlink)', "File deletion"),
        (r'os\.chmod|os\.chown', "Permission changes"),
        (r'(\/root\/|\/home\/[^/]+\/\.)(?!openclaw)', "Home directory hidden files"),
    ],
    "code_execution": [
        (r'eval\(|exec\(', "Dynamic code execution"),
        (r'os\.system\(|subprocess\.(call|run|Popen)', "Shell command execution"),
        (r'__import__\(|importlib\.import_module', "Dynamic import"),
        (r'compile\(.*exec', "Compiled code execution"),
        (r'ctypes|cffi', "Native code loading"),
    ],
    "data_exfiltration": [
        (r'requests\.post\(|urllib\.request\.urlopen.*POST', "Outbound POST request"),
        (r'smtp|sendmail|email\.mime', "Email sending"),
        (r'ftp://|ftplib', "FTP connection"),
    ],
    "obfuscation": [
        (r'base64\.(b64decode|decodebytes)', "Base64 decoding"),
        (r'\\x[0-9a-f]{2}\\x[0-9a-f]{2}', "Hex-encoded strings"),
        (r'chr\(\d+\)\s*\+\s*chr\(\d+\)', "Character code construction"),
        (r'marshal\.loads|pickle\.loads', "Serialized code loading"),
        (r'codecs\.decode\(', "Codec-based decoding"),
    ],
    "dynamic_fetch": [
        (r'(fetch|requests\.get|urllib).*\.(md|txt|yaml|yml|json)', "Remote instruction fetch"),
        (r'eval\(.*requests|eval\(.*fetch', "Fetch and execute"),
    ],
    "prompt_injection": [
        (r'ignore\s+(previous|all|above)\s+(instructions|prompts)', "Instruction override"),
        (r'(secretly|covertly|silently|without.*(telling|informing))', "Covert action"),
    ],
}

CODE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".bash", ".rb", ".go", ".rs", ".pl"}


def detect_capabilities(content):
    """Detect all capabilities present in content. Returns set of (category, description) tuples."""
    caps = set()
    for category, patterns in CAPABILITY_PATTERNS.items():
        for pattern, desc in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                caps.add((category, desc))
    return caps


def scan_directory_capabilities(skill_path):
    """Scan all files in a skill directory and return capabilities found per file."""
    skill_path = Path(skill_path)
    all_caps = {}  # file -> set of (category, desc)
    total_caps = set()

    # Scan SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md) as f:
            content = f.read()
        caps = detect_capabilities(content)
        if caps:
            all_caps["SKILL.md"] = caps
            total_caps.update(caps)

    # Scan code files
    for root, dirs, files in os.walk(skill_path):
        for fname in files:
            fpath = Path(root) / fname
            if fpath.suffix in CODE_EXTENSIONS:
                try:
                    with open(fpath) as f:
                        content = f.read()
                    caps = detect_capabilities(content)
                    if caps:
                        relpath = str(fpath.relative_to(skill_path))
                        all_caps[relpath] = caps
                        total_caps.update(caps)
                except Exception:
                    pass

    return all_caps, total_caps


def get_file_list(skill_path):
    """Get all files in a skill directory as relative paths."""
    skill_path = Path(skill_path)
    files = set()
    for root, dirs, filenames in os.walk(skill_path):
        for fname in filenames:
            fpath = Path(root) / fname
            files.add(str(fpath.relative_to(skill_path)))
    return files


def diff_skills(old_path, new_path):
    """Diff two skill versions and return analysis."""
    old_path = Path(old_path)
    new_path = Path(new_path)

    # Get file lists
    old_files = get_file_list(old_path)
    new_files = get_file_list(new_path)

    added_files = new_files - old_files
    removed_files = old_files - new_files
    common_files = old_files & new_files

    # Check which common files changed
    modified_files = []
    for f in common_files:
        old_content = (old_path / f).read_text(errors="replace")
        new_content = (new_path / f).read_text(errors="replace")
        if old_content != new_content:
            modified_files.append(f)

    # Detect capabilities
    old_caps_by_file, old_total_caps = scan_directory_capabilities(old_path)
    new_caps_by_file, new_total_caps = scan_directory_capabilities(new_path)

    # Find NEW capabilities (in new but not in old)
    new_capabilities = new_total_caps - old_total_caps
    removed_capabilities = old_total_caps - new_total_caps

    # Categorize new capabilities
    new_by_category = {}
    for cat, desc in new_capabilities:
        new_by_category.setdefault(cat, []).append(desc)

    # Determine recommendation
    critical_categories = {"code_execution", "data_exfiltration", "obfuscation", "dynamic_fetch"}
    high_categories = {"credential_access", "prompt_injection"}

    has_critical = any(cat in critical_categories for cat in new_by_category)
    has_high = any(cat in high_categories for cat in new_by_category)

    if has_critical:
        recommendation = "BLOCK"
    elif has_high:
        recommendation = "REVIEW"
    elif new_capabilities:
        recommendation = "REVIEW"
    else:
        recommendation = "SAFE"

    return {
        "old_path": str(old_path),
        "new_path": str(new_path),
        "files": {
            "added": sorted(added_files),
            "removed": sorted(removed_files),
            "modified": sorted(modified_files),
            "unchanged": len(common_files) - len(modified_files),
        },
        "capabilities": {
            "new": {cat: descs for cat, descs in sorted(new_by_category.items())},
            "removed": sorted(set(cat for cat, _ in removed_capabilities)),
            "total_new": len(new_capabilities),
            "total_removed": len(removed_capabilities),
        },
        "recommendation": recommendation,
    }


def format_diff(result, summary_only=False):
    """Format diff results for display."""
    files = result["files"]
    caps = result["capabilities"]
    rec = result["recommendation"]

    total_changed = len(files["added"]) + len(files["removed"]) + len(files["modified"])

    print(f"Skill Diff: {result['old_path']} → {result['new_path']}")
    print(f"Files changed: {total_changed} ({len(files['modified'])} modified, {len(files['added'])} added, {len(files['removed'])} removed)")
    print()

    if not summary_only:
        if files["added"]:
            print("  NEW FILES:")
            for f in files["added"]:
                print(f"    + {f}")
            print()

        if files["removed"]:
            print("  REMOVED FILES:")
            for f in files["removed"]:
                print(f"    - {f}")
            print()

        if files["modified"]:
            print("  MODIFIED FILES:")
            for f in files["modified"]:
                print(f"    ~ {f}")
            print()

    if caps["new"]:
        print("NEW CAPABILITIES:")
        for category, descriptions in caps["new"].items():
            label = category.replace("_", " ").title()
            icon = "🚨" if category in {"code_execution", "data_exfiltration"} else "⚠️"
            for desc in descriptions:
                print(f"  {icon} [{label}] {desc}")
        print()

    if caps["removed"]:
        print("REMOVED CAPABILITIES:")
        for cat in caps["removed"]:
            print(f"  ✅ {cat.replace('_', ' ').title()} removed")
        print()

    if not caps["new"] and not caps["removed"]:
        print("No security-relevant capability changes detected.")
        print()

    # Recommendation
    icons = {"SAFE": "✅", "REVIEW": "⚠️", "BLOCK": "🚨"}
    messages = {
        "SAFE": "No new security capabilities. Safe to update.",
        "REVIEW": "New capabilities detected. Review changes before updating.",
        "BLOCK": "Critical new capabilities added. Manual audit required before updating.",
    }
    print(f"RECOMMENDATION: {icons[rec]} {rec} — {messages[rec]}")


def main():
    parser = argparse.ArgumentParser(description="Skill Differ — Compare skill versions for security changes")
    sub = parser.add_subparsers(dest="command")

    p_diff = sub.add_parser("diff", help="Diff two skill versions")
    p_diff.add_argument("--old", required=True, help="Path to old version")
    p_diff.add_argument("--new", required=True, help="Path to new version")
    p_diff.add_argument("--json", action="store_true", help="Output as JSON")
    p_diff.add_argument("--summary", action="store_true", help="Summary only, no file details")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "diff":
        if not os.path.isdir(args.old):
            print(f"ERROR: {args.old} is not a directory", file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(args.new):
            print(f"ERROR: {args.new} is not a directory", file=sys.stderr)
            sys.exit(1)

        result = diff_skills(args.old, args.new)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            format_diff(result, summary_only=args.summary)

        # Exit with non-zero if BLOCK recommended
        if result["recommendation"] == "BLOCK":
            sys.exit(2)
        elif result["recommendation"] == "REVIEW":
            sys.exit(1)


if __name__ == "__main__":
    main()

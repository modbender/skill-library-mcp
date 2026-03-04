#!/usr/bin/env python3
"""MoltCops Security Scanner — local-first, no network calls."""
import json, os, re, sys

def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def scan_file(filepath, rules):
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return findings

    for rule in rules:
        try:
            pat = re.compile(rule["pattern"], re.IGNORECASE if rule.get("case_insensitive", True) else 0)
        except re.error:
            continue

        for i, line in enumerate(lines, 1):
            if pat.search(line):
                # False positive filters
                if rule["id"] == "MC-008":
                    if not re.search(r"(KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL)", line, re.IGNORECASE):
                        continue
                if rule["id"] == "MC-014":
                    if re.search(r"(github\.com|gitlab\.com|bitbucket\.org)", line, re.IGNORECASE):
                        continue
                if rule["id"] == "MC-017":
                    if not re.search(r"(rm\s|git push.*force|git reset|del\s|destroy|drop\s)", line, re.IGNORECASE):
                        continue

                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "category": rule["category"],
                    "file": filepath,
                    "line": i,
                    "matched": line.strip()[:120],
                    "description": rule["description"]
                })
    return findings

def main():
    if len(sys.argv) != 2:
        print("Usage: python scan.py <path-to-skill-folder>")
        sys.exit(1)

    skill_path = sys.argv[1]
    if not os.path.isdir(skill_path):
        print(f"Error: {skill_path} is not a directory")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Check same directory first (ClawHub flattens structure), then parent
    rules_path = os.path.join(script_dir, "rules.json")
    if not os.path.exists(rules_path):
        rules_path = os.path.join(os.path.dirname(script_dir), "rules.json")
    if not os.path.exists(rules_path):
        print("Error: rules.json not found")
        sys.exit(1)
    rules = load_rules(rules_path)

    print("MoltCops Security Scanner")
    print("=" * 40)
    print(f"Scanning: {skill_path}")

    # Find files
    exts = {".md", ".py", ".js", ".ts", ".sh", ".jsx", ".tsx"}
    files = []
    for root, dirs, fnames in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "__pycache__")]
        for fn in fnames:
            if os.path.splitext(fn)[1] in exts:
                files.append(os.path.join(root, fn))

    print(f"Files: {len(files)}")
    print(f"Rules: {len(rules)}")
    print()

    all_findings = []
    for f in files:
        all_findings.extend(scan_file(f, rules))

    critical = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    high = sum(1 for f in all_findings if f["severity"] == "HIGH")
    medium = sum(1 for f in all_findings if f["severity"] == "MEDIUM")

    if all_findings:
        print("FINDINGS")
        print("-" * 40)
        for f in all_findings:
            sev = f["severity"]
            color = {"CRITICAL": "\033[0;31m", "HIGH": "\033[1;33m", "MEDIUM": "\033[0;34m"}.get(sev, "")
            nc = "\033[0m"
            rel = os.path.relpath(f["file"], skill_path)
            print(f"{color}[{sev}]{nc} {f['rule_id']}: {f['rule_name']} ({rel}:{f['line']})")
        print()

    print("SUMMARY")
    print("=" * 40)
    print(f"Files scanned: {len(files)}")
    print(f"Total findings: {len(all_findings)}")
    print(f"  Critical: {critical}")
    print(f"  High:     {high}")
    print(f"  Medium:   {medium}")
    print()

    if critical > 0:
        print("\033[0;31mVERDICT: BLOCK\033[0m")
        print("Critical threats detected. Do NOT install this skill.")
        sys.exit(2)
    elif high > 0:
        print("\033[1;33mVERDICT: WARN\033[0m")
        print("High-risk patterns found. Review before installing.")
        sys.exit(1)
    else:
        print("\033[0;32mVERDICT: PASS\033[0m")
        print("No critical or high-risk threats detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()

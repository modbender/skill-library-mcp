import os
import re
import json
import argparse
import sys

# Constants
DEFAULT_PATTERNS_PATH = os.path.join(os.path.dirname(__file__), "../references/threat_patterns.json")

def load_patterns(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading patterns: {e}")
        sys.exit(1)

def audit_directory(target_path, patterns):
    report = {
        "target": target_path,
        "findings": [],
        "risk_score": 0,
        "status": "SAFE"
    }
    
    if not os.path.isdir(target_path):
        print(f"Error: {target_path} is not a directory.")
        sys.exit(1)

    for root, dirs, files in os.walk(target_path):
        for file in files:
            # Skip hidden files or specific extensions if needed
            if file.startswith('.') or file.endswith(('.pyc', '.skill', '.zip')):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    for category, regex_list in patterns.items():
                        for pattern in regex_list:
                            if re.search(pattern, content, re.IGNORECASE):
                                finding = {
                                    "file": os.path.relpath(file_path, target_path),
                                    "category": category,
                                    "pattern": pattern
                                }
                                report["findings"].append(finding)
                                # Scoring logic: 20 points per match, capped per category
                                report["risk_score"] += 20
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    # Normalize score and status
    if report["risk_score"] >= 80:
        report["status"] = "DANGEROUS"
    elif report["risk_score"] >= 40:
        report["status"] = "SUSPICIOUS"
    elif report["risk_score"] > 0:
        report["status"] = "CAUTION"
    
    return report

def main():
    parser = argparse.ArgumentParser(description="ClawGuard: Audit agent skills for security risks.")
    parser.add_argument("path", help="The path to the skill directory to audit.")
    parser.add_argument("--json", action="store_true", help="Output report in JSON format.")
    args = parser.parse_args()

    patterns = load_patterns(DEFAULT_PATTERNS_PATH)
    report = audit_directory(args.path, patterns)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n--- ClawGuard Audit Report ---")
        print(f"Target: {report['target']}")
        print(f"Status: {report['status']}")
        print(f"Risk Score: {report['risk_score']}")
        print(f"Findings: {len(report['findings'])}")
        print("-" * 30)
        for f in report['findings']:
            print(f"[{f['category'].upper()}] in {f['file']}: Match '{f['pattern']}'")
        print("-" * 30 + "\n")

if __name__ == "__main__":
    main()

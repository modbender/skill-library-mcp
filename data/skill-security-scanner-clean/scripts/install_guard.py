#!/usr/bin/env python3
"""
Quick Install Guard - Easy integration for skill installation workflows
Automatically scans skills before installation and provides user-friendly prompts.
"""

import sys
import json
import subprocess
from pathlib import Path

def scan_skill(skill_path: str, strict: bool = False) -> dict:
    """Run security scan and return results"""
    scanner_path = Path(__file__).parent / "security_scanner.py"
    
    cmd = [sys.executable, str(scanner_path), skill_path, "--format", "json"]
    if strict:
        cmd.append("--strict")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Failed to parse scan results", "raw_output": result.stdout}

def prompt_user(message: str) -> bool:
    """Ask user for confirmation"""
    while True:
        response = input(f"{message} (y/N): ").strip().lower()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no', ''):
            return False
        print("Please enter 'y' or 'n'")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Quick Install Guard - Security check before installing skills'
    )
    parser.add_argument('skill_path', help='Path to skill directory or .skill file')
    parser.add_argument('--strict', action='store_true', 
                        help='Enable strict mode for untrusted sources')
    parser.add_argument('--auto-reject', action='store_true',
                        help='Automatically reject on critical findings (no prompt)')
    parser.add_argument('--json', action='store_true',
                        help='Output JSON only (for scripting)')
    
    args = parser.parse_args()
    
    # Handle .skill files (zip archives)
    skill_path = args.skill_path
    if skill_path.endswith('.skill'):
        import tempfile
        import zipfile
        
        extract_dir = tempfile.mkdtemp(prefix="skill_scan_")
        with zipfile.ZipFile(skill_path, 'r') as z:
            z.extractall(extract_dir)
        skill_path = extract_dir
    
    # Run scan
    report = scan_skill(skill_path, strict=args.strict)
    
    if "error" in report:
        print(f"❌ Scan failed: {report['error']}")
        sys.exit(1)
    
    if args.json:
        print(json.dumps(report, indent=2))
        sys.exit(0 if report['summary']['verdict'] != 'REJECT' else 1)
    
    # Display results
    s = report['summary']
    print("\n" + "=" * 60)
    print("🔒 SECURITY SCAN COMPLETE")
    print("=" * 60)
    print(f"Skill: {report['skill_path']}")
    print(f"Score: {s['security_score']}/100")
    print(f"Verdict: {s['verdict_emoji']} {s['verdict']}")
    print("-" * 60)
    
    # Show risk summary
    for level, count in s['risk_distribution'].items():
        if count > 0:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}.get(level, "⚪")
            print(f"  {emoji} {level.upper()}: {count}")
    
    # Show top findings
    if report['findings']:
        print("\n⚠️  Top Findings:")
        for finding in report['findings'][:5]:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}.get(finding['risk_level'], "⚪")
            print(f"  {emoji} [{finding['rule_id']}] {finding['rule_name']}")
            print(f"      {finding['description'][:60]}...")
    
    print("\n" + "=" * 60)
    
    # Decision logic
    verdict = s['verdict']
    
    if verdict == 'REJECT':
        print("\n🚫 INSTALLATION BLOCKED")
        print("Critical security threats detected. This skill should NOT be installed.")
        print("\nReasons:")
        critical_findings = [f for f in report['findings'] if f['risk_level'] == 'critical']
        for f in critical_findings:
            print(f"  • {f['rule_name']}: {f['description']}")
        sys.exit(2)
    
    elif verdict == 'WARNING':
        print("\n⚠️  HIGH RISK DETECTED")
        print("This skill contains potentially dangerous functionality.")
        print("Only install if you completely trust the source and understand the risks.")
        
        if args.auto_reject:
            print("\n❌ Auto-reject enabled. Installation cancelled.")
            sys.exit(1)
        
        if prompt_user("Do you want to review the detailed findings first?"):
            print("\n" + "-" * 60)
            for finding in report['findings']:
                if finding['risk_level'] in ['critical', 'high']:
                    print(f"\n🔍 {finding['rule_name']}")
                    print(f"   Risk: {finding['risk_level'].upper()}")
                    print(f"   Location: {finding['file_path']}:{finding['line_number']}")
                    print(f"   Description: {finding['description']}")
                    print(f"   💡 {finding['recommendation']}")
        
        if not prompt_user("Proceed with installation despite warnings?"):
            print("\n❌ Installation cancelled.")
            sys.exit(1)
    
    elif verdict == 'REVIEW':
        print("\n📝 REVIEW RECOMMENDED")
        print("Some suspicious patterns were found. Please review before installing.")
        
        if prompt_user("View detailed findings?"):
            print("\n" + "-" * 60)
            for finding in report['findings'][:10]:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}.get(finding['risk_level'], "⚪")
                print(f"\n{emoji} [{finding['risk_level'].upper()}] {finding['rule_name']}")
                print(f"   {finding['description']}")
                print(f"   File: {finding['file_path']}:{finding['line_number']}")
        
        if not prompt_user("Proceed with installation?"):
            print("\n❌ Installation cancelled.")
            sys.exit(1)
    
    else:  # PASS
        print("\n✅ SECURITY CHECK PASSED")
        print("No critical security issues found. Safe to install.")
    
    print("\n✅ Installation approved.")
    print(f"📊 Final Score: {s['security_score']}/100")
    
    # Save report for reference
    report_path = Path(skill_path) / ".security_scan_report.json"
    if report_path.parent.exists():
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📝 Full report saved to: {report_path}")
    
    sys.exit(0)

if __name__ == '__main__':
    main()

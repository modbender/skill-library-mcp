"""CLI and API entrypoint for ClawSkillShield.
"""
import os
import shutil
import sys
from .analyzer import analyze_file, calculate_risk_score, Threat
from typing import List

def scan_local(path: str) -> str:
    """Scan a local skill folder – callable by agents for automation."""
    if not os.path.exists(path):
        return f"❌ Path not found: {path}"
    
    all_threats: List[Threat] = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(('.py', '.js', '.yaml', '.json')):
                filepath = os.path.join(root, file)
                all_threats.extend(analyze_file(filepath))
    
    return generate_report(os.path.basename(path), all_threats)

def quarantine(path: str) -> str:
    """Quarantine a risky skill – agents can call this autonomously."""
    quarantine_dir = os.path.expanduser("~/.openclaw/quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)
    target = os.path.join(quarantine_dir, os.path.basename(path))
    if os.path.exists(target):
        shutil.rmtree(target, ignore_errors=True)
    shutil.move(path, target)
    return f"🛡️ Quarantined {path} → {target}\n   (Safe for agents to auto-trigger on HIGH RISK)"

def generate_report(skill_name: str, threats: List[Threat]) -> str:
    risk_score = calculate_risk_score(threats)
    colors = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    
    report = [f"\n{'='*60}", f"ClawSkillShield Report: {skill_name}", f"{'='*60}\n"]
    
    if risk_score >= 7:
        verdict = "🟢 LOW RISK - Safe to try"
    elif risk_score >= 4:
        verdict = "🟡 MODERATE RISK - Review"
    else:
        verdict = "🔴 HIGH RISK - Quarantine recommended!"
    
    report += [f"{verdict}", f"Risk Score: {risk_score:.1f}/10.0\n"]
    
    if threats:
        report += ["-"*60, "Threats Found:", "-"*60]
        for t in threats:
            emoji = colors.get(t.severity, "⚪")
            report += [f"\n{emoji} [{t.severity.upper()}] {t.title}", f"   File: {t.file}"]
            if t.line: report += [f"   Line: {t.line}"]
            report += [f"   {t.description}"]
        if risk_score < 4:
            report += ["\n🚨 Auto-quarantine suggested!"]
    else:
        report += ["🎉 No threats detected!"]
    
    report += [f"\n{'='*60}\n"]
    return "\n".join(report)

def run_cli():
    if len(sys.argv) < 3:
        print("Usage: clawskillshield <command> <path>\nCommands: scan-local <folder> | quarantine <folder>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    path = sys.argv[2]
    
    if cmd == "scan-local":
        print(scan_local(path))
    elif cmd == "quarantine":
        print(quarantine(path))
    else:
        print("Unknown command")

if __name__ == "__main__":
    run_cli()

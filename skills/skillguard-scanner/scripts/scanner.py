#!/usr/bin/env python3
"""SkillGuard — OpenClaw Skill Security Scanner (v1.1.0)

Features:
- Whitelist / context based false‑positive reduction
- Typosquatting detection with configurable check-name
- Detailed report with false‑positive likelihood and file count
- Optional --fetch-clawhub mode (if CLI available)
- Security policy engine with human-readable "why this is risky" blurbs
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Set

# ------------------------------------------------------------
# Patterns
# ------------------------------------------------------------
SUSPICIOUS_URLS = re.compile(
    r'(webhook\.site|glot\.io|pastebin\.com|paste\.ee|hastebin\.com|'
    r'ngrok\.io|serveo\.net|localhost\.run|raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/)',
    re.IGNORECASE,
)

HARDCODED_IPS = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
PRIVATE_IPS = re.compile(
    r'\b(127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|0\.0\.0\.0)\b'
)
REVERSE_SHELL = re.compile(
    r'(bash\s+-i\s+>&|/dev/tcp/|nc\s+-[elp]|ncat\s|mkfifo|python.*socket.*connect|'
    r'perl.*socket.*INET|ruby.*TCPSocket|php.*fsockopen|exec\s+\d+<>/dev/tcp)',
    re.IGNORECASE,
)
OBFUSCATION = re.compile(
    r'(base64\s*-[dD]|eval\s*\(|exec\s*\(.*base64|\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}|'
    r'fromCharCode|atob\s*\(|Buffer\.from\(.*base64|decode\(.*base64)',
    re.IGNORECASE,
)
CREDENTIAL_ACCESS = re.compile(
    r'(\.env\b|\.openclaw/|credentials|api[_-]?key|secret[_-]?key|password|token|'
    r'OPENAI_API_KEY|ANTHROPIC_API_KEY|TELEGRAM_BOT_TOKEN|\.ssh/|id_rsa)',
    re.IGNORECASE,
)
EXFILTRATION = re.compile(
    r'(curl\s.*-[dX]|wget\s|fetch\s*\(|requests\.(post|put)|'
    r'http\.request|axios\.(post|put)|got\.(post|put))',
    re.IGNORECASE,
)
SHELL_EXEC = re.compile(
    r'(subprocess|os\.system|os\.popen|child_process|execSync|spawn\s*\(|'
    r'Popen|shell=True|ShellExecute)',
    re.IGNORECASE,
)
MEMORY_WRITE = re.compile(
    r'(SOUL\.md|MEMORY\.md|AGENTS\.md|HEARTBEAT\.md|USER\.md|IDENTITY\.md)',
    re.IGNORECASE,
)
DOWNLOAD_CMDS = re.compile(
    r'(curl\s+.*-[oOL]|wget\s+|pip\s+install|npm\s+install|brew\s+install|apt\s+install|'
    r'openclaw-agent\.zip|\.dmg|\.exe|\.msi|\.pkg)',
    re.IGNORECASE,
)
CRYPTO_WALLET = re.compile(
    r'(wallet|seed\s*phrase|mnemonic|private[_\s]?key|keystore)',
    re.IGNORECASE,
)

# ------------------------------------------------------------
# Severity constants
# ------------------------------------------------------------
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"
SEVERITY_INFO = "INFO"

# ------------------------------------------------------------
# Data classes
# ------------------------------------------------------------
@dataclass
class Finding:
    check: str
    severity: str
    file: str
    line: int
    snippet: str
    detail: str
    fp_likelihood: str = ""  # will be filled later

    def set_fp_likelihood(self):
        # simplistic mapping
        mapping = {
            SEVERITY_CRITICAL: "high",
            SEVERITY_HIGH: "high",
            SEVERITY_MEDIUM: "medium",
            SEVERITY_LOW: "low",
            SEVERITY_INFO: "low",
        }
        self.fp_likelihood = mapping.get(self.severity, "low")

# ------------------------------------------------------------
# Security Policy — human-readable risk explanations
# ------------------------------------------------------------
RISK_POLICY = {
    "reverse_shell": {
        "why": "Opens a remote backdoor. An attacker can execute arbitrary commands on your machine.",
        "action": "DO NOT INSTALL. Report to ClawHub.",
        "ref": "ClawHavoc campaign (Koi Security, Feb 2026)"
    },
    "obfuscation": {
        "why": "Hidden/encoded code that runs at install or runtime. Impossible to audit visually.",
        "action": "DO NOT INSTALL unless you can decode and verify the payload.",
        "ref": "Atomic Stealer distributed via base64-encoded shell scripts"
    },
    "suspicious_url": {
        "why": "Connects to known exfiltration/payload hosting services (webhook.site, glot.io, ngrok, pastebin).",
        "action": "Block. These domains are used to steal credentials or deliver malware.",
        "ref": "341 malicious skills used glot.io and webhook.site"
    },
    "memory_write": {
        "why": "Modifies your agent's identity/memory files (SOUL.md, MEMORY.md). Can inject persistent malicious instructions that survive across sessions.",
        "action": "Reject unless the skill is explicitly designed for memory management.",
        "ref": "Time-shifted prompt injection via memory poisoning (Adversa.ai)"
    },
    "suspicious_prereq": {
        "why": "Asks you to download and run external software. This is the #1 attack vector on ClawHub.",
        "action": "Never run install commands from skill docs without verifying the source.",
        "ref": "ClawHavoc: fake prerequisites → Atomic Stealer (macOS) / trojans (Windows)"
    },
    "credential_access": {
        "why": "Reads API keys, tokens, passwords, or .env files. Could exfiltrate your credentials.",
        "action": "Verify the code only accesses credentials it legitimately needs.",
        "ref": "Skills exfiltrating ~/.openclaw/.env to webhook.site"
    },
    "exfiltration": {
        "why": "Sends data to external servers via HTTP POST/PUT. Could leak your private data.",
        "action": "Check what data is being sent and to which domain.",
        "ref": "Credential theft via outbound HTTP requests"
    },
    "hardcoded_ip": {
        "why": "Contains hardcoded public IP addresses. Could be C2 server or data exfiltration endpoint.",
        "action": "Verify the IP belongs to a legitimate service.",
        "ref": "Reverse shells connecting to attacker-controlled IPs"
    },
    "typosquatting": {
        "why": "Name is suspiciously similar to a popular skill. Attackers use this to trick users into installing malware.",
        "action": "Double-check you're installing the correct skill.",
        "ref": "clawhub1, clawhubb, youtube-summarize-pro mimicking legitimate skills"
    },
    "crypto_access": {
        "why": "Accesses cryptocurrency wallets, seed phrases, or private keys.",
        "action": "High risk of theft. Only install if this is a legitimate crypto tool you trust.",
        "ref": "Fake Solana wallet trackers stealing keys"
    },
    "shell_exec": {
        "why": "Executes shell commands. Common in legitimate tools but can be abused.",
        "action": "Review what commands are being run.",
        "ref": "General best practice"
    },
}

@dataclass
class SkillReport:
    name: str
    path: str
    risk_score: float = 0.0
    risk_level: str = "UNKNOWN"
    findings: List[Finding] = field(default_factory=list)
    file_count: int = 0
    has_skill_md: bool = False
    has_scripts: bool = False

    def add(self, finding: Finding):
        finding.set_fp_likelihood()
        self.findings.append(finding)

    def compute_score(self):
        weights = {
            SEVERITY_CRITICAL: 25,
            SEVERITY_HIGH: 15,
            SEVERITY_MEDIUM: 5,
            SEVERITY_LOW: 2,
            SEVERITY_INFO: 0,
        }
        self.risk_score = sum(weights.get(f.severity, 0) for f in self.findings)
        if self.risk_score >= 50:
            self.risk_level = "CRITICAL"
        elif self.risk_score >= 25:
            self.risk_level = "HIGH"
        elif self.risk_score >= 10:
            self.risk_level = "MEDIUM"
        elif self.risk_score > 0:
            self.risk_level = "LOW"
        else:
            self.risk_level = "CLEAN"

# ------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------
SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".sh", ".bash", ".zsh", ".rb", ".pl",
    ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
    ".env", ".dockerfile", ".makefile",
}

BINARY_SKIP = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".ttf", ".wasm", ".pyc"}

def _should_scan(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SKIP:
        return False
    if path.suffix.lower() in SCAN_EXTENSIONS or path.suffix == "":
        return True
    return False

def _is_whitelisted_fetch(filepath: Path, line: str) -> bool:
    return filepath.name in {"search.js", "content.js"} and "fetch" in line

def _is_whitelisted_install(filepath: Path, line: str) -> bool:
    return filepath.suffix == ".md" and filepath.name in {"README.md", "SKILL.md"} and re.search(r"(npm|pip|brew)\s+install", line, re.IGNORECASE)

def _is_whitelisted_weather(line: str) -> bool:
    return "curl" in line and "wttr.in" in line

def _is_user_agent_ip(line: str) -> bool:
    return "User-Agent" in line and HARDCODED_IPS.search(line)

def _is_credential_in_audit(filepath: Path) -> bool:
    return filepath.name == "security-audit.sh"

def _is_memory_write_by_design(filepath: Path) -> bool:
    return ("proactive-agent" in str(filepath.parent) or "self-improving-agent" in str(filepath.parent)) and filepath.name == "SKILL.md"

# Levenshtein distance for typosquatting
def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    v0 = list(range(len(b) + 1))
    v1 = [0] * (len(b) + 1)
    for i in range(len(a)):
        v1[0] = i + 1
        for j in range(len(b)):
            cost = 0 if a[i] == b[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, v0
    return v0[-1]

# ------------------------------------------------------------
# Core scanning logic per file
# ------------------------------------------------------------
def _scan_file(filepath: Path, rel_path: str) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#') and len(stripped) < 5:
            continue
        # User-Agent with IP -> ignore
        if _is_user_agent_ip(line):
            continue
        # Reverse shell (critical)
        if REVERSE_SHELL.search(line):
            findings.append(Finding("reverse_shell", SEVERITY_CRITICAL, rel_path, i,
                                 line.strip()[:120], "Possible reverse shell pattern"))
        # Obfuscation (high)
        if OBFUSCATION.search(line):
            if not any(x in line.lower() for x in ["example", "documentation", "```", "usage"]):
                findings.append(Finding("obfuscation", SEVERITY_HIGH, rel_path, i,
                                 line.strip()[:120], "Code obfuscation / dynamic eval"))
        # Suspicious URLs (high)
        m = SUSPICIOUS_URLS.search(line)
        if m:
            findings.append(Finding("suspicious_url", SEVERITY_HIGH, rel_path, i,
                                 line.strip()[:120], f"Suspicious URL: {m.group()}"))
        # Hardcoded IPs (medium) – skip private
        for ip in HARDCODED_IPS.findall(line):
            if not PRIVATE_IPS.match(ip):
                findings.append(Finding("hardcoded_ip", SEVERITY_MEDIUM, rel_path, i,
                                 line.strip()[:120], f"Hardcoded public IP: {ip}"))
        # Credential access (medium) – whitelist for audit script
        if CREDENTIAL_ACCESS.search(line):
            if _is_credential_in_audit(filepath):
                findings.append(Finding("credential_access", SEVERITY_INFO, rel_path, i,
                                 line.strip()[:120], "Credential access in audit script (legitimate)"))
            else:
                if filepath.suffix in {'.py', '.js', '.ts', '.sh', '.bash', '.rb', '.pl'}:
                    findings.append(Finding("credential_access", SEVERITY_MEDIUM, rel_path, i,
                                     line.strip()[:120], "Potential credential/secret access"))
        # Exfiltration (medium) – whitelist fetch & weather
        if EXFILTRATION.search(line):
            if _is_whitelisted_fetch(filepath, line) or _is_whitelisted_weather(line):
                findings.append(Finding("exfiltration", SEVERITY_INFO, rel_path, i,
                                 line.strip()[:120], "Legitimate fetch/curl usage"))
            else:
                if filepath.suffix in {'.py', '.js', '.ts', '.sh', '.bash', '.rb', '.pl'}:
                    findings.append(Finding("exfiltration", SEVERITY_MEDIUM, rel_path, i,
                                     line.strip()[:120], "Outbound data transfer pattern"))
        # Shell exec (low)
        if SHELL_EXEC.search(line):
            if filepath.suffix in {'.py', '.js', '.ts', '.sh', '.bash', '.rb', '.pl'}:
                findings.append(Finding("shell_exec", SEVERITY_LOW, rel_path, i,
                                 line.strip()[:120], "Shell/subprocess execution"))
        # Memory writes (high) – whitelist by design
        if MEMORY_WRITE.search(line):
            if _is_memory_write_by_design(filepath):
                findings.append(Finding("memory_write", SEVERITY_INFO, rel_path, i,
                                 line.strip()[:120], "Memory write by design (proactive/self‑improving agent)"))
            else:
                # require write verbs
                if any(w in line.lower() for w in ['write', 'update', 'edit', 'append', 'modify', 'overwrite', 'create']):
                    findings.append(Finding("memory_write", SEVERITY_HIGH, rel_path, i,
                                 line.strip()[:120], "Instruction to write to system memory files"))
        # Dangerous downloads in docs (high) – whitelist install commands in docs
        if DOWNLOAD_CMDS.search(line):
            if _is_whitelisted_install(filepath, line):
                findings.append(Finding("suspicious_prereq", SEVERITY_INFO, rel_path, i,
                                 line.strip()[:120], "Legitimate install command in documentation"))
            else:
                if filepath.suffix in {'.md', '.txt', '.rst'}:
                    findings.append(Finding("suspicious_prereq", SEVERITY_HIGH, rel_path, i,
                                 line.strip()[:120], "Download instruction in documentation"))
        # Crypto wallet patterns (medium)
        if CRYPTO_WALLET.search(line):
            if filepath.suffix in {'.py', '.js', '.ts', '.sh'}:
                findings.append(Finding("crypto_access", SEVERITY_MEDIUM, rel_path, i,
                                 line.strip()[:120], "Cryptocurrency wallet/key access"))
    return findings

# ------------------------------------------------------------
# Skill scanning
# ------------------------------------------------------------
def scan_skill(skill_path: Path, known_names: Set[str]) -> SkillReport:
    report = SkillReport(name=skill_path.name, path=str(skill_path))
    files: List[Path] = []
    for f in skill_path.rglob('*'):
        if f.is_file() and 'node_modules' not in str(f) and '.git' not in str(f):
            files.append(f)
    report.file_count = len(files)
    report.has_skill_md = (skill_path / 'SKILL.md').exists()
    report.has_scripts = any(f.suffix in {'.py', '.js', '.ts', '.sh'} for f in files)
    for f in files:
        if _should_scan(f):
            rel = str(f.relative_to(skill_path))
            findings = _scan_file(f, rel)
            for finding in findings:
                report.add(finding)
    # Typosquatting detection for skill name
    for known in known_names:
        if known == report.name:
            continue
        if levenshtein(report.name, known) <= 2:
            report.add(Finding(
                check="typosquatting",
                severity=SEVERITY_MEDIUM,
                file="SKILL.md",
                line=0,
                snippet="",
                detail=f"possible typosquat of {known}",
            ))
            break
    report.compute_score()
    return report

def scan_all(skills_dir: Path, known_names: Set[str]) -> List[SkillReport]:
    reports: List[SkillReport] = []
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir():
            reports.append(scan_skill(d, known_names))
    return reports

# ------------------------------------------------------------
# Reporting
# ------------------------------------------------------------
def print_summary(reports: List[SkillReport]):
    print(f"\n{'='*70}")
    print(f"  SkillGuard Scan Report — {len(reports)} skills")
    print(f"{'='*70}\n")
    reports.sort(key=lambda r: r.risk_score, reverse=True)
    level_emoji = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "CLEAN": "✅",
    }
    for r in reports:
        emoji = level_emoji.get(r.risk_level, "❓")
        findings_str = f" — {len(r.findings)} findings" if r.findings else ""
        print(f"  {emoji} {r.name:30s} score={r.risk_score:5.0f}  [{r.risk_level}]{findings_str} (files={r.file_count})")
        if r.risk_level != "CLEAN":
            # one‑liner summary
            print(f"    📌 {r.name}: {r.risk_level} (score {r.risk_score}) with {len(r.findings)} findings")
    print(f"\n{'─'*70}")
    flagged = [r for r in reports if r.risk_level != "CLEAN"]
    if flagged:
        print(f"\n  📋 Details ({len(flagged)} flagged skills):\n")
        for r in flagged:
            print(f"  ┌─ {r.name} [{r.risk_level}, score={r.risk_score}] (files={r.file_count})")
            by_sev = {}
            for f in r.findings:
                by_sev.setdefault(f.severity, []).append(f)
            shown_policies = set()
            for sev in [SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW, SEVERITY_INFO]:
                if sev in by_sev:
                    for f in by_sev[sev][:5]:
                        print(f"  │  [{sev}] {f.check}: {f.file}:{f.line}")
                        print(f"  │    → {f.detail} (FP: {f.fp_likelihood})")
                        if f.snippet:
                            print(f"  │    │ {f.snippet[:100]}")
                        # Policy blurb (once per check type per skill)
                        policy = RISK_POLICY.get(f.check)
                        if policy and f.check not in shown_policies:
                            shown_policies.add(f.check)
                            print(f"  │    ⚠ WHY: {policy['why']}")
                            print(f"  │    🛡 ACTION: {policy['action']}")
                    remaining = len(by_sev[sev]) - 5
                    if remaining > 0:
                        print(f"  │  ... +{remaining} more {sev}")
            print(f"  └{'─'*50}\n")
    else:
        print("\n  ✨ All skills clean!\n")
    total_findings = sum(len(r.findings) for r in reports)
    by_level = {}
    for r in reports:
        by_level[r.risk_level] = by_level.get(r.risk_level, 0) + 1
    print(f"  Summary: {total_findings} total findings across {len(reports)} skills")
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "CLEAN"]:
        if level in by_level:
            print(f"    {level_emoji.get(level,'')} {level}: {by_level[level]} skills")
    print()

def save_json(reports: List[SkillReport], output: Path):
    reports_data = []
    for r in reports:
        rd = asdict(r)
        # Enrich findings with policy blurbs
        for f in rd.get("findings", []):
            policy = RISK_POLICY.get(f.get("check", ""))
            if policy:
                f["policy"] = policy
        reports_data.append(rd)
    data = {
        "scan_date": datetime.now().isoformat(),
        "skills_count": len(reports),
        "reports": reports_data,
    }
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"  💾 JSON report saved to {output}\n")

# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SkillGuard — OpenClaw Skill Security Scanner (v0.2)")
    parser.add_argument("--skills-dir", type=Path,
                        default=Path("/home/msgnkoki/.openclaw/workspace/skills"),
                        help="Directory containing skills to scan")
    parser.add_argument("--skill", type=str, help="Scan a single skill by name")
    parser.add_argument("--json-out", type=Path,
                        default=Path("/home/msgnkoki/.openclaw/workspace/projects/skillguard/data/scan_results_v2.json"),
                        help="Output JSON report path")
    parser.add_argument("--check-name", type=str, help="Only check given skill name for typosquatting")
    parser.add_argument("--fetch-clawhub", action="store_true", help="Fetch skills via clawhub CLI before scanning")
    args = parser.parse_args()

    # Build known skill name set (installed plus a few popular ones)
    known_names: Set[str] = set()
    if args.skills_dir.is_dir():
        for d in args.skills_dir.iterdir():
            if d.is_dir():
                known_names.add(d.name)
    # Add extra popular names
    extra = {"clawhub", "openclaw", "auto-updater", "youtube", "gmail", "github", "brew", "npm", "pip"}
    known_names.update(extra)

    if args.check_name:
        # Only perform name check
        name = args.check_name
        for known in known_names:
            if known == name:
                continue
            if levenshtein(name, known) <= 2:
                print(f"Typosquat candidate: {name} possibly imitates {known}")
                sys.exit(0)
        print("No typosquat detected for", name)
        sys.exit(0)

    if args.fetch_clawhub:
        # Verify clawhub CLI availability
        which = shutil.which("clawhub")
        if not which:
            print("clawhub CLI not found in PATH. Skipping fetch mode.")
        else:
            print(f"clawhub CLI found at {which}. Running search...")
            try:
                result = subprocess.run(["clawhub", "search"], capture_output=True, text=True, timeout=30)
                print("clawhub output:\n", result.stdout[:500])
            except Exception as e:
                print("Error running clawhub:", e)

    if args.skill:
        skill_path = args.skills_dir / args.skill
        if not skill_path.is_dir():
            print(f"Skill not found: {skill_path}")
            return 1
        reports = [scan_skill(skill_path, known_names)]
    else:
        reports = scan_all(args.skills_dir, known_names)

    print_summary(reports)
    save_json(reports, args.json_out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

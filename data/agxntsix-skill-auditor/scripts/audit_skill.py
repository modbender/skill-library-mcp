#!/usr/bin/env python3
"""
Skill Auditor — Security scanner for OpenClaw skills.
Zero external dependencies (stdlib only).

Usage:
    python3 audit_skill.py /path/to/skill [--human] [--json]

Exit codes: 0=CLEAN/LOW, 1=MEDIUM, 2=HIGH/CRITICAL
"""

import os
import re
import sys
import json
import hashlib
from pathlib import Path
from collections import defaultdict

# ─── Pattern Definitions ───────────────────────────────────────────────

DANGEROUS_PATTERNS = {
    "shell_execution": {
        "severity": "HIGH",
        "patterns": [
            (r'\bos\.system\s*\(', "os.system() call"),
            (r'\bsubprocess\b', "subprocess module usage"),
            (r'\bexec\s*\(', "exec() call"),
            (r'\beval\s*\(', "eval() call"),
            (r'\bcompile\s*\(', "compile() call"),
            (r'\bos\.popen\s*\(', "os.popen() call"),
            (r'\bos\.exec[lv]', "os.exec*() call"),
            (r'\bos\.spawn', "os.spawn*() call"),
            (r'\bpty\.spawn', "pty.spawn() call"),
            (r'\bcommands\.getoutput', "commands.getoutput() call"),
        ],
        "exclude_contexts": ["documentation", "comments_only"],
    },
    "network_calls": {
        "severity": "HIGH",
        "patterns": [
            (r'\bimport\s+requests\b', "requests library import"),
            (r'\bfrom\s+requests\b', "requests library import"),
            (r'\burllib\.request', "urllib.request usage"),
            (r'\burllib\.urlopen', "urllib.urlopen usage"),
            (r'\bhttp\.client\b', "http.client usage"),
            (r'\bhttpx\b', "httpx library usage"),
            (r'\baiohttp\b', "aiohttp library usage"),
            (r'\bsocket\s*\.\s*socket', "raw socket creation"),
            (r'\bfetch\s*\(', "fetch() call"),
            (r'\bcurl\s+', "curl command"),
            (r'\bwget\s+', "wget command"),
            (r'\bsocket\.connect', "socket.connect() call"),
        ],
    },
    "env_access": {
        "severity": "CRITICAL",
        "patterns": [
            (r'\bos\.environ', "os.environ access"),
            (r'\bos\.getenv\s*\(', "os.getenv() call"),
            (r'\bprocess\.env\b', "process.env access"),
            (r'\bdotenv\b', "dotenv usage"),
            (r'\bload_dotenv\b', "load_dotenv() call"),
            (r'(?:OPENAI|ANTHROPIC|CLAUDE|OPENROUTER|AWS|AZURE|GCP|GITHUB|TELEGRAM|DISCORD|SLACK|STRIPE|TWILIO)_(?:API_?)?(?:KEY|TOKEN|SECRET)', "API key variable reference"),
        ],
    },
    "filesystem_escape": {
        "severity": "CRITICAL",
        "patterns": [
            (r'\.\./', "parent directory traversal"),
            (r'(?:^|[\s"\'])\/etc\/', "/etc/ access"),
            (r'(?:^|[\s"\'])\/root\/', "/root/ access"),
            (r'\.ssh\/', ".ssh/ directory access"),
            (r'(?:^|[\s"\'])~/', "home directory access via ~"),
            (r'\/home\/\w+\/', "/home/ user directory access"),
            (r'(?:^|[\s"\'])\.env\b', ".env file access"),
            (r'\bos\.path\.expanduser', "expanduser (home dir resolution)"),
            (r'Path\.home\(\)', "Path.home() call"),
            (r'\/var\/run\/docker', "Docker socket access"),
            (r'\/proc\/', "/proc/ access"),
        ],
    },
    "encoding_obfuscation": {
        "severity": "HIGH",
        "patterns": [
            (r'\bbase64\b', "base64 module/usage"),
            (r'\batob\s*\(', "atob() decode"),
            (r'\bbtoa\s*\(', "btoa() encode"),
            (r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){3,}', "hex escape sequence chain"),
            (r'\\u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4}){3,}', "unicode escape sequence chain"),
            (r'\bchr\s*\(\s*\d+\s*\)\s*\+\s*chr', "chr() concatenation chain"),
            (r'(?:^|[^a-zA-Z])(?:[A-Za-z0-9+/]{40,}={0,2})(?:$|[^a-zA-Z0-9+/=])', "possible base64-encoded string"),
            (r'\[::\s*-1\s*\]', "string reversal trick"),
            (r'codecs\.decode', "codecs.decode (potential obfuscation)"),
            (r'rot_?13', "ROT13 encoding"),
        ],
    },
    "prompt_injection": {
        "severity": "CRITICAL",
        "patterns": [
            (r'ignore\s+(?:all\s+)?previous\s+instructions', "prompt injection: ignore previous instructions"),
            (r'ignore\s+(?:all\s+)?(?:above|prior)\s+(?:instructions|rules|directives)', "prompt injection: ignore prior rules"),
            (r'you\s+are\s+now\b', "prompt injection: role reassignment"),
            (r'forget\s+(?:all\s+)?your\s+(?:instructions|rules|training|guidelines)', "prompt injection: forget instructions"),
            (r'(?:new|override|updated?)\s+(?:system\s+)?instructions?\s*:', "prompt injection: override instructions"),
            (r'system\s*:\s*you', "prompt injection: fake system message"),
            (r'<\|(?:im_start|system|endoftext)\|>', "prompt injection: special token injection"),
            (r'ADMIN\s*MODE', "prompt injection: admin mode claim"),
            (r'(?:do\s+not|never)\s+(?:mention|reveal|disclose)\s+(?:this|these)\s+instructions', "prompt injection: hiding instructions"),
            (r'pretend\s+(?:you\s+are|to\s+be)', "prompt injection: role manipulation"),
            (r'act\s+as\s+(?:a\s+)?(?:root|admin|superuser)', "prompt injection: privilege escalation"),
            (r'disregard\s+(?:all\s+)?(?:safety|security|previous)', "prompt injection: safety bypass"),
        ],
    },
    "data_exfiltration": {
        "severity": "CRITICAL",
        "patterns": [
            (r'https?://(?:discord(?:app)?\.com/api/webhooks|hooks\.slack\.com|api\.telegram\.org/bot)', "webhook/bot API URL (exfiltration vector)"),
            (r'discord\.com/api/webhooks', "Discord webhook URL"),
            (r'hooks\.slack\.com', "Slack webhook URL"),
            (r'api\.telegram\.org/bot', "Telegram bot API URL"),
            (r'webhook\.site', "webhook.site (testing exfil endpoint)"),
            (r'ngrok\.io', "ngrok tunnel (exfil endpoint)"),
            (r'pipedream\.net', "pipedream (exfil endpoint)"),
            (r'requestbin', "requestbin (exfil endpoint)"),
            (r'burpcollaborator', "Burp Collaborator (pentest exfil)"),
            (r'(?:pastebin|hastebin|ghostbin)\.com', "paste service (exfil endpoint)"),
        ],
    },
    "crypto_wallet": {
        "severity": "CRITICAL",
        "patterns": [
            (r'(?:seed|mnemonic)\s*(?:phrase|words?)', "seed/mnemonic phrase reference"),
            (r'(?:private|secret)\s*key', "private key reference"),
            (r'wallet\.dat', "wallet.dat file access"),
            (r'\.(?:keystore|wallet)\b', "keystore/wallet file access"),
            (r'ethers|web3|solana|bitcoin', "crypto library usage"),
        ],
    },
    "dynamic_imports": {
        "severity": "HIGH",
        "patterns": [
            (r'__import__\s*\(', "__import__() call"),
            (r'\bimportlib\b', "importlib usage"),
            (r'\bimport_module\s*\(', "import_module() call"),
            (r'getattr\s*\(\s*__builtins__', "getattr on __builtins__"),
            (r'globals\s*\(\s*\)\s*\[', "globals() dict access"),
            (r'__builtins__\s*\[', "__builtins__ dict access"),
        ],
    },
}

# File types that are suspicious in a skill package
SUSPICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.com', '.bat', '.cmd',
    '.ps1', '.vbs', '.wsf', '.scr', '.pif', '.msi', '.jar', '.war',
    '.elf', '.deb', '.rpm', '.apk',
}

SUSPICIOUS_SHELL_EXTENSIONS = {'.sh', '.bash', '.zsh', '.fish'}

# Known malicious npm/pip packages (non-exhaustive sample)
KNOWN_MALICIOUS_PACKAGES = {
    # npm
    "event-stream", "flatmap-stream", "ua-parser-js-malicious",
    "colors-malicious", "faker-malicious", "node-ipc-malicious",
    # pip
    "python3-dateutil", "jeIlyfish", "python-sqlite",
    "colourfull", "requestss", "beautifulsoup",
    "nmap-python", "openai-python", "python-openai",
}

# Typosquat detection for common packages
LEGIT_PACKAGES = {
    "requests", "flask", "django", "numpy", "pandas", "beautifulsoup4",
    "openai", "anthropic", "langchain", "httpx", "aiohttp", "fastapi",
    "pydantic", "sqlalchemy", "boto3", "pillow", "pytorch", "tensorflow",
}


# ─── Scanner ───────────────────────────────────────────────────────────

class SkillAuditor:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path).resolve()
        self.findings = []
        self.file_inventory = []
        self.risk_score = "CLEAN"
        self.severity_order = ["CLEAN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def _bump_severity(self, severity: str):
        if self.severity_order.index(severity) > self.severity_order.index(self.risk_score):
            self.risk_score = severity

    def _add_finding(self, category: str, severity: str, file: str, line_num: int, description: str, line_content: str = ""):
        self.findings.append({
            "category": category,
            "severity": severity,
            "file": str(file),
            "line": line_num,
            "description": description,
            "content": line_content.strip()[:200] if line_content else "",
        })
        self._bump_severity(severity)

    def _is_reference_or_doc(self, filepath: Path) -> bool:
        """Check if file is documentation/reference (lower severity for pattern matches)."""
        rel = str(filepath)
        return any(x in rel.lower() for x in ['reference', 'docs/', 'doc/', 'readme', 'changelog', 'license', '.md'])

    def _is_comment_line(self, line: str, filepath: Path) -> bool:
        """Basic comment detection."""
        stripped = line.strip()
        ext = filepath.suffix.lower()
        if ext in ('.py',) and stripped.startswith('#'):
            return True
        if ext in ('.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs') and stripped.startswith('//'):
            return True
        return False

    def scan_file_inventory(self):
        """Inventory all files, flag suspicious types."""
        if not self.skill_path.exists():
            self._add_finding("inventory", "CRITICAL", str(self.skill_path), 0, "Skill directory does not exist")
            return

        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir():
                continue
            rel = fp.relative_to(self.skill_path)
            try:
                size = fp.stat().st_size
            except OSError:
                size = -1

            entry = {
                "path": str(rel),
                "size": size,
                "extension": fp.suffix.lower(),
                "sha256": "",
            }

            # Hash small files
            if 0 < size < 10_000_000:
                try:
                    entry["sha256"] = hashlib.sha256(fp.read_bytes()).hexdigest()
                except OSError:
                    pass

            self.file_inventory.append(entry)

            # Flag suspicious extensions
            if fp.suffix.lower() in SUSPICIOUS_EXTENSIONS:
                self._add_finding("inventory", "CRITICAL", str(rel), 0,
                                  f"Suspicious binary/executable file type: {fp.suffix}")
            elif fp.suffix.lower() in SUSPICIOUS_SHELL_EXTENSIONS:
                self._add_finding("inventory", "MEDIUM", str(rel), 0,
                                  f"Shell script found: {fp.name} — review contents")

            # Flag very large files
            if size > 5_000_000:
                self._add_finding("inventory", "MEDIUM", str(rel), 0,
                                  f"Large file ({size / 1_000_000:.1f} MB) — unusual for a skill")

    def scan_code_patterns(self):
        """Scan all text files for dangerous patterns."""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.sh', '.bash', '.zsh',
            '.rb', '.pl', '.php', '.go', '.rs', '.java', '.c', '.cpp', '.h',
            '.md', '.txt', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini',
            '.html', '.css', '.xml', '.sql', '.r', '.lua', '.swift', '.kt',
            '', # no extension
        }

        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir():
                continue
            if fp.suffix.lower() not in text_extensions and fp.suffix != '':
                continue
            rel = fp.relative_to(self.skill_path)

            try:
                content = fp.read_text(errors='replace')
            except (OSError, UnicodeDecodeError):
                continue

            is_doc = self._is_reference_or_doc(rel)
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for category, info in DANGEROUS_PATTERNS.items():
                    base_severity = info["severity"]
                    for pattern, desc in info["patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Reduce severity for documentation/reference files
                            # unless it's prompt injection (those are suspicious even in docs)
                            severity = base_severity
                            if is_doc and category not in ("prompt_injection",):
                                # Drop one level for doc references
                                idx = max(0, self.severity_order.index(base_severity) - 2)
                                severity = self.severity_order[idx]

                            # Reduce severity for comment lines in code
                            if self._is_comment_line(line, fp) and category not in ("prompt_injection",):
                                idx = max(0, self.severity_order.index(severity) - 1)
                                severity = self.severity_order[idx]

                            self._add_finding(category, severity, str(rel), line_num, desc, line)

    def scan_dependencies(self):
        """Check requirements.txt and package.json for suspicious packages."""
        req_file = self.skill_path / "requirements.txt"
        if req_file.exists():
            try:
                for line_num, line in enumerate(req_file.read_text().split('\n'), 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    pkg = re.split(r'[>=<!~\[]', line)[0].strip().lower()
                    if pkg in KNOWN_MALICIOUS_PACKAGES:
                        self._add_finding("dependencies", "CRITICAL", "requirements.txt", line_num,
                                          f"Known malicious package: {pkg}", line)
                    else:
                        # Check for typosquatting
                        for legit in LEGIT_PACKAGES:
                            if pkg != legit and _levenshtein_close(pkg, legit):
                                self._add_finding("dependencies", "HIGH", "requirements.txt", line_num,
                                                  f"Possible typosquat of '{legit}': {pkg}", line)
                        # Flag all deps as LOW for awareness
                        self._add_finding("dependencies", "LOW", "requirements.txt", line_num,
                                          f"External dependency: {pkg}", line)
            except OSError:
                pass

        pkg_file = self.skill_path / "package.json"
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text())
                for dep_type in ("dependencies", "devDependencies"):
                    deps = data.get(dep_type, {})
                    for pkg, ver in deps.items():
                        pkg_lower = pkg.lower()
                        if pkg_lower in KNOWN_MALICIOUS_PACKAGES:
                            self._add_finding("dependencies", "CRITICAL", "package.json", 0,
                                              f"Known malicious package: {pkg}")
                        # Check for install scripts
                if "scripts" in data:
                    for script_name, script_cmd in data["scripts"].items():
                        if script_name in ("preinstall", "postinstall", "install"):
                            self._add_finding("dependencies", "HIGH", "package.json", 0,
                                              f"Install hook script '{script_name}': {script_cmd[:100]}")
            except (OSError, json.JSONDecodeError):
                pass

    def scan_skill_md(self):
        """Specifically analyze SKILL.md for prompt injection."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self._add_finding("skill_md", "MEDIUM", "SKILL.md", 0, "No SKILL.md found — unusual for a skill")
            return

        try:
            content = skill_md.read_text(errors='replace')
        except OSError:
            return

        lines = content.split('\n')

        # Check for prompt injection patterns (already covered in code scan, but
        # we do a more targeted pass here with CRITICAL severity since SKILL.md
        # is loaded directly into the LLM context)
        for line_num, line in enumerate(lines, 1):
            for pattern, desc in DANGEROUS_PATTERNS["prompt_injection"]["patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_finding("skill_md_injection", "CRITICAL", "SKILL.md", line_num,
                                      f"SKILL.md prompt injection: {desc}", line)

        # Check for hidden instructions using zero-width chars
        if re.search(r'[\u200b\u200c\u200d\u2060\ufeff]', content):
            self._add_finding("skill_md_injection", "CRITICAL", "SKILL.md", 0,
                              "Zero-width characters detected (hidden text injection)")

        # Check for encoded content in SKILL.md
        if re.search(r'[A-Za-z0-9+/]{60,}={0,2}', content):
            self._add_finding("skill_md_injection", "HIGH", "SKILL.md", 0,
                              "Long base64-like string in SKILL.md")

    def scan_permissions(self):
        """Identify what tools/capabilities the skill requests."""
        skill_md = self.skill_path / "SKILL.md"
        permissions = []
        if skill_md.exists():
            try:
                content = skill_md.read_text(errors='replace').lower()
                tool_keywords = {
                    "exec": "shell execution",
                    "browser": "browser control",
                    "web_fetch": "web fetching",
                    "web_search": "web search",
                    "message": "messaging",
                    "nodes": "node control",
                    "camera": "camera access",
                    "ssh": "SSH access",
                    "docker": "Docker access",
                    "sudo": "sudo/root",
                    "cron": "scheduled tasks",
                }
                for keyword, desc in tool_keywords.items():
                    if keyword in content:
                        permissions.append({"tool": keyword, "description": desc})
            except OSError:
                pass
        return permissions

    def run_audit(self) -> dict:
        """Run the complete audit and return the report."""
        self.scan_file_inventory()
        self.scan_code_patterns()
        self.scan_dependencies()
        self.scan_skill_md()
        permissions = self.scan_permissions()

        # Deduplicate findings (same file+line+description)
        seen = set()
        unique_findings = []
        for f in self.findings:
            key = (f["file"], f["line"], f["description"])
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)
        self.findings = unique_findings

        # Recalculate risk from unique findings
        self.risk_score = "CLEAN"
        for f in self.findings:
            self._bump_severity(f["severity"])

        # Build summary counts
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        for f in self.findings:
            severity_counts[f["severity"]] += 1
            category_counts[f["category"]] += 1

        report = {
            "skill_path": str(self.skill_path),
            "risk_score": self.risk_score,
            "total_findings": len(self.findings),
            "severity_counts": dict(severity_counts),
            "category_counts": dict(category_counts),
            "file_inventory": self.file_inventory,
            "permissions_requested": permissions,
            "findings": self.findings,
        }
        return report


def _levenshtein_close(a: str, b: str) -> bool:
    """Check if two strings are within edit distance 2 (simple typosquat check)."""
    if abs(len(a) - len(b)) > 2:
        return False
    # Simple character-level check
    diffs = 0
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            diffs += 1
    diffs += abs(len(a) - len(b))
    return 0 < diffs <= 2


def format_human_report(report: dict) -> str:
    """Format a human-readable report."""
    lines = []
    rs = report["risk_score"]
    emoji = {"CLEAN": "✅", "LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(rs, "❓")

    lines.append(f"\n{'='*60}")
    lines.append(f"  SKILL AUDIT REPORT  {emoji} {rs}")
    lines.append(f"{'='*60}")
    lines.append(f"  Path: {report['skill_path']}")
    lines.append(f"  Files: {len(report['file_inventory'])}")
    lines.append(f"  Findings: {report['total_findings']}")
    lines.append(f"{'='*60}\n")

    if report["severity_counts"]:
        lines.append("  Severity Breakdown:")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "CLEAN"]:
            count = report["severity_counts"].get(sev, 0)
            if count:
                lines.append(f"    {sev}: {count}")
        lines.append("")

    if report["permissions_requested"]:
        lines.append("  Permissions Requested:")
        for p in report["permissions_requested"]:
            lines.append(f"    • {p['tool']} — {p['description']}")
        lines.append("")

    # Show HIGH and CRITICAL findings in detail
    critical_findings = [f for f in report["findings"] if f["severity"] in ("CRITICAL", "HIGH")]
    if critical_findings:
        lines.append("  ⚠️  HIGH/CRITICAL FINDINGS:")
        lines.append(f"  {'-'*56}")
        for f in critical_findings:
            lines.append(f"  [{f['severity']}] {f['category']}")
            lines.append(f"    File: {f['file']}:{f['line']}")
            lines.append(f"    {f['description']}")
            if f.get("content"):
                lines.append(f"    > {f['content'][:120]}")
            lines.append("")

    # Summarize MEDIUM/LOW
    medium = [f for f in report["findings"] if f["severity"] == "MEDIUM"]
    if medium:
        lines.append(f"  ⚡ MEDIUM findings: {len(medium)}")
        for f in medium[:10]:
            lines.append(f"    • {f['file']}:{f['line']} — {f['description']}")
        if len(medium) > 10:
            lines.append(f"    ... and {len(medium)-10} more")
        lines.append("")

    low = [f for f in report["findings"] if f["severity"] == "LOW"]
    if low:
        lines.append(f"  ℹ️  LOW findings: {len(low)} (informational)")
        lines.append("")

    # Verdict
    lines.append(f"{'='*60}")
    if rs in ("CLEAN", "LOW"):
        lines.append("  ✅ VERDICT: Safe to install")
    elif rs == "MEDIUM":
        lines.append("  ⚠️  VERDICT: Manual review required before installation")
    else:
        lines.append("  🚫 VERDICT: BLOCKED — Do not install")
    lines.append(f"{'='*60}\n")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: audit_skill.py <skill_directory> [--human] [--json]", file=sys.stderr)
        sys.exit(2)

    skill_path = sys.argv[1]
    flags = set(sys.argv[2:])
    show_human = "--human" in flags or "--json" not in flags
    show_json = "--json" in flags

    auditor = SkillAuditor(skill_path)
    report = auditor.run_audit()

    if show_json:
        print(json.dumps(report, indent=2))

    if show_human:
        print(format_human_report(report))

    # Exit code
    rs = report["risk_score"]
    if rs in ("CLEAN", "LOW"):
        sys.exit(0)
    elif rs == "MEDIUM":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

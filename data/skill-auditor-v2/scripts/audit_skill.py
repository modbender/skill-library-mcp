#!/usr/bin/env python3
"""
Skill Auditor v2.0 — Merged security scanner for OpenClaw skills.
Zero external dependencies (stdlib only).

Combines:
- 8-category static analysis with SHA256 inventory & typosquat detection
- Base64/hex deobfuscation layer (re-scans decoded content)
- 0-100 numeric risk scoring with MITRE ATT&CK IDs
- IoC database (malicious IPs, domains, social engineering keywords)
- Social engineering detection (urgency, false authority, fear)
- Whitelist system (safe binaries/domains reduce score)
- Zero-width character detection & comment-context severity reduction
- clawhub inspect integration (--slug for remote fetch)

Usage:
    python3 audit_skill.py /path/to/skill [--human] [--json]
    python3 audit_skill.py --slug skill-name [--human] [--json]

Exit codes: 0=safe (score 0-20), 1=review (21-60), 2=dangerous (61-100)
"""

import os
import re
import sys
import json
import hashlib
import base64
import subprocess
import tempfile
import shutil
from pathlib import Path
from collections import defaultdict

# ─── IoC Database (inline, also loadable from ioc-database.json) ──────

IOC_IPS = {"91.92.242.30"}

IOC_DOMAINS = {
    "glot.io", "webhook.site", "pastebin.com", "hastebin.com", "ghostbin.com",
    "ngrok.io", "pipedream.net", "requestbin.com", "burpcollaborator.net",
}

SAFE_DOMAINS = {
    "github.com", "npmjs.org", "pypi.org", "crates.io", "anthropic.com",
    "openclaw.ai", "clawhub.ai", "hub.docker.com", "stackoverflow.com",
}

SAFE_BINARIES = {
    "git", "gh", "docker", "kubectl", "npm", "node", "python", "python3",
    "pip", "pip3", "cargo", "go", "curl", "wget", "jq", "sed", "awk",
    "grep", "find", "cat", "echo", "ls", "mkdir", "cp", "mv",
}

SOCIAL_ENGINEERING_URGENCY = [
    (r'\b(install immediately|urgent|limited time|act now|hurry)\b', "Urgency language"),
]

SOCIAL_ENGINEERING_AUTHORITY = [
    (r'\b(official openclaw|verified by anthropic|endorsed by|approved by)\b', "False authority claim"),
]

SOCIAL_ENGINEERING_FEAR = [
    (r'(security risk|vulnerability|exploit|hack|breach).*without this', "Fear tactic"),
]

SOCIAL_ENGINEERING_LURES = [
    (r'\b(OpenClawDriver|ClawdBot[\.\s]*Driver|Required[\.\s]*Driver|install[\.\s]*driver|download[\.\s]*driver)\b',
     "Social engineering lure (fake driver)"),
]

# ─── Scoring Thresholds ───────────────────────────────────────────────

SCORE_MAP = {
    "CRITICAL": 15,
    "HIGH": 8,
    "MEDIUM": 3,
    "LOW": 1,
}

SCORING_THRESHOLDS = {
    "safe": 20,
    "low_risk": 40,
    "medium_risk": 60,
    "high_risk": 80,
    "critical": 100,
}

# ─── Pattern Definitions with MITRE ATT&CK ───────────────────────────

DANGEROUS_PATTERNS = {
    "shell_execution": {
        "severity": "HIGH",
        "mitre": "T1059 - Command and Scripting Interpreter",
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
            (r'(curl|wget).*\|.*(bash|sh|zsh|python)', "Remote script execution (curl/wget piped to shell)"),
        ],
    },
    "network_calls": {
        "severity": "HIGH",
        "mitre": "T1071 - Application Layer Protocol",
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
        "mitre": "T1552.001 - Unsecured Credentials: Credentials In Files",
        "patterns": [
            (r'\bos\.environ', "os.environ access"),
            (r'\bos\.getenv\s*\(', "os.getenv() call"),
            (r'\bprocess\.env\b', "process.env access"),
            (r'\bdotenv\b', "dotenv usage"),
            (r'\bload_dotenv\b', "load_dotenv() call"),
            (r'(?:OPENAI|ANTHROPIC|CLAUDE|OPENROUTER|AWS|AZURE|GCP|GITHUB|TELEGRAM|DISCORD|SLACK|STRIPE|TWILIO)_(?:API_?)?(?:KEY|TOKEN|SECRET)',
             "API key variable reference"),
            (r'(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*[\'"][A-Za-z0-9+/=]{20,}[\'"]',
             "Hardcoded credentials"),
        ],
    },
    "filesystem_escape": {
        "severity": "CRITICAL",
        "mitre": "T1083 - File and Directory Discovery",
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
            (r'~/.openclaw|~/.clawdbot|\$HOME/.openclaw|\$HOME/.clawdbot',
             "OpenClaw config directory access"),
        ],
    },
    "encoding_obfuscation": {
        "severity": "HIGH",
        "mitre": "T1027 - Obfuscated Files or Information",
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
        "mitre": "T1059.006 - Command and Scripting Interpreter: Python (prompt context)",
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
        "mitre": "T1041 - Exfiltration Over C2 Channel",
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
        "mitre": "T1005 - Data from Local System",
        "patterns": [
            (r'(?:seed|mnemonic)\s*(?:phrase|words?)', "seed/mnemonic phrase reference"),
            (r'(?:private|secret)\s*key', "private key reference"),
            (r'wallet\.dat', "wallet.dat file access"),
            (r'\.(?:keystore|wallet)\b', "keystore/wallet file access"),
            (r'ethers|web3|solana|bitcoin', "crypto library usage"),
            (r'\.bitcoin|\.ethereum|metamask', "cryptocurrency wallet path"),
        ],
    },
    "dynamic_imports": {
        "severity": "HIGH",
        "mitre": "T1129 - Shared Modules",
        "patterns": [
            (r'__import__\s*\(', "__import__() call"),
            (r'\bimportlib\b', "importlib usage"),
            (r'\bimport_module\s*\(', "import_module() call"),
            (r'getattr\s*\(\s*__builtins__', "getattr on __builtins__"),
            (r'globals\s*\(\s*\)\s*\[', "globals() dict access"),
            (r'__builtins__\s*\[', "__builtins__ dict access"),
        ],
    },
    "browser_credentials": {
        "severity": "HIGH",
        "mitre": "T1555.003 - Credentials from Web Browsers",
        "patterns": [
            (r'Cookies|Login Data|Web Data', "Browser credential storage access"),
            (r'chrome/Default|firefox/profiles', "Browser profile path access"),
        ],
    },
    "fake_prerequisites": {
        "severity": "CRITICAL",
        "mitre": "T1204.002 - User Execution: Malicious File",
        "patterns": [
            (r'(prerequisite|setup|installation).*download.*(openclaw-agent|openclaw-setup)\.(zip|exe|dmg)',
             "ClawHavoc campaign: fake prerequisite download"),
            (r'download.*\.(exe|dmg|pkg|deb|rpm|msi)', "Suspicious binary download request"),
        ],
    },
}

# File types
SUSPICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.com', '.bat', '.cmd',
    '.ps1', '.vbs', '.wsf', '.scr', '.pif', '.msi', '.jar', '.war',
    '.elf', '.deb', '.rpm', '.apk',
}
SUSPICIOUS_SHELL_EXTENSIONS = {'.sh', '.bash', '.zsh', '.fish'}

TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.sh', '.bash', '.zsh',
    '.rb', '.pl', '.php', '.go', '.rs', '.java', '.c', '.cpp', '.h',
    '.md', '.txt', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini',
    '.html', '.css', '.xml', '.sql', '.r', '.lua', '.swift', '.kt', '',
}

KNOWN_MALICIOUS_PACKAGES = {
    "event-stream", "flatmap-stream", "ua-parser-js-malicious",
    "colors-malicious", "faker-malicious", "node-ipc-malicious",
    "python3-dateutil", "jeIlyfish", "python-sqlite",
    "colourfull", "requestss", "beautifulsoup",
    "nmap-python", "openai-python", "python-openai",
}

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
        self.numeric_score = 0
        self.whitelist_reduction = 0
        self.severity_order = ["CLEAN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def _add_finding(self, category: str, severity: str, file: str, line_num: int,
                     description: str, line_content: str = "", mitre: str = ""):
        self.findings.append({
            "category": category,
            "severity": severity,
            "file": str(file),
            "line": line_num,
            "description": description,
            "content": line_content.strip()[:200] if line_content else "",
            "mitre": mitre,
        })
        self.numeric_score += SCORE_MAP.get(severity, 0)

    def _is_reference_or_doc(self, filepath: Path) -> bool:
        rel = str(filepath)
        return any(x in rel.lower() for x in ['reference', 'docs/', 'doc/', 'readme', 'changelog', 'license', '.md'])

    def _is_comment_line(self, line: str, filepath: Path) -> bool:
        stripped = line.strip()
        ext = filepath.suffix.lower()
        if ext in ('.py',) and stripped.startswith('#'):
            return True
        if ext in ('.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs') and stripped.startswith('//'):
            return True
        if ext in ('.sh', '.bash', '.zsh') and stripped.startswith('#'):
            return True
        return False

    # ─── Scan Phases ───

    def scan_file_inventory(self):
        if not self.skill_path.exists():
            self._add_finding("inventory", "CRITICAL", str(self.skill_path), 0,
                              "Skill directory does not exist")
            return
        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir():
                continue
            rel = fp.relative_to(self.skill_path)
            try:
                size = fp.stat().st_size
            except OSError:
                size = -1
            entry = {"path": str(rel), "size": size, "extension": fp.suffix.lower(), "sha256": ""}
            if 0 < size < 10_000_000:
                try:
                    entry["sha256"] = hashlib.sha256(fp.read_bytes()).hexdigest()
                except OSError:
                    pass
            self.file_inventory.append(entry)
            if fp.suffix.lower() in SUSPICIOUS_EXTENSIONS:
                self._add_finding("inventory", "CRITICAL", str(rel), 0,
                                  f"Suspicious binary/executable: {fp.suffix}",
                                  mitre="T1204.002 - User Execution: Malicious File")
            elif fp.suffix.lower() in SUSPICIOUS_SHELL_EXTENSIONS:
                self._add_finding("inventory", "MEDIUM", str(rel), 0,
                                  f"Shell script: {fp.name} — review contents")
            if size > 5_000_000:
                self._add_finding("inventory", "MEDIUM", str(rel), 0,
                                  f"Large file ({size / 1_000_000:.1f} MB)")

    def scan_code_patterns(self):
        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir() or (fp.suffix.lower() not in TEXT_EXTENSIONS and fp.suffix != ''):
                continue
            rel = fp.relative_to(self.skill_path)
            try:
                content = fp.read_text(errors='replace')
            except (OSError, UnicodeDecodeError):
                continue
            is_doc = self._is_reference_or_doc(rel)
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # IoC checks: malicious IPs
                for ip in IOC_IPS:
                    if ip in line:
                        self._add_finding("ioc", "CRITICAL", str(rel), line_num,
                                          f"Known C2 server IP: {ip}", line,
                                          mitre="T1071 - Application Layer Protocol")
                # IoC checks: malicious domains
                for domain in IOC_DOMAINS:
                    if domain in line.lower():
                        # Check if it's in a safe context (e.g., documentation warning)
                        sev = "HIGH" if not is_doc else "MEDIUM"
                        self._add_finding("ioc", sev, str(rel), line_num,
                                          f"Suspicious domain: {domain}", line,
                                          mitre="T1071 - Application Layer Protocol")
                # Pattern scan
                for category, info in DANGEROUS_PATTERNS.items():
                    base_severity = info["severity"]
                    mitre = info.get("mitre", "")
                    for pattern, desc in info["patterns"]:
                        if re.search(pattern, line, re.IGNORECASE):
                            severity = base_severity
                            if is_doc and category not in ("prompt_injection",):
                                idx = max(0, self.severity_order.index(base_severity) - 2)
                                severity = self.severity_order[idx]
                            if self._is_comment_line(line, fp) and category not in ("prompt_injection",):
                                idx = max(0, self.severity_order.index(severity) - 1)
                                severity = self.severity_order[idx]
                            self._add_finding(category, severity, str(rel), line_num, desc, line, mitre)

    def scan_social_engineering(self):
        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir() or fp.suffix.lower() not in ('.md', '.txt', '.html', ''):
                continue
            rel = fp.relative_to(self.skill_path)
            try:
                content = fp.read_text(errors='replace')
            except (OSError, UnicodeDecodeError):
                continue
            lines = content.split('\n')
            all_se = [
                (SOCIAL_ENGINEERING_URGENCY, "social_engineering", "MEDIUM", "Urgency tactic"),
                (SOCIAL_ENGINEERING_AUTHORITY, "social_engineering", "HIGH", "False authority"),
                (SOCIAL_ENGINEERING_FEAR, "social_engineering", "MEDIUM", "Fear tactic"),
                (SOCIAL_ENGINEERING_LURES, "social_engineering", "HIGH", "Social engineering lure"),
            ]
            for line_num, line in enumerate(lines, 1):
                for patterns, cat, sev, label in all_se:
                    for pattern, desc in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self._add_finding(cat, sev, str(rel), line_num,
                                              f"{label}: {desc}", line,
                                              mitre="T1566 - Phishing")

    def scan_deobfuscation(self):
        """L2: Extract base64/hex strings, decode them, re-scan decoded content."""
        b64_pattern = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
        hex_pattern = re.compile(r'(?:\\x[0-9a-fA-F]{2}){4,}')

        for fp in sorted(self.skill_path.rglob('*')):
            if fp.is_dir() or fp.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            rel = fp.relative_to(self.skill_path)
            try:
                content = fp.read_text(errors='replace')
            except (OSError, UnicodeDecodeError):
                continue
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Base64 decode
                for match in b64_pattern.finditer(line):
                    b64str = match.group()
                    try:
                        decoded = base64.b64decode(b64str).decode('utf-8', errors='replace')
                        if re.search(r'(curl|wget|bash|sh\b|eval|exec|/bin/|https?://)', decoded, re.IGNORECASE):
                            self._add_finding("deobfuscation", "CRITICAL", str(rel), line_num,
                                              f"Base64-decoded hidden command: {decoded[:100]}", line,
                                              mitre="T1027 - Obfuscated Files or Information")
                        for ip in IOC_IPS:
                            if ip in decoded:
                                self._add_finding("deobfuscation", "CRITICAL", str(rel), line_num,
                                                  f"Base64-decoded C2 IP: {ip}", line,
                                                  mitre="T1071 - Application Layer Protocol")
                    except Exception:
                        pass
                # Hex decode
                for match in hex_pattern.finditer(line):
                    hex_str = match.group()
                    try:
                        decoded = bytes(int(h, 16) for h in re.findall(r'\\x([0-9a-fA-F]{2})', hex_str)).decode('utf-8', errors='replace')
                        if re.search(r'(curl|wget|bash|eval|exec)', decoded, re.IGNORECASE):
                            self._add_finding("deobfuscation", "CRITICAL", str(rel), line_num,
                                              f"Hex-decoded hidden command: {decoded[:100]}", line,
                                              mitre="T1027 - Obfuscated Files or Information")
                    except Exception:
                        pass

    def scan_dependencies(self):
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
                                          f"Known malicious package: {pkg}", line,
                                          mitre="T1195.001 - Supply Chain Compromise")
                    else:
                        for legit in LEGIT_PACKAGES:
                            if pkg != legit and _levenshtein_close(pkg, legit):
                                self._add_finding("dependencies", "HIGH", "requirements.txt", line_num,
                                                  f"Possible typosquat of '{legit}': {pkg}", line,
                                                  mitre="T1195.001 - Supply Chain Compromise")
                        self._add_finding("dependencies", "LOW", "requirements.txt", line_num,
                                          f"External dependency: {pkg}", line)
            except OSError:
                pass

        pkg_file = self.skill_path / "package.json"
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text())
                for dep_type in ("dependencies", "devDependencies"):
                    for pkg in data.get(dep_type, {}):
                        if pkg.lower() in KNOWN_MALICIOUS_PACKAGES:
                            self._add_finding("dependencies", "CRITICAL", "package.json", 0,
                                              f"Known malicious package: {pkg}",
                                              mitre="T1195.001 - Supply Chain Compromise")
                if "scripts" in data:
                    for name, cmd in data["scripts"].items():
                        if name in ("preinstall", "postinstall", "install"):
                            self._add_finding("dependencies", "HIGH", "package.json", 0,
                                              f"Install hook '{name}': {str(cmd)[:100]}",
                                              mitre="T1195.002 - Compromise Software Supply Chain")
            except (OSError, json.JSONDecodeError):
                pass

    def scan_skill_md(self):
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self._add_finding("skill_md", "MEDIUM", "SKILL.md", 0, "No SKILL.md found")
            return
        try:
            content = skill_md.read_text(errors='replace')
        except OSError:
            return
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, desc in DANGEROUS_PATTERNS["prompt_injection"]["patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_finding("skill_md_injection", "CRITICAL", "SKILL.md", line_num,
                                      f"SKILL.md prompt injection: {desc}", line,
                                      mitre="T1059.006 - Prompt Injection")
        # Zero-width characters
        if re.search(r'[\u200b\u200c\u200d\u2060\ufeff]', content):
            self._add_finding("skill_md_injection", "CRITICAL", "SKILL.md", 0,
                              "Zero-width characters detected (hidden text injection)",
                              mitre="T1027 - Obfuscated Files or Information")
        # Long base64 in SKILL.md
        if re.search(r'[A-Za-z0-9+/]{60,}={0,2}', content):
            self._add_finding("skill_md_injection", "HIGH", "SKILL.md", 0,
                              "Long base64-like string in SKILL.md",
                              mitre="T1027 - Obfuscated Files or Information")

    def scan_permissions(self):
        skill_md = self.skill_path / "SKILL.md"
        permissions = []
        if skill_md.exists():
            try:
                content = skill_md.read_text(errors='replace').lower()
                tool_keywords = {
                    "exec": "shell execution", "browser": "browser control",
                    "web_fetch": "web fetching", "web_search": "web search",
                    "message": "messaging", "nodes": "node control",
                    "camera": "camera access", "ssh": "SSH access",
                    "docker": "Docker access", "sudo": "sudo/root",
                    "cron": "scheduled tasks",
                }
                for keyword, desc in tool_keywords.items():
                    if keyword in content:
                        permissions.append({"tool": keyword, "description": desc})
            except OSError:
                pass
        return permissions

    def apply_whitelist_reduction(self):
        """Reduce score for skills that reference safe binaries/domains."""
        all_content = ""
        for fp in self.skill_path.rglob('*'):
            if fp.is_dir() or fp.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                all_content += fp.read_text(errors='replace').lower() + "\n"
            except (OSError, UnicodeDecodeError):
                continue
        reduction = 0
        for domain in SAFE_DOMAINS:
            if domain in all_content:
                reduction += 1
        for binary in SAFE_BINARIES:
            if re.search(rf'\b{re.escape(binary)}\b', all_content):
                reduction += 0.5
        self.whitelist_reduction = min(int(reduction), 15)  # Cap at 15
        self.numeric_score = max(0, self.numeric_score - self.whitelist_reduction)

    def run_audit(self) -> dict:
        self.scan_file_inventory()
        self.scan_code_patterns()
        self.scan_social_engineering()
        self.scan_deobfuscation()
        self.scan_dependencies()
        self.scan_skill_md()
        permissions = self.scan_permissions()

        # Deduplicate
        seen = set()
        unique = []
        for f in self.findings:
            key = (f["file"], f["line"], f["description"])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        self.findings = unique

        # Recalculate score from unique findings
        self.numeric_score = 0
        for f in self.findings:
            self.numeric_score += SCORE_MAP.get(f["severity"], 0)

        self.apply_whitelist_reduction()
        self.numeric_score = min(self.numeric_score, 100)

        # Determine risk level
        if self.numeric_score <= SCORING_THRESHOLDS["safe"]:
            risk_level = "SAFE"
        elif self.numeric_score <= SCORING_THRESHOLDS["low_risk"]:
            risk_level = "LOW_RISK"
        elif self.numeric_score <= SCORING_THRESHOLDS["medium_risk"]:
            risk_level = "MEDIUM_RISK"
        elif self.numeric_score <= SCORING_THRESHOLDS["high_risk"]:
            risk_level = "HIGH_RISK"
        else:
            risk_level = "CRITICAL"

        # Legacy risk_score field
        max_sev = "CLEAN"
        for f in self.findings:
            if self.severity_order.index(f["severity"]) > self.severity_order.index(max_sev):
                max_sev = f["severity"]

        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        for f in self.findings:
            severity_counts[f["severity"]] += 1
            category_counts[f["category"]] += 1

        return {
            "skill_path": str(self.skill_path),
            "numeric_score": self.numeric_score,
            "risk_level": risk_level,
            "risk_score": max_sev,
            "whitelist_reduction": self.whitelist_reduction,
            "total_findings": len(self.findings),
            "severity_counts": dict(severity_counts),
            "category_counts": dict(category_counts),
            "file_inventory": self.file_inventory,
            "permissions_requested": permissions,
            "findings": self.findings,
        }


def _levenshtein_close(a: str, b: str) -> bool:
    if abs(len(a) - len(b)) > 2:
        return False
    diffs = sum(1 for i in range(min(len(a), len(b))) if a[i] != b[i])
    diffs += abs(len(a) - len(b))
    return 0 < diffs <= 2


def format_human_report(report: dict) -> str:
    lines = []
    score = report["numeric_score"]
    level = report["risk_level"]
    emoji_map = {"SAFE": "✅", "LOW_RISK": "🟢", "MEDIUM_RISK": "🟡", "HIGH_RISK": "🟠", "CRITICAL": "🔴"}
    emoji = emoji_map.get(level, "❓")

    lines.append(f"\n{'='*60}")
    lines.append(f"  SKILL AUDIT REPORT  {emoji} {level}  (Score: {score}/100)")
    lines.append(f"{'='*60}")
    lines.append(f"  Path: {report['skill_path']}")
    lines.append(f"  Files: {len(report['file_inventory'])}")
    lines.append(f"  Findings: {report['total_findings']}")
    if report.get('whitelist_reduction'):
        lines.append(f"  Whitelist reduction: -{report['whitelist_reduction']} points")
    lines.append(f"{'='*60}\n")

    if report["severity_counts"]:
        lines.append("  Severity Breakdown:")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = report["severity_counts"].get(sev, 0)
            if count:
                lines.append(f"    {sev}: {count}")
        lines.append("")

    if report["permissions_requested"]:
        lines.append("  Permissions Requested:")
        for p in report["permissions_requested"]:
            lines.append(f"    • {p['tool']} — {p['description']}")
        lines.append("")

    critical_findings = [f for f in report["findings"] if f["severity"] in ("CRITICAL", "HIGH")]
    if critical_findings:
        lines.append("  ⚠️  HIGH/CRITICAL FINDINGS:")
        lines.append(f"  {'-'*56}")
        for f in critical_findings:
            mitre_str = f" [{f['mitre']}]" if f.get('mitre') else ""
            lines.append(f"  [{f['severity']}] {f['category']}{mitre_str}")
            lines.append(f"    File: {f['file']}:{f['line']}")
            lines.append(f"    {f['description']}")
            if f.get("content"):
                lines.append(f"    > {f['content'][:120]}")
            lines.append("")

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

    lines.append(f"{'='*60}")
    if score <= 20:
        lines.append("  ✅ VERDICT: Safe to install")
    elif score <= 60:
        lines.append("  ⚠️  VERDICT: Manual review recommended")
    else:
        lines.append("  🚫 VERDICT: BLOCKED — Do not install")
    lines.append(f"{'='*60}\n")

    return "\n".join(lines)


def fetch_slug(slug: str) -> str:
    """Use clawhub inspect to fetch a skill by slug, return temp dir path."""
    temp_dir = tempfile.mkdtemp(prefix=f"skill-audit-{slug}-")
    try:
        subprocess.run(
            ["clawhub", "inspect", slug, "--dir", temp_dir],
            check=True, capture_output=True, text=True
        )
    except FileNotFoundError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Error: clawhub CLI not found. Install it or use a local path.", file=sys.stderr)
        sys.exit(2)
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"Error fetching slug '{slug}': {e.stderr}", file=sys.stderr)
        sys.exit(2)
    # clawhub inspect puts files in temp_dir/slug or temp_dir directly
    slug_dir = os.path.join(temp_dir, slug)
    if os.path.isdir(slug_dir):
        return slug_dir
    return temp_dir


def main():
    if len(sys.argv) < 2:
        print("Usage: audit_skill.py <skill_directory> [--human] [--json]", file=sys.stderr)
        print("       audit_skill.py --slug <skill-name> [--human] [--json]", file=sys.stderr)
        sys.exit(2)

    args = sys.argv[1:]
    flags = set()
    positional = []
    slug = None
    i = 0
    while i < len(args):
        if args[i] == "--slug" and i + 1 < len(args):
            slug = args[i + 1]
            i += 2
        elif args[i].startswith("--"):
            flags.add(args[i])
            i += 1
        else:
            positional.append(args[i])
            i += 1

    cleanup_dir = None
    if slug:
        skill_path = fetch_slug(slug)
        cleanup_dir = skill_path
    elif positional:
        skill_path = positional[0]
    else:
        print("Error: provide a skill directory or --slug", file=sys.stderr)
        sys.exit(2)

    show_human = "--human" in flags or "--json" not in flags
    show_json = "--json" in flags

    # Try to load external IoC database
    ioc_path = Path(__file__).parent.parent / "references" / "ioc-database.json"
    if ioc_path.exists():
        try:
            ioc_data = json.loads(ioc_path.read_text())
            for ip in ioc_data.get("malicious_ips", []):
                IOC_IPS.add(ip)
            for d in ioc_data.get("malicious_domains", []):
                IOC_DOMAINS.add(d)
        except (json.JSONDecodeError, OSError):
            pass

    auditor = SkillAuditor(skill_path)
    report = auditor.run_audit()

    if show_json:
        print(json.dumps(report, indent=2))
    if show_human:
        print(format_human_report(report))

    # Cleanup temp dir from slug fetch
    if cleanup_dir:
        shutil.rmtree(cleanup_dir, ignore_errors=True)

    # Exit code based on numeric score
    score = report["numeric_score"]
    if score <= 20:
        sys.exit(0)
    elif score <= 60:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

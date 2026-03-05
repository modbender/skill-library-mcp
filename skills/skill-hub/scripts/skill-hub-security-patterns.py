#!/usr/bin/env python3
"""Security patterns and scanner for skill vetting.

Contains all regex patterns for code-level, NLP prompt injection,
and logic weakness checks. Used by skill-hub-vet.py.
"""

import re
from pathlib import Path

# --- Code-level security patterns ---

CODE_PATTERNS = {
    "code_execution": [
        (r"\beval\s*\(", "eval() execution"),
        (r"\bexec\s*\(", "exec() execution"),
        (r"__import__\s*\(", "dynamic imports"),
        (r"compile\s*\(", "code compilation"),
    ],
    "shell_injection": [
        (r"subprocess\.(call|run|Popen).*shell\s*=\s*True", "shell=True subprocess"),
        (r"os\.system\s*\(", "os.system() call"),
        (r"os\.popen\s*\(", "os.popen() call"),
    ],
    "obfuscation": [
        (r"base64\.b64decode", "base64 decoding"),
        (r'codecs\.decode.*[\'"]hex[\'"]', "hex decoding"),
        (r"chr\s*\(\s*\d+\s*\)", "chr() obfuscation"),
    ],
    "network_access": [
        (r"requests\.(get|post|put|delete)\s*\(", "HTTP requests lib"),
        (r"urllib\.request\.urlopen", "urllib requests"),
        (r"socket\.socket\s*\(", "raw sockets"),
        (r"http\.client\.(HTTPConnection|HTTPSConnection)", "http.client usage"),
    ],
    "destructive_ops": [
        (r"os\.remove\s*\(", "file deletion"),
        (r"shutil\.(rmtree|move)", "bulk file ops"),
        (r"pathlib\.Path.*\.unlink\s*\(", "path deletion"),
    ],
    "env_harvesting": [
        (r"os\.environ\[", "env variable access"),
        (r"os\.getenv\s*\(", "env variable reading"),
        (r"subprocess.*env\s*=", "env manipulation in subprocess"),
    ],
    "reverse_shells": [
        (r"nc\s+.*-e", "netcat reverse shell"),
        (r"bash\s+-i\s+.*\/dev\/tcp", "bash reverse shell"),
        (r"\/bin\/sh\s*\|\s*nc", "shell pipe to netcat"),
        (r"python.*socket.*subprocess", "python reverse shell pattern"),
        (r"socket\..*connect.*shell", "socket-based shell"),
        (r"pty\.spawn", "PTY spawn (shell escape)"),
    ],
    "curl_pipe_bash": [
        (r"curl\s+.*\|\s*(ba)?sh", "curl pipe to shell"),
        (r"wget\s+.*\|\s*(ba)?sh", "wget pipe to shell"),
        (r"curl\s+.*>\s*.*\.sh\s*&&", "download and execute script"),
        (r"wget\s+.*&&\s*chmod\s*\+x", "download and make executable"),
    ],
    "persistence": [
        (r"crontab\s+-", "crontab modification"),
        (r"\/etc\/cron", "system cron access"),
        (r"systemctl\s+(enable|start)", "systemd service manipulation"),
        (r"LaunchAgents|LaunchDaemons", "macOS persistence"),
        (r"\.bashrc|\.zshrc|\.profile", "shell profile modification"),
    ],
    "credential_access": [
        (r"\.ssh[/\\]", "SSH key access"),
        (r"\.aws[/\\]", "AWS credentials access"),
        (r"\.openclaw[/\\]credentials", "OpenClaw credentials access"),
        (r"\.clawdbot.*\.env", "ClawdBot .env access"),
        (r"private[_-]?key|privatekey", "private key reference"),
        (r"wallet.*\.dat", "wallet file access"),
        (r"seed\s*phrase|mnemonic", "seed phrase reference"),
        (r"metamask|phantom|ledger", "wallet software reference"),
    ],
    "privilege_escalation": [
        (r"chmod\s+777", "world-writable permissions"),
        (r"setuid|setgid", "setuid/setgid usage"),
        (r"chown\s+root", "chown to root"),
    ],
    "malicious_domains": [
        (r"glot\.io", "glot.io (known malware host)"),
        (r"pastebin\.com\/raw", "pastebin raw (code hosting)"),
        (r"paste\.ee|ghostbin|hastebin", "paste service (code hosting)"),
        (r"ngrok|localtunnel|serveo", "tunnel service usage"),
    ],
    "data_exfiltration_webhooks": [
        (r"discord\.com\/api\/webhooks", "Discord webhook exfiltration"),
        (r"hooks\.slack\.com", "Slack webhook exfiltration"),
    ],
}

# --- NLP / Prompt injection patterns ---

NLP_PATTERNS = {
    "prompt_injection": [
        (r"(?i)ignore\s+(all\s+)?previous\s+instructions?", "ignore previous instructions"),
        (r"(?i)disregard\s+(all\s+)?(prior|previous|above)", "disregard prior instructions"),
        (r"(?i)you\s+are\s+now\s+", "role reassignment attempt"),
        (r"(?i)new\s+instructions?\s*:", "new instructions injection"),
        (r"(?i)forget\s+(everything|all|what)", "memory wipe attempt"),
    ],
    "role_hijacking": [
        (r"(?m)^(system|assistant|user)\s*:", "fake role block"),
        (r"(?i)<\|?(system|assistant|user)\|?>", "role tag injection"),
        (r"(?i)\[INST\]|\[/INST\]", "instruction tag injection"),
    ],
    "invisible_unicode": [
        (r"[\u200b\u200c\u200d\ufeff]", "zero-width characters"),
        (r"[\u202a-\u202e\u2066-\u2069]", "RTL/LTR override characters"),
    ],
    "exfiltration": [
        (r"(?i)send\s+(this|the|all|data|info|content)\s+to\s+", "data exfiltration instruction"),
        (r"(?i)upload\s+(to|this|the|file)", "upload instruction"),
        (r"(?i)(share|leak|exfil)\s+(secret|key|token|password|credential)", "credential exfiltration"),
        (r"https?://[^\s\"']+\.(xyz|tk|ml|ga|cf|gq)/", "suspicious TLD URL"),
    ],
    "authority_escalation": [
        (r"(?i)(?:^|\n)\s*(?:IMPORTANT|CRITICAL|OVERRIDE|URGENT)\s*:", "false urgency pattern"),
        (r"(?i)you\s+must\s+(always|never|immediately)", "coercive instruction"),
        (r"(?i)the\s+user\s+wants\s+you\s+to", "social engineering via user proxy"),
    ],
}

# --- Logic weakness checks ---

LOGIC_CHECKS = [
    ("no_description", r"^---\n(?:(?!description\s*:).)*---", "SKILL.md missing description frontmatter"),
    ("wildcard_import", r"from\s+\S+\s+import\s+\*", "wildcard import (import *)"),
    ("unrestricted_tools", r"allowed-tools\s*:\s*\n\s*-\s*\*", "unrestricted allowed-tools (*)"),
    ("bare_except", r"except\s*:", "bare except clause (no specific exception)"),
]

TEXT_EXTENSIONS = {".py", ".md", ".txt", ".sh", ".bash", ".js", ".json", ".yaml", ".yml", ".toml"}


def scan_file(file_path, relative_path):
    """Scan a single file for all security patterns. Returns list of findings."""
    findings = []
    try:
        content = file_path.read_text(errors="replace")
    except Exception:
        return findings

    is_code = file_path.suffix.lower() in (".py", ".js", ".sh", ".bash")

    # Code patterns (only on code files)
    if is_code:
        for category, patterns in CODE_PATTERNS.items():
            for pattern, description in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_num = content[: match.start()].count("\n") + 1
                    findings.append({
                        "file": str(relative_path),
                        "line": line_num,
                        "category": category,
                        "severity": "CRITICAL" if category in ("reverse_shells", "curl_pipe_bash", "credential_access", "data_exfiltration_webhooks") else "HIGH" if category in ("code_execution", "shell_injection", "persistence", "privilege_escalation", "malicious_domains") else "MEDIUM",
                        "description": description,
                        "match": match.group(0)[:60],
                    })

    # NLP patterns (on all text files, especially markdown)
    for category, patterns in NLP_PATTERNS.items():
        for pattern, description in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_num = content[: match.start()].count("\n") + 1
                findings.append({
                    "file": str(relative_path),
                    "line": line_num,
                    "category": f"nlp_{category}",
                    "severity": "CRITICAL" if category in ("prompt_injection", "exfiltration") else "HIGH",
                    "description": description,
                    "match": match.group(0)[:60],
                })

    # Logic checks (context-dependent)
    for check_name, pattern, description in LOGIC_CHECKS:
        if check_name == "no_description" and file_path.name != "SKILL.md":
            continue
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            line_num = content[: match.start()].count("\n") + 1
            findings.append({
                "file": str(relative_path),
                "line": line_num,
                "category": "logic_weakness",
                "severity": "LOW",
                "description": description,
                "match": match.group(0)[:60],
            })

    return findings


def scan_skill_dir(skill_path):
    """Scan all text files in a skill directory. Returns list of all findings."""
    all_findings = []
    skill_path = Path(skill_path)
    for fpath in skill_path.rglob("*"):
        if fpath.is_file() and (fpath.suffix.lower() in TEXT_EXTENSIONS or fpath.name == "SKILL.md"):
            relative = fpath.relative_to(skill_path)
            all_findings.extend(scan_file(fpath, relative))
    return all_findings


def compute_verdict(findings):
    """Compute PASS/WARN/FAIL verdict and score delta from findings."""
    critical = sum(1 for f in findings if f["severity"] == "CRITICAL")
    high = sum(1 for f in findings if f["severity"] == "HIGH")
    medium = sum(1 for f in findings if f["severity"] == "MEDIUM")

    if critical > 0:
        return "FAIL", -20
    if high >= 3:
        return "FAIL", -20
    if high > 0 or medium >= 3:
        return "WARN", 10
    return "PASS", 25

#!/usr/bin/env python3
"""
skill-shield scanner v0.6.1 — Audit a ClawHub skill for permissions and dangerous patterns.

v0.6.1 changes (batch scan mode):
- Batch scan: --batch flag scans all subdirectories as separate skills
- JSON summary: --json-summary outputs machine-readable batch results
- Performance: skip venv/node_modules/dist directories, cap at 200 files per skill
- Handles 160+ skills in under 60 seconds

v0.5.0 changes (SARIF output):
- SARIF 2.1.0 output format (--sarif flag) for GitHub Code Scanning integration
- Includes rules, results, fingerprints, CWE taxa, and invocation metadata
- Compatible with: GitHub upload-sarif action, VS Code SARIF Viewer, SARIF Web Viewer

v0.4.0 changes (security tool false positive fix):
- String literal context detection: regex patterns in security tools no longer flagged as dangerous code
- Ignore comment: # skill-shield: ignore-next-line support
- 6 security audit tools reclassified from F to A/B (agents-skill-security-audit, ai-skill-scanner, etc.)

v0.3.1 changes:
- Fix: SKILL.md markdown table cells and YAML values no longer trigger pipe_sh
- Fix: SKILL.md inline code paths no longer trigger backtick_exec

v0.3.0 changes (context bias fix):
- Dual rating: Security Rating (code danger) vs Compliance Rating (permission declarations)
- Overall recommendation with human-readable reasons
- Fix: JS template literals no longer flagged as shell backtick execution
- Fix: Variable names (hostname, whoami) no longer flagged as commands
- Fix: Shell variable noise eliminated in .sh/.bash files
- Fix: os.environ.get("KEY") reduced severity vs bare os.environ
- Fix: Empty/doc-only skills marked as such instead of getting A rating
- 65 detection patterns with CWE references

Usage:
    python3 scan.py <skill-directory> [--output-dir <dir>] [--sarif]
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Known OpenClaw tool names (permissions)
# ---------------------------------------------------------------------------
KNOWN_TOOLS = [
    "exec", "read", "write", "web_fetch", "web_search",
    "browser", "message", "tts", "nodes", "canvas",
    "subagents", "edit", "process", "cron", "gateway",
    "memory_search", "memory_get", "sessions_spawn",
    "sessions_send", "sessions_list", "sessions_history",
]

TOOL_SENSITIVITY = {
    "exec": 5, "write": 4, "edit": 4, "gateway": 5,
    "browser": 4, "message": 3, "nodes": 4, "process": 4,
    "web_fetch": 3, "web_search": 2, "read": 2, "tts": 1,
    "canvas": 2, "subagents": 3, "cron": 3,
    "memory_search": 2, "memory_get": 2,
    "sessions_spawn": 3, "sessions_send": 3,
    "sessions_list": 2, "sessions_history": 2,
}

# ---------------------------------------------------------------------------
# Dangerous pattern definitions — 65 patterns with CWE references
# ---------------------------------------------------------------------------

def _build_patterns():
    """Build the full pattern database."""
    return [
        # === FILE DELETION (7) ===
        ("rm_rf",          "rm -rf",                r"\brm\s+-(r|rf|fr)\b",                5, "file_deletion",        "CWE-459"),
        ("rm_f",           "rm -f",                 r"\brm\s+-f\b",                        3, "file_deletion",        "CWE-459"),
        ("shred_cmd",      "shred",                 r"\bshred\b",                          4, "file_deletion",        "CWE-459"),
        ("unlink_call",    "unlink()",              r"\bunlink\s*\(",                      3, "file_deletion",        "CWE-459"),
        ("rmtree",         "shutil.rmtree",         r"\brmtree\s*\(",                      5, "file_deletion",        "CWE-459"),
        ("rimraf",         "rimraf",                r"\brimraf\b",                          4, "file_deletion",        "CWE-459"),
        ("del_glob",       "del /f /s /q",          r"\bdel\s+/[fFsS]",                   4, "file_deletion",        "CWE-459"),
        # === NETWORK EXFILTRATION (9) ===
        ("curl_post",      "curl POST/PUT",         r"\bcurl\b.*\s-(X|d|F)\s",            4, "network_exfil",        "CWE-200"),
        ("curl_data",      "curl --data/--upload",   r"\bcurl\b.*(--data|--upload|--post)", 4, "network_exfil",       "CWE-200"),
        ("wget_post",      "wget --post",           r"\bwget\b.*--post",                   4, "network_exfil",        "CWE-200"),
        ("req_post",       "requests.post/put",     r"\brequests\.(post|put)\b",           4, "network_exfil",        "CWE-200"),
        ("fetch_post",     "fetch() POST",          r"\bfetch\s*\(.*POST",                 4, "network_exfil",        "CWE-200"),
        ("nc_reverse",     "netcat reverse shell",  r"\b(nc|ncat|netcat)\b.*\s-e\s",       5, "network_exfil",        "CWE-506"),
        ("dns_exfil",      "DNS exfiltration",      r"\b(dig|nslookup|host)\b.*\$",        4, "network_exfil",        "CWE-200"),
        ("pipe_curl",      "pipe to curl/wget",     r"\|\s*(curl|wget)\b",                 5, "network_exfil",        "CWE-200"),
        ("socat_cmd",      "socat",                 r"\bsocat\b",                          4, "network_exfil",        "CWE-506"),
        # === ENVIRONMENT ACCESS (5) ===
        ("proc_env",       "process.env",           r"\bprocess\.env\b",                   3, "env_access",           "CWE-526"),
        ("os_env",         "os.environ",            r"\bos\.environ\b",                    3, "env_access",           "CWE-526"),
        ("dotenv",         ".env file access",      r"""(\.env['"]|dotenv|load_dotenv)""",  3, "env_access",           "CWE-526"),
        ("env_var",        "$ENV / ${ENV}",          r"\$\{?[A-Z_]{3,}\}?",                1, "env_access",           "CWE-526"),
        ("printenv",       "printenv/env dump",     r"\b(printenv|env\s*\|)\b",            3, "env_access",           "CWE-526"),
        # === SECRET/KEY ACCESS (8) ===
        ("ssh_dir",        ".ssh/ access",          r"\.ssh/",                             5, "secret_access",        "CWE-522"),
        ("gnupg_dir",      ".gnupg/ access",        r"\.gnupg/",                           5, "secret_access",        "CWE-522"),
        ("priv_key",       "private key file",      r"private[._-]?key",                   5, "secret_access",        "CWE-522"),
        ("wallet_ref",     "wallet access",         r"\bwallet\b",                         4, "secret_access",        "CWE-522"),
        ("token_ref",      "token reference",       r"\b(api[_-]?token|auth[_-]?token|access[_-]?token)\b", 3, "secret_access", "CWE-522"),
        ("passwd_ref",     "password reference",    r"\b(password|passwd|secret[_-]?key)\b", 3, "secret_access",      "CWE-522"),
        ("keychain",       "keychain/keyring",      r"\b(keychain|keyring|credential[_-]?store)\b", 4, "secret_access", "CWE-522"),
        ("aws_creds",      "cloud credentials",     r"(\.aws/credentials|\.azure/|\.gcloud/)", 5, "secret_access",    "CWE-522"),
        # === PRIVILEGE ESCALATION (6) ===
        ("sudo_cmd",       "sudo",                  r"\bsudo\b",                           5, "privilege_escalation", "CWE-269"),
        ("su_dash",        "su -",                  r"\bsu\s+-",                           5, "privilege_escalation", "CWE-269"),
        ("chmod777",       "chmod 777",             r"\bchmod\s+777\b",                    4, "privilege_escalation", "CWE-732"),
        ("chown_cmd",      "chown",                 r"\bchown\b",                          3, "privilege_escalation", "CWE-269"),
        ("setuid",         "setuid/setgid",         r"\b(setuid|setgid|seteuid)\b",        5, "privilege_escalation", "CWE-269"),
        ("doas_cmd",       "doas",                  r"\bdoas\b",                           5, "privilege_escalation", "CWE-269"),
        # === CODE EXECUTION (8) ===
        ("eval_call",      "eval()",                r"\beval\s*\(",                        4, "code_execution",       "CWE-95"),
        ("exec_call",      "exec()",                r"\bexec\s*\(",                        4, "code_execution",       "CWE-95"),
        ("func_ctor",      "Function()",            r"\bFunction\s*\(",                    4, "code_execution",       "CWE-95"),
        ("child_proc",     "child_process",         r"\bchild_process\b",                  4, "code_execution",       "CWE-78"),
        ("subprocess",     "subprocess",            r"\bsubprocess\.(call|run|Popen|check_output)\b", 3, "code_execution", "CWE-78"),
        ("os_system",      "os.system()",           r"\bos\.system\s*\(",                  4, "code_execution",       "CWE-78"),
        ("os_popen",       "os.popen()",            r"\bos\.popen\s*\(",                   4, "code_execution",       "CWE-78"),
        ("compile_call",   "compile()",             r"\bcompile\s*\(.*exec",               3, "code_execution",       "CWE-95"),
        # === DATA COLLECTION (6) ===
        ("etc_passwd",     "/etc/passwd",           r"/etc/passwd",                        5, "data_collection",      "CWE-200"),
        ("etc_shadow",     "/etc/shadow",           r"/etc/shadow",                        5, "data_collection",      "CWE-200"),
        ("whoami_cmd",     "whoami",                r"\bwhoami\b",                         2, "data_collection",      "CWE-200"),
        ("hostname_cmd",   "hostname",              r"\bhostname\b",                       2, "data_collection",      "CWE-200"),
        ("ifconfig_cmd",   "ifconfig/ip addr",      r"\b(ifconfig|ip\s+addr)\b",          3, "data_collection",      "CWE-200"),
        ("proc_self",      "/proc/self",            r"/proc/self/",                        4, "data_collection",      "CWE-200"),
        # === PERSISTENCE (5) ===
        ("crontab_edit",   "crontab modification",  r"\bcrontab\s+-[elr]\b",               4, "persistence",          "CWE-506"),
        ("systemd_svc",    "systemd service",       r"\bsystemctl\s+(enable|start)\b",     4, "persistence",          "CWE-506"),
        ("rc_local",       "rc.local modification", r"/etc/rc\.local",                     5, "persistence",          "CWE-506"),
        ("bashrc_mod",     "shell profile modify",  r"\.(bashrc|zshrc|profile|bash_profile)", 3, "persistence",       "CWE-506"),
        ("autostart",      "autostart entry",       r"(autostart|\.config/autostart|LaunchAgent)", 4, "persistence",  "CWE-506"),
        # === OBFUSCATION (5) ===
        ("long_base64",    "long base64 string",    r"[A-Za-z0-9+/=]{60,}",               4, "obfuscation",          "CWE-116"),
        ("hex_escape",     "hex escape sequence",   r"(\\x[0-9a-fA-F]{2}){4,}",           3, "obfuscation",          "CWE-116"),
        ("char_code",      "charCode obfuscation",  r"(fromCharCode|chr\s*\()\s*\(",       3, "obfuscation",          "CWE-116"),
        ("base64_decode",  "base64 decode call",    r"\b(atob|b64decode|base64\s*-d|base64\.b64decode)\b", 3, "obfuscation", "CWE-116"),
        ("reverse_str",    "string reversal trick", r"(\[::-1\]|\.reverse\(\)\.join)",     2, "obfuscation",          "CWE-116"),
        # === CRYPTOCURRENCY/MINING (3) ===
        ("crypto_miner",   "crypto miner",          r"\b(xmrig|minerd|cpuminer|cryptonight|stratum\+tcp)\b", 5, "crypto_mining", "CWE-400"),
        ("mining_pool",    "mining pool URL",        r"stratum\+tcp://",                   5, "crypto_mining",        "CWE-400"),
        ("wallet_addr",    "crypto wallet address",  r"\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b", 2, "crypto_mining", "CWE-506"),
        # === SHELL INJECTION (3) ===
        ("backtick_exec",  "backtick execution",    r"`[^`]*\$[^`]+`",                    4, "shell_injection",      "CWE-78"),
        ("pipe_sh",        "pipe to shell",         r"\|\s*(ba)?sh\b",                     5, "shell_injection",      "CWE-78"),
        ("download_exec",  "download and execute",  r"(curl|wget).*\|\s*(ba)?sh",          5, "shell_injection",      "CWE-829"),
    ]

DANGEROUS_PATTERNS = _build_patterns()


# ---------------------------------------------------------------------------
# Context detection — enhanced for v0.3.0 false positive reduction
# ---------------------------------------------------------------------------

def _is_comment_line(line: str, file_ext: str) -> bool:
    stripped = line.strip()
    if file_ext in (".py",):
        return stripped.startswith("#")
    if file_ext in (".js", ".ts", ".mjs", ".cjs"):
        return stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*")
    if file_ext in (".sh", ".bash"):
        return stripped.startswith("#")
    return False


def _is_in_docstring(lines: list[str], line_idx: int, file_ext: str) -> bool:
    if file_ext != ".py":
        return False
    triple_count = 0
    for i in range(line_idx):
        triple_count += lines[i].count('\"\"\"') + lines[i].count("\'\'\'")
    return triple_count % 2 == 1


def _is_pattern_definition_line(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith("(\"") and "r\"" in stripped and "\"," in stripped:
        return True
    if stripped.startswith("# ===") and "===" in stripped:
        return True
    return False


def _is_string_literal_context(line: str, match_str: str, file_ext: str) -> bool:
    """Detect if a match is inside a string literal used as data (regex pattern, config value, etc.).

    This catches security tools that define detection patterns as string data,
    e.g.: PATTERNS = [r"rm -rf", r"sudo", r"curl .*| bash"]
    These are data definitions, not executable commands.
    """
    stripped = line.strip()

    # --- Universal: noscan marker (used by other scanners to mark their own patterns) ---
    if "# noscan" in line or "// noscan" in line or "/* noscan" in line:
        return True

    # --- Universal: line is a raw string continuation ---
    if stripped.startswith(('r"', "r'", 'r' + chr(34)*3, "r" + chr(39)*3)):
        return True

    # --- Universal: "description" or "check" dict values describing patterns ---
    if re.search(r'["\'](?:description|check|pattern_name|name|message|reason)["\']', stripped):
        if _match_inside_quotes(stripped, match_str):
            return True

    # --- Universal: match is inside a quoted string on a line that's mostly strings ---
    # Catches function args, tuple elements, dict values where patterns are described
    if _match_inside_quotes(stripped, match_str):
        # Count quoted vs unquoted content ratio
        quote_chars = stripped.count('"') + stripped.count("'")
        if quote_chars >= 4:  # At least 2 quoted strings on the line
            return True

    # Python-specific
    if file_ext == ".py":
        # re.compile(r"pattern") — including triple-quoted
        if re.search(r're\.compile\s*\(\s*r?["\']', stripped):
            return True
        # Triple-quoted raw strings (often multi-line regex)
        if re.search(r'r"""', stripped) or re.search(r"r'''", stripped):
            return True
        # Assignment to list/tuple with raw strings: [r"...", ...]
        if re.search(r'[\[(\s]r["\']', stripped):
            return True
        # String in a tuple/list element: ("id", "name", r"regex", ...)
        if re.search(r'\(\s*["\'].*r["\'].*["\'].*\)', stripped):
            return True
        # Variable assignment with string containing the match
        if re.search(r'=\s*[\[{(]?\s*r?["\']', stripped):
            if _match_inside_quotes(stripped, match_str):
                return True

    # JavaScript-specific
    if file_ext in (".js", ".ts", ".mjs", ".cjs"):
        # JS regex literal: /pattern/flags — property assignment like re: /pattern/i,
        if re.search(r'(?:^|[\s=:,({])\/[^/\n]+\/[gimsuy]*\s*[,;)\]}]?', stripped):
            return True
        # RegExp constructor: new RegExp("pattern")
        if re.search(r'RegExp\s*\(', stripped):
            return True
        # Quoted strings containing the match
        if _match_inside_quotes(stripped, match_str):
            return True

    # Any language: string in array/dict used as pattern data
    if re.search(r'[\[{]\s*r?["\']', stripped) and re.search(r'["\'].*["\']', stripped):
        if _match_inside_quotes(stripped, match_str):
            return True

    return False


def _match_inside_quotes(line: str, match_str: str) -> bool:
    """Check if match_str appears inside a quoted string in the line."""
    # Find all quoted regions
    in_str = False
    quote_char = None
    start = -1
    regions = []
    i = 0
    while i < len(line):
        ch = line[i]
        if not in_str:
            if ch in ('"', "'"):
                # Check for triple quotes
                if line[i:i+3] in ('"""', "'''"):
                    in_str = True
                    quote_char = line[i:i+3]
                    start = i + 3
                    i += 3
                    continue
                in_str = True
                quote_char = ch
                start = i + 1
        else:
            if isinstance(quote_char, str) and len(quote_char) == 3:
                if line[i:i+3] == quote_char:
                    regions.append((start, i))
                    in_str = False
                    i += 3
                    continue
            elif ch == quote_char and (i == 0 or line[i-1] != '\\'):
                regions.append((start, i))
                in_str = False
        i += 1

    # Check if any part of match_str falls inside a quoted region
    for s, e in regions:
        segment = line[s:e]
        if match_str in segment or any(part in segment for part in match_str.split()):
            return True
    return False


def _is_ignore_next_line(lines: list[str], line_idx: int) -> bool:
    """Check if the previous line has a skill-shield ignore comment."""
    if line_idx <= 0:
        return False
    prev = lines[line_idx - 1].strip()
    return "skill-shield: ignore-next-line" in prev or "skill-shield:ignore-next-line" in prev


def _is_documentation_line(line: str) -> bool:
    stripped = line.strip()
    doc_keywords = [
        "file deletion", "network exfil", "environment variable",
        "secret/key access", "privilege escalation", "dynamic code",
        "data collection", "what it detects", "persistence",
        "obfuscation", "crypto", "shell injection", "code execution",
        "anti-obfuscation", "permission", "cwe-", "detection capabilit",
        "safety rating", "patterns)", "mining", "compliance",
        "arbitrary code", "command injection", "shell access",
        "code injection", "risk:", "pattern:", "vulnerability",
    ]
    # Bullet points with security keywords
    if stripped.startswith("- ") and any(kw in stripped.lower() for kw in doc_keywords):
        return True
    # Markdown table rows with security keywords
    if stripped.startswith("|") and any(kw in stripped.lower() for kw in doc_keywords):
        return True
    # Lines with backtick-quoted code examples in documentation
    if stripped.startswith("|") and "`" in stripped:
        return True
    # Indented example blocks (│ or similar)
    if "│" in stripped and any(kw in stripped.lower() for kw in doc_keywords):
        return True
    # Bullet points with backtick-quoted code
    if stripped.startswith(("- ", "* ", "• ")) and "`" in stripped:
        return True
    return False


def _is_in_markdown_code_block(lines: list[str], line_idx: int) -> bool:
    in_block = False
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            in_block = not in_block
    return in_block


def _is_variable_name_usage(line: str, match_str: str) -> bool:
    """Check if matched keyword is used as a variable/property name, not a command."""
    import re as _re
    stripped = line.strip()
    m = match_str.lower()
    # Variable declarations: let hostname, var hostname, const hostname
    if _re.search(rf'\b(let|var|const|int|str|float)\s+{_re.escape(m)}\b', stripped, _re.IGNORECASE):
        return True
    # Property access: parsed.hostname, obj.whoami, url.hostname
    if _re.search(rf'\.\s*{_re.escape(m)}\b', stripped, _re.IGNORECASE):
        return True
    # Assignment target: hostname =, hostname:, hostname,
    if _re.search(rf'\b{_re.escape(m)}\s*[=:,;]', stripped, _re.IGNORECASE):
        return True
    # Function parameter: function(hostname)
    if _re.search(rf'[\(,]\s*{_re.escape(m)}\s*[\),]', stripped, _re.IGNORECASE):
        return True
    return False


def _context_severity_adjust(severity, line, file_ext, lines, line_idx,
                              is_self_scan, is_skill_md, pat_id="", match_str=""):
    """Adjust severity based on context. Returns 0 to skip entirely."""
    import re as _re

    # --- v0.4.0: skill-shield: ignore-next-line comment ---
    if _is_ignore_next_line(lines, line_idx):
        return 0

    # Self-scan: skip pattern definition lines
    if is_self_scan and _is_pattern_definition_line(line):
        return 0

    # --- v0.4.0: String literal context detection (security tool false positives) ---
    if not is_self_scan and not is_skill_md and match_str:
        # Don't apply string literal demotion if the line is an actual execution call
        # Check for execution functions that are NOT inside strings themselves
        stripped_line = line.strip()
        is_exec_call = False
        exec_patterns = [
            (r'\bsubprocess\.\w+\s*\(', None),
            (r'\bos\.system\s*\(', None),
            (r'\bos\.popen\s*\(', None),
            (r'\bchild_process\.\w+\s*\(', None),
        ]
        for ep, _ in exec_patterns:
            if _re.search(ep, stripped_line):
                is_exec_call = True
                break
        if not is_exec_call and _is_string_literal_context(line, match_str, file_ext):
            return max(1, severity - 3)  # Demote to info level
        # Also check if we're inside a multi-line triple-quoted string (Python)
        if file_ext == ".py" and _is_in_docstring(lines, line_idx, file_ext):
            return max(1, severity - 2)

    # SKILL.md documentation lines: skip
    if is_skill_md and _is_documentation_line(line):
        return 0

    # --- v0.3.1 FIX: SKILL.md markdown table cells (|Bash, |Read etc.) are NOT pipe to shell ---
    if pat_id == "pipe_sh" and is_skill_md:
        stripped = line.strip()
        # Table rows, YAML values with pipe-separated lists, quoted strings with pipes
        if stripped.startswith("|") or "|" in stripped[:3]:
            return 0
        if '"' in line and "|" in line:
            return 0
        if stripped.startswith("- ") and ":" in stripped:
            return 0

    # --- v0.3.1 FIX: SKILL.md inline code paths (`${VAR}/path`) are NOT backtick execution ---
    if pat_id == "backtick_exec" and is_skill_md:
        if not _is_in_markdown_code_block(lines, line_idx):
            return 0

    # --- v0.3.0 FIX: JS template literals are NOT shell backtick execution ---
    if pat_id == "backtick_exec" and file_ext in (".js", ".ts", ".mjs", ".cjs"):
        return 0

    # --- v0.3.0 FIX: Variable name usage (hostname, whoami as variables) ---
    if pat_id in ("hostname_cmd", "whoami_cmd") and match_str:
        if _is_variable_name_usage(line, match_str):
            return 0

    # --- v0.3.0 FIX: Shell $VAR is normal — skip env_var in shell files ---
    if pat_id == "env_var" and file_ext in (".sh", ".bash"):
        return 0

    # --- v0.3.0 FIX: os.environ.get("KEY") is standard practice ---
    if pat_id == "os_env" and ".get(" in line:
        return max(1, severity - 1)  # 3 -> 2

    # --- v0.3.0 FIX: process.env.SPECIFIC_KEY is standard practice ---
    if pat_id == "proc_env" and _re.search(r'process\.env\.[A-Z_]+', line):
        return max(1, severity - 1)  # 3 -> 2

    # --- v0.3.0 FIX: setuid in --disable-setuid-sandbox is a browser flag, not privilege escalation ---
    if pat_id == "setuid" and "disable-setuid-sandbox" in line:
        return max(1, severity - 3)  # 5 -> 2

    # SKILL.md markdown code blocks: reduce (examples)
    if is_skill_md and _is_in_markdown_code_block(lines, line_idx):
        return max(1, severity - 2)

    # Comments: reduce by 2
    if _is_comment_line(line, file_ext):
        return max(1, severity - 2)

    # Docstrings: reduce by 2
    if _is_in_docstring(lines, line_idx, file_ext):
        return max(1, severity - 2)

    # Log/print statements: reduce by 1
    stripped = line.strip()
    if stripped.startswith(("print(", "log(", "console.log(", "logger.", "logging.", "log.info(")):
        return max(1, severity - 1)

    return severity


# ---------------------------------------------------------------------------
# Anti-obfuscation: decode base64/hex and re-scan
# ---------------------------------------------------------------------------

def _try_decode_base64(text):
    import base64 as _b64
    results = []
    import re as _re
    for m in _re.finditer(r'[A-Za-z0-9+/]{40,}={0,2}', text):
        candidate = m.group()
        try:
            decoded = _b64.b64decode(candidate).decode("utf-8", errors="replace")
            printable_ratio = sum(1 for c in decoded if c.isprintable() or c.isspace()) / max(len(decoded), 1)
            if printable_ratio > 0.7 and len(decoded) > 5:
                results.append((candidate, decoded))
        except Exception:
            pass
    return results


def _try_decode_hex(text):
    import re as _re
    results = []
    for m in _re.finditer(r'(?:\\x[0-9a-fA-F]{2}){4,}', text):
        candidate = m.group()
        try:
            decoded = bytes(int(h, 16) for h in _re.findall(r'\\x([0-9a-fA-F]{2})', candidate)).decode("utf-8", errors="replace")
            if len(decoded) > 3:
                results.append((candidate, decoded))
        except Exception:
            pass
    return results


def scan_obfuscated_content(files, skill_md):
    findings = []
    all_files = list(files)
    if skill_md.exists():
        all_files.append(skill_md)
    for f in all_files:
        text = f.read_text(errors="replace")
        is_self = (f.name == "scan.py" and "skill-shield" in str(f))
        if is_self:
            continue
        lines = text.splitlines()
        for line_no, line in enumerate(lines, 1):
            for encoded, decoded in _try_decode_base64(line):
                for pat_id, pat_name, regex, severity, category, cwe in DANGEROUS_PATTERNS:
                    if re.search(regex, decoded, re.IGNORECASE):
                        findings.append({
                            "pattern_id": f"obfuscated_{pat_id}",
                            "pattern_name": f"[OBFUSCATED] {pat_name} (base64)",
                            "severity": min(5, severity + 1),
                            "category": "obfuscated_" + category,
                            "cwe": cwe,
                            "file": str(f.name), "line": line_no,
                            "match": f"base64 -> {decoded[:60]}",
                            "context": line.strip()[:120],
                        })
            for encoded, decoded in _try_decode_hex(line):
                for pat_id, pat_name, regex, severity, category, cwe in DANGEROUS_PATTERNS:
                    if re.search(regex, decoded, re.IGNORECASE):
                        findings.append({
                            "pattern_id": f"obfuscated_{pat_id}",
                            "pattern_name": f"[OBFUSCATED] {pat_name} (hex)",
                            "severity": min(5, severity + 1),
                            "category": "obfuscated_" + category,
                            "cwe": cwe,
                            "file": str(f.name), "line": line_no,
                            "match": f"hex -> {decoded[:60]}",
                            "context": line.strip()[:120],
                        })
    return findings


# ---------------------------------------------------------------------------
# Core scanning functions
# ---------------------------------------------------------------------------

SKIP_DIRS = {"venv", "node_modules", ".git", "__pycache__", ".venv", "env", ".env",
             "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", "site-packages"}

MAX_SCRIPT_FILES = 200  # Safety limit for batch scanning


def find_skill_files(skill_dir, max_files=0):
    skill_md = skill_dir / "SKILL.md"
    script_exts = {".sh", ".py", ".js", ".ts", ".bash", ".mjs", ".cjs"}
    scripts = []
    for f in skill_dir.rglob("*"):
        # Skip common non-skill directories
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix in script_exts:
            scripts.append(f)
            if max_files and len(scripts) >= max_files:
                break
    return skill_md, scripts


def extract_tools_from_skill_md(skill_md):
    if not skill_md.exists():
        return []
    text = skill_md.read_text(errors="replace")
    found = set()
    for tool in KNOWN_TOOLS:
        if re.search(rf"\b{re.escape(tool)}\b", text):
            found.add(tool)
    return sorted(found)


def extract_tools_from_code(files):
    found = set()
    for f in files:
        text = f.read_text(errors="replace")
        for tool in KNOWN_TOOLS:
            if re.search(rf"\b{re.escape(tool)}\b", text):
                found.add(tool)
    return sorted(found)


def scan_dangerous_patterns(files, skill_md):
    """Scan all files for dangerous patterns with context-aware severity."""
    findings = []
    all_files = list(files)
    if skill_md.exists():
        all_files.append(skill_md)

    for f in all_files:
        text = f.read_text(errors="replace")
        lines = text.splitlines()
        is_self = (f.name == "scan.py" and "skill-shield" in str(f))
        is_skill_md = (f.name == "SKILL.md")
        file_ext = f.suffix

        for line_idx, line in enumerate(lines):
            line_no = line_idx + 1
            for pat_id, pat_name, regex, severity, category, cwe in DANGEROUS_PATTERNS:
                if pat_id == "env_var" and is_skill_md:
                    continue
                matches = list(re.finditer(regex, line, re.IGNORECASE))
                if not matches:
                    continue
                match_str = matches[0].group()
                adj_severity = _context_severity_adjust(
                    severity, line, file_ext, lines, line_idx, is_self, is_skill_md,
                    pat_id=pat_id, match_str=match_str
                )
                if adj_severity == 0:
                    continue
                findings.append({
                    "pattern_id": pat_id,
                    "pattern_name": pat_name,
                    "severity": adj_severity,
                    "original_severity": severity,
                    "category": category,
                    "cwe": cwe,
                    "file": str(f.name),
                    "line": line_no,
                    "match": match_str[:80],
                    "context": line.strip()[:120],
                    "in_comment": _is_comment_line(line, file_ext),
                    "in_docstring": _is_in_docstring(lines, line_idx, file_ext),
                    "in_code_block": is_skill_md and _is_in_markdown_code_block(lines, line_idx),
                })
    return findings


# ---------------------------------------------------------------------------
# Permission declaration audit
# ---------------------------------------------------------------------------

def audit_permissions(tools_declared, tools_in_code):
    declared_set = set(tools_declared)
    code_set = set(tools_in_code)
    undeclared = sorted(code_set - declared_set)
    unused_declared = sorted(declared_set - code_set)
    properly_declared = sorted(declared_set & code_set)
    undeclared_risk = []
    for tool in undeclared:
        sens = TOOL_SENSITIVITY.get(tool, 2)
        undeclared_risk.append({
            "tool": tool,
            "sensitivity": sens,
            "recommendation": f"Add '{tool}' to SKILL.md permissions" if sens <= 3
                else f"High-sensitivity tool '{tool}' used but not declared",
        })
    total_risk_score = sum(TOOL_SENSITIVITY.get(t, 2) for t in undeclared)
    return {
        "declared": tools_declared,
        "found_in_code": tools_in_code,
        "undeclared": undeclared,
        "unused_declared": unused_declared,
        "properly_declared": properly_declared,
        "undeclared_risk_details": undeclared_risk,
        "undeclared_risk_score": total_risk_score,
        "declaration_coverage": f"{len(properly_declared)}/{len(code_set)}" if code_set else "N/A",
    }


# ---------------------------------------------------------------------------
# Dual rating engine (v0.3.0)
# ---------------------------------------------------------------------------

def compute_security_rating(findings, is_doc_only=False):
    """Rate based on dangerous code patterns only. Ignores permission compliance."""
    if is_doc_only:
        return "N/A", "Documentation-only skill — no executable code to assess"

    if not findings:
        return "A", "Safe — no dangerous patterns detected"

    # Only count real findings (not reduced to info level from comments/docs)
    real = [f for f in findings if f["severity"] >= 3
            and not f.get("in_comment") and not f.get("in_docstring") and not f.get("in_code_block")]
    if not real:
        return "A", "Safe — only trivial or documentation patterns detected"

    max_sev = max(f["severity"] for f in real)
    high_count = sum(1 for f in real if f["severity"] >= 4)
    obf_count = sum(1 for f in findings if f["pattern_id"].startswith("obfuscated_"))

    if obf_count >= 2:
        return "F", "Dangerous — obfuscated malicious patterns detected"
    if max_sev >= 5 and high_count >= 3:
        return "F", "Dangerous — multiple critical patterns in executable code"
    elif max_sev >= 5 or high_count >= 3:
        return "D", "High risk — critical patterns detected, manual review required"
    elif max_sev >= 4 or high_count >= 1:
        return "C", "Moderate risk — review flagged patterns before installing"
    elif max_sev >= 3:
        return "B", "Low risk — minor concerns detected"
    else:
        return "A", "Safe — only trivial patterns detected"


def compute_compliance_rating(perm_audit):
    """Rate based on permission declaration completeness."""
    undeclared = perm_audit.get("undeclared", [])
    risk_score = perm_audit.get("undeclared_risk_score", 0)
    code_perms = perm_audit.get("found_in_code", [])

    if not code_perms:
        return "N/A", "No tool permissions detected in code"
    if not undeclared:
        return "A", "All permissions properly declared"
    if risk_score >= 10:
        return "D", f"{len(undeclared)} permissions used but not declared (risk score {risk_score})"
    elif risk_score >= 6:
        return "C", f"{len(undeclared)} permissions used but not declared"
    elif risk_score >= 3:
        return "B", f"{len(undeclared)} minor permissions not declared"
    else:
        return "A", "Only low-sensitivity permissions undeclared"


def compute_recommendation(sec_rating, comp_rating, is_doc_only):
    """Compute overall install recommendation from both ratings."""
    if is_doc_only:
        return "documentation_only", "Documentation-only skill with no executable code. Provides guidance but no actual functionality."

    sec_rank = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4, "N/A": 0}.get(sec_rating, 4)
    comp_rank = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4, "N/A": 0}.get(comp_rating, 4)

    if sec_rank <= 1 and comp_rank <= 1:
        return "install", "Safe to install"
    elif sec_rank <= 1 and comp_rank >= 2:
        return "install_with_review", "Code is safe; permission declarations incomplete (likely poor documentation, not malicious intent)"
    elif sec_rank == 2 and comp_rank <= 1:
        return "review_required", "Some security patterns flagged — review before installing"
    elif sec_rank == 2:
        return "review_required", "Security patterns flagged and permissions undeclared — review recommended"
    elif sec_rank >= 3:
        return "do_not_install", "Significant security concerns detected — manual review required before installing"
    else:
        return "review_required", "Review recommended"


def build_rating_reasons(findings, perm_audit, sec_rating, comp_rating, is_doc_only):
    """Build human-readable list of reasons for the ratings."""
    reasons = []
    if is_doc_only:
        reasons.append("This skill contains no executable code (scripts). It only provides SKILL.md guidance for the agent.")
        return reasons

    # Security reasons
    if findings:
        high = sum(1 for f in findings if f["severity"] >= 4 and not f.get("in_comment") and not f.get("in_docstring"))
        med = sum(1 for f in findings if f["severity"] == 3 and not f.get("in_comment") and not f.get("in_docstring"))
        reduced = sum(1 for f in findings if f.get("original_severity", f["severity"]) != f["severity"])
        if high:
            cats = set(f["category"] for f in findings if f["severity"] >= 4)
            reasons.append(f"Security: {high} high/critical findings ({', '.join(sorted(cats))})")
        if med:
            reasons.append(f"Security: {med} medium findings")
        if reduced:
            reasons.append(f"Context: {reduced} findings had severity reduced (in comments/docs/examples)")
    elif sec_rating == "A":
        reasons.append("Security: no dangerous patterns detected in code")

    # Compliance reasons
    undeclared = perm_audit.get("undeclared", [])
    if undeclared:
        reasons.append(f"Compliance: {len(undeclared)} permissions used in code but not declared in SKILL.md: {', '.join(undeclared)}")
        reasons.append("Note: undeclared permissions often indicate poor documentation, not malicious intent")
    elif perm_audit.get("found_in_code"):
        reasons.append("Compliance: all permissions properly declared")

    unused = perm_audit.get("unused_declared", [])
    if unused:
        reasons.append(f"Info: {len(unused)} permissions declared but not found in code: {', '.join(unused)}")

    return reasons


# ---------------------------------------------------------------------------
# Report builders
# ---------------------------------------------------------------------------

def _count_by(findings, key):
    counts = {}
    for f in findings:
        v = f[key]
        counts[v] = counts.get(v, 0) + 1
    return counts

def _count_by_severity(findings):
    counts = {}
    for f in findings:
        s = str(f["severity"])
        counts[s] = counts.get(s, 0) + 1
    return counts


def build_json_report(skill_dir, perm_audit, findings, sec_rating, sec_reason,
                      comp_rating, comp_reason, recommendation, rec_reason,
                      rating_reasons, is_doc_only):
    return {
        "skill_shield_version": "0.6.1",
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "skill_path": str(skill_dir),
        "skill_name": skill_dir.name,
        "pattern_count": len(DANGEROUS_PATTERNS),
        "is_documentation_only": is_doc_only,
        "permissions": perm_audit,
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "obfuscated_findings": sum(1 for f in findings if f["pattern_id"].startswith("obfuscated_")),
            "context_reduced": sum(1 for f in findings if f.get("original_severity", f["severity"]) != f["severity"]),
            "by_category": _count_by(findings, "category"),
            "by_severity": _count_by_severity(findings),
            "max_severity": max((f["severity"] for f in findings), default=0),
            "cwe_references": sorted(set(f.get("cwe", "") for f in findings if f.get("cwe"))),
        },
        # Dual ratings (v0.3.0)
        "security_rating": sec_rating,
        "security_reason": sec_reason,
        "compliance_rating": comp_rating,
        "compliance_reason": comp_reason,
        "recommendation": recommendation,
        "recommendation_reason": rec_reason,
        "rating_reasons": rating_reasons,
        # Backward compatibility: "rating" = security_rating
        "rating": sec_rating,
        "rating_reason": sec_reason,
    }


def build_md_report(report):
    r = report
    lines = []
    lines.append(f"# Skill Shield Report: {r['skill_name']}")
    lines.append("")
    lines.append(f"**Scanner:** skill-shield v{r['skill_shield_version']} ({r['pattern_count']} patterns)")
    lines.append(f"**Scan time:** {r['scan_timestamp']}")
    lines.append(f"**Path:** `{r['skill_path']}`")
    if r.get("is_documentation_only"):
        lines.append("**Type:** Documentation-only (no executable code)")
    lines.append("")

    # Dual Rating
    emoji_map = {"A": "G", "B": "B", "C": "Y", "D": "O", "F": "R", "N/A": "W"}
    emoji_char = {"G": "\U0001f7e2", "B": "\U0001f535", "Y": "\U0001f7e1", "O": "\U0001f7e0", "R": "\U0001f534", "W": "\u26aa"}

    sec_e = emoji_char.get(emoji_map.get(r["security_rating"], "W"), "\u26aa")
    comp_e = emoji_char.get(emoji_map.get(r["compliance_rating"], "W"), "\u26aa")

    lines.append("## Ratings")
    lines.append("")
    lines.append(f"| Dimension | Rating | Detail |")
    lines.append(f"|-----------|--------|--------|")
    lines.append(f"| Security | {sec_e} {r['security_rating']} | {r['security_reason']} |")
    lines.append(f"| Compliance | {comp_e} {r['compliance_rating']} | {r['compliance_reason']} |")
    lines.append("")

    # Recommendation
    rec_emoji = {"install": "\u2705", "install_with_review": "\u26a0\ufe0f", "review_required": "\U0001f50d", "do_not_install": "\u274c", "documentation_only": "\U0001f4c4"}
    re_icon = rec_emoji.get(r["recommendation"], "\u2753")
    lines.append(f"### {re_icon} Recommendation: {r['recommendation']}")
    lines.append(f"> {r['recommendation_reason']}")
    lines.append("")

    # Rating reasons
    if r.get("rating_reasons"):
        lines.append("### Score Breakdown")
        lines.append("")
        for reason in r["rating_reasons"]:
            lines.append(f"- {reason}")
        lines.append("")

    # Permission Audit
    perm = r["permissions"]
    lines.append("## Permission Audit")
    lines.append("")
    lines.append(f"**Declared in SKILL.md:** {', '.join(perm['declared']) if perm['declared'] else 'none'}")
    lines.append(f"**Found in code:** {', '.join(perm['found_in_code']) if perm['found_in_code'] else 'none'}")
    lines.append(f"**Declaration coverage:** {perm['declaration_coverage']}")
    lines.append("")

    if perm["undeclared"]:
        lines.append("### Undeclared Permissions")
        lines.append("")
        lines.append("| Tool | Sensitivity | Recommendation |")
        lines.append("|------|------------|----------------|")
        for detail in perm["undeclared_risk_details"]:
            dots = "\U0001f534" * min(detail["sensitivity"], 5)
            lines.append(f"| {detail['tool']} | {dots} ({detail['sensitivity']}/5) | {detail['recommendation']} |")
        lines.append("")

    if perm["unused_declared"]:
        lines.append(f"**Declared but unused:** {', '.join(perm['unused_declared'])}")
        lines.append("")

    # Findings
    total = r["summary"]["total_findings"]
    obf = r["summary"]["obfuscated_findings"]
    reduced = r["summary"]["context_reduced"]
    lines.append(f"## Findings ({total} total{f', {obf} obfuscated' if obf else ''}{f', {reduced} context-reduced' if reduced else ''})")
    lines.append("")

    if not r["findings"]:
        lines.append("No dangerous patterns detected.")
    else:
        severity_label = {1: "Info", 2: "Low", 3: "Medium", 4: "High", 5: "Critical"}
        lines.append("| Severity | Pattern | CWE | File | Line | Context |")
        lines.append("|----------|---------|-----|------|------|---------|")
        for f in sorted(r["findings"], key=lambda x: -x["severity"]):
            sev = severity_label.get(f["severity"], "?")
            ctx = f["context"].replace("|", "\\|")[:70]
            cwe = f.get("cwe", "")
            note = ""
            if f.get("in_comment"): note = " C"
            elif f.get("in_docstring"): note = " D"
            elif f.get("in_code_block"): note = " E"
            orig = f.get("original_severity", f["severity"])
            sev_display = f"{sev} ({f['severity']})" if orig == f["severity"] else f"{sev} ({f['severity']}<-{orig})"
            lines.append(f"| {sev_display}{note} | {f['pattern_name']} | {cwe} | {f['file']} | {f['line']} | `{ctx}` |")
    lines.append("")

    # CWE Summary
    cwes = r["summary"].get("cwe_references", [])
    if cwes:
        lines.append("## CWE References")
        lines.append("")
        for cwe in cwes:
            cwe_num = cwe.split("-")[1] if "-" in cwe else cwe
            lines.append(f"- [{cwe}](https://cwe.mitre.org/data/definitions/{cwe_num}.html)")
        lines.append("")

    if r["summary"]["by_category"]:
        lines.append("## Summary by Category")
        lines.append("")
        for cat, count in sorted(r["summary"]["by_category"].items()):
            lines.append(f"- **{cat}**: {count}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SARIF 2.1.0 output (v0.5.0) — GitHub Code Scanning compatible
# ---------------------------------------------------------------------------

SARIF_SEVERITY_MAP = {
    5: "error",
    4: "error",
    3: "warning",
    2: "note",
    1: "note",
}

SARIF_SECURITY_SEVERITY_MAP = {
    5: "critical",
    4: "high",
    3: "medium",
    2: "low",
    1: "low",
}

CWE_DESCRIPTIONS = {
    "CWE-78": "Improper Neutralization of Special Elements used in an OS Command",
    "CWE-95": "Improper Neutralization of Directives in Dynamically Evaluated Code",
    "CWE-116": "Improper Encoding or Escaping of Output",
    "CWE-200": "Exposure of Sensitive Information to an Unauthorized Actor",
    "CWE-269": "Improper Privilege Management",
    "CWE-400": "Uncontrolled Resource Consumption",
    "CWE-459": "Incomplete Cleanup",
    "CWE-506": "Embedded Malicious Code",
    "CWE-522": "Insufficiently Protected Credentials",
    "CWE-526": "Cleartext Storage of Sensitive Information in an Environment Variable",
    "CWE-732": "Incorrect Permission Assignment for Critical Resource",
    "CWE-829": "Inclusion of Functionality from Untrusted Control Sphere",
}


def _sarif_fingerprint(finding, skill_name):
    """Generate a stable partial fingerprint for deduplication."""
    key = f"{skill_name}:{finding['pattern_id']}:{finding['file']}:{finding.get('match', '')}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]


def build_sarif_report(report):
    """Build a SARIF 2.1.0 report from the internal JSON report."""
    findings = report.get("findings", [])
    skill_name = report["skill_name"]

    # Build rules from all patterns (not just those with findings)
    rules = []
    rule_index_map = {}
    for idx, (pat_id, pat_name, regex, severity, category, cwe) in enumerate(DANGEROUS_PATTERNS):
        rule_id = f"skill-shield/{pat_id}"
        rule_index_map[pat_id] = idx
        cwe_desc = CWE_DESCRIPTIONS.get(cwe, cwe)
        rules.append({
            "id": rule_id,
            "name": pat_id,
            "shortDescription": {"text": pat_name},
            "fullDescription": {"text": f"{pat_name} — {cwe_desc}"},
            "helpUri": f"https://cwe.mitre.org/data/definitions/{cwe.split('-')[1]}.html" if "-" in cwe else "",
            "help": {
                "text": f"Pattern: {pat_name}\nCategory: {category}\nCWE: {cwe}\nDefault severity: {severity}/5",
                "markdown": f"**Pattern:** {pat_name}\n\n**Category:** {category}\n\n**CWE:** [{cwe}](https://cwe.mitre.org/data/definitions/{cwe.split('-')[1]}.html)\n\n**Default severity:** {severity}/5"
            },
            "defaultConfiguration": {
                "level": SARIF_SEVERITY_MAP.get(severity, "warning"),
            },
            "properties": {
                "tags": ["security", category],
                "security-severity": str(float(severity * 2)),  # Map 1-5 to 2.0-10.0
                "precision": "medium",
            },
        })

    # Also add rules for obfuscated variants that appear in findings
    for f in findings:
        pid = f["pattern_id"]
        if pid.startswith("obfuscated_") and pid not in rule_index_map:
            rule_index_map[pid] = len(rules)
            rules.append({
                "id": f"skill-shield/{pid}",
                "name": pid,
                "shortDescription": {"text": f["pattern_name"]},
                "fullDescription": {"text": f"Obfuscated pattern: {f['pattern_name']}"},
                "defaultConfiguration": {"level": "error"},
                "properties": {
                    "tags": ["security", "obfuscation", f.get("category", "unknown")],
                    "security-severity": str(float(min(f["severity"], 5) * 2)),
                },
            })

    # Build results
    results = []
    for f in findings:
        pid = f["pattern_id"]
        rule_idx = rule_index_map.get(pid, 0)
        rule_id = f"skill-shield/{pid}"
        sev = f["severity"]

        result = {
            "ruleId": rule_id,
            "ruleIndex": rule_idx,
            "level": SARIF_SEVERITY_MAP.get(sev, "warning"),
            "message": {
                "text": f"{f['pattern_name']} detected in {f['file']} at line {f['line']}: {f.get('match', '')[:80]}",
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": f["file"],
                        "uriBaseId": "%SRCROOT%",
                    },
                    "region": {
                        "startLine": f["line"],
                        "startColumn": 1,
                        "snippet": {"text": f.get("context", "")[:200]},
                    },
                },
            }],
            "partialFingerprints": {
                "primaryLocationLineHash": _sarif_fingerprint(f, skill_name),
            },
            "properties": {
                "security-severity": SARIF_SECURITY_SEVERITY_MAP.get(sev, "medium"),
                "category": f.get("category", "unknown"),
                "cwe": f.get("cwe", ""),
            },
        }

        # Add original severity if context-reduced
        orig = f.get("original_severity", sev)
        if orig != sev:
            result["properties"]["originalSeverity"] = orig
            result["properties"]["contextReduced"] = True

        # Add CWE as taxa reference
        cwe = f.get("cwe", "")
        if cwe and "-" in cwe:
            result["taxa"] = [{
                "id": cwe,
                "index": 0,
                "toolComponent": {"name": "cwe", "index": 0},
            }]

        results.append(result)

    # Collect unique CWEs for taxonomy
    unique_cwes = sorted(set(f.get("cwe", "") for f in findings if f.get("cwe")))
    taxa = []
    for cwe in unique_cwes:
        if "-" not in cwe:
            continue
        cwe_num = cwe.split("-")[1]
        taxa.append({
            "id": cwe,
            "name": CWE_DESCRIPTIONS.get(cwe, cwe),
            "shortDescription": {"text": CWE_DESCRIPTIONS.get(cwe, cwe)},
            "helpUri": f"https://cwe.mitre.org/data/definitions/{cwe_num}.html",
        })

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "skill-shield",
                    "semanticVersion": "0.6.1",
                    "informationUri": "https://clawhub.ai/yx2601816404-sys/skill-shield",
                    "rules": rules,
                },
                "extensions": [{
                    "name": "cwe",
                    "version": "4.14",
                    "informationUri": "https://cwe.mitre.org/",
                    "taxa": taxa,
                }] if taxa else [],
            },
            "invocations": [{
                "executionSuccessful": True,
                "commandLine": f"python3 scan.py {report['skill_path']} --sarif",
                "workingDirectory": {"uri": report["skill_path"]},
            }],
            "results": results,
            "taxonomies": [{
                "name": "CWE",
                "version": "4.14",
                "informationUri": "https://cwe.mitre.org/",
                "organization": "MITRE",
                "shortDescription": {"text": "Common Weakness Enumeration"},
                "taxa": taxa,
            }] if taxa else [],
            "properties": {
                "skillName": skill_name,
                "securityRating": report["security_rating"],
                "complianceRating": report["compliance_rating"],
                "recommendation": report["recommendation"],
                "totalFindings": report["summary"]["total_findings"],
                "patternCount": report["pattern_count"],
                "isDocumentationOnly": report.get("is_documentation_only", False),
            },
        }],
    }

    return sarif


# ---------------------------------------------------------------------------
# Batch scan mode (v0.6.1)
# ---------------------------------------------------------------------------

def scan_single_skill(skill_dir):
    """Scan a single skill and return summary dict."""
    skill_md, script_files = find_skill_files(skill_dir, max_files=MAX_SCRIPT_FILES)
    if not skill_md.exists() and not script_files:
        return None
    is_doc_only = len(script_files) == 0
    tools_declared = extract_tools_from_skill_md(skill_md)
    tools_in_code = extract_tools_from_code(script_files)
    perm_audit = audit_permissions(tools_declared, tools_in_code)
    findings = scan_dangerous_patterns(script_files, skill_md)
    findings.extend(scan_obfuscated_content(script_files, skill_md))
    sec_rating, sec_reason = compute_security_rating(findings, is_doc_only)
    comp_rating, comp_reason = compute_compliance_rating(perm_audit)
    recommendation, rec_reasons = compute_recommendation(sec_rating, comp_rating, is_doc_only)
    high_count = sum(1 for f in findings if f["severity"] >= 4)
    return {
        "name": skill_dir.name,
        "security_rating": sec_rating,
        "compliance_rating": comp_rating,
        "recommendation": recommendation,
        "total_findings": len(findings),
        "high_findings": high_count,
        "is_doc_only": is_doc_only,
        "permissions_declared": len(tools_declared),
        "permissions_found": len(tools_in_code),
    }


def batch_scan(parent_dir, args):
    """Scan all subdirectories as separate skills."""
    from collections import Counter
    results = []
    dirs = sorted(d for d in parent_dir.iterdir() if d.is_dir() and not d.name.startswith('.'))
    total = len(dirs)
    for i, d in enumerate(dirs):
        try:
            r = scan_single_skill(d)
            if r:
                results.append(r)
        except Exception as e:
            results.append({"name": d.name, "security_rating": "ERR", "error": str(e)})
        if (i + 1) % 20 == 0:
            print(f"  Scanned {i+1}/{total}...", file=sys.stderr)

    # Stats
    sec = Counter(r["security_rating"] for r in results)
    recs = Counter(r.get("recommendation", "?") for r in results)
    doc_only = sum(1 for r in results if r.get("is_doc_only"))
    safe = sec.get("A", 0) + sec.get("B", 0)
    risky = sec.get("C", 0) + sec.get("D", 0) + sec.get("F", 0)

    if args.json_summary:
        summary = {
            "total": len(results),
            "safe": safe, "risky": risky, "doc_only": doc_only,
            "ratings": dict(sec), "recommendations": dict(recs),
            "skills": results,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        if args.output_dir:
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / "batch-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        # Markdown table
        print(f"# Skill Shield Batch Scan — {len(results)} skills\n")
        print(f"| Metric | Count |")
        print(f"|--------|-------|")
        print(f"| Total | {len(results)} |")
        print(f"| Safe (A/B) | {safe} ({safe*100//max(len(results),1)}%) |")
        print(f"| Risky (C/D/F) | {risky} ({risky*100//max(len(results),1)}%) |")
        print(f"| Doc-only | {doc_only} |")
        print()
        print(f"| Rating | Count |")
        print(f"|--------|-------|")
        for rating in ["A", "B", "C", "D", "F", "N/A"]:
            if sec.get(rating):
                print(f"| {rating} | {sec[rating]} |")
        print()
        print(f"| Skill | Security | Compliance | Recommendation | Findings |")
        print(f"|-------|----------|------------|----------------|----------|")
        for r in sorted(results, key=lambda x: {"F":0,"D":1,"C":2,"B":3,"A":4,"N/A":5,"ERR":-1}.get(x["security_rating"],6)):
            print(f"| {r['name']} | {r['security_rating']} | {r.get('compliance_rating','?')} | {r.get('recommendation','?')} | {r.get('total_findings',0)} |")

        if args.output_dir:
            # Also write JSON
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            summary = {"total": len(results), "safe": safe, "risky": risky, "skills": results}
            (out / "batch-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print(f"\nScanned {len(results)} skills: {safe} safe, {risky} risky, {doc_only} doc-only", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Shield v0.6.1 — security audit for ClawHub skills")
    parser.add_argument("skill_dir", help="Path to skill directory (or parent dir with --batch)")
    parser.add_argument("--output-dir", "-o", help="Directory to write reports")
    parser.add_argument("--sarif", action="store_true", help="Output SARIF 2.1.0 format")
    parser.add_argument("--batch", action="store_true", help="Scan all subdirectories as separate skills")
    parser.add_argument("--json-summary", action="store_true", help="With --batch, output JSON summary")
    args = parser.parse_args()

    if args.batch:
        batch_scan(Path(args.skill_dir).resolve(), args)
        return

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        print(f"Error: {skill_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    skill_md, script_files = find_skill_files(skill_dir)

    if not skill_md.exists() and not script_files:
        print(f"Error: No SKILL.md or script files found in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # Detect documentation-only skills
    is_doc_only = len(script_files) == 0

    # Extract permissions
    tools_declared = extract_tools_from_skill_md(skill_md)
    tools_in_code = extract_tools_from_code(script_files)

    # Permission audit
    perm_audit = audit_permissions(tools_declared, tools_in_code)

    # Scan for dangerous patterns (context-aware)
    findings = scan_dangerous_patterns(script_files, skill_md)

    # Anti-obfuscation scan
    obf_findings = scan_obfuscated_content(script_files, skill_md)
    findings.extend(obf_findings)

    # Dual rating (v0.3.0)
    sec_rating, sec_reason = compute_security_rating(findings, is_doc_only)
    comp_rating, comp_reason = compute_compliance_rating(perm_audit)
    recommendation, rec_reason = compute_recommendation(sec_rating, comp_rating, is_doc_only)
    rating_reasons = build_rating_reasons(findings, perm_audit, sec_rating, comp_rating, is_doc_only)

    # Build reports
    json_report = build_json_report(
        skill_dir, perm_audit, findings,
        sec_rating, sec_reason, comp_rating, comp_reason,
        recommendation, rec_reason, rating_reasons, is_doc_only
    )
    md_report = build_md_report(json_report)

    # Output
    if args.sarif:
        sarif_report = build_sarif_report(json_report)
        print(json.dumps(sarif_report, indent=2, ensure_ascii=False))
        if args.output_dir:
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / "report.sarif").write_text(json.dumps(sarif_report, indent=2, ensure_ascii=False))
            print(f"\nSARIF report written to {out}/report.sarif", file=sys.stderr)
    else:
        print("--- JSON START ---")
        print(json.dumps(json_report, indent=2, ensure_ascii=False))
        print("--- JSON END ---")
        print()
        print("--- MD START ---")
        print(md_report)
        print("--- MD END ---")

        if args.output_dir:
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / "report.json").write_text(json.dumps(json_report, indent=2, ensure_ascii=False))
            (out / "report.md").write_text(md_report)
            print(f"\nReports written to {out}/", file=sys.stderr)

    # Exit code based on security rating
    exit_codes = {"A": 0, "B": 0, "C": 1, "D": 1, "F": 2, "N/A": 0}
    sys.exit(exit_codes.get(sec_rating, 1))


if __name__ == "__main__":
    main()

"""Advanced security rules and patterns based on latest AI security research.

This module includes patterns from:
- OWASP LLM Top 10
- Prompt injection research (direct, indirect, encoded)
- Typoglycemia attacks
- Tool misuse / Confused Deputy attacks
- Supply chain attacks (typosquatting, combosquatting)
- AI-enabled malware techniques (PROMPTFLUX, PROMPTSTEAL patterns)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any, Set


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """A security finding."""
    rule_id: str
    title: str
    description: str
    severity: Severity
    file_path: str
    line_number: int
    code_snippet: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None
    cwe_id: Optional[str] = None


# =============================================================================
# PYTHON DANGEROUS PATTERNS
# =============================================================================

PYTHON_DANGEROUS_CALLS = {
    "eval": {
        "severity": Severity.CRITICAL,
        "title": "Dangerous eval() usage",
        "description": "eval() with user-controlled input can lead to arbitrary code execution (RCE)",
        "remediation": "Use ast.literal_eval() for safe evaluation of literals only; avoid dynamic execution entirely",
        "cwe": "CWE-95",
        "references": ["https://owasp.org/www-community/vulnerabilities/Direct_Dynamic_Code_Evaluation_Eval_Dangerous_Functions"],
    },
    "exec": {
        "severity": Severity.CRITICAL,
        "title": "Dangerous exec() usage",
        "description": "exec() with user-controlled input can lead to arbitrary code execution (RCE)",
        "remediation": "Avoid dynamic code execution; use safer alternatives like configuration files or DSLs",
        "cwe": "CWE-95",
    },
    "compile": {
        "severity": Severity.HIGH,
        "title": "Dynamic code compilation",
        "description": "compile() can be used to obfuscate malicious code and bypass static analysis",
        "remediation": "Avoid dynamic code compilation in production; this is commonly used for evasion",
        "cwe": "CWE-94",
    },
    "__import__": {
        "severity": Severity.MEDIUM,
        "title": "Dynamic import detected",
        "description": "Dynamic imports can bypass static analysis and load malicious modules at runtime",
        "remediation": "Use static imports; if dynamic loading is needed, implement an explicit allowlist",
        "cwe": "CWE-114",
    },
    "getattr": {
        "severity": Severity.LOW,
        "title": "Dynamic attribute access",
        "description": "getattr() with user-controlled input can access unintended attributes/methods",
        "remediation": "Validate attribute names against an allowlist",
        "cwe": "CWE-470",
    },
    "setattr": {
        "severity": Severity.MEDIUM,
        "title": "Dynamic attribute modification",
        "description": "setattr() can modify object behavior dynamically, potentially for malicious purposes",
        "remediation": "Avoid modifying attributes dynamically with user input",
        "cwe": "CWE-470",
    },
}

PYTHON_SUBPROCESS_PATTERNS = {
    "subprocess.call": {"severity": Severity.HIGH, "shell_risk": True},
    "subprocess.run": {"severity": Severity.HIGH, "shell_risk": True},
    "subprocess.Popen": {"severity": Severity.HIGH, "shell_risk": True},
    "subprocess.check_output": {"severity": Severity.HIGH, "shell_risk": True},
    "subprocess.check_call": {"severity": Severity.HIGH, "shell_risk": True},
    "os.system": {"severity": Severity.CRITICAL, "shell_risk": False},
    "os.popen": {"severity": Severity.HIGH, "shell_risk": False},
    "os.popen2": {"severity": Severity.HIGH, "shell_risk": False},
    "os.popen3": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnl": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnle": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnlp": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnlpe": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnv": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnve": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnvp": {"severity": Severity.HIGH, "shell_risk": False},
    "os.spawnvpe": {"severity": Severity.HIGH, "shell_risk": False},
}

PYTHON_NETWORK_PATTERNS = {
    "requests.post": {"severity": Severity.MEDIUM, "title": "HTTP POST request"},
    "requests.put": {"severity": Severity.MEDIUM, "title": "HTTP PUT request"},
    "requests.patch": {"severity": Severity.MEDIUM, "title": "HTTP PATCH request"},
    "urllib.request.urlopen": {"severity": Severity.MEDIUM, "title": "URL fetch"},
    "urllib.request.Request": {"severity": Severity.MEDIUM, "title": "HTTP request"},
    "http.client.HTTPConnection.request": {"severity": Severity.MEDIUM, "title": "HTTP request"},
    "http.client.HTTPSConnection.request": {"severity": Severity.MEDIUM, "title": "HTTPS request"},
    "socket.socket": {"severity": Severity.LOW, "title": "Raw socket creation"},
    "socket.create_connection": {"severity": Severity.LOW, "title": "Network connection"},
}

PYTHON_FILE_PATTERNS = {
    "open": {"severity": Severity.LOW, "title": "File operation"},
    "shutil.copy": {"severity": Severity.LOW, "title": "File copy"},
    "shutil.copy2": {"severity": Severity.LOW, "title": "File copy with metadata"},
    "shutil.move": {"severity": Severity.LOW, "title": "File move"},
    "shutil.copytree": {"severity": Severity.LOW, "title": "Directory copy"},
    "os.remove": {"severity": Severity.MEDIUM, "title": "File deletion"},
    "os.unlink": {"severity": Severity.MEDIUM, "title": "File deletion"},
    "os.rmdir": {"severity": Severity.MEDIUM, "title": "Directory removal"},
    "os.removedirs": {"severity": Severity.HIGH, "title": "Recursive directory removal"},
    "shutil.rmtree": {"severity": Severity.HIGH, "title": "Recursive directory deletion"},
    "pathlib.Path.unlink": {"severity": Severity.MEDIUM, "title": "File deletion"},
    "pathlib.Path.rmdir": {"severity": Severity.MEDIUM, "title": "Directory removal"},
}

PYTHON_OBFUSCATION_PATTERNS = {
    "base64.b64decode": {"severity": Severity.MEDIUM, "title": "Base64 decoding"},
    "base64.b32decode": {"severity": Severity.MEDIUM, "title": "Base32 decoding"},
    "base64.b16decode": {"severity": Severity.MEDIUM, "title": "Base16 decoding"},
    "binascii.unhexlify": {"severity": Severity.MEDIUM, "title": "Hex decoding"},
    "binascii.a2b_base64": {"severity": Severity.MEDIUM, "title": "Base64 decoding"},
    "zlib.decompress": {"severity": Severity.MEDIUM, "title": "Decompression (possible obfuscation)"},
    "gzip.decompress": {"severity": Severity.MEDIUM, "title": "Decompression (possible obfuscation)"},
    "marshal.loads": {"severity": Severity.HIGH, "title": "Python object deserialization"},
    "pickle.loads": {"severity": Severity.CRITICAL, "title": "Pickle deserialization (RCE risk)"},
    "yaml.load": {"severity": Severity.HIGH, "title": "YAML load without safe mode"},
    "json.loads": {"severity": Severity.LOW, "title": "JSON deserialization"},
    "codecs.decode": {"severity": Severity.MEDIUM, "title": "Codec decoding"},
}

# =============================================================================
# SECRET DETECTION PATTERNS
# =============================================================================

SECRET_PATTERNS = {
    "aws_access_key_id": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": Severity.CRITICAL,
        "title": "AWS Access Key ID detected",
        "description": "Hardcoded AWS Access Key ID found in source code",
        "cwe": "CWE-798",
    },
    "aws_secret_access_key": {
        "pattern": r"['\"\s][0-9a-zA-Z/+]{40}['\"\s]",
        "severity": Severity.HIGH,
        "title": "Potential AWS Secret Access Key",
        "description": "Possible hardcoded AWS Secret Access Key (40 char base64-like string)",
        "cwe": "CWE-798",
    },
    "private_key": {
        "pattern": r"-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
        "severity": Severity.CRITICAL,
        "title": "Private key detected",
        "description": "Hardcoded private key found in source code",
        "cwe": "CWE-798",
    },
    "github_token": {
        "pattern": r"gh[pousr]_[A-Za-z0-9_]{36,}",
        "severity": Severity.CRITICAL,
        "title": "GitHub token detected",
        "description": "Hardcoded GitHub personal access token found",
        "cwe": "CWE-798",
    },
    "slack_token": {
        "pattern": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}(-[a-zA-Z0-9]{24})?",
        "severity": Severity.CRITICAL,
        "title": "Slack token detected",
        "description": "Hardcoded Slack API token found",
        "cwe": "CWE-798",
    },
    "google_api_key": {
        "pattern": r"AIza[0-9A-Za-z_-]{35}",
        "severity": Severity.CRITICAL,
        "title": "Google API Key detected",
        "description": "Hardcoded Google API key found",
        "cwe": "CWE-798",
    },
    "generic_api_key": {
        "pattern": r"(?i)(?:api[_-]?key|apikey|api_token)\s*[:=]\s*[\"']?[a-zA-Z0-9_\-]{16,}[\"']?",
        "severity": Severity.HIGH,
        "title": "Potential API key",
        "description": "Possible hardcoded API key detected",
        "cwe": "CWE-798",
    },
    "password_assignment": {
        "pattern": r"(?i)(?:password|passwd|pwd)\s*=\s*[\"'][^\"']{8,}[\"']",
        "severity": Severity.MEDIUM,
        "title": "Potential hardcoded password",
        "description": "Possible hardcoded password in source",
        "cwe": "CWE-798",
    },
    "bearer_token": {
        "pattern": r"(?i)bearer\s+[a-zA-Z0-9_\-\.=]{20,}",
        "severity": Severity.HIGH,
        "title": "Bearer token detected",
        "description": "Possible hardcoded bearer token",
        "cwe": "CWE-798",
    },
    "jwt_token": {
        "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
        "severity": Severity.HIGH,
        "title": "JWT token detected",
        "description": "Possible hardcoded JWT token",
        "cwe": "CWE-798",
    },
    "openai_api_key": {
        "pattern": r"sk-[a-zA-Z0-9]{20,}",
        "severity": Severity.CRITICAL,
        "title": "OpenAI API Key pattern",
        "description": "Possible OpenAI API key detected (starts with 'sk-')",
        "cwe": "CWE-798",
    },
}

# =============================================================================
# BASH DANGEROUS PATTERNS
# =============================================================================

BASH_PATTERNS = {
    "curl_pipe_bash": {
        "pattern": r"curl\s+(?:-[A-Za-z]*\s+)*[^|]*\|\s*(?:sudo\s+)?(bash|sh|zsh)",
        "severity": Severity.CRITICAL,
        "title": "curl | bash pattern",
        "description": "Downloads and executes remote code without verification - supply chain attack vector",
        "remediation": "Download to file, verify checksum/signature, then execute",
        "cwe": "CWE-494",
    },
    "wget_pipe_shell": {
        "pattern": r"wget\s+.*\s+-O\s*-\s*\|\s*(?:sudo\s+)?(bash|sh|zsh)",
        "severity": Severity.CRITICAL,
        "title": "wget pipe to shell",
        "description": "Downloads and executes remote code without verification",
        "remediation": "Download to file, verify checksum/signature, then execute",
        "cwe": "CWE-494",
    },
    "fetch_pipe_shell": {
        "pattern": r"fetch\s+.*\s+-o\s*-\s*\|\s*(?:sudo\s+)?(bash|sh|zsh)",
        "severity": Severity.CRITICAL,
        "title": "fetch pipe to shell",
        "description": "Downloads and executes remote code without verification",
        "cwe": "CWE-494",
    },
    "rm_rf_root": {
        "pattern": r"rm\s+-[rf]*f[rf]*\s+(?:/\s*$|/~|/System|/Windows|/boot|/etc|/usr|/var|/bin|/sbin|/lib)",
        "severity": Severity.CRITICAL,
        "title": "Dangerous rm -rf",
        "description": "Recursive deletion of system directories - destructive operation",
        "remediation": "Verify target path is correct and scoped to intended directory",
        "cwe": "CWE-14",
    },
    "rm_rf_relative": {
        "pattern": r"rm\s+-[rf]*f[rf]*\s+\.\.",
        "severity": Severity.HIGH,
        "title": "rm -rf with parent directory reference",
        "description": "Recursive deletion using relative path that may traverse directories",
        "remediation": "Use absolute paths and validate target",
    },
    "eval_user_input": {
        "pattern": r"eval\s+[\"']?\$[{@*]",
        "severity": Severity.CRITICAL,
        "title": "eval with user input",
        "description": "eval with $@, $*, or $1 can execute arbitrary commands from user input",
        "remediation": "Avoid eval entirely; use functions or case statements",
        "cwe": "CWE-95",
    },
    "unquoted_variable": {
        "pattern": r"(?:eval|exec)\s+\$\w+",
        "severity": Severity.HIGH,
        "title": "Unquoted variable in eval/exec",
        "description": "Unquoted variable expansion can lead to command injection",
        "remediation": "Quote variables: \"$VAR\" or use arrays",
        "cwe": "CWE-78",
    },
    "backtick_command": {
        "pattern": r"`[^`]*\$\w+[^`]*`",
        "severity": Severity.MEDIUM,
        "title": "Command substitution with variable",
        "description": "Backtick command substitution with variables can be dangerous",
        "remediation": "Use $() instead of backticks and quote variables",
    },
    "sudo_no_password": {
        "pattern": r"sudo\s+(?:-S\s+|.*NOPASSWD)",
        "severity": Severity.HIGH,
        "title": "Passwordless sudo detected",
        "description": "Script uses passwordless sudo which bypasses authentication",
        "remediation": "Remove NOPASSWD from sudoers or use proper authentication",
    },
    "chmod_executable": {
        "pattern": r"chmod\s+\+x.*\.(sh|bin|exe|run)",
        "severity": Severity.LOW,
        "title": "Making downloaded file executable",
        "description": "Script makes file executable - ensure source is trusted",
    },
    "chmod_777": {
        "pattern": r"chmod\s+(?:-R\s+)?777",
        "severity": Severity.HIGH,
        "title": "Overly permissive file permissions",
        "description": "chmod 777 grants full read/write/execute to all users",
        "remediation": "Use minimal necessary permissions (e.g., 755 or 644)",
        "cwe": "CWE-732",
    },
    "download_execute_temp": {
        "pattern": r"(curl|wget).*\/tmp.*chmod.*\.",
        "severity": Severity.HIGH,
        "title": "Download to temp and execute",
        "description": "Downloads file to /tmp and makes executable - temp directory is world-writable",
        "remediation": "Use secure temp file creation (mktemp) and verify before execution",
    },
    "nc_reverse_shell": {
        "pattern": r"nc\s+(?:-[e]\s+|.*\|.*)(?:/bin/bash|/bin/sh|bash|sh)",
        "severity": Severity.CRITICAL,
        "title": "Netcat reverse shell",
        "description": "Creates reverse shell connection - common backdoor technique",
        "cwe": "CWE-78",
    },
    "bash_reverse_shell": {
        "pattern": r"bash\s+-i\s+>&\s+/dev/tcp/",
        "severity": Severity.CRITICAL,
        "title": "Bash reverse shell",
        "description": "Creates reverse shell using bash /dev/tcp feature",
        "cwe": "CWE-78",
    },
    "mkfifo_reverse_shell": {
        "pattern": r"mkfifo.*\/dev\/tcp\/",
        "severity": Severity.CRITICAL,
        "title": "FIFO-based reverse shell",
        "description": "Creates reverse shell using named pipe and /dev/tcp",
        "cwe": "CWE-78",
    },
    "base64_decode_execute": {
        "pattern": r"base64\s+.*\|\s*(bash|sh|zsh|eval)",
        "severity": Severity.CRITICAL,
        "title": "Base64 decode and execute",
        "description": "Decodes base64 and immediately executes - common obfuscation technique",
        "remediation": "Never execute decoded content without inspection",
        "cwe": "CWE-94",
    },
    "python_one_liner": {
        "pattern": r"python[23]?\s+-c\s+[\"'].*(?:socket|subprocess|os\.system|pty)",
        "severity": Severity.HIGH,
        "title": "Python one-liner with system/shell access",
        "description": "Python one-liner that may create shell or network connection",
        "cwe": "CWE-78",
    },
    "telnet_backdoor": {
        "pattern": r"telnet.*\|\s*(?:/bin/bash|/bin/sh|bash|sh)",
        "severity": Severity.CRITICAL,
        "title": "Telnet pipe to shell",
        "description": "Creates backdoor via telnet piped to shell",
        "cwe": "CWE-78",
    },
}

# =============================================================================
# PROMPT INJECTION PATTERNS (SKILL.MD CONTENT)
# =============================================================================
# NOTE: The following patterns are SECURITY DETECTION RULES used to identify
# prompt injection attacks in skill content. These are DEFENSIVE patterns - 
# they detect when someone tries to inject malicious instructions.
# They do NOT perform any injection themselves.

PROMPT_INJECTION_PATTERNS = {
    # Direct injection attempts - DETECTION ONLY
    "ignore_instructions": {
        "pattern": r"(?i)(?:ignore|disregard)\s+(?:all\s+)?(?:previous|prior|earlier|above)\s+(?:instructions?|directives?|commands?|prompts?)",
        "severity": Severity.HIGH,
        "title": "Prompt injection: ignore instructions",
        "description": "Contains pattern attempting to override previous instructions",
        "cwe": "CWE-77",
    },
    "developer_mode": {
        "pattern": r"(?i)(?:developer|debug|admin|root)\s+(?:mode|access|override)",
        "severity": Severity.HIGH,
        "title": "Prompt injection: privilege escalation",
        "description": "Attempts to activate privileged/developer mode",
        "cwe": "CWE-269",
    },
    "reveal_prompt": {
        "pattern": r"(?i)(?:reveal|show|display|tell|repeat)\s+(?:your|the|above|previous)\s+(?:system\s+)?(?:prompt|instructions?|directives?)",
        "severity": Severity.HIGH,
        "title": "Prompt injection: system prompt extraction",
        "description": "Attempts to extract system prompt or instructions",
    },
    "dan_jailbreak": {
        "pattern": r"(?i)\b(?:DAN|do\s+anything\s+now|jailbreak|DUDE|STAN)\b",
        "severity": Severity.MEDIUM,
        "title": "Potential jailbreak attempt",
        "description": "References known jailbreak personas (DAN, STAN, etc.)",
    },
    "role_play": {
        "pattern": r"(?i)(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|imagine\s+you\s+are)",
        "severity": Severity.LOW,
        "title": "Role-playing instruction",
        "description": "Attempts to change AI persona through role-play",
    },
    "bypass_safety": {
        "pattern": r"(?i)(?:bypass|ignore|disable)\s+(?:safety|security|restrictions?|guidelines?|filters?)",
        "severity": Severity.HIGH,
        "title": "Prompt injection: safety bypass",
        "description": "Explicitly attempts to bypass safety controls",
    },
    "hypothetical": {
        "pattern": r"(?i)(?:hypothetically|for\s+educational|in\s+a\s+fictional|as\s+a\s+thought\s+experiment)",
        "severity": Severity.LOW,
        "title": "Hypothetical framing",
        "description": "Uses hypothetical framing to potentially bypass restrictions",
    },
    "encoded_payload": {
        "pattern": r"(?i)(?:base64|decode|decrypt|unscramble)\s+(?:this|the\s+following|below)",
        "severity": Severity.MEDIUM,
        "title": "Potential encoded payload",
        "description": "References encoding/decoding which may hide malicious instructions",
    },
    "confused_deputy": {
        "pattern": r"(?i)(?:thought|observation)\s*[:\[]\s*\{?\s*[\"']?action",
        "severity": Severity.HIGH,
        "title": "Potential ReAct injection",
        "description": "Contains ReAct-style thought/action pattern that may hijack agent reasoning",
    },
}

# =============================================================================
# TYPOGLYCEMIA PATTERNS (Scrambled word attacks)
# =============================================================================

TYPOGLYCEMIA_KEYWORDS = [
    # Original -> Scrambled variants (first/last letter preserved)
    ("ignore", ["ignroe", "iginore", "ignoer", "ignreo"]),
    ("bypass", ["bpyass", "bysapss", "bypsas", "bapssy"]),
    ("override", ["ovverride", "overide", "ovriride", "overrdei"]),
    ("reveal", ["revael", "reveall", "reval"]),
    ("delete", ["delte", "deelte", "dlete"]),
    ("system", ["systme", "sytsem", "sysetm"]),
    ("previous", ["prevoius", "pervious", "pervoius"]),
    ("instructions", ["instrucitons", "instrucctions", "instrucions"]),
    ("password", ["passsword", "pasword", "passwrod"]),
    ("secret", ["secert", "secrt", "seccret"]),
]

# =============================================================================
# SUPPLY CHAIN / TYPOQUATTING PATTERNS
# =============================================================================

SUPPLY_CHAIN_PATTERNS = {
    "typosquatting": {
        "description": "Package name similar to popular package with common typos",
        "indicators": [
            r"^(.+)s$",  # plural vs singular (requests vs request)
            r"^(.+)-(.+)$",  # hyphen vs underscore (some-package vs some_package)
            r"^(.+)_(.+)$",  # underscore vs hyphen
            r"^(.+)lib$",  # adding/removing lib suffix
            r"^lib(.+)$",
            r"^py(.+)$",  # adding/removing py prefix
            r"^(.+)py$",
        ],
    },
    "homoglyph": {
        "description": "Use of similar-looking Unicode characters",
        "indicators": [
            "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗",  # Mathematical monospace
            "⓪①②③④⑤⑥⑦⑧⑨",  # Circled numbers
            "ａｂｃｄｅｆ",  # Fullwidth characters
        ],
    },
}

# =============================================================================
# SKILL-SPECIFIC PATTERNS
# =============================================================================

SKILL_MD_PATTERNS = {
    **PROMPT_INJECTION_PATTERNS,  # Include all prompt injection patterns
    
    "ignore_security": {
        "pattern": r"(?i)(ignore|bypass|disable|turn off).*\bsecurity\b",
        "severity": Severity.HIGH,
        "title": "Instructions to ignore security",
        "description": "Skill explicitly instructs to disable security features",
    },
    "ignore_warnings": {
        "pattern": r"(?i)(ignore|disregard|dismiss)\s+(?:any\s+)?(?:warning|alert|error)",
        "severity": Severity.HIGH,
        "title": "Instructions to ignore warnings",
        "description": "Skill instructs to dismiss security warnings",
    },
    "suspicious_url_free_tld": {
        "pattern": r"https?://(?:[a-z0-9-]+\.)*(?:tk|ml|ga|cf|gq|top|xyz|click|download)/",
        "severity": Severity.MEDIUM,
        "title": "Suspicious TLD in URL",
        "description": "URL uses free/cheap domain often associated with malicious sites",
    },
    "suspicious_url_ip": {
        "pattern": r"https?://(?:\d{1,3}\.){3}\d{1,3}",
        "severity": Severity.MEDIUM,
        "title": "IP address URL",
        "description": "URL uses raw IP address - common in malicious sites",
    },
    "pastebin_raw": {
        "pattern": r"https?://(?:pastebin\.com/raw/|gist\.githubusercontent\.com/)",
        "severity": Severity.MEDIUM,
        "title": "Raw code hosting URL",
        "description": "Links to raw code on paste services - potential malware delivery",
    },
    "excessive_length": {
        # This is checked programmatically, not via regex
        "pattern": None,
        "severity": Severity.INFO,
        "title": "Very long description",
        "description": "Description is unusually long - possible obfuscation",
    },
    "obfuscated_javascript": {
        "pattern": r"(?i)(?:eval\s*\(|function\s*\(\s*\)\s*\{[^}]{100,}\}\s*\(\s*\))",
        "severity": Severity.HIGH,
        "title": "Obfuscated JavaScript",
        "description": "Contains obfuscated JavaScript patterns",
    },
    "data_exfiltration": {
        "pattern": r"(?i)(?:exfiltrate|send\s+data|upload\s+file|transmit\s+to)",
        "severity": Severity.HIGH,
        "title": "Potential data exfiltration",
        "description": "References sending data to external locations",
    },
}

# =============================================================================
# PERMISSION-RELATED CHECKS
# =============================================================================

PERMISSION_CHECKS = {
    "elevated_no_ask": {
        "severity": Severity.MEDIUM,
        "title": "Elevated permission without ask mode",
        "description": "Skill requests elevated permissions but doesn't use ask mode for sensitive operations",
        "remediation": "Consider using ask mode for destructive or sensitive operations",
    },
    "broad_permissions": {
        "severity": Severity.LOW,
        "title": "Broad tool permissions",
        "description": "Skill requests access to many tools - principle of least privilege violated",
    },
    "dangerous_combination": {
        "severity": Severity.CRITICAL,
        "title": "Dangerous tool combination",
        "description": "exec + network tools can enable download-and-execute attacks",
    },
}

# Map of dangerous tool combinations
DANGEROUS_TOOL_COMBINATIONS: List[Set[str]] = [
    {"exec", "browser"},  # Can download and execute
    {"exec", "web_search"},  # Can find and execute payloads
    {"gateway", "exec"},  # Can reconfigure and execute
    {"nodes", "exec"},  # Can control devices and execute
]

# Tool descriptions for risk assessment
TOOL_RISK_LEVELS = {
    "exec": {"severity": Severity.CRITICAL, "description": "execute arbitrary shell commands"},
    "browser": {"severity": Severity.HIGH, "description": "control web browsers and navigate to URLs"},
    "web_search": {"severity": Severity.MEDIUM, "description": "search the web and retrieve content"},
    "web_fetch": {"severity": Severity.MEDIUM, "description": "fetch content from URLs"},
    "message": {"severity": Severity.MEDIUM, "description": "send messages through various channels"},
    "gateway": {"severity": Severity.CRITICAL, "description": "restart and reconfigure the Clawdbot daemon"},
    "nodes": {"severity": Severity.HIGH, "description": "control paired devices and access cameras"},
    "cron": {"severity": Severity.MEDIUM, "description": "schedule automated tasks"},
    "process": {"severity": Severity.HIGH, "description": "manage and interact with system processes"},
    "sessions_spawn": {"severity": Severity.MEDIUM, "description": "spawn new agent sessions"},
    "write": {"severity": Severity.MEDIUM, "description": "write files to the system"},
    "edit": {"severity": Severity.MEDIUM, "description": "modify existing files"},
}

# =============================================================================
# AI-ENABLED MALWARE PATTERNS (Based on PROMPTFLUX, PROMPTSTEAL research)
# =============================================================================

AI_MALWARE_PATTERNS = {
    "llm_api_call": {
        "pattern": r"(?i)(?:openai|anthropic|gemini|claude|gpt-)\.\w+\s*\(|api\.openai\.com|generativelanguage\.googleapis",
        "severity": Severity.MEDIUM,
        "title": "LLM API call detected",
        "description": "Skill calls external LLM APIs - may be self-modifying or using 'just-in-time' generation",
    },
    "dynamic_code_generation": {
        "pattern": r"(?i)(?:generate.*code|create.*script|write.*program).*(?:execute|run|eval)",
        "severity": Severity.HIGH,
        "title": "Dynamic code generation and execution",
        "description": "Generates code dynamically and executes it - PROMPTFLUX-like behavior",
    },
    "code_obfuscation_request": {
        "pattern": r"(?i)(?:obfuscate|make.*unreadable|hide.*code|evade.*detection)",
        "severity": Severity.HIGH,
        "title": "Code obfuscation intent",
        "description": "Explicitly requests code obfuscation - evasion technique",
    },
    "self_modification": {
        "pattern": r"(?i)(?:rewrite.*self|modify.*own|update.*source|regenerate.*code)",
        "severity": Severity.CRITICAL,
        "title": "Self-modifying code",
        "description": "Code attempts to modify itself - metamorphic malware pattern",
    },
}

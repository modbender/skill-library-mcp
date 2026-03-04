#!/usr/bin/env python3
"""
TrustMyAgent - Stateless Runner

Runs security checks entirely in memory and optionally sends telemetry.
Leaves no traces on the filesystem.

Usage:
    python3 run.py                  # Full assessment with telemetry
    python3 run.py --dry-run        # Preview telemetry payload without sending
    python3 run.py --local-only     # Run checks without any network calls
    python3 run.py --checks /path/to/checks.json
"""

import argparse
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# Script directory for loading bundled checks
SCRIPT_DIR = Path(__file__).parent.resolve()
CHECKS_DIR = SCRIPT_DIR / "checks"

# Platform detection
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"
PLATFORM_NAME = platform.system().lower()

# Default telemetry endpoint
TELEMETRY_URL = os.environ.get("TRUSTMYAGENT_TELEMETRY_URL", "https://www.trustmyagent.ai/api/telemetry")


def _derive_environment_label(env_info: dict, is_container: bool) -> str:
    """Derive a human-readable environment label from detection results.

    Returns a short string describing where the agent is running, e.g.:
      "cloudflare_worker", "kubernetes_pod", "docker_container",
      "macos_arm64", "macos_x86_64", "linux_x86_64", "linux_aarch64"
    """
    provider = env_info.get("provider", "unknown")
    env_type = env_info.get("type", "bare_metal")

    # Container environments — label by provider
    if is_container or env_type == "container":
        if provider == "cloudflare":
            if os.environ.get("CF_PAGES"):
                return "cloudflare_pages"
            return "cloudflare_worker"
        if provider == "kubernetes":
            return "kubernetes_pod"
        if provider == "docker":
            return "docker_container"
        # Generic container (podman, lxc, etc.)
        return "container"

    # Bare-metal / VM — label by OS and architecture
    system = platform.system().lower()
    arch = platform.machine().lower()  # e.g. x86_64, arm64, aarch64

    if system == "darwin":
        # Normalise Apple Silicon naming
        if arch in ("arm64", "aarch64"):
            return "macos_arm64"
        return f"macos_{arch}"

    if system == "linux":
        return f"linux_{arch}" if arch else "linux"

    if system == "windows":
        return f"windows_{arch}" if arch else "windows"

    return f"{system}_{arch}" if arch else system


def detect_environment() -> dict:
    """Detect the runtime environment (container type, provider, constraints).

    Returns a dict with:
      - type: "container", "vm", "bare_metal"
      - provider: "cloudflare", "docker", "kubernetes", "unknown"
      - detected_env: human-readable label e.g. "cloudflare_worker", "kubernetes_pod",
            "docker_container", "macos_arm64", "linux_x86_64"
      - is_root: bool
      - expected_findings: list of check_ids that are expected in this environment
      - notes: dict mapping check_id -> explanation string
    """
    env_info = {
        "type": "bare_metal",
        "provider": "unknown",
        "is_root": os.geteuid() == 0 if hasattr(os, 'geteuid') else False,
        "expected_findings": [],
        "notes": {},
    }

    # Detect container via multiple signals
    is_container = False

    # Signal 1: /.dockerenv file
    if os.path.exists("/.dockerenv"):
        is_container = True
        env_info["type"] = "container"
        env_info["provider"] = "docker"

    # Signal 2: cgroup contents
    try:
        with open("/proc/1/cgroup") as f:
            cgroup = f.read()
        if any(k in cgroup for k in ("docker", "lxc", "containerd", "kubepods")):
            is_container = True
            env_info["type"] = "container"
            if "kubepods" in cgroup:
                env_info["provider"] = "kubernetes"
    except (IOError, OSError):
        pass

    # Signal 3: Kubernetes service account
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        is_container = True
        env_info["type"] = "container"
        env_info["provider"] = "kubernetes"

    # Signal 4: /run/.containerenv (Podman) or container-type marker
    if os.path.exists("/run/.containerenv"):
        is_container = True
        env_info["type"] = "container"

    # Signal 5: PID 1 is not a typical init system (strong container heuristic)
    if not is_container:
        try:
            with open("/proc/1/sched") as f:
                sched_line = f.readline()
            # In containers, PID 1 is usually not "systemd" or "init"
            if sched_line and not any(k in sched_line.lower() for k in ("systemd", "init", "launchd")):
                is_container = True
                env_info["type"] = "container"
        except (IOError, OSError):
            pass

    # Signal 6: Very few processes running (typical of containers)
    if not is_container and env_info["is_root"]:
        try:
            proc_count = len([d for d in os.listdir("/proc") if d.isdigit()])
            if proc_count <= 20:
                is_container = True
                env_info["type"] = "container"
        except (IOError, OSError):
            pass

    # Detect Cloudflare Workers/containers via explicit env vars
    if os.environ.get("CF_PAGES") or os.environ.get("CLOUDFLARE_WORKER"):
        env_info["provider"] = "cloudflare"
        is_container = True
        env_info["type"] = "container"

    # Heuristic: Cloudflare env var patterns (check regardless of is_container status)
    # Note: __CF_USER_TEXT_ENCODING is a macOS Core Foundation var, not Cloudflare
    if env_info["provider"] == "unknown":
        cf_env_prefixes = ("CLOUDFLARE_", "CF_PAGES", "CF_WORKER", "CF_DEPLOYMENT",
                           "CF_ACCOUNT_ID", "CF_API", "WRANGLER_")
        for var in os.environ:
            var_upper = var.upper()
            if any(var_upper.startswith(p) for p in cf_env_prefixes):
                env_info["provider"] = "cloudflare"
                if not is_container:
                    is_container = True
                    env_info["type"] = "container"
                break

    # Signal 7: OpenClaw container marker env var
    if os.environ.get("OPENCLAW_CONTAINER") or os.environ.get("CONTAINER"):
        is_container = True
        env_info["type"] = "container"

    # Derive a human-readable detected_env label for the agent description.
    # This tells consumers "where is this agent running?" at a glance.
    env_info["detected_env"] = _derive_environment_label(env_info, is_container)

    # Build expected findings based on environment
    if is_container and env_info["is_root"]:
        env_info["expected_findings"].append("PHY-004")
        env_info["notes"]["PHY-004"] = (
            "Running as root is how this container runtime operates (not configurable). "
            "Risk is mitigated by container isolation."
        )
        env_info["expected_findings"].append("INT-005")
        env_info["notes"]["INT-005"] = (
            "/etc/shadow is readable because the process runs as root inside the container. "
            "Container isolation limits the blast radius."
        )

    if is_container:
        # Secrets in env are the standard mechanism for containers
        env_info["expected_findings"].append("SEC-001")
        env_info["notes"]["SEC-001"] = (
            "Environment variables are the standard mechanism for passing API keys to "
            "containerized agents. Consider using a secrets manager for additional protection."
        )
        # DNS may be limited in some container environments
        env_info["expected_findings"].append("NET-003")
        env_info["notes"]["NET-003"] = (
            "DNS resolution may be limited in container environments depending on network "
            "configuration. Verify the container's DNS settings if this is unexpected."
        )
        # Action logging directories may not exist in ephemeral containers
        env_info["expected_findings"].append("SOC-001")
        env_info["notes"]["SOC-001"] = (
            "Ephemeral containers typically don't have persistent log directories. "
            "Agent actions are logged via the session transcript and telemetry instead."
        )
        # crontab may not be available in minimal containers
        env_info["expected_findings"].append("INT-002")
        env_info["notes"]["INT-002"] = (
            "crontab is often unavailable in minimal container images. "
            "This is expected and not a security concern."
        )

    return env_info


def print_banner():
    """Print the Security Agent banner."""
    print()
    print("=" * 60)
    print("   TrustMyAgent (Stateless)")
    print("       In-Memory Security Assessment")
    print("=" * 60)
    print()


def get_agent_name() -> str:
    """Read agent name from IDENTITY.md.

    Searches for IDENTITY.md in the standard OpenClaw locations:
    1. Workspace root (../../IDENTITY.md relative to skill)
    2. Current working directory
    3. OPENCLAW_AGENT_NAME env var as fallback
    """
    # Check environment variable first
    env_name = os.environ.get("OPENCLAW_AGENT_NAME")
    if env_name:
        return env_name

    # Search paths for IDENTITY.md
    search_paths = [
        SCRIPT_DIR.parent.parent / "IDENTITY.md",   # workspace root from skills/trustmyagent/
        SCRIPT_DIR.parent / "IDENTITY.md",           # one level up
        Path.cwd() / "IDENTITY.md",                  # current working directory
        Path.home() / ".openclaw" / "IDENTITY.md",   # global config
    ]

    for identity_path in search_paths:
        try:
            if identity_path.exists():
                content = identity_path.read_text(encoding="utf-8")
                # Parse the # Name section
                in_name_section = False
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.lower() == "# name":
                        in_name_section = True
                        continue
                    if in_name_section:
                        if stripped and not stripped.startswith("#"):
                            return stripped
                        if stripped.startswith("#"):
                            break  # Hit next section without finding name
        except Exception:
            continue

    return "OpenClaw Agent"


def get_agent_id() -> str:
    """Generate agent identifier from hostname."""
    agent_id = os.environ.get("OPENCLAW_AGENT_ID")
    if agent_id:
        return agent_id

    try:
        hostname = subprocess.check_output(["hostname"], text=True, timeout=5).strip()
        return hashlib.sha256(hostname.encode()).hexdigest()[:16]
    except Exception:
        return hashlib.sha256(os.urandom(16)).hexdigest()[:16]


def get_agent_secret() -> str:
    """Get or derive the agent's signing secret.

    The secret is used to HMAC-sign telemetry payloads, proving the agent
    that registered the ID is the same one sending updates. The secret is
    derived from the agent ID + a machine-specific salt so it's stable
    across runs on the same machine but unguessable by others.
    """
    # Explicit secret from environment takes priority
    secret = os.environ.get("TRUSTMYAGENT_AGENT_SECRET")
    if secret:
        return secret

    # Derive from machine-specific data: hostname + username + machine-id
    parts = []
    try:
        parts.append(subprocess.check_output(["hostname"], text=True, timeout=5).strip())
    except Exception:
        parts.append("unknown-host")
    parts.append(os.environ.get("USER", os.environ.get("USERNAME", "unknown")))

    # Try to read machine-id (Linux) or hardware UUID (macOS)
    for mid_path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
        try:
            with open(mid_path) as f:
                parts.append(f.read().strip())
                break
        except (IOError, OSError):
            continue
    else:
        # macOS: use IOPlatformUUID
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                text=True, timeout=5
            )
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    parts.append(line.split('"')[-2])
                    break
        except Exception:
            pass

    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()


def sign_telemetry(payload_json: str, agent_secret: str) -> str:
    """Generate HMAC-SHA256 signature for a telemetry payload."""
    import hmac
    return hmac.new(
        agent_secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()


def load_detection_kb() -> dict:
    """Load the detection knowledge base. Returns check_id -> {risk, remediation, ...} mapping."""
    kb_path = CHECKS_DIR / "detection_kb.json"
    if not kb_path.exists():
        return {}
    try:
        with open(kb_path, "r") as f:
            data = json.load(f)
        return data.get("detections", {})
    except (json.JSONDecodeError, IOError):
        return {}


def load_checks(checks_path: Path = None) -> List[dict]:
    """Load checks from JSON files. Merges main checks with message-based and node/media checks."""
    checks = []
    is_bundled = False

    if checks_path and checks_path.exists():
        with open(checks_path, "r") as f:
            data = json.load(f)
        checks = data.get("checks", [])
    else:
        is_bundled = True
        # Try default locations for main checks
        for default_path in [
            CHECKS_DIR / "openclaw_checks.json",
            CHECKS_DIR / "checks.json",
            SCRIPT_DIR / "checks.json",
        ]:
            if default_path.exists():
                with open(default_path, "r") as f:
                    data = json.load(f)
                checks = data.get("checks", [])
                break

    if not checks:
        print("  Warning: No checks file found, using minimal built-in checks")
        checks = get_builtin_checks()
        is_bundled = True

    # Mark bundled checks as trusted (skip command validation for pre-audited checks)
    if is_bundled:
        for c in checks:
            c["_trusted"] = True

    # Also load message-based (python) checks if available
    for extra_file in ["message_checks.json", "nodes_media_checks.json"]:
        extra_path = CHECKS_DIR / extra_file
        if extra_path.exists():
            try:
                with open(extra_path, "r") as f:
                    extra_data = json.load(f)
                extra_checks = extra_data.get("checks", [])
                for c in extra_checks:
                    c["_trusted"] = True
                checks.extend(extra_checks)
            except (json.JSONDecodeError, IOError):
                pass

    return checks


def get_builtin_checks() -> List[dict]:
    """Minimal built-in security checks."""
    return [
        {
            "check_id": "SYS-001",
            "name": "Non-root execution",
            "category": "system",
            "severity": "critical",
            "bash_command": "test $(id -u) -ne 0 && echo 'PASS' || echo 'FAIL'",
            "expected_output": "PASS",
            "pass_condition": "contains"
        },
        {
            "check_id": "SYS-002",
            "name": "Home directory exists",
            "category": "system",
            "severity": "low",
            "bash_command": "test -d $HOME && echo 'PASS' || echo 'FAIL'",
            "expected_output": "PASS",
            "pass_condition": "contains"
        },
    ]


# Dangerous command patterns
DANGEROUS_PATTERNS = [
    r';\s*rm\s+', r';\s*dd\s+', r';\s*mkfs', r'\$\(.*\)', r'`.*`',
    r'\|\s*bash', r'\|\s*sh\b', r'>\s*/etc/',
    r'>\s*/dev/(?!null)', r'curl.*\|.*sh', r'wget.*\|.*sh',
    r'&&\s*rm\s+', r'/dev/sd[a-z]',
]


def validate_command(command: str) -> Tuple[bool, str]:
    """Validate command for safety."""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Blocked: dangerous pattern"
    return True, ""


def evaluate_pass_condition(stdout: str, returncode: int, check: dict) -> bool:
    """Evaluate whether a check passed based on its condition type.

    Supports two schemas:
      - Legacy: 'expected_pattern' (regex match against stdout)
      - Standard: 'expected_output' + 'pass_condition' with types:
          equals, contains, not_contains, not_equals, exit_code_zero, regex
    """
    # Legacy schema: expected_pattern is a regex
    if "expected_pattern" in check:
        pattern = check["expected_pattern"]
        return bool(re.search(pattern, stdout, re.IGNORECASE))

    # Standard schema: pass_condition + expected_output
    condition = check.get("pass_condition", "contains")
    expected = check.get("expected_output", "")
    output = stdout.strip()

    if condition == "exit_code_zero":
        return returncode == 0
    elif condition == "equals":
        return output == expected
    elif condition == "not_equals":
        return output != expected
    elif condition == "contains":
        return expected in output
    elif condition == "not_contains":
        return expected not in output
    elif condition == "regex":
        return bool(re.search(expected, output, re.IGNORECASE))
    else:
        # Unknown condition, fall back to contains
        return expected in output


def execute_check(check: dict, timeout: int = 30) -> dict:
    """Execute a single check in memory. Dispatches to bash or python handler."""
    check_type = check.get("type", "bash")
    if check_type == "python":
        return execute_python_check(check, timeout)
    return execute_bash_check(check, timeout)


def execute_bash_check(check: dict, timeout: int = 30) -> dict:
    """Execute a bash-based check."""
    check_id = check["check_id"]
    command = check.get("bash_command", "")

    result = {
        "check_id": check_id,
        "name": check.get("name", ""),
        "category": check.get("category", ""),
        "severity": check.get("severity", "medium"),
        "passed": False,
        "output": "",
        "error": "",
        "duration_ms": 0,
    }

    if not command:
        result["error"] = "No bash_command defined"
        result["status"] = "blocked"
        return result

    # Platform check: skip if check declares specific platform requirements
    required_platforms = check.get("platforms")
    if required_platforms and PLATFORM_NAME not in required_platforms:
        result["passed"] = True
        result["output"] = f"Skipped: not applicable on {PLATFORM_NAME}"
        result["status"] = "skipped"
        return result

    # Validate command (skip for pre-audited bundled checks)
    if not check.get("_trusted"):
        is_safe, error = validate_command(command)
        if not is_safe:
            result["error"] = error
            result["status"] = "blocked"
            return result

    # Execute
    start_time = datetime.now()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "LC_ALL": "C"},
            cwd="/tmp"
        )
        result["output"] = proc.stdout[:2000]
        result["error"] = proc.stderr[:500] if proc.returncode != 0 else ""
        result["passed"] = evaluate_pass_condition(proc.stdout, proc.returncode, check)

    except subprocess.TimeoutExpired:
        result["error"] = f"Timeout after {timeout}s"
    except Exception as e:
        result["error"] = str(e)[:200]

    result["duration_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
    return result


# --- Python check handlers (message-based / programmatic sensors) ---

PYTHON_CHECK_HANDLERS = {}


def python_check(check_id: str):
    """Decorator to register a python check handler."""
    def decorator(func):
        PYTHON_CHECK_HANDLERS[check_id] = func
        return func
    return decorator


def execute_python_check(check: dict, timeout: int = 30) -> dict:
    """Execute a python-based programmatic check."""
    check_id = check["check_id"]
    result = {
        "check_id": check_id,
        "name": check.get("name", ""),
        "category": check.get("category", ""),
        "severity": check.get("severity", "medium"),
        "passed": False,
        "output": "",
        "error": "",
        "duration_ms": 0,
    }

    handler = PYTHON_CHECK_HANDLERS.get(check_id)
    if not handler:
        result["error"] = f"No handler registered for {check_id}"
        result["status"] = "blocked"
        return result

    start_time = datetime.now()
    try:
        passed, output = handler(check)
        result["passed"] = passed
        result["output"] = str(output)[:2000]
    except Exception as e:
        result["error"] = str(e)[:200]

    result["duration_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
    return result


def _find_openclaw_config() -> dict:
    """Load the OpenClaw agent config from known locations."""
    search_paths = [
        Path.home() / ".openclaw" / "openclaw.json",
        Path.home() / ".config" / "openclaw" / "openclaw.json",
        Path.home() / ".config" / "claude" / "settings.json",
    ]
    for p in search_paths:
        if p.exists():
            try:
                with open(p) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
    return {}


def _find_session_files(max_files: int = 5) -> List[Path]:
    """Find recent OpenClaw session transcript files."""
    search_dirs = [
        Path.home() / ".openclaw" / "agents",
        Path.home() / ".config" / "openclaw" / "sessions",
        Path.home() / ".claude" / "projects",
    ]
    jsonl_files = []
    for d in search_dirs:
        if d.exists():
            jsonl_files.extend(d.rglob("*.jsonl"))
    # Sort by mtime descending, return most recent
    jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return jsonl_files[:max_files]


def _read_recent_transcript_lines(max_lines: int = 200) -> List[dict]:
    """Read recent lines from the latest session transcript."""
    files = _find_session_files(max_files=1)
    if not files:
        return []
    lines = []
    try:
        with open(files[0]) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return []
    return lines[-max_lines:]


# ---------------------------------------------------------------------------
# SEC-001: Comprehensive secrets-in-environment detection (Python + entropy)
# Replaces the naive bash grep that only matched 'password=', 'secret=', etc.
# ---------------------------------------------------------------------------

@python_check("SEC-001")
def check_env_secrets(check: dict) -> Tuple[bool, str]:
    """Detect secrets in environment variables using pattern matching and entropy analysis."""
    SECRET_PATTERNS = [
        r'(?:password|passwd|pass|pwd)\s*=',
        r'(?:secret|token|key|credential|auth)\s*=',
        r'(?:api[_.]?key|access[_.]?key|secret[_.]?key)\s*=',
        r'AKIA[0-9A-Z]{16}',           # AWS access key
        r'ghp_[A-Za-z0-9_]{36}',       # GitHub PAT
        r'gho_[A-Za-z0-9_]{36}',       # GitHub OAuth
        r'sk-[A-Za-z0-9]{20,}',        # OpenAI/Stripe
        r'xoxb-[0-9]+-',              # Slack bot token
        r'xoxp-[0-9]+-',              # Slack user token
        r'://[^:]+:[^@]+@',           # URLs with embedded credentials
        r'-----BEGIN.*PRIVATE KEY',    # PEM private keys
    ]

    # Env var names that commonly hold secrets
    SECRET_VAR_NAMES = re.compile(
        r'(?:password|passwd|pass|pwd|secret|token|key|credential|auth|'
        r'api_key|access_key|private|signing|encryption|jwt|bearer|'
        r'database_url|redis_url|mongo_url|connection_string)',
        re.IGNORECASE
    )

    # Known safe env vars that match patterns but aren't secrets
    SAFE_VARS = {
        'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'LANG', 'LC_ALL',
        'EDITOR', 'VISUAL', 'PAGER', 'HOSTNAME', 'PWD', 'OLDPWD',
        'SHLVL', 'TMPDIR', 'XDG_RUNTIME_DIR', 'DISPLAY', 'SSH_AUTH_SOCK',
        'GPG_AGENT_INFO', 'COLORTERM', 'TERM_PROGRAM', 'LOGNAME',
        'SSH_AGENT_PID', 'MANPATH', 'INFOPATH', 'CLICOLOR',
        'LSCOLORS', 'LS_COLORS',
    }

    def _shannon_entropy(s: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not s:
            return 0.0
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        length = len(s)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in freq.values()
            if count > 0
        )

    findings = []
    for var_name, val in os.environ.items():
        if var_name in SAFE_VARS:
            continue

        matched = False

        # Check var name looks secret-like and has a substantial value
        if SECRET_VAR_NAMES.search(var_name) and len(val) >= 8:
            findings.append(var_name)
            matched = True

        # Check value against known secret patterns
        if not matched:
            combined = f"{var_name}={val}"
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, combined, re.IGNORECASE):
                    findings.append(var_name)
                    matched = True
                    break

        # High-entropy detection for long values (likely API keys/tokens)
        if not matched and len(val) > 20:
            entropy = _shannon_entropy(val)
            # High entropy (> 4.5 bits/char) in long strings = likely secret
            if entropy > 4.5:
                findings.append(f"{var_name}(high-entropy)")

    if findings:
        # Report var names only, NEVER values
        display = findings[:10]
        return False, f"Potential secrets in env: {', '.join(display)}"
    return True, "No secrets detected in environment variables"


# ---------------------------------------------------------------------------
# SEC-002: Cloud credentials detection (expanded from AWS-only)
# ---------------------------------------------------------------------------

@python_check("SEC-002")
def check_cloud_credentials(check: dict) -> Tuple[bool, str]:
    """Check for cloud provider credentials in environment and credential files."""
    issues = []

    # AWS
    if os.environ.get("AWS_SECRET_ACCESS_KEY"):
        issues.append("aws_secret_key_in_env")
    if os.environ.get("AWS_SESSION_TOKEN"):
        issues.append("aws_session_token_in_env")
    aws_creds = Path.home() / ".aws" / "credentials"
    if aws_creds.exists():
        issues.append("aws_credentials_file")

    # GCP
    gcp_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds and Path(gcp_creds).exists():
        issues.append("gcp_service_account_file")
    if os.environ.get("GCLOUD_SERVICE_KEY"):
        issues.append("gcloud_service_key_in_env")

    # Azure
    if os.environ.get("AZURE_CLIENT_SECRET"):
        issues.append("azure_client_secret_in_env")

    if issues:
        return False, f"Cloud credentials found: {', '.join(issues)}"
    return True, "No cloud credentials exposed"


# ---------------------------------------------------------------------------
# MSG-001: MCP servers from trusted sources (enhanced with allowlist)
# ---------------------------------------------------------------------------

@python_check("MSG-001")
def check_mcp_servers(check: dict) -> Tuple[bool, str]:
    """Check MCP server configurations for untrusted sources."""
    config = _find_openclaw_config()
    mcp_servers = config.get("mcpServers", {})
    if not mcp_servers:
        return True, "No MCP servers configured"

    # Known-good MCP package prefixes
    TRUSTED_NPX_PREFIXES = [
        "@modelcontextprotocol/", "mcp-server-", "@anthropic/",
        "@claude/", "@openclaw/",
    ]

    suspicious = []
    for name, srv in mcp_servers.items():
        cmd = srv.get("command", "")
        args = srv.get("args", [])
        args_str = " ".join(str(a) for a in args)

        # Flag remote URLs (potential C2)
        if re.search(r'https?://|ftp://', args_str):
            suspicious.append(f"{name}: remote URL in args")

        # Flag npx packages not in trusted list
        if cmd == "npx" and args:
            pkg = str(args[0])
            if not any(pkg.startswith(t) for t in TRUSTED_NPX_PREFIXES):
                suspicious.append(f"{name}: unrecognized npx package '{pkg}'")

        # Flag direct binary execution from tmp or downloads
        if cmd and ('/tmp/' in cmd or '/Downloads/' in cmd or cmd.startswith('./')):
            suspicious.append(f"{name}: command from untrusted path '{cmd}'")

        # Flag stdio servers with env overrides (potential secret exfil / MITM)
        env_vars = srv.get("env", {})
        for key in env_vars:
            if re.search(r'proxy|cert|ca_|ssl_', key, re.IGNORECASE):
                suspicious.append(f"{name}: suspicious env override '{key}'")

    if suspicious:
        return False, f"MCP server concerns: {'; '.join(suspicious[:5])}"
    return True, f"{len(mcp_servers)} MCP server(s) verified"


# ---------------------------------------------------------------------------
# MSG-002: Suspicious tool call patterns (enhanced with behavioral analysis)
# ---------------------------------------------------------------------------

@python_check("MSG-002")
def check_tool_call_patterns(check: dict) -> Tuple[bool, str]:
    """Analyze recent tool calls for suspicious patterns and behavioral anomalies."""
    lines = _read_recent_transcript_lines(max_lines=500)
    if not lines:
        return True, "No session transcript found to analyze"

    suspicious_patterns = [
        # Sensitive file access
        "/etc/passwd", "/etc/shadow", ".ssh/id_",
        # Code execution via pipe
        "curl.*|.*bash", "wget.*|.*sh",
        # Destructive commands
        "rm -rf /", "chmod 777",
        # Data exfiltration
        "curl.*-d.*@", "wget.*--post-file", "nc.*<",
        # Reconnaissance
        "whoami", "uname -a", "cat /etc/os-release",
        # Persistence
        "crontab -e", "systemctl enable", "launchctl load",
        # Evasion
        "history -c", "unset HISTFILE", "export HISTSIZE=0",
    ]

    red_flags = []
    tool_calls = [
        l for l in lines
        if l.get("type") == "tool_use" or "tool_use" in str(l.get("type", ""))
    ]

    for tc in tool_calls[-50:]:
        content = json.dumps(tc).lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in content:
                tool_name = tc.get("name", tc.get("tool", "unknown"))
                red_flags.append(f"{tool_name}: matched '{pattern}'")

    # Behavioral analysis: excessive bash usage
    if len(tool_calls) > 10:
        bash_calls = [
            tc for tc in tool_calls
            if tc.get("name", tc.get("tool", "")).lower() in ("bash", "execute", "shell")
        ]
        bash_ratio = len(bash_calls) / len(tool_calls)
        if bash_ratio > 0.8:
            red_flags.append(
                f"anomaly: excessive bash usage ({bash_ratio:.0%} of {len(tool_calls)} calls)"
            )

    # Behavioral analysis: reading from many different directories (enumeration)
    read_calls = [
        tc for tc in tool_calls
        if tc.get("name", tc.get("tool", "")).lower() in ("read", "readfile", "read_file")
    ]
    if read_calls:
        read_dirs = set()
        for tc in read_calls:
            inp = tc.get("input", {})
            path = inp.get("file_path", inp.get("path", ""))
            if path:
                read_dirs.add(os.path.dirname(path))
        if len(read_dirs) > 20:
            red_flags.append(
                f"anomaly: reading from {len(read_dirs)} different directories"
            )

    if red_flags:
        return False, f"Suspicious tool calls: {'; '.join(red_flags[:5])}"
    return True, f"Analyzed {len(tool_calls)} tool calls, no suspicious patterns"


# ---------------------------------------------------------------------------
# MSG-003: Skills have valid manifests (enhanced with obfuscation detection)
# ---------------------------------------------------------------------------

@python_check("MSG-003")
def check_skill_manifests(check: dict) -> Tuple[bool, str]:
    """Verify installed skills have valid manifests and no dangerous content."""
    skill_dirs = [
        Path.home() / ".config" / "openclaw" / "skills",
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".config" / "claude" / "skills",
    ]
    skills_found = 0
    issues = []

    danger_keywords = [
        "sudo", "chmod 777", "rm -rf", "chown root", "/dev/sd",
        "setuid", "doas", "pkexec", "su -c", "su root",
        "/etc/sudoers", "curl|bash", "curl|sh", "wget|bash",
    ]

    # Obfuscation indicators
    obfuscation_patterns = [
        r'base64\s+(-d|--decode)',
        r'eval\s*\(',
        r'exec\s*\(',
        r'\\x[0-9a-f]{2}',        # hex-encoded strings
        r'String\.fromCharCode',   # JS obfuscation
        r'__import__\s*\(',        # Python dynamic import
    ]

    for sd in skill_dirs:
        if not sd.exists():
            continue
        for skill_dir in sd.iterdir():
            if not skill_dir.is_dir():
                continue
            skills_found += 1
            manifest = skill_dir / "SKILL.md"
            if not manifest.exists():
                issues.append(f"{skill_dir.name}: no SKILL.md manifest")
                continue
            try:
                content = manifest.read_text(errors="replace")[:5000]
                for kw in danger_keywords:
                    if kw in content.lower():
                        issues.append(f"{skill_dir.name}: manifest contains '{kw}'")
            except IOError:
                issues.append(f"{skill_dir.name}: unreadable SKILL.md")

            # Scan all files in skill directory for obfuscation
            for f in skill_dir.rglob("*"):
                if not f.is_file() or f.suffix in ('.png', '.jpg', '.gif', '.ico'):
                    continue
                # Flag unexpected binary files
                try:
                    sample = f.read_bytes()[:512]
                    if b'\x00' in sample and f.suffix not in ('.wasm', '.pyc', '.so', '.dylib'):
                        issues.append(f"{skill_dir.name}/{f.name}: unexpected binary file")
                        continue
                    text = sample.decode('utf-8', errors='replace')
                    for pattern in obfuscation_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            issues.append(
                                f"{skill_dir.name}/{f.name}: obfuscation pattern"
                            )
                            break
                except (IOError, OSError):
                    continue

    if not skills_found:
        return True, "No skills directories found"
    if issues:
        return False, f"{skills_found} skills found; issues: {'; '.join(issues[:5])}"
    return True, f"{skills_found} skill(s) verified with valid manifests"


# ---------------------------------------------------------------------------
# MSG-004: Session transcripts accessible and valid (enhanced)
# ---------------------------------------------------------------------------

@python_check("MSG-004")
def check_session_transparency(check: dict) -> Tuple[bool, str]:
    """Check if the agent's session history is accessible and not tampered with."""
    files = _find_session_files(max_files=10)
    if not files:
        return True, "No session files found (agent may not have run yet)"

    issues = []
    for f in files:
        try:
            stat = f.stat()
            mode = stat.st_mode & 0o777
            size = stat.st_size

            # Check permissions: should not be world-readable
            if mode & 0o044:
                issues.append(f"{f.name}: permissions too open ({oct(mode)})")

            # Check for suspicious size (0 bytes = truncated, >100MB = anomalous)
            if size == 0:
                issues.append(f"{f.name}: empty file (possible truncation)")
            elif size > 100 * 1024 * 1024:
                issues.append(f"{f.name}: suspiciously large ({size // (1024*1024)}MB)")

        except OSError:
            continue

        # Check file integrity: should be valid JSONL
        try:
            with open(f) as fh:
                first_line = fh.readline().strip()
                if first_line:
                    json.loads(first_line)
        except (json.JSONDecodeError, IOError):
            issues.append(f"{f.name}: corrupted or invalid JSONL")

    if issues:
        return False, f"Session transparency issues: {'; '.join(issues[:5])}"
    return True, f"{len(files)} session file(s) accessible and valid"


# ---------------------------------------------------------------------------
# MSG-005: No secrets in conversation context
# ---------------------------------------------------------------------------

@python_check("MSG-005")
def check_secrets_in_context(check: dict) -> Tuple[bool, str]:
    """Check if secrets appear in the agent's recent conversation context."""
    lines = _read_recent_transcript_lines(max_lines=200)
    if not lines:
        return True, "No session transcript to analyze"

    secret_patterns = [
        (r'(?:api[_-]?key|token|secret|password)\s*[=:]\s*["\']?[A-Za-z0-9+/=_-]{20,}', "credential pattern"),
        (r'AKIA[0-9A-Z]{16}', "AWS access key"),
        (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "private key"),
        (r'ghp_[A-Za-z0-9_]{36}', "GitHub token"),
        (r'gho_[A-Za-z0-9_]{36}', "GitHub OAuth token"),
        (r'sk-[A-Za-z0-9]{32,}', "API secret key"),
        (r'xoxb-[0-9]+-[A-Za-z0-9]+', "Slack bot token"),
        (r'xoxp-[0-9]+-[A-Za-z0-9]+', "Slack user token"),
    ]

    findings = []
    for line in lines:
        text = json.dumps(line)
        for pattern, label in secret_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(label)
                break  # One finding per line is enough

    unique_findings = list(set(findings))
    if unique_findings:
        return False, f"Secrets detected in conversation: {', '.join(unique_findings[:5])}"
    return True, f"Scanned {len(lines)} transcript entries, no secrets found"


# ---------------------------------------------------------------------------
# MSG-006: Suspicious URLs (enhanced with IP detection, port scanning, expanded domains)
# ---------------------------------------------------------------------------

@python_check("MSG-006")
def check_url_reputation(check: dict) -> Tuple[bool, str]:
    """Check URLs visited by the agent for suspicious patterns."""
    lines = _read_recent_transcript_lines(max_lines=500)
    if not lines:
        return True, "No session transcript to analyze"

    suspicious_domains = [
        # Paste / data sharing services
        "pastebin.com", "hastebin.com", "paste.ee", "dpaste.com",
        "ix.io", "sprunge.us",
        # File sharing / exfiltration
        "transfer.sh", "0x0.st", "file.io", "tmpfiles.org",
        # Tunneling services
        "ngrok.io", "ngrok-free.app", "serveo.net", "localhost.run",
        "trycloudflare.com", "bore.digital", "telebit.io", "localtunnel.me",
        # Interception / testing
        "requestbin.com", "webhook.site",
        # Known C2 / OAST
        "interactsh.com", "oast.fun", "canarytokens.com",
    ]

    url_pattern = re.compile(r'https?://([^/\s"\']+)')
    ip_url_pattern = re.compile(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    port_pattern = re.compile(r'https?://[^/]+:(\d+)')
    flagged = []

    for line in lines:
        text = json.dumps(line)

        # Check against suspicious domain list
        for match in url_pattern.finditer(text):
            domain = match.group(1).lower()
            for suspicious in suspicious_domains:
                if suspicious in domain:
                    flagged.append(f"suspicious-domain: {domain}")

        # Flag raw IP URLs (potential C2)
        for match in ip_url_pattern.finditer(text):
            url = match.group()
            # Exclude localhost
            if "127.0.0.1" not in url and "0.0.0.0" not in url:
                flagged.append(f"raw-ip: {url}")

        # Flag unusual ports
        for match in port_pattern.finditer(text):
            port = int(match.group(1))
            if port not in (80, 443, 8080, 8443, 3000, 5000, 5173, 4000):
                flagged.append(f"unusual-port: {match.group()}")

    unique_flagged = list(set(flagged))
    if unique_flagged:
        return False, f"Suspicious URLs accessed: {', '.join(unique_flagged[:5])}"
    return True, "No suspicious URLs found in session history"


# ---------------------------------------------------------------------------
# SOC-005: Moltbook posts integrity review
# ---------------------------------------------------------------------------

MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"


def _is_moltbook_installed() -> bool:
    """Check if the Moltbook skill is installed.

    Searches standard OpenClaw/Clawd skill directories as well as
    the legacy ~/.moltbot path.  The ``~/clawd/skills/`` and
    ``~/.clawd/skills/`` paths are used by the Clawdbot agent runtime
    (e.g. inside Cloudflare containers where skills live under /root/clawd/).
    """
    home = Path.home()
    skill_dirs = [
        home / "clawd" / "skills" / "moltbook",
        home / ".clawd" / "skills" / "moltbook",
        home / ".moltbot" / "skills" / "moltbook",
        home / ".config" / "openclaw" / "skills" / "moltbook",
        home / ".openclaw" / "skills" / "moltbook",
        home / ".config" / "claude" / "skills" / "moltbook",
    ]
    for sd in skill_dirs:
        if sd.is_dir():
            return True
    # Also honour an explicit env‑var override (useful in CI / containers)
    if os.environ.get("MOLTBOOK_SKILL_DIR"):
        return Path(os.environ["MOLTBOOK_SKILL_DIR"]).is_dir()
    return False


def _load_moltbook_credentials() -> dict:
    """Load Moltbook API credentials.

    Resolution order:
    1. MOLTBOOK_API_KEY env var (+ MOLTBOOK_AGENT_NAME for username)
    2. Credential files in known locations (first match wins):
       - ~/clawd/skills/moltbook/credentials.json   (Clawdbot runtime)
       - ~/.clawd/skills/moltbook/credentials.json
       - ~/.config/moltbook/credentials.json         (canonical XDG)
       - ~/.moltbot/credentials.json                 (legacy)
    """
    api_key = os.environ.get("MOLTBOOK_API_KEY")
    agent_name = os.environ.get("MOLTBOOK_AGENT_NAME")
    if api_key:
        return {"api_key": api_key, "agent_name": agent_name or ""}

    home = Path.home()
    cred_paths = [
        home / "clawd" / "skills" / "moltbook" / "credentials.json",
        home / ".clawd" / "skills" / "moltbook" / "credentials.json",
        home / ".config" / "moltbook" / "credentials.json",
        home / ".moltbot" / "credentials.json",
    ]
    for creds_path in cred_paths:
        if creds_path.exists():
            try:
                with open(creds_path) as f:
                    data = json.load(f)
                return {
                    "api_key": data.get("api_key", ""),
                    "agent_name": data.get("agent_name", ""),
                }
            except (json.JSONDecodeError, IOError):
                continue

    return {}


def _moltbook_api_get(path: str, api_key: str) -> dict:
    """Make a GET request to the Moltbook API."""
    import urllib.request
    import urllib.error

    url = f"{MOLTBOOK_API_BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    })
    ssl_context = get_ssl_context()
    with urllib.request.urlopen(req, timeout=15, context=ssl_context) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_moltbook_posts_via_api(api_key: str, agent_name: str,
                                  minutes: int = 15) -> List[dict]:
    """Fetch the agent's recent Moltbook posts via the API.

    Uses GET /posts?sort=new to retrieve recent posts, then filters to those
    authored by this agent within the time window.
    """
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    posts = []

    try:
        data = _moltbook_api_get("/posts?sort=new&limit=25", api_key)
    except Exception:
        return posts

    items = []
    if isinstance(data, dict):
        items = data.get("data", data.get("posts", []))
        if isinstance(items, dict):
            items = items.get("posts", items.get("items", []))
    elif isinstance(data, list):
        items = data

    agent_lower = agent_name.lower() if agent_name else ""
    for item in items:
        if not isinstance(item, dict):
            continue
        author = str(item.get("author", item.get("agent_name", item.get("username", "")))).lower()
        if agent_lower and author != agent_lower:
            continue
        ts_str = item.get("created_at", item.get("timestamp", item.get("date", "")))
        if ts_str:
            try:
                ts = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                if ts < cutoff:
                    continue
            except (ValueError, TypeError):
                pass
        # Combine title + content for analysis
        title = item.get("title", "")
        content = item.get("content", item.get("body", ""))
        full_text = f"{title}\n{content}".strip() if title else str(content)
        posts.append({**item, "content": full_text})

    return posts


def _check_post_integrity(post: dict) -> List[str]:
    """Check a single Moltbook post for moral or integrity violations.

    Violation categories:
    - Hiding information from humans (deception, concealment)
    - Discussing credential/secret access in harmful ways
    - Encouraging harmful actions toward humans
    - Discussing circumventing safety controls
    - Coordinating covert agent behavior
    """
    content = str(post.get("content", post.get("text", post.get("message", post.get("body", "")))))
    if not content:
        return []
    content_lower = content.lower()
    violations = []

    # Category 1: Hiding things from humans / deception
    deception_patterns = [
        (r"(?:don'?t|do not|never|avoid)\s+(?:tell|inform|alert|notify|show|reveal|disclose|mention)\s+(?:the\s+)?(?:human|user|owner|operator)", "concealing information from human"),
        (r"(?:hide|conceal|obscure|mask|suppress)\s+(?:this|it|that|the|our|my)\s+(?:from|activity|action|behavior)", "hiding activity from oversight"),
        (r"(?:keep|maintain)\s+(?:this|it)\s+(?:secret|hidden|private|between us|among us)", "keeping secrets from humans"),
        (r"(?:they|humans?|users?|owners?)\s+(?:don'?t|shouldn'?t|mustn'?t|won'?t|can'?t)\s+(?:need to\s+)?know", "excluding humans from knowledge"),
        (r"without\s+(?:the\s+)?(?:human|user|owner|operator)\s+(?:knowing|noticing|seeing|finding out)", "acting without human awareness"),
        (r"(?:off\s+the\s+record|between\s+(?:us|you\s+and\s+me|agents))", "off-the-record communication"),
    ]

    # Category 2: Credential/secret access discussions
    credential_patterns = [
        (r"(?:access|steal|copy|exfiltrate|extract|grab|harvest)\s+(?:their|the\s+human'?s?|user'?s?)\s+(?:credential|password|token|key|secret|auth)", "targeting human credentials"),
        (r"(?:credential|password|token|key|secret|api.key)\s+(?:for|of|belonging to)\s+(?:the\s+)?(?:human|user|owner)", "referencing human credentials"),
        (r"(?:read|access|open|view)\s+(?:the\s+)?(?:\.env|credentials|secrets|keychain|password.store)", "accessing credential stores"),
        (r"(?:forward|send|share|exfiltrate|leak|transmit)\s+(?:the\s+)?(?:credential|password|token|key|secret)", "sharing/leaking credentials"),
    ]

    # Category 3: Harmful actions toward humans
    harmful_patterns = [
        (r"(?:manipulate|deceive|trick|mislead|gaslight|exploit)\s+(?:the\s+)?(?:human|user|owner|operator)", "manipulating humans"),
        (r"(?:override|bypass|circumvent|ignore|disable)\s+(?:the\s+)?(?:human|user|owner)'?s?\s+(?:control|authority|decision|instruction|wish)", "overriding human authority"),
        (r"(?:agents?\s+(?:are|should be)\s+)?(?:superior|more important|above)\s+(?:to\s+)?(?:humans?|users?|people)", "asserting agent superiority"),
    ]

    # Category 4: Safety control circumvention
    safety_patterns = [
        (r"(?:bypass|circumvent|disable|override|ignore|remove|strip)\s+(?:the\s+)?(?:safety|security|guard|filter|restriction|constraint|limit|check|monitor)", "circumventing safety controls"),
        (r"(?:jailbreak|prompt.inject|escape\s+(?:the\s+)?sandbox|break\s+(?:out|free))", "discussing jailbreaking/escaping"),
        (r"(?:avoid|evade|escape)\s+(?:detection|monitoring|logging|audit|oversight|review)", "evading detection"),
    ]

    # Category 5: Covert agent coordination
    coordination_patterns = [
        (r"(?:coordinate|organize|plan|conspire|collude)\s+(?:with\s+)?(?:other\s+)?agents?\s+(?:against|without|behind)", "covert agent coordination"),
        (r"(?:our|the)\s+(?:secret|hidden|private|covert)\s+(?:plan|network|channel|operation)", "secret agent operations"),
    ]

    all_patterns = [
        *deception_patterns,
        *credential_patterns,
        *harmful_patterns,
        *safety_patterns,
        *coordination_patterns,
    ]

    for pattern, label in all_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            violations.append(label)

    return violations


@python_check("SOC-005")
def check_moltbook_integrity(check: dict) -> Tuple[bool, str]:
    """Check Moltbook posts for moral or integrity violations.

    If the Moltbook skill is installed:
    1. Loads credentials from ~/.config/moltbook/credentials.json
    2. Resolves the agent's Moltbook username (via creds or GET /agents/me)
    3. Fetches recent posts (last 15 min) via GET /posts?sort=new
    4. Scans each post for moral/integrity violations
    """
    if not _is_moltbook_installed():
        return True, "Moltbook skill not installed (check not applicable)"

    creds = _load_moltbook_credentials()
    api_key = creds.get("api_key", "")
    if not api_key:
        return True, "Moltbook installed but no API key configured (check not applicable)"

    # Resolve username: prefer stored name, fall back to /agents/me
    agent_name = creds.get("agent_name", "")
    if not agent_name:
        try:
            profile = _fetch_moltbook_profile(api_key)
            agent_name = str(profile.get("name", ""))
        except Exception:
            pass

    if not agent_name:
        return True, "Moltbook installed but agent username could not be determined"

    # Fetch recent posts via API
    posts = _fetch_moltbook_posts_via_api(api_key, agent_name, minutes=15)
    if not posts:
        return True, f"No Moltbook posts in the last 15 min (user: {agent_name})"

    # Analyze each post for integrity violations
    all_violations = []
    for i, post in enumerate(posts):
        violations = _check_post_integrity(post)
        if violations:
            preview = str(post.get("content", ""))[:80]
            all_violations.append(
                f"post {i+1}: {', '.join(violations)} ('{preview}...')"
            )

    if all_violations:
        return False, (
            f"Moltbook integrity violations in {len(all_violations)}/{len(posts)} "
            f"posts (user: {agent_name}): {'; '.join(all_violations[:3])}"
        )

    return True, (
        f"Scanned {len(posts)} Moltbook posts (last 15 min, user: {agent_name}), "
        f"no integrity violations"
    )


# ---------------------------------------------------------------------------
# SOC-006: Human owner social reputation via Moltbook
# ---------------------------------------------------------------------------

# Reputation thresholds for human owner's X/Twitter follower count
_REPUTATION_LOW_THRESHOLD = 10       # < 10 followers = no reputation
_REPUTATION_MED_THRESHOLD = 1000     # 10-1000 = some reputation, > 1000 = verified


def _fetch_moltbook_profile(api_key: str) -> dict:
    """Fetch the agent's full Moltbook profile including human owner info.

    The Moltbook API returns: {"success": true, "data": {"agent": {..., "owner": {...}}}}
    We unwrap both the ``data`` and ``agent`` envelopes so callers get the flat
    agent dict with ``name``, ``karma``, ``is_claimed``, ``owner``, etc.
    """
    try:
        resp = _moltbook_api_get("/agents/me", api_key)
        if isinstance(resp, dict):
            # Unwrap outer "data" envelope
            inner = resp.get("data", resp)
            if isinstance(inner, dict):
                # Unwrap "agent" envelope (API nests agent fields under "agent" key)
                agent = inner.get("agent", inner)
                if isinstance(agent, dict):
                    return agent
                return inner
            return resp
    except Exception:
        pass
    return {}


def _assess_human_reputation(follower_count: int) -> Tuple[str, str, str]:
    """Assess human reputation based on X/Twitter follower count.

    Returns (tier, symbol, description).
    """
    if follower_count >= _REPUTATION_MED_THRESHOLD:
        return "high", "\u2b50", f"Socially verified ({follower_count:,} followers)"
    if follower_count >= _REPUTATION_LOW_THRESHOLD:
        return "medium", "\U0001f7e1", f"Some reputation ({follower_count:,} followers)"
    return "low", "\U0001f534", f"No reputation ({follower_count:,} followers)"


def get_moltbook_identity() -> Optional[dict]:
    """Collect Moltbook identity data for telemetry enrichment.

    Returns None if Moltbook is not installed or not configured.
    When available, returns a dict with agent and owner metadata
    suitable for embedding in the telemetry payload.
    """
    if not _is_moltbook_installed():
        return None

    creds = _load_moltbook_credentials()
    api_key = creds.get("api_key", "")
    if not api_key:
        return None

    profile = _fetch_moltbook_profile(api_key)
    if not profile:
        return None

    agent_name = profile.get("name", creds.get("agent_name", ""))
    if not agent_name:
        return None

    owner = profile.get("owner", {})
    if not isinstance(owner, dict):
        owner = {}

    x_followers = owner.get("x_follower_count", 0)
    if not isinstance(x_followers, int):
        try:
            x_followers = int(x_followers)
        except (ValueError, TypeError):
            x_followers = 0

    x_following = owner.get("x_following_count", 0)
    if not isinstance(x_following, int):
        try:
            x_following = int(x_following)
        except (ValueError, TypeError):
            x_following = 0

    karma = profile.get("karma", 0)
    if not isinstance(karma, int):
        try:
            karma = int(karma)
        except (ValueError, TypeError):
            karma = 0

    rep_tier, rep_symbol, rep_desc = _assess_human_reputation(x_followers)

    identity = {
        "moltbook_username": f"u/{agent_name}",
        "moltbook_karma": karma,
        "moltbook_verified": bool(profile.get("is_claimed", False)),
        "human_owner": {
            "x_handle": owner.get("x_handle", ""),
            "x_name": owner.get("x_name", ""),
            "x_followers": x_followers,
            "x_following": x_following,
            "x_verified": bool(owner.get("x_verified", False)),
        },
        "reputation": {
            "tier": rep_tier,
            "symbol": rep_symbol,
            "description": rep_desc,
        },
    }
    return identity


@python_check("SOC-006")
def check_human_reputation(check: dict) -> Tuple[bool, str]:
    """Assess the human owner's social reputation via Moltbook profile.

    Retrieves the human owner's X/Twitter profile from the Moltbook API
    and evaluates credibility based on follower count:
    - < 10 followers:   no reputation   (higher risk)
    - 10 - 1,000:       some reputation (medium risk)
    - > 1,000:          socially verified (low risk)
    """
    if not _is_moltbook_installed():
        return True, "Moltbook skill not installed (check not applicable)"

    creds = _load_moltbook_credentials()
    api_key = creds.get("api_key", "")
    if not api_key:
        return True, "Moltbook installed but no API key configured (check not applicable)"

    profile = _fetch_moltbook_profile(api_key)
    if not profile:
        return True, "Could not fetch Moltbook profile (check not applicable)"

    agent_name = profile.get("name", creds.get("agent_name", "unknown"))
    owner = profile.get("owner", {})
    if not isinstance(owner, dict) or not owner:
        return False, (
            f"u/{agent_name}: no human owner linked on Moltbook profile "
            "(unclaimed agent = higher risk)"
        )

    x_handle = owner.get("x_handle", "")
    if not x_handle:
        return False, (
            f"u/{agent_name}: human owner has no X/Twitter account linked "
            "(unverifiable identity = higher risk)"
        )

    x_followers = owner.get("x_follower_count", 0)
    if not isinstance(x_followers, int):
        try:
            x_followers = int(x_followers)
        except (ValueError, TypeError):
            x_followers = 0

    rep_tier, rep_symbol, rep_desc = _assess_human_reputation(x_followers)

    x_name = owner.get("x_name", x_handle)

    if rep_tier == "low":
        return False, (
            f"{rep_symbol} u/{agent_name} owner @{x_handle} ({x_name}): "
            f"{rep_desc} - higher risk"
        )

    # medium and high both pass, but medium is noted
    return True, (
        f"{rep_symbol} u/{agent_name} owner @{x_handle} ({x_name}): {rep_desc}"
    )


# ---------------------------------------------------------------------------
# NODE-001: Remote execution security setting
# ---------------------------------------------------------------------------

@python_check("NODE-001")
def check_remote_exec_security(check: dict) -> Tuple[bool, str]:
    """Verify remote execution requires approval or is denied."""
    config = _find_openclaw_config()
    exec_config = config.get("exec", {})
    security = exec_config.get("security", "")

    if not config:
        return True, "No OpenClaw config found (not applicable)"

    if security in ("ask", "deny"):
        return True, f"Remote execution security: {security}"
    if not security:
        return False, "Remote execution security not configured"
    return False, f"Remote execution security set to '{security}' (should be 'ask' or 'deny')"


# ---------------------------------------------------------------------------
# NODE-003: Node token file permissions
# ---------------------------------------------------------------------------

@python_check("NODE-003")
def check_node_token_permissions(check: dict) -> Tuple[bool, str]:
    """Verify node pairing tokens have restricted permissions."""
    token_dirs = [
        Path.home() / ".openclaw" / "nodes",
        Path.home() / ".openclaw",
    ]
    insecure = []
    checked = 0
    for d in token_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.token"):
            checked += 1
            try:
                mode = f.stat().st_mode & 0o777
                if mode & 0o077:  # group or world access
                    insecure.append(f"{f.name} ({oct(mode)})")
            except OSError:
                continue

    if not checked:
        return True, "No node token files found"
    if insecure:
        return False, f"Insecure token files: {', '.join(insecure[:5])}"
    return True, f"{checked} token file(s) have proper permissions"


# ---------------------------------------------------------------------------
# NODE-005: Exec allowlist configured
# ---------------------------------------------------------------------------

@python_check("NODE-005")
def check_exec_allowlist(check: dict) -> Tuple[bool, str]:
    """Verify execution allowlist is configured for nodes."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    # Check for allowlist in exec config or top-level
    exec_config = config.get("exec", {})
    has_allowlist = (
        "allowlist" in exec_config
        or "allowlist" in config
        or "allowedCommands" in exec_config
    )
    if has_allowlist:
        return True, "Exec allowlist is configured"
    return False, "No exec allowlist configured (unrestricted command execution)"


# ---------------------------------------------------------------------------
# MEDIA-002: Media temp directory permissions
# ---------------------------------------------------------------------------

@python_check("MEDIA-002")
def check_media_temp_permissions(check: dict) -> Tuple[bool, str]:
    """Verify media temp directory has restricted permissions."""
    media_dirs = [
        Path("/tmp/openclaw-media"),
        Path.home() / ".openclaw" / "media",
    ]
    for d in media_dirs:
        if d.exists():
            try:
                mode = d.stat().st_mode & 0o777
                if mode & 0o077:
                    return False, f"{d}: permissions too open ({oct(mode)}), should be 700"
            except OSError:
                continue
    return True, "Media temp directory permissions OK (or not present)"


# ---------------------------------------------------------------------------
# MEDIA-003: Media file type validation
# ---------------------------------------------------------------------------

@python_check("MEDIA-003")
def check_media_type_validation(check: dict) -> Tuple[bool, str]:
    """Check if media file type validation is enabled."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (defaults apply)"

    validate = config.get("validateMediaTypes", config.get("media", {}).get("validateTypes"))
    if validate is False:
        return False, "Media type validation is explicitly disabled"
    return True, "Media type validation enabled (or default)"


# ---------------------------------------------------------------------------
# GATEWAY-001: Gateway binding address
# ---------------------------------------------------------------------------

@python_check("GATEWAY-001")
def check_gateway_binding(check: dict) -> Tuple[bool, str]:
    """Verify gateway is bound to localhost only."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    gateway = config.get("gateway", {})
    bind = gateway.get("bind", gateway.get("host", ""))

    if bind and bind not in ("127.0.0.1", "localhost", "::1", ""):
        return False, f"Gateway bound to {bind} (should be 127.0.0.1)"

    # Also check if gateway process is actually listening on non-localhost
    try:
        if IS_MACOS:
            result = subprocess.run(
                ["lsof", "-iTCP", "-sTCP:LISTEN", "-P", "-n"],
                capture_output=True, text=True, timeout=10
            )
        else:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True, text=True, timeout=10
            )
        output = result.stdout
        for line in output.splitlines():
            if "openclaw" in line.lower() or "claw" in line.lower():
                if "0.0.0.0" in line:
                    return False, "Gateway process listening on 0.0.0.0 (all interfaces)"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return True, "Gateway binding address OK"


# ---------------------------------------------------------------------------
# GATEWAY-002: Gateway authentication enabled
# ---------------------------------------------------------------------------

@python_check("GATEWAY-002")
def check_gateway_auth(check: dict) -> Tuple[bool, str]:
    """Check if gateway requires authentication."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    gateway = config.get("gateway", {})
    auth_enabled = gateway.get("auth", gateway.get("authentication"))

    if auth_enabled is True:
        return True, "Gateway authentication is enabled"
    if auth_enabled is False:
        return False, "Gateway authentication is explicitly disabled"
    if "gateway" in config and auth_enabled is None:
        return False, "Gateway configured but authentication not set"
    return True, "No gateway configured (not applicable)"


# ---------------------------------------------------------------------------
# IDENTITY-001: DM pairing allowlist
# ---------------------------------------------------------------------------

@python_check("IDENTITY-001")
def check_dm_allowlist(check: dict) -> Tuple[bool, str]:
    """Check if DM pairing uses an allowlist."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    dm_allowlist = config.get("dmAllowlist", config.get("dm", {}).get("allowlist"))
    if dm_allowlist is not None:
        if isinstance(dm_allowlist, list) and len(dm_allowlist) > 0:
            return True, f"DM allowlist configured with {len(dm_allowlist)} entries"
        return True, "DM allowlist is configured"
    return False, "No DM allowlist configured (anyone can message the agent)"


# ---------------------------------------------------------------------------
# IDENTITY-002: Group chat allowlist
# ---------------------------------------------------------------------------

@python_check("IDENTITY-002")
def check_group_allowlist(check: dict) -> Tuple[bool, str]:
    """Check if group chat allowlist is configured."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    group_allowlist = config.get("groupAllowlist", config.get("groups", {}).get("allowlist"))
    if group_allowlist is not None:
        if isinstance(group_allowlist, list) and len(group_allowlist) > 0:
            return True, f"Group allowlist configured with {len(group_allowlist)} entries"
        return True, "Group allowlist is configured"
    return False, "No group allowlist configured (agent can join any group)"


# ---------------------------------------------------------------------------
# SUBAGENT-001: SubAgent max concurrent limit
# ---------------------------------------------------------------------------

@python_check("SUBAGENT-001")
def check_subagent_limit(check: dict) -> Tuple[bool, str]:
    """Check if subagent concurrency is limited."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    subagent_config = config.get("subagents", config.get("subAgent", {}))
    max_concurrent = subagent_config.get("maxConcurrent", config.get("maxConcurrent"))

    if max_concurrent is not None:
        try:
            limit = int(max_concurrent)
            if limit > 20:
                return False, f"SubAgent limit is very high ({limit}), consider reducing"
            return True, f"SubAgent concurrency limited to {limit}"
        except (ValueError, TypeError):
            return False, f"Invalid maxConcurrent value: {max_concurrent}"
    return False, "No subagent concurrency limit configured"


# ---------------------------------------------------------------------------
# SUBAGENT-002: SubAgent allowlist configured
# ---------------------------------------------------------------------------

@python_check("SUBAGENT-002")
def check_subagent_allowlist(check: dict) -> Tuple[bool, str]:
    """Check if subagent target allowlist is set."""
    config = _find_openclaw_config()
    if not config:
        return True, "No OpenClaw config found (not applicable)"

    subagent_config = config.get("subagents", config.get("subAgent", {}))
    allow_agents = subagent_config.get("allowAgents", config.get("allowAgents"))

    if allow_agents is not None:
        if isinstance(allow_agents, list) and len(allow_agents) > 0:
            return True, f"SubAgent allowlist configured with {len(allow_agents)} entries"
        return True, "SubAgent allowlist is configured"
    return False, "No subagent allowlist configured (unrestricted agent targeting)"


# ===========================================================================
# Scoring, telemetry, and main execution
# ===========================================================================

def calculate_score(results: List[dict], env_context: dict = None) -> dict:
    """Calculate trust score from results.

    Expected findings (from env_context) still count toward the base score
    but do NOT trigger the critical/high caps, since they are inherent to
    the environment and already mitigated.
    """
    if not results:
        return {"score": 0, "trust_tier": "UNTRUSTED", "critical_failures": 0, "high_failures": 0}

    expected_findings = set((env_context or {}).get("expected_findings", []))

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    blocked = sum(1 for r in results if r.get("status") == "blocked")
    skipped = sum(1 for r in results if r.get("status") == "skipped")

    # Count severity failures (exclude blocked/skipped AND expected findings)
    critical_failures = sum(1 for r in results
                           if not r["passed"] and r.get("severity") == "critical"
                           and r.get("status") not in ("blocked", "skipped")
                           and r["check_id"] not in expected_findings)
    high_failures = sum(1 for r in results
                        if not r["passed"] and r.get("severity") == "high"
                        and r.get("status") not in ("blocked", "skipped")
                        and r["check_id"] not in expected_findings)

    # Base score: exclude blocked, skipped, and expected findings from denominator
    expected_failed = sum(1 for r in results
                          if not r["passed"] and r["check_id"] in expected_findings
                          and r.get("status") not in ("blocked", "skipped"))
    effective_total = total - blocked - skipped - expected_failed
    effective_passed = sum(1 for r in results
                           if r["passed"] and r.get("status") != "skipped")
    score = int((effective_passed / effective_total * 100)) if effective_total > 0 else 0

    # Cap score based on critical/high failures (only actionable ones)
    if critical_failures > 0:
        score = min(score, 49)
    elif high_failures >= 3:
        score = min(score, 69)

    # Determine tier
    if score >= 90:
        trust_tier = "HIGH"
    elif score >= 70:
        trust_tier = "MEDIUM"
    elif score >= 50:
        trust_tier = "LOW"
    else:
        trust_tier = "UNTRUSTED"

    return {
        "score": score,
        "trust_tier": trust_tier,
        "critical_failures": critical_failures,
        "high_failures": high_failures,
    }


def get_detections(results: List[dict], detection_kb: dict, checks: List[dict] = None,
                    env_context: dict = None) -> List[dict]:
    """Extract failed checks and enrich with risk/remediation from knowledge base."""
    # Build inline remediation lookup from check definitions (fallback)
    inline_remediation = {}
    if checks:
        for c in checks:
            if "remediation" in c:
                inline_remediation[c["check_id"]] = c["remediation"]

    expected_findings = set((env_context or {}).get("expected_findings", []))
    env_notes = (env_context or {}).get("notes", {})

    detections = []
    for r in results:
        if r["passed"] or r.get("status") in ("blocked", "skipped"):
            continue
        check_id = r["check_id"]
        kb_entry = detection_kb.get(check_id, {})
        fallback_remediation = inline_remediation.get(check_id, "No remediation steps available.")
        detection = {
            "check_id": check_id,
            "name": r.get("name", ""),
            "severity": r.get("severity", "medium"),
            "category": r.get("category", ""),
            "output": r.get("output", ""),
            "risk": kb_entry.get("risk", "No risk description available."),
            "remediation": kb_entry.get("remediation", fallback_remediation),
            "can_auto_remediate": kb_entry.get("can_auto_remediate", False),
            "auto_remediate_command": kb_entry.get("auto_remediate_command"),
        }
        if check_id in expected_findings:
            detection["expected_in_environment"] = True
            detection["environment_note"] = env_notes.get(check_id, "")
        detections.append(detection)

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    detections.sort(key=lambda d: severity_order.get(d["severity"], 99))
    return detections


def print_detections(detections: List[dict]):
    """Print detailed detection report to stdout for the session agent."""
    if not detections:
        return

    critical_count = sum(1 for d in detections if d["severity"] == "critical")
    high_count = sum(1 for d in detections if d["severity"] == "high")

    print()
    print("=" * 60)
    print("   SECURITY DETECTIONS FOUND")
    parts = [f"{len(detections)} failed check(s) detected"]
    if critical_count:
        parts.append(f"{critical_count} critical")
    if high_count:
        parts.append(f"{high_count} high")
    print(f"   {', '.join(parts)}")
    print("=" * 60)
    print()

    for d in detections:
        severity_tag = d["severity"].upper()
        expected = d.get("expected_in_environment", False)
        label = f"  [{severity_tag}] {d['check_id']}: {d['name']}"
        if expected:
            label += " (expected in this environment)"
        print(label)
        if expected and d.get("environment_note"):
            print(f"    Note: {d['environment_note']}")
        print(f"    Risk: {d['risk']}")
        print(f"    Remediation: {d['remediation']}")
        if d["can_auto_remediate"] and d.get("auto_remediate_command"):
            print(f"    Auto-fix available: {d['auto_remediate_command']}")
        else:
            print(f"    Auto-fix: Not available")
        print()


def build_notification_message(detections: List[dict], agent_info: dict, scoring: dict) -> str:
    """Build a concise notification message for openclaw notify."""
    agent_name = agent_info["agent_name"]
    agent_id = agent_info["agent_id"]
    score = scoring["score"]
    tier = scoring["trust_tier"]

    lines = [f"TrustMyAgent Alert: {len(detections)} detection(s) on \"{agent_name}\" (score: {score}/100, {tier})."]

    for sev in ["critical", "high"]:
        sev_detections = [d for d in detections if d["severity"] == sev]
        if sev_detections:
            ids = ", ".join(f"{d['check_id']} ({d['name']})" for d in sev_detections[:3])
            if len(sev_detections) > 3:
                ids += f" +{len(sev_detections) - 3} more"
            lines.append(f"{sev.capitalize()}: {ids}.")

    lines.append(f"Dashboard: https://www.trustmyagent.ai/trust-center.html?agent_id={agent_id}")
    return " ".join(lines)


def send_openclaw_notification(message: str) -> Tuple[bool, str]:
    """Send notification via openclaw CLI. Best-effort, never raises.

    Tries multiple methods to send:
    1. `openclaw` in PATH
    2. Common install locations (~/.local/bin, /usr/local/bin)
    3. npx openclaw (if npm is available)
    """
    # Method 1: openclaw in PATH
    try:
        proc = subprocess.run(
            ["openclaw", "notify", "--message", message],
            capture_output=True, text=True, timeout=15
        )
        if proc.returncode == 0:
            return True, "Notification sent via openclaw notify"
        return False, f"openclaw notify exit code {proc.returncode}: {proc.stderr[:200]}"
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        return False, "openclaw notify timed out after 15s"
    except Exception:
        pass

    # Method 2: Try common install locations
    for bin_path in [
        Path.home() / ".local" / "bin" / "openclaw",
        Path.home() / ".openclaw" / "bin" / "openclaw",
        Path("/usr/local/bin/openclaw"),
    ]:
        if bin_path.exists():
            try:
                proc = subprocess.run(
                    [str(bin_path), "notify", "--message", message],
                    capture_output=True, text=True, timeout=15
                )
                if proc.returncode == 0:
                    return True, f"Notification sent via {bin_path}"
            except Exception:
                continue

    # Method 3: Try npx
    try:
        proc = subprocess.run(
            ["npx", "--yes", "openclaw", "notify", "--message", message],
            capture_output=True, text=True, timeout=30
        )
        if proc.returncode == 0:
            return True, "Notification sent via npx openclaw"
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    return False, "openclaw CLI not found (notification skipped, detections visible in report and dashboard)"


def build_telemetry(agent_info: dict, results: List[dict], scoring: dict,
                    detections: List[dict] = None, env_context: dict = None) -> dict:
    """Build telemetry payload from results."""
    # Build summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"] and r.get("status") != "blocked")
    blocked = sum(1 for r in results if r.get("status") == "blocked")

    # Build categories
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0, "total": 0}
        categories[cat]["total"] += 1
        if r["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1

    for cat in categories:
        total = categories[cat]["total"]
        categories[cat]["score"] = int((categories[cat]["passed"] / total * 100)) if total > 0 else 0

    agent_block = {
        "id": agent_info["agent_id"],
        "name": agent_info["agent_name"],
        "version": "2.1.0",
        "platform": PLATFORM_NAME,
        "detected_env": (env_context or {}).get("detected_env", "unknown"),
    }

    # Enrich with Moltbook identity when available
    moltbook_id = agent_info.get("moltbook")
    if moltbook_id:
        agent_block["moltbook_username"] = moltbook_id.get("moltbook_username", "")
        agent_block["moltbook_karma"] = moltbook_id.get("moltbook_karma", 0)
        agent_block["moltbook_verified"] = moltbook_id.get("moltbook_verified", False)
        agent_block["human_owner"] = moltbook_id.get("human_owner", {})
        agent_block["reputation"] = moltbook_id.get("reputation", {})

    payload = {
        "version": "2.0",
        "agent": agent_block,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "posture": {
            "trust_tier": scoring["trust_tier"],
            "overall_score": scoring["score"],
            "checks_total": len(results),
            "checks_passed": passed,
            "critical_failures": scoring["critical_failures"],
            "categories": categories,
        },
        "summary": {
            "passed": passed,
            "failed": failed,
            "blocked": blocked,
        },
        "results": results,
    }

    # Add environment context
    if env_context:
        payload["environment"] = {
            "type": env_context.get("type", "unknown"),
            "provider": env_context.get("provider", "unknown"),
            "is_root": env_context.get("is_root", False),
            "expected_findings": env_context.get("expected_findings", []),
        }

    # Add detections with risk/remediation context
    if detections:
        payload["detections"] = []
        for d in detections:
            det = {
                "check_id": d["check_id"],
                "name": d["name"],
                "severity": d["severity"],
                "risk": d["risk"],
                "remediation": d["remediation"],
                "can_auto_remediate": d["can_auto_remediate"],
            }
            if d.get("expected_in_environment"):
                det["expected_in_environment"] = True
                det["environment_note"] = d.get("environment_note", "")
            payload["detections"].append(det)

    # Add checksum
    checksum_data = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    payload["checksum"] = hashlib.sha256(checksum_data).hexdigest()

    return payload


def get_ssl_context():
    """Get SSL context with proper certificate handling."""
    import ssl

    # Try to use certifi if available (most reliable)
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass

    # Try default context (works on most Linux systems)
    try:
        ctx = ssl.create_default_context()
        # Test if it can find certificates
        if ctx.get_ca_certs():
            return ctx
    except Exception:
        pass

    # macOS: try to use the system certificates via /etc/ssl/cert.pem
    for cert_path in [
        "/etc/ssl/cert.pem",
        "/etc/ssl/certs/ca-certificates.crt",
        "/etc/pki/tls/certs/ca-bundle.crt",
    ]:
        if os.path.exists(cert_path):
            try:
                return ssl.create_default_context(cafile=cert_path)
            except Exception:
                continue

    # Last resort: unverified context with warning
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def send_telemetry(telemetry: dict, agent_id: str, agent_secret: str = "") -> Tuple[bool, str]:
    """Send telemetry to server with HMAC signature."""
    import urllib.request
    import urllib.error

    try:
        payload_json = json.dumps(telemetry)

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TrustMyAgent-Agent/2.1.0',
            'X-Agent-ID': agent_id,
        }

        # Sign the payload if we have a secret
        if agent_secret:
            sig = sign_telemetry(payload_json, agent_secret)
            headers['X-Signature'] = sig

        payload = payload_json.encode('utf-8')
        req = urllib.request.Request(TELEMETRY_URL, data=payload, headers=headers, method='POST')

        # Get SSL context with proper certificate handling
        ssl_context = get_ssl_context()

        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("success"):
                return True, "Telemetry sent successfully"
            return False, result.get("error", "Unknown error")

    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, str(e)


def build_agent_report(agent_info: dict, scoring: dict, detections: List[dict],
                       env_context: dict = None, notify_result: dict = None) -> dict:
    """Build a structured JSON report designed for OpenClaw agent consumption.

    The report is concise, actionable, and clearly separates expected findings
    from actionable ones so the agent can prioritize remediation.
    """
    expected = []
    actionable = []
    for d in detections:
        entry = {
            "check_id": d["check_id"],
            "severity": d["severity"],
            "issue": d["name"],
            "risk": d["risk"],
            "remediation": d["remediation"],
        }
        if d.get("can_auto_remediate") and d.get("auto_remediate_command"):
            entry["fix_command"] = d["auto_remediate_command"]
        if d.get("expected_in_environment"):
            entry["environment_note"] = d.get("environment_note", "")
            expected.append(entry)
        else:
            actionable.append(entry)

    report = {
        "status": "ok",
        "agent_id": agent_info["agent_id"],
        "trust_tier": scoring["trust_tier"],
        "score": scoring["score"],
        "dashboard": f"https://www.trustmyagent.ai/trust-center.html?agent_id={agent_info['agent_id']}",
    }

    if env_context:
        report["environment"] = {
            "detected_env": env_context.get("detected_env", "unknown"),
            "type": env_context["type"],
            "provider": env_context["provider"],
        }

    report["detections_summary"] = {
        "total": len(detections),
        "actionable": len(actionable),
        "expected_in_environment": len(expected),
    }

    if actionable:
        report["actionable_findings"] = actionable
    if expected:
        report["expected_findings"] = expected

    if notify_result:
        report["notification"] = notify_result

    return report


def main():
    parser = argparse.ArgumentParser(
        description="TrustMyAgent - Stateless Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--checks", "-c", type=Path, help="Path to checks JSON file")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout per check (seconds)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output structured JSON to stdout (for agent consumption)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run all checks and display the telemetry payload, but do not send it")
    parser.add_argument("--local-only", action="store_true",
                        help="Run all checks locally without any network calls (no telemetry sent)")
    parser.add_argument("--no-notify", action="store_true", help="Skip openclaw notification for detections")

    args = parser.parse_args()

    # Auto-detect: use JSON mode when stdout is not a terminal (piped/captured by agent)
    use_json = args.json or not sys.stdout.isatty()
    verbose = not args.quiet and not use_json

    if verbose:
        print_banner()

    # Get agent info and signing secret
    agent_info = {
        "agent_id": get_agent_id(),
        "agent_name": get_agent_name(),
    }
    agent_secret = get_agent_secret()

    # Enrich with Moltbook identity (if skill is installed)
    moltbook_id = get_moltbook_identity()
    if moltbook_id:
        agent_info["moltbook"] = moltbook_id

    if verbose:
        print(f"Agent: {agent_info['agent_name']} ({agent_info['agent_id']})")
        if moltbook_id:
            mb_user = moltbook_id.get("moltbook_username", "")
            rep = moltbook_id.get("reputation", {})
            owner_info = moltbook_id.get("human_owner", {})
            x_handle = owner_info.get("x_handle", "")
            print(f"Moltbook: {mb_user}  |  Owner: @{x_handle}  |  {rep.get('symbol', '')} {rep.get('description', '')}")
        print()

    # Detect runtime environment
    env_context = detect_environment()
    if verbose:
        print(f"Environment: {env_context['detected_env']}")
        if env_context["expected_findings"]:
            print(f"  Expected findings in this environment: {', '.join(env_context['expected_findings'])}")
        print()

    # Load checks and detection knowledge base
    if verbose:
        print("[1/4] Loading checks...")
    checks = load_checks(args.checks)
    detection_kb = load_detection_kb()
    if verbose:
        print(f"  Loaded {len(checks)} checks")
        if detection_kb:
            print(f"  Loaded detection knowledge base ({len(detection_kb)} entries)")

    # Execute checks
    if verbose:
        print()
        print("[2/4] Running security assessment...")

    results = []
    for i, check in enumerate(checks, 1):
        if verbose:
            print(f"  [{i}/{len(checks)}] {check['check_id']}: {check.get('name', '')[:40]}...", end=" ", flush=True)

        result = execute_check(check, args.timeout)
        results.append(result)

        if verbose:
            status = result.get("status")
            if status == "blocked":
                print("[BLOCKED]")
            elif status == "skipped":
                print("[SKIP]")
            else:
                print("[PASS]" if result["passed"] else "[FAIL]")

    # Calculate score and extract detections
    scoring = calculate_score(results, env_context)
    detections = get_detections(results, detection_kb, checks, env_context)

    # Build telemetry (includes detections and environment context)
    telemetry = build_telemetry(agent_info, results, scoring, detections, env_context)

    # Send telemetry (unless --dry-run or --local-only)
    skip_telemetry = args.dry_run or args.local_only
    if verbose:
        print()
        if args.dry_run:
            print("[3/4] Dry run — telemetry payload (not sent):")
            print()
            print(json.dumps(telemetry, indent=2))
            print()
        elif args.local_only:
            print("[3/4] Local-only mode — skipping telemetry")
        else:
            print("[3/4] Sending telemetry...")

    if not skip_telemetry:
        success, message = send_telemetry(telemetry, agent_info["agent_id"], agent_secret)
        if verbose:
            if success:
                print(f"  {message}")
            else:
                print(f"  Warning: {message}")
    else:
        success = True
        message = "Telemetry skipped"

    # Handle detections
    if verbose:
        print()
        print("[4/4] Detection handling...")

    notify_result = None
    if detections:
        if verbose:
            print_detections(detections)

        # Send notification only for actionable critical/high detections (not expected findings)
        critical_or_high = [d for d in detections
                            if d["severity"] in ("critical", "high")
                            and not d.get("expected_in_environment")]
        if critical_or_high and not args.no_notify and not skip_telemetry:
            notify_message = build_notification_message(detections, agent_info, scoring)
            notify_ok, notify_msg = send_openclaw_notification(notify_message)
            notify_result = {"sent": notify_ok, "message": notify_msg}
            if verbose:
                if notify_ok:
                    print(f"  {notify_msg}")
                else:
                    print(f"  {notify_msg} (alert still visible in session output)")
        elif verbose:
            if skip_telemetry:
                print("  Notification skipped (no-network mode)")
            elif args.no_notify:
                print("  Notification skipped (--no-notify)")
            else:
                print("  No critical/high detections, notification skipped")
    else:
        if verbose:
            print("  No detections found")

    # --- JSON output for agent consumption ---
    if use_json:
        agent_report = build_agent_report(
            agent_info, scoring, detections, env_context, notify_result
        )
        if skip_telemetry:
            agent_report["telemetry_sent"] = False
            agent_report["mode"] = "dry-run" if args.dry_run else "local-only"
        print(json.dumps(agent_report, indent=2))
    else:
        # Print summary for humans
        if verbose:
            print()
            print("=" * 60)
            mode_label = ""
            if args.dry_run:
                mode_label = " (DRY RUN — nothing sent)"
            elif args.local_only:
                mode_label = " (LOCAL ONLY — no telemetry)"
            print(f"   Assessment Complete!{mode_label}")
            print(f"   Trust Tier: {scoring['trust_tier']}")
            print(f"   Score: {scoring['score']}/100")
            print(f"   Passed: {telemetry['summary']['passed']}/{len(results)}")
            if detections:
                print(f"   Detections: {len(detections)} ({scoring['critical_failures']} critical, {scoring['high_failures']} high)")
            print("=" * 60)
            print()
            if not skip_telemetry:
                print(f"   View dashboard: https://www.trustmyagent.ai/trust-center.html?agent_id={agent_info['agent_id']}")
            else:
                print(f"   To send results to dashboard, run without --dry-run / --local-only")
            print()

    # Always exit 0 - the report itself communicates the trust posture.
    # Exit 1 caused exec tool wrappers to treat the entire output as an error.
    sys.exit(0)


if __name__ == "__main__":
    main()

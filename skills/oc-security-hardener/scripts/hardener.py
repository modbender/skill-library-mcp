#!/usr/bin/env python3
"""
security-hardener: Audit and harden OpenClaw configurations.
Scans for vulnerabilities, exposed credentials, insecure settings.
"""

import argparse
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
DEFAULT_CONFIG_DIR = Path.home() / ".openclaw"

# API key patterns to detect exposed secrets
SECRET_PATTERNS = [
    (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API Key"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
    (r"gsk_[a-zA-Z0-9]{20,}", "Groq API Key"),
    (r"AIza[a-zA-Z0-9_-]{35}", "Google API Key"),
    (r"tvly-[a-zA-Z0-9_-]{20,}", "Tavily API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"xoxb-[0-9]+-[a-zA-Z0-9]+", "Slack Bot Token"),
    (r"sk-ant-oat01-[a-zA-Z0-9_-]+", "Anthropic OAuth Token"),
]


class SecurityCheck:
    def __init__(self, name: str, severity: str, description: str):
        self.name = name
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.description = description
        self.passed = False
        self.details = ""
        self.fix = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "severity": self.severity,
            "passed": self.passed,
            "description": self.description,
            "details": self.details,
            "fix": self.fix,
        }


SEVERITY_SCORES = {"CRITICAL": 20, "HIGH": 15, "MEDIUM": 10, "LOW": 5}


def load_config(path: Path) -> dict | None:
    if not path.exists():
        print(f"Config file not found: {path}", file=sys.stderr)
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {path}: {e}", file=sys.stderr)
        return None


# ─── Security Checks ────────────────────────────────────────

def check_gateway_bind(config: dict) -> SecurityCheck:
    c = SecurityCheck("gateway-bind", "CRITICAL", "Gateway should be bound to loopback only")
    bind = config.get("gateway", {}).get("bind", "")
    if bind in ("loopback", "localhost", "127.0.0.1"):
        c.passed = True
        c.details = f"Gateway bound to '{bind}'"
    elif not bind:
        c.details = "No gateway bind configured (may default to all interfaces)"
        c.fix = 'Set "gateway": {"bind": "loopback"}'
    else:
        c.details = f"Gateway bound to '{bind}' — exposed to network"
        c.fix = 'Change to "gateway": {"bind": "loopback"}'
    return c


def check_insecure_auth(config: dict) -> SecurityCheck:
    c = SecurityCheck("insecure-auth", "HIGH", "Insecure auth options should be disabled")
    ui = config.get("gateway", {}).get("controlUi", {})
    issues = []
    if ui.get("allowInsecureAuth"):
        issues.append("allowInsecureAuth is enabled")
    if ui.get("dangerouslyDisableDeviceAuth"):
        issues.append("dangerouslyDisableDeviceAuth is enabled")
    if issues:
        c.details = "; ".join(issues)
        c.fix = "Remove these keys from gateway.controlUi"
    else:
        c.passed = True
        c.details = "No insecure auth options found"
    return c


def check_exec_sandbox(config: dict) -> SecurityCheck:
    c = SecurityCheck("exec-sandbox", "HIGH", "Exec sandbox should be restricted")
    sandbox = config.get("tools", {}).get("exec", {}).get("sandboxMode", "")
    if sandbox == "restricted":
        c.passed = True
        c.details = "Exec sandbox mode: restricted"
    elif sandbox:
        c.details = f"Exec sandbox mode: {sandbox}"
        c.fix = 'Set "tools": {"exec": {"sandboxMode": "restricted"}}'
    else:
        c.details = "No exec sandbox mode configured"
        c.fix = 'Add "tools": {"exec": {"sandboxMode": "restricted"}}'
    return c


def check_agent_permissions(config: dict) -> SecurityCheck:
    c = SecurityCheck("agent-allow-all", "MEDIUM", "Agent-to-agent permissions should be specific")
    a2a = config.get("tools", {}).get("agentToAgent", {})
    allow = a2a.get("allow", [])
    if not a2a.get("enabled"):
        c.passed = True
        c.details = "Agent-to-agent communication disabled"
    elif allow == ["*"]:
        c.details = 'agentToAgent.allow is ["*"] — all agents can call each other'
        c.fix = "List specific agent names instead of wildcard"
    else:
        c.passed = True
        c.details = f"Agent-to-agent limited to: {allow}"
    return c


def check_heartbeat(config: dict) -> SecurityCheck:
    c = SecurityCheck("no-heartbeat", "MEDIUM", "Heartbeat should be configured for outage detection")
    hb = config.get("agents", {}).get("defaults", {}).get("heartbeat", {})
    if hb.get("every"):
        c.passed = True
        c.details = f"Heartbeat configured: every {hb['every']}"
    else:
        c.details = "No heartbeat configured"
        c.fix = 'Add "agents.defaults.heartbeat": {"every": "15m", "target": "last"}'
    return c


def check_session_reset(config: dict) -> SecurityCheck:
    c = SecurityCheck("no-session-reset", "MEDIUM", "Session reset policy prevents memory leaks")
    session = config.get("session", {}).get("reset", {})
    if session.get("mode"):
        c.passed = True
        c.details = f"Session reset: {session['mode']}"
    else:
        c.details = "No session reset policy configured"
        c.fix = 'Add "session": {"reset": {"mode": "daily", "atHour": 4, "idleMinutes": 120}}'
    return c


def check_context_pruning(config: dict) -> SecurityCheck:
    c = SecurityCheck("no-pruning", "LOW", "Context pruning prevents cost overrun")
    pruning = config.get("agents", {}).get("defaults", {}).get("contextPruning", {})
    if pruning.get("mode"):
        c.passed = True
        c.details = f"Pruning mode: {pruning['mode']}, TTL: {pruning.get('ttl', 'N/A')}"
    else:
        c.details = "No context pruning configured"
        c.fix = 'Add "agents.defaults.contextPruning": {"mode": "cache-ttl", "ttl": "6h"}'
    return c


def check_memory_flush(config: dict) -> SecurityCheck:
    c = SecurityCheck("no-memory-flush", "LOW", "Memory flush preserves context during pruning")
    flush = config.get("agents", {}).get("defaults", {}).get("compaction", {}).get("memoryFlush", {})
    if flush.get("enabled"):
        c.passed = True
        c.details = f"Memory flush enabled at {flush.get('softThresholdTokens', 'N/A')} tokens"
    else:
        c.details = "Memory flush not enabled"
        c.fix = 'Enable under "agents.defaults.compaction.memoryFlush"'
    return c


ALL_CHECKS = [
    check_gateway_bind,
    check_insecure_auth,
    check_exec_sandbox,
    check_agent_permissions,
    check_heartbeat,
    check_session_reset,
    check_context_pruning,
    check_memory_flush,
]


def check_exposed_keys(config: dict) -> SecurityCheck:
    """Scan config for exposed API keys."""
    c = SecurityCheck("exposed-keys", "CRITICAL", "API keys should be in .env, not in config")
    config_str = json.dumps(config)
    found = []
    for pattern, name in SECRET_PATTERNS:
        matches = re.findall(pattern, config_str)
        if matches:
            # Mask the key
            for m in matches:
                masked = m[:8] + "..." + m[-4:]
                found.append(f"{name}: {masked}")
    if found:
        c.details = "Found exposed keys: " + "; ".join(found)
        c.fix = "Move all API keys to ~/.openclaw/.env and use environment variable references"
    else:
        c.passed = True
        c.details = "No exposed API keys found in config"
    return c


def check_file_permissions(config_dir: Path) -> SecurityCheck:
    """Check that sensitive files have correct permissions."""
    c = SecurityCheck("file-perms", "HIGH", "Sensitive files should have 600 permissions")
    issues = []
    for filename in ["openclaw.json", ".env"]:
        filepath = config_dir / filename
        if filepath.exists():
            mode = filepath.stat().st_mode
            perms = stat.S_IMODE(mode)
            if perms & (stat.S_IRGRP | stat.S_IROTH):
                issues.append(f"{filename}: {oct(perms)} (readable by group/others)")
    if issues:
        c.details = "; ".join(issues)
        c.fix = "Run: chmod 600 ~/.openclaw/openclaw.json ~/.openclaw/.env"
    else:
        c.passed = True
        c.details = "File permissions are correct"
    return c


# ─── Commands ────────────────────────────────────────────────

def compute_score(results: list[SecurityCheck]) -> int:
    """Compute security score 0-100."""
    total_possible = sum(SEVERITY_SCORES[c.severity] for c in results)
    penalty = sum(SEVERITY_SCORES[c.severity] for c in results if not c.passed)
    return max(0, round(100 - (penalty / max(total_possible, 1) * 100)))


def score_label(score: int) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    return "Poor"


def cmd_audit(config_path: Path, fmt: str = "text"):
    config = load_config(config_path)
    if not config:
        sys.exit(1)

    results = [check_fn(config) for check_fn in ALL_CHECKS]
    results.append(check_exposed_keys(config))
    results.append(check_file_permissions(config_path.parent))

    score = compute_score(results)

    if fmt == "json":
        output = {
            "score": score,
            "label": score_label(score),
            "checks": [r.to_dict() for r in results],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  OPENCLAW SECURITY AUDIT")
        print(f"{'='*55}")
        print(f"  Score: {score}/100 ({score_label(score)})")
        print(f"{'='*55}")

        for r in results:
            icon = "  PASS" if r.passed else "  FAIL"
            sev = f"[{r.severity}]"
            print(f"  {icon} {sev:10} {r.name}")
            if not r.passed:
                print(f"         {r.details}")
                if r.fix:
                    print(f"         Fix: {r.fix}")
        print(f"{'='*55}\n")


def cmd_fix(config_path: Path, only: list = None):
    config = load_config(config_path)
    if not config:
        sys.exit(1)

    # Create backup
    backup = config_path.with_suffix(f".json.bak-security-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    backup.write_text(json.dumps(config, indent=2))
    print(f"Backup saved to: {backup}")

    fixes_applied = 0

    # Fix gateway bind
    if not only or "gateway" in only:
        bind = config.get("gateway", {}).get("bind", "")
        if bind not in ("loopback", "localhost", "127.0.0.1"):
            config.setdefault("gateway", {})["bind"] = "loopback"
            print("  Fixed: gateway.bind → loopback")
            fixes_applied += 1

    # Fix insecure auth
    if not only or "auth" in only:
        ui = config.get("gateway", {}).get("controlUi", {})
        for key in ["allowInsecureAuth", "dangerouslyDisableDeviceAuth"]:
            if key in ui:
                del ui[key]
                print(f"  Fixed: removed gateway.controlUi.{key}")
                fixes_applied += 1

    # Fix exec sandbox
    if not only or "exec" in only:
        sandbox = config.get("tools", {}).get("exec", {}).get("sandboxMode", "")
        if sandbox != "restricted":
            config.setdefault("tools", {}).setdefault("exec", {})["sandboxMode"] = "restricted"
            print("  Fixed: tools.exec.sandboxMode → restricted")
            fixes_applied += 1

    # Fix permissions
    if not only or "permissions" in only:
        for filename in ["openclaw.json", ".env"]:
            filepath = config_path.parent / filename
            if filepath.exists():
                os.chmod(filepath, 0o600)
                print(f"  Fixed: {filename} permissions → 600")
                fixes_applied += 1

    # Save config
    config_path.write_text(json.dumps(config, indent=2))

    print(f"\n{fixes_applied} fix(es) applied. Config saved.")
    print("Run 'hardener.py audit' to verify.")


def cmd_scan_secrets(config_path: Path):
    config = load_config(config_path)
    if not config:
        sys.exit(1)

    result = check_exposed_keys(config)
    if result.passed:
        print("No exposed secrets found in config.")
    else:
        print("EXPOSED SECRETS DETECTED:")
        print(result.details)
        print(f"\nFix: {result.fix}")


def cmd_report(config_path: Path, output: str = None):
    config = load_config(config_path)
    if not config:
        sys.exit(1)

    results = [check_fn(config) for check_fn in ALL_CHECKS]
    results.append(check_exposed_keys(config))
    results.append(check_file_permissions(config_path.parent))

    score = compute_score(results)

    lines = []
    lines.append(f"# OpenClaw Security Audit Report")
    lines.append(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append(f"*Config: {config_path}*")
    lines.append("")
    lines.append(f"## Score: {score}/100 ({score_label(score)})")
    lines.append("")

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        checks = [r for r in results if r.severity == severity]
        if not checks:
            continue
        lines.append(f"### {severity}")
        for r in checks:
            icon = "PASS" if r.passed else "**FAIL**"
            lines.append(f"- [{icon}] **{r.name}**: {r.description}")
            if not r.passed:
                lines.append(f"  - Issue: {r.details}")
                if r.fix:
                    lines.append(f"  - Fix: {r.fix}")
        lines.append("")

    lines.append("## Recommendations")
    failed = [r for r in results if not r.passed]
    if failed:
        for r in failed:
            lines.append(f"1. **{r.name}** ({r.severity}): {r.fix}")
    else:
        lines.append("All checks passed. Configuration meets security best practices.")
    lines.append("")

    text = "\n".join(lines)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Report saved to {output}", file=sys.stderr)
    else:
        print(text)


def cmd_check_perms(config_dir: Path):
    result = check_file_permissions(config_dir)
    if result.passed:
        print("All file permissions are correct.")
    else:
        print("Permission issues found:")
        print(result.details)
        print(f"\nFix: {result.fix}")


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="OpenClaw Security Hardener")
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="Full security audit")
    p_audit.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    p_audit.add_argument("-f", "--format", default="text", choices=["text", "json"])

    p_fix = sub.add_parser("fix", help="Auto-fix issues")
    p_fix.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    p_fix.add_argument("--only", help="Comma-separated: gateway,auth,exec,permissions")

    p_scan = sub.add_parser("scan-secrets", help="Scan for exposed credentials")
    p_scan.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))

    p_report = sub.add_parser("report", help="Generate security report")
    p_report.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    p_report.add_argument("-o", "--output", help="Output file")

    p_perms = sub.add_parser("check-perms", help="Check file permissions")
    p_perms.add_argument("--config-dir", default=str(DEFAULT_CONFIG_DIR))

    args = parser.parse_args()

    if args.command == "audit":
        cmd_audit(Path(args.config), args.format)
    elif args.command == "fix":
        only = [o.strip() for o in args.only.split(",")] if args.only else None
        cmd_fix(Path(args.config), only)
    elif args.command == "scan-secrets":
        cmd_scan_secrets(Path(args.config))
    elif args.command == "report":
        cmd_report(Path(args.config), args.output)
    elif args.command == "check-perms":
        cmd_check_perms(Path(args.config_dir))


if __name__ == "__main__":
    main()

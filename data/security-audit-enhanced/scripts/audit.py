#!/usr/bin/env python3
"""
Security Audit Enhanced - Automated security scanning for AI agent configurations.

Features:
- 13 security domain checks
- Cross-platform support (macOS/Linux)
- Security scoring (0-100)
- Multiple output formats (JSON/HTML/Markdown)
- Baseline comparison
- CI/CD integration
"""

import os
import sys
import json
import subprocess
import platform
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configuration paths
CONFIG_PATHS = [
    Path.home() / ".clawdbot" / "clawdbot.json",
    Path.home() / ".clawdbot" / "config.yaml",
    Path(".clawdbotrc"),
]

CREDENTIALS_PATHS = [
    Path.home() / ".clawdbot" / "credentials",
    Path.home() / ".clawdbot" / "agents",
]

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
    "passed": 0,
}


class SecurityAudit:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.config = {}
        self.findings: List[Dict[str, Any]] = []
        self.platform = platform.system().lower()
        self.score = 100

    def _find_config(self) -> Optional[Path]:
        """Find the configuration file."""
        for path in CONFIG_PATHS:
            if path.exists():
                return path
        return None

    def _run_command(self, cmd: List[str]) -> Tuple[str, int]:
        """Run a shell command and return output + return code."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip(), result.returncode
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "", 1

    def _run_jq(self, query: str, file_path: Path) -> Any:
        """Run jq query on JSON file."""
        if not file_path or not file_path.exists():
            return None
        output, code = self._run_command(["jq", query, str(file_path)])
        if code != 0:
            return None
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output if output else None

    def _get_file_permissions(self, path: Path) -> Optional[str]:
        """Get file permissions in octal format (cross-platform)."""
        if not path.exists():
            return None
        if self.platform == "darwin":
            output, _ = self._run_command(["stat", "-f", "%Lp", str(path)])
        else:
            output, _ = self._run_command(["stat", "-c", "%a", str(path)])
        return output if output else None

    def _add_finding(
        self,
        domain: str,
        severity: str,
        finding: str,
        recommendation: str,
        details: Optional[Dict] = None,
    ):
        """Add a finding to the results."""
        self.findings.append({
            "domain": domain,
            "severity": severity,
            "finding": finding,
            "recommendation": recommendation,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        })

    def check_gateway_exposure(self) -> bool:
        """Check gateway binding and authentication."""
        domain = "gateway-exposure"

        if not self.config_path:
            return True

        # Check bind address
        bind = self._run_jq(".gateway.bind", self.config_path)
        if bind and bind in ["0.0.0.0", "public", "*"]:
            self._add_finding(
                domain,
                "critical",
                f"Gateway bound to public address: {bind}",
                "Set gateway.bind to '127.0.0.1' or 'lan'",
                {"current_bind": bind}
            )
            return False

        # Check authentication
        auth_token = self._run_jq(".gateway.auth_token", self.config_path)
        env_token = os.environ.get("CLAWDBOT_GATEWAY_TOKEN")

        if not auth_token and not env_token:
            if bind and bind not in ["127.0.0.1", "localhost"]:
                self._add_finding(
                    domain,
                    "critical",
                    "Gateway has no authentication token",
                    "Set CLAWDBOT_GATEWAY_TOKEN environment variable or gateway.auth_token in config",
                )
                return False

        return True

    def check_dm_policy(self) -> bool:
        """Check DM policy configuration."""
        domain = "dm-policy"
        passed = True

        if not self.config_path:
            return True

        # Get all channel DM policies
        channels = self._run_jq(".channels", self.config_path)
        if not channels or not isinstance(channels, dict):
            return True

        for channel_name, channel_config in channels.items():
            if not isinstance(channel_config, dict):
                continue
            dm_policy = channel_config.get("dmPolicy", "unknown")
            if dm_policy in ["open", "allow", "public"]:
                self._add_finding(
                    domain,
                    "high",
                    f"Channel '{channel_name}' has open DM policy: {dm_policy}",
                    f"Set channels.{channel_name}.dmPolicy to 'allowlist' with trusted users",
                    {"channel": channel_name, "policy": dm_policy}
                )
                passed = False

        return passed

    def check_group_policy(self) -> bool:
        """Check group access control."""
        domain = "group-access-control"
        passed = True

        if not self.config_path:
            return True

        channels = self._run_jq(".channels", self.config_path)
        if not channels or not isinstance(channels, dict):
            return True

        for channel_name, channel_config in channels.items():
            if not isinstance(channel_config, dict):
                continue
            group_policy = channel_config.get("groupPolicy", "unknown")
            if group_policy in ["open", "allow", "public"]:
                self._add_finding(
                    domain,
                    "high",
                    f"Channel '{channel_name}' has open group policy: {group_policy}",
                    f"Set channels.{channel_name}.groupPolicy to 'allowlist' with approved group IDs",
                    {"channel": channel_name, "policy": group_policy}
                )
                passed = False

        return passed

    def check_credentials_security(self) -> bool:
        """Check credential file permissions and storage."""
        domain = "credentials-security"
        passed = True

        # Check main config permissions
        if self.config_path and self.config_path.exists():
            perms = self._get_file_permissions(self.config_path)
            if perms and int(perms, 8) > 0o600:
                self._add_finding(
                    domain,
                    "critical",
                    f"Config file has overly permissive permissions: {perms}",
                    f"Run: chmod 600 {self.config_path}",
                    {"file": str(self.config_path), "permissions": perms}
                )
                passed = False

        # Check credentials directory
        for cred_path in CREDENTIALS_PATHS:
            if cred_path.exists():
                perms = self._get_file_permissions(cred_path)
                if perms and int(perms, 8) > 0o700:
                    self._add_finding(
                        domain,
                        "high",
                        f"Credentials directory has loose permissions: {perms}",
                        f"Run: chmod 700 {cred_path}",
                        {"path": str(cred_path), "permissions": perms}
                    )
                    passed = False

                # Check JSON files in credentials
                for json_file in cred_path.rglob("*.json"):
                    perms = self._get_file_permissions(json_file)
                    if perms and int(perms, 8) > 0o600:
                        self._add_finding(
                            domain,
                            "high",
                            f"Credential file has loose permissions: {perms}",
                            f"Run: chmod 600 {json_file}",
                            {"file": str(json_file), "permissions": perms}
                        )
                        passed = False

        return passed

    def check_browser_control(self) -> bool:
        """Check browser control security."""
        domain = "browser-control-exposure"

        if not self.config_path:
            return True

        remote_url = self._run_jq(".browser.remoteControlUrl", self.config_path)
        remote_token = self._run_jq(".browser.remoteControlToken", self.config_path)

        if remote_url and not remote_token:
            self._add_finding(
                domain,
                "high",
                "Browser remote control enabled without authentication token",
                "Set browser.remoteControlToken in config",
                {"remote_url": remote_url}
            )
            return False

        if remote_url and not remote_url.startswith("https://"):
            self._add_finding(
                domain,
                "medium",
                "Browser remote control using insecure HTTP",
                "Use HTTPS for browser.remoteControlUrl",
                {"remote_url": remote_url}
            )
            return False

        return True

    def check_network_binding(self) -> bool:
        """Check network exposure configuration."""
        domain = "gateway-bind-network"

        if not self.config_path:
            return True

        mode = self._run_jq(".gateway.mode", self.config_path)
        tailscale = self._run_jq(".gateway.tailscale.mode", self.config_path)

        if mode == "public":
            self._add_finding(
                domain,
                "high",
                "Gateway is in public mode",
                "Set gateway.mode to 'local' or 'lan' for development",
                {"mode": mode}
            )
            return False

        if tailscale and tailscale not in ["off", None]:
            self._add_finding(
                domain,
                "medium",
                f"Tailscale mode is enabled: {tailscale}",
                "Ensure this is intentional. Set gateway.tailscale.mode to 'off' if unused",
                {"tailscale_mode": tailscale}
            )
            return False

        return True

    def check_tool_access(self) -> bool:
        """Check tool access restrictions."""
        domain = "tool-access-sandboxing"

        if not self.config_path:
            return True

        restrict_tools = self._run_jq(".restrict_tools", self.config_path)
        workspace_access = self._run_jq(".workspaceAccess", self.config_path)
        sandbox = self._run_jq(".sandbox", self.config_path)

        issues = []

        if restrict_tools is False:
            issues.append("Tool restriction is disabled")

        if workspace_access and workspace_access not in ["ro", "none"]:
            issues.append(f"Workspace access is '{workspace_access}', should be 'ro' or 'none'")

        if sandbox == "none":
            issues.append("Sandboxing is disabled")

        if issues:
            self._add_finding(
                domain,
                "medium",
                "; ".join(issues),
                "Enable tool restrictions and sandboxing for sensitive operations",
                {"restrict_tools": restrict_tools, "workspace_access": workspace_access, "sandbox": sandbox}
            )
            return False

        return True

    def check_file_permissions(self) -> bool:
        """Check overall file permissions."""
        domain = "file-permissions-disk"
        passed = True

        clawdbot_dir = Path.home() / ".clawdbot"
        if clawdbot_dir.exists():
            perms = self._get_file_permissions(clawdbot_dir)
            if perms and int(perms, 8) > 0o700:
                self._add_finding(
                    domain,
                    "medium",
                    f"Clawdbot directory has loose permissions: {perms}",
                    f"Run: chmod 700 {clawdbot_dir}",
                    {"path": str(clawdbot_dir), "permissions": perms}
                )
                passed = False

        return passed

    def check_plugin_trust(self) -> bool:
        """Check plugin allowlist configuration."""
        domain = "plugin-trust-model"

        if not self.config_path:
            return True

        plugins = self._run_jq(".plugins", self.config_path)

        if plugins and isinstance(plugins, dict):
            allowlist = plugins.get("allowlist", [])
            if not allowlist:
                self._add_finding(
                    domain,
                    "medium",
                    "No plugin allowlist configured",
                    "Add trusted plugins to plugins.allowlist array",
                    {"plugins": plugins}
                )
                return False

        return True

    def check_logging_redaction(self) -> bool:
        """Check logging redaction settings."""
        domain = "logging-redaction"

        if not self.config_path:
            return True

        redact = self._run_jq(".logging.redactSensitive", self.config_path)

        if redact in ["off", None]:
            self._add_finding(
                domain,
                "medium",
                f"Sensitive data redaction is disabled or not set: {redact}",
                "Set logging.redactSensitive to 'tools' or 'all'",
                {"redact_sensitive": redact}
            )
            return False

        return True

    def check_prompt_injection(self) -> bool:
        """Check prompt injection protection."""
        domain = "prompt-injection"

        if not self.config_path:
            return True

        wrap_content = self._run_jq(".wrap_untrusted_content", self.config_path)
        mention_gate = self._run_jq(".mentionGate", self.config_path)

        issues = []

        if not wrap_content:
            issues.append("Untrusted content wrapping is disabled")

        if not mention_gate:
            issues.append("Mention gate is disabled")

        if issues:
            self._add_finding(
                domain,
                "medium",
                "; ".join(issues),
                "Enable wrap_untrusted_content and mentionGate for protection",
                {"wrap_untrusted_content": wrap_content, "mention_gate": mention_gate}
            )
            return False

        return True

    def check_dangerous_commands(self) -> bool:
        """Check dangerous command blocking."""
        domain = "dangerous-commands"

        if not self.config_path:
            return True

        blocked = self._run_jq(".blocked_commands", self.config_path)

        if not blocked or not isinstance(blocked, list):
            self._add_finding(
                domain,
                "medium",
                "No blocked commands configured",
                "Add dangerous patterns to blocked_commands array",
                {"blocked_commands": blocked}
            )
            return False

        # Check if critical patterns are included
        critical_patterns = ["rm -rf", "curl |", "wget |", "mkfs"]
        missing = [p for p in critical_patterns if not any(p in cmd for cmd in blocked)]

        if missing:
            self._add_finding(
                domain,
                "medium",
                f"Missing critical blocked patterns: {', '.join(missing)}",
                "Add these patterns to blocked_commands",
                {"missing_patterns": missing, "current_blocked": blocked}
            )
            return False

        return True

    def check_secret_scanning(self) -> bool:
        """Check secret scanning setup."""
        domain = "secret-scanning"

        # Check if detect-secrets is installed
        output, code = self._run_command(["which", "detect-secrets"])

        if code != 0:
            self._add_finding(
                domain,
                "low",
                "detect-secrets is not installed",
                "Install: pip install detect-secrets",
            )
            return False

        # Check for baseline file
        baseline_exists = (Path.cwd() / ".secrets.baseline").exists()
        if not baseline_exists:
            self._add_finding(
                domain,
                "low",
                "No .secrets.baseline file found",
                "Run: detect-secrets scan --baseline .secrets.baseline",
            )
            return False

        return True

    def run_audit(self, critical_only: bool = False) -> Dict[str, Any]:
        """Run all security checks."""
        checks = [
            ("Gateway Exposure", self.check_gateway_exposure, True),
            ("DM Policy", self.check_dm_policy, True),
            ("Group Policy", self.check_group_policy, True),
            ("Credentials Security", self.check_credentials_security, True),
            ("Browser Control", self.check_browser_control, not critical_only),
            ("Network Binding", self.check_network_binding, not critical_only),
            ("Tool Access", self.check_tool_access, not critical_only),
            ("File Permissions", self.check_file_permissions, not critical_only),
            ("Plugin Trust", self.check_plugin_trust, not critical_only),
            ("Logging Redaction", self.check_logging_redaction, not critical_only),
            ("Prompt Injection", self.check_prompt_injection, not critical_only),
            ("Dangerous Commands", self.check_dangerous_commands, not critical_only),
            ("Secret Scanning", self.check_secret_scanning, not critical_only),
        ]

        passed_count = 0
        for name, check_func, should_run in checks:
            if should_run:
                try:
                    if check_func():
                        passed_count += 1
                except Exception as e:
                    self._add_finding(
                        name.lower().replace(" ", "-"),
                        "medium",
                        f"Check failed with error: {str(e)}",
                        "Review configuration manually",
                    )

        # Calculate score
        self._calculate_score()

        return self._generate_report(passed_count, len(checks))

    def _calculate_score(self):
        """Calculate overall security score."""
        self.score = 100
        for finding in self.findings:
            severity = finding.get("severity", "low")
            weight = SEVERITY_WEIGHTS.get(severity, 3)
            self.score = max(0, self.score - weight)

    def _generate_report(self, passed: int, total: int) -> Dict[str, Any]:
        """Generate the audit report."""
        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in self.findings:
            sev = finding.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Determine rating
        if self.score >= 90:
            rating = "Excellent"
        elif self.score >= 70:
            rating = "Good"
        elif self.score >= 50:
            rating = "Fair"
        elif self.score >= 30:
            rating = "Poor"
        else:
            rating = "Critical"

        return {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "config_path": str(self.config_path) if self.config_path else None,
            "score": self.score,
            "rating": rating,
            "summary": {
                "critical": severity_counts["critical"],
                "high": severity_counts["high"],
                "medium": severity_counts["medium"],
                "low": severity_counts["low"],
                "passed": passed,
                "total_checks": total,
            },
            "findings": self.findings,
        }

    def print_report(self, report: Dict[str, Any], format: str = "text"):
        """Print the report in specified format."""
        if format == "json":
            print(json.dumps(report, indent=2))
            return

        if format == "markdown":
            self._print_markdown(report)
            return

        # Text format
        print("\n" + "=" * 65)
        print("🔒 SECURITY AUDIT REPORT")
        print("=" * 65)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Platform: {report['platform']}")
        print(f"Config: {report.get('config_path', 'Not found')}")
        print()
        print(f"Security Score: {report['score']}/100 ({report['rating']})")
        print()
        print("┌─ SUMMARY ──────────────────────────────────────────────")
        print(f"│ 🔴 Critical:  {report['summary']['critical']}")
        print(f"│ 🟠 High:      {report['summary']['high']}")
        print(f"│ 🟡 Medium:    {report['summary']['medium']}")
        print(f"│ 🔵 Low:       {report['summary']['low']}")
        print(f"│ ✅ Passed:    {report['summary']['passed']}/{report['summary']['total_checks']}")
        print("└─────────────────────────────────────────────────────────")

        if report['findings']:
            print()
            print("┌─ FINDINGS ─────────────────────────────────────────────")
            for finding in report['findings']:
                severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
                icon = severity_icons.get(finding['severity'], "⚪")
                print(f"│ {icon} [{finding['severity'].upper()}] {finding['domain']}")
                print(f"│    Finding: {finding['finding']}")
                print(f"│    → Fix: {finding['recommendation']}")
                print("│")
            print("└─────────────────────────────────────────────────────────")

        print()
        print("This audit was performed by Security Audit Enhanced.")
        print("No changes were made to your configuration.")

    def _print_markdown(self, report: Dict[str, Any]):
        """Print markdown formatted report."""
        print(f"# 🔒 Security Audit Report\n")
        print(f"**Timestamp:** {report['timestamp']}")
        print(f"**Platform:** {report['platform']}")
        print(f"**Config:** {report.get('config_path', 'Not found')}\n")
        print(f"## Score: {report['score']}/100 ({report['rating']})\n")
        print("## Summary\n")
        print("| Severity | Count |")
        print("|----------|-------|")
        print(f"| 🔴 Critical | {report['summary']['critical']} |")
        print(f"| 🟠 High | {report['summary']['high']} |")
        print(f"| 🟡 Medium | {report['summary']['medium']} |")
        print(f"| 🔵 Low | {report['summary']['low']} |")
        print(f"| ✅ Passed | {report['summary']['passed']}/{report['summary']['total_checks']} |\n")

        if report['findings']:
            print("## Findings\n")
            for finding in report['findings']:
                print(f"### {finding['severity'].upper()}: {finding['domain']}\n")
                print(f"- **Finding:** {finding['finding']}")
                print(f"- **Recommendation:** {finding['recommendation']}\n")


def main():
    parser = argparse.ArgumentParser(description="Security Audit Enhanced")
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument("--full", action="store_true", help="Run all checks")
    parser.add_argument("--critical", action="store_true", help="Run critical checks only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--markdown", action="store_true", help="Output as Markdown")
    parser.add_argument("--output", type=Path, help="Write output to file")
    parser.add_argument("--baseline", type=Path, help="Compare with baseline file")
    parser.add_argument("--save-baseline", type=Path, help="Save current state as baseline")

    args = parser.parse_args()

    audit = SecurityAudit(args.config)

    # Determine output format
    if args.json:
        format_type = "json"
    elif args.markdown:
        format_type = "markdown"
    else:
        format_type = "text"

    # Run audit
    report = audit.run_audit(critical_only=args.critical and not args.full)

    # Handle baseline comparison
    if args.baseline and args.baseline.exists():
        with open(args.baseline) as f:
            baseline = json.load(f)
        report["baseline_comparison"] = {
            "previous_score": baseline.get("score", 0),
            "score_change": report["score"] - baseline.get("score", 0),
        }

    # Save baseline if requested
    if args.save_baseline:
        with open(args.save_baseline, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Baseline saved to {args.save_baseline}")

    # Output
    if args.output:
        with open(args.output, "w") as f:
            if args.json:
                json.dump(report, f, indent=2)
            else:
                # Redirect print to file
                import io
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                audit.print_report(report, format_type)
                f.write(sys.stdout.getvalue())
                sys.stdout = old_stdout
        print(f"Report saved to {args.output}")
    else:
        audit.print_report(report, format_type)

    # Exit with error code if critical issues found
    if report["summary"]["critical"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

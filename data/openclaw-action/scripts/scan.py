#!/usr/bin/env python3
"""
OpenClaw GitHub Action Scanner

Orchestrates security scans and outputs findings in GitHub Actions format.
Free tier: detect + alert only. No automated remediation.

Zero external dependencies - Python stdlib only.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_scanner(scanner_path: Path, workspace: Path, command: str) -> dict:
    """Run a scanner and capture its JSON output."""
    try:
        # Each scanner outputs JSON to stdout when given --json flag
        result = subprocess.run(
            [sys.executable, str(scanner_path), command, "-w", str(workspace), "--json"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return {"findings": [], "error": result.stderr if result.stderr else None}
    except subprocess.TimeoutExpired:
        return {"findings": [], "error": "Scanner timed out"}
    except json.JSONDecodeError:
        return {"findings": [], "error": "Invalid JSON output"}
    except Exception as e:
        return {"findings": [], "error": str(e)}


def severity_to_level(severity: str) -> str:
    """Map severity to GitHub annotation level."""
    severity = severity.lower()
    if severity in ("critical", "high"):
        return "error"
    elif severity in ("medium", "warning"):
        return "warning"
    return "notice"


def emit_annotation(level: str, file: str, line: int, message: str, title: str = ""):
    """Emit a GitHub Actions annotation."""
    # Format: ::error file={name},line={line},title={title}::{message}
    title_part = f",title={title}" if title else ""
    print(f"::{level} file={file},line={line}{title_part}::{message}")


def emit_summary(findings: list, scanner_results: dict):
    """Write findings to GitHub Actions job summary."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return

    with open(summary_file, "a") as f:
        f.write("## OpenClaw Security Scan Results\n\n")

        if not findings:
            f.write("No security issues detected.\n")
            return

        # Count by severity
        critical = sum(1 for f in findings if f.get("severity", "").lower() in ("critical", "high"))
        medium = sum(1 for f in findings if f.get("severity", "").lower() in ("medium", "warning"))
        low = len(findings) - critical - medium

        f.write(f"| Severity | Count |\n")
        f.write(f"|----------|-------|\n")
        if critical:
            f.write(f"| Critical/High | {critical} |\n")
        if medium:
            f.write(f"| Medium | {medium} |\n")
        if low:
            f.write(f"| Low | {low} |\n")
        f.write(f"| **Total** | **{len(findings)}** |\n\n")

        # Group by scanner
        f.write("### Findings by Scanner\n\n")
        for scanner, result in scanner_results.items():
            scanner_findings = result.get("findings", [])
            if scanner_findings:
                f.write(f"<details>\n<summary><b>{scanner}</b> ({len(scanner_findings)} findings)</summary>\n\n")
                f.write("| File | Line | Severity | Issue |\n")
                f.write("|------|------|----------|-------|\n")
                for finding in scanner_findings[:50]:  # Limit to 50 per scanner
                    file = finding.get("file", "unknown")
                    line = finding.get("line", 0)
                    severity = finding.get("severity", "unknown")
                    message = finding.get("message", finding.get("issue", "No description"))
                    # Escape pipe characters in message
                    message = message.replace("|", "\\|")[:100]
                    f.write(f"| `{file}` | {line} | {severity} | {message} |\n")
                if len(scanner_findings) > 50:
                    f.write(f"\n*... and {len(scanner_findings) - 50} more findings*\n")
                f.write("\n</details>\n\n")

        # Recommendations
        f.write("### Next Steps\n\n")
        f.write("1. Review the findings above\n")
        f.write("2. For secrets: rotate exposed credentials immediately\n")
        f.write("3. For injection: review and sanitize flagged patterns\n")
        f.write("4. For egress: verify any network calls are intentional\n\n")
        f.write("---\n")
        f.write("*Scanned by [OpenClaw Security](https://github.com/AtlasPA/openclaw-security)*\n")


def set_output(name: str, value: str):
    """Set a GitHub Actions output variable."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")


def main():
    # Get configuration from environment
    workspace = Path(os.environ.get("WORKSPACE", ".")).resolve()
    scanners_dir = Path(os.environ.get("SCANNERS_DIR", "."))
    scan_secrets = os.environ.get("SCAN_SECRETS", "true").lower() == "true"
    scan_injection = os.environ.get("SCAN_INJECTION", "true").lower() == "true"
    scan_egress = os.environ.get("SCAN_EGRESS", "true").lower() == "true"

    print(f"::group::OpenClaw Security Scan")
    print(f"Workspace: {workspace}")
    print(f"Scanners: secrets={scan_secrets}, injection={scan_injection}, egress={scan_egress}")
    print(f"::endgroup::")

    all_findings = []
    scanner_results = {}

    # Run enabled scanners
    if scan_secrets:
        print("::group::Scanning for exposed secrets (sentry)")
        sentry_path = scanners_dir / "sentry.py"
        if sentry_path.exists():
            result = run_scanner(sentry_path, workspace, "scan")
            scanner_results["sentry"] = result
            findings = result.get("findings", [])
            for f in findings:
                f["scanner"] = "sentry"
            all_findings.extend(findings)
            print(f"Found {len(findings)} secret exposure(s)")
            if result.get("error"):
                print(f"::warning::Sentry scanner error: {result['error']}")
        else:
            print("::warning::Sentry scanner not found")
        print("::endgroup::")

    if scan_injection:
        print("::group::Scanning for injection patterns (bastion)")
        bastion_path = scanners_dir / "bastion.py"
        if bastion_path.exists():
            # bastion uses subparser: --workspace before scan
            try:
                result = subprocess.run(
                    [sys.executable, str(bastion_path), "--workspace", str(workspace), "scan", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode == 0 and result.stdout.strip():
                    result_data = json.loads(result.stdout)
                else:
                    result_data = {"findings": [], "error": result.stderr if result.stderr else None}
            except Exception as e:
                result_data = {"findings": [], "error": str(e)}

            scanner_results["bastion"] = result_data
            findings = result_data.get("findings", [])
            for f in findings:
                f["scanner"] = "bastion"
            all_findings.extend(findings)
            print(f"Found {len(findings)} injection pattern(s)")
            if result_data.get("error"):
                print(f"::warning::Bastion scanner error: {result_data['error']}")
        else:
            print("::warning::Bastion scanner not found")
        print("::endgroup::")

    if scan_egress:
        print("::group::Scanning for exfiltration patterns (egress)")
        egress_path = scanners_dir / "egress.py"
        if egress_path.exists():
            result = run_scanner(egress_path, workspace, "scan")
            scanner_results["egress"] = result
            findings = result.get("findings", [])
            for f in findings:
                f["scanner"] = "egress"
            all_findings.extend(findings)
            print(f"Found {len(findings)} egress pattern(s)")
            if result.get("error"):
                print(f"::warning::Egress scanner error: {result['error']}")
        else:
            print("::warning::Egress scanner not found")
        print("::endgroup::")

    # Emit annotations for each finding
    print("::group::Security Findings")
    if all_findings:
        for finding in all_findings:
            file = finding.get("file", "unknown")
            line = finding.get("line", 1)
            severity = finding.get("severity", "medium")
            scanner = finding.get("scanner", "unknown")
            message = finding.get("message", finding.get("issue", "Security issue detected"))

            level = severity_to_level(severity)
            title = f"[{scanner}] {severity.upper()}"
            emit_annotation(level, file, line, message, title)

        print(f"\nTotal findings: {len(all_findings)}")
    else:
        print("No security issues detected.")
    print("::endgroup::")

    # Write job summary
    emit_summary(all_findings, scanner_results)

    # Set outputs
    has_critical = any(
        f.get("severity", "").lower() in ("critical", "high")
        for f in all_findings
    )
    set_output("findings-count", str(len(all_findings)))
    set_output("has-critical", "true" if has_critical else "false")

    # Exit code based on findings (but don't fail here - let action.yml handle it)
    print(f"\nScan complete. {len(all_findings)} finding(s), critical={has_critical}")


if __name__ == "__main__":
    main()

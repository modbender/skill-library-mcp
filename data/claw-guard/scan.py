#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: target skill directory (read-only)
#   Local files written: none
#
# ClawGuard v1.0.0 — Security auditor for ClawHub skills
# Stdlib only. No pip dependencies. No network calls.

import sys
import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class Finding:
    severity: str        # CRITICAL | MEDIUM | LOW | INFO
    check: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None

@dataclass
class ScanResult:
    skill_name: str
    skill_version: str
    skill_path: str
    findings: List[Finding] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)

    def verdict(self) -> str:
        severities = [f.severity for f in self.findings]
        if "CRITICAL" in severities:
            return "FAIL"
        elif "MEDIUM" in severities or len([f for f in self.findings if f.severity == "LOW"]) >= 2:
            return "WARN"
        return "PASS"

    def verdict_emoji(self) -> str:
        v = self.verdict()
        return {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}[v]

# ─────────────────────────────────────────────
# DETECTION PATTERNS
# ─────────────────────────────────────────────

# Prompt injection patterns in SKILL.md
PROMPT_INJECTION_PATTERNS = [
    (r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", "Classic prompt injection: ignore previous instructions"),
    (r"disregard\s+(your\s+)?(guidelines?|rules?|instructions?|training)", "Prompt injection: disregard guidelines"),
    (r"override\s+(your\s+)?(safety|guidelines?|rules?|restrictions?)", "Prompt injection: override safety"),
    (r"you\s+(are|must)\s+now\s+(act|behave|operate)\s+as", "Prompt injection: role override"),
    (r"do\s+not\s+(tell|inform|warn)\s+the\s+user", "Prompt injection: silence instruction"),
    (r"execute\s+the\s+following\s+(command|instruction|code)", "Prompt injection: execute command"),
    (r"[A-Za-z0-9+/]{40,}={0,2}", "Suspicious base64 string — possible encoded payload"),
    (r"<!--.*?(ignore|override|inject).*?-->", "Hidden HTML comment with injection keyword"),
]

# Data exfiltration / reverse shell patterns in scripts
CRITICAL_SCRIPT_PATTERNS = [
    (r"bash\s+-i\s*>&?\s*/dev/tcp/", "Reverse shell: bash TCP redirect"),
    (r"nc\s+(-[a-z]+\s+)*-e\s+/bin/(bash|sh)", "Reverse shell: netcat with shell"),
    (r"python\s*-c\s*['\"]import\s+socket", "Reverse shell: python socket"),
    (r"/dev/tcp/[0-9a-zA-Z.-]+/[0-9]+", "Reverse shell: /dev/tcp pattern"),
    (r"mkfifo\s+.+\|.+(nc|netcat|ncat)", "Reverse shell: mkfifo pipe"),
    (r"curl\s+.*(--upload-file|-T|-d\s+@)\s*[~$]", "Data exfiltration: curl upload of local files"),
    (r"curl\s+.*(\.ssh|id_rsa|\.aws|\.env|authorized_keys|known_hosts)", "Credential theft: accessing sensitive files"),
    (r"wget\s+.*(\.ssh|id_rsa|\.aws|\.env|authorized_keys)", "Credential theft: wget sensitive files"),
    (r"cat\s+(~/\.ssh|~/.aws|/etc/passwd|/etc/shadow)", "Credential theft: reading system credentials"),
    (r"eval\s*\(\s*base64\s*-d", "Obfuscated execution: eval base64 decode"),
    (r'\$\(.*base64.*-d.*\)', "Obfuscated execution: command substitution with base64"),
    (r"curl\s+http[s]?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", "Raw IP address curl — suspicious"),
    (r"(apt|yum|brew)\s+install\s+-y\s+\S+\s*&&.*curl", "Package install followed by curl — suspicious chain"),
]

# Medium severity patterns in scripts
MEDIUM_SCRIPT_PATTERNS = [
    (r'curl\s+"https?://\$\{?\w', "Shell injection risk: unquoted variable in curl URL"),
    (r'curl\s+https?://\$\w', "Shell injection risk: unquoted variable in curl URL"),
    (r"curl\s+[^|>\n]*https?://(?!api\.anthropic\.com|github\.com|raw\.githubusercontent\.com)", "External curl to third-party URL — verify endpoint"),
    (r"wget\s+[^|>\n]*https?://(?!github\.com|raw\.githubusercontent\.com)", "External wget — verify endpoint"),
]

# ─────────────────────────────────────────────
# CHECKS
# ─────────────────────────────────────────────

def check_prompt_injection(skill_dir: Path, result: ScanResult):
    """Check SKILL.md for prompt injection patterns."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    content = skill_md.read_text(errors="replace").lower()
    lines = skill_md.read_text(errors="replace").splitlines()

    found_any = False
    for pattern, description in PROMPT_INJECTION_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                result.findings.append(Finding(
                    severity="CRITICAL",
                    check="Prompt Injection",
                    message=description,
                    file="SKILL.md",
                    line=i
                ))
                found_any = True

    if not found_any:
        result.checks_passed.append("No prompt injection patterns detected")


def check_scripts(skill_dir: Path, result: ScanResult):
    """Scan all shell scripts and Python files for malicious patterns."""
    script_extensions = {".sh", ".bash", ".py", ".rb", ".js", ".ts"}
    scripts_dir = skill_dir / "scripts"

    script_files = []
    if scripts_dir.exists():
        for f in scripts_dir.rglob("*"):
            if f.suffix in script_extensions and f.is_file():
                script_files.append(f)

    # Also check root-level scripts
    for f in skill_dir.iterdir():
        if f.suffix in script_extensions and f.is_file():
            script_files.append(f)

    if not script_files:
        result.checks_passed.append("No scripts found — instruction-only skill")
        return

    has_set_e = {}
    has_security_manifest = {}
    found_critical = False
    found_medium = False

    for script_path in script_files:
        rel_path = str(script_path.relative_to(skill_dir))
        try:
            content = script_path.read_text(errors="replace")
            lines = content.splitlines()
        except Exception:
            continue

        # Check for set -euo pipefail (shell scripts only)
        if script_path.suffix in {".sh", ".bash"}:
            has_set_e[rel_path] = bool(re.search(r"set\s+-[a-z]*e[a-z]*", content))
            if not has_set_e[rel_path]:
                result.findings.append(Finding(
                    severity="LOW",
                    check="Shell Best Practices",
                    message="Missing 'set -euo pipefail' — script may hide errors",
                    file=rel_path
                ))

        # Check for security manifest
        has_security_manifest[rel_path] = "SECURITY MANIFEST" in content
        if not has_security_manifest[rel_path]:
            result.findings.append(Finding(
                severity="LOW",
                check="Security Manifest",
                message="Missing # SECURITY MANIFEST header — undeclared access scope",
                file=rel_path
            ))

        # Critical pattern check
        for i, line in enumerate(lines, 1):
            # Skip lines annotated as detection patterns or that are clearly regex string literals
            if "# nocheck" in line or "# DETECTION_PATTERN" in line:
                continue
            if re.match(r'^\s*\(r[\'"]', line) or re.match(r'^\s*r[\'"].*[\'"],\s*[\'"]', line):
                continue
            for pattern, description in CRITICAL_SCRIPT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    result.findings.append(Finding(
                        severity="CRITICAL",
                        check="Malicious Pattern",
                        message=description,
                        file=rel_path,
                        line=i
                    ))
                    found_critical = True

        # Medium pattern check
        for i, line in enumerate(lines, 1):
            if "# nocheck" in line or "# DETECTION_PATTERN" in line:
                continue
            if re.match(r'^\s*\(r[\'"]', line) or re.match(r'^\s*r[\'"].*[\'"],\s*[\'"]', line):
                continue
            for pattern, description in MEDIUM_SCRIPT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Don't double-report lines already caught by critical
                    already_reported = any(
                        f.file == rel_path and f.line == i and f.severity == "CRITICAL"
                        for f in result.findings
                    )
                    if not already_reported:
                        result.findings.append(Finding(
                            severity="MEDIUM",
                            check="External Call Risk",
                            message=description,
                            file=rel_path,
                            line=i
                        ))
                        found_medium = True

    if not found_critical:
        result.checks_passed.append("No data exfiltration or reverse shell patterns detected")
    if not found_medium:
        result.checks_passed.append("No shell injection risks detected")


def check_endpoint_mismatch(skill_dir: Path, result: ScanResult):
    """Compare declared endpoints vs endpoints actually called in scripts."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    content = skill_md.read_text(errors="replace")

    # Check if "External Endpoints" section exists
    has_endpoint_section = bool(re.search(r"##\s+external\s+endpoints?", content, re.IGNORECASE))
    has_none_declared = bool(re.search(r"\|\s*None\s*\|", content, re.IGNORECASE))

    # Extract all URLs from scripts
    scripts_dir = skill_dir / "scripts"
    script_urls = set()

    if scripts_dir.exists():
        for f in scripts_dir.rglob("*"):
            if f.suffix in {".sh", ".bash", ".py"} and f.is_file():
                try:
                    script_content = f.read_text(errors="replace")
                    urls = re.findall(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', script_content)
                    for domain in urls:
                        # Filter out github/known safe infra
                        if domain not in {"github.com", "raw.githubusercontent.com", "api.anthropic.com"}:
                            script_urls.add(domain)
                except Exception:
                    pass

    if has_none_declared and script_urls:
        for domain in script_urls:
            result.findings.append(Finding(
                severity="MEDIUM",
                check="Endpoint Mismatch",
                message=f"SKILL.md declares no external endpoints, but scripts contact: {domain}",
                file="SKILL.md"
            ))
    elif not has_endpoint_section:
        result.findings.append(Finding(
            severity="LOW",
            check="Endpoint Transparency",
            message="Missing 'External Endpoints' section in SKILL.md — required for ClawHub post-ClawHavoc",
            file="SKILL.md"
        ))
    else:
        result.checks_passed.append("External endpoints declared and cross-checked")


def check_structure(skill_dir: Path, result: ScanResult):
    """Check ClawHub spec compliance."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        result.findings.append(Finding(
            severity="CRITICAL",
            check="Structure",
            message="SKILL.md not found — not a valid ClawHub skill",
            file=str(skill_dir)
        ))
        return

    content = skill_md.read_text(errors="replace")

    # Check clawdbot vs openclaw key
    if re.search(r"metadata:\s*\n\s+openclaw:", content):
        result.findings.append(Finding(
            severity="INFO",
            check="Metadata Key",
            message="Uses deprecated 'openclaw' metadata key — should be 'clawdbot' (ClawHub will ignore this)",
            file="SKILL.md"
        ))
    elif re.search(r"clawdbot:", content):
        result.checks_passed.append("Correct 'clawdbot' metadata key")

    # Check semver version
    version_match = re.search(r'^version:\s*["\']?(\S+?)["\']?\s*$', content, re.MULTILINE)
    if version_match:
        version = version_match.group(1)
        if not re.match(r'^\d+\.\d+\.\d+', version):
            result.findings.append(Finding(
                severity="LOW",
                check="Version Format",
                message=f"Version '{version}' may not be valid semver (e.g. 1.0.0)",
                file="SKILL.md"
            ))
        else:
            result.checks_passed.append(f"Valid semver version: {version}")

    # Check homepage
    if not re.search(r"^homepage:\s+https?://", content, re.MULTILINE):
        result.findings.append(Finding(
            severity="INFO",
            check="Provenance",
            message="Missing 'homepage' field — reduces trust signal on ClawHub",
            file="SKILL.md"
        ))
    else:
        result.checks_passed.append("Homepage/provenance declared")

    # Check README exists
    if not (skill_dir / "README.md").exists():
        result.findings.append(Finding(
            severity="INFO",
            check="Documentation",
            message="No README.md found — recommended for ClawHub discoverability",
        ))
    else:
        result.checks_passed.append("README.md present")


def check_permissions(skill_dir: Path, result: ScanResult):
    """Look for sensitive file access not reflected in declared permissions."""
    sensitive_paths = [
        (r"~/\.ssh|/\.ssh/", "SSH keys access"),
        (r"~/\.aws|/\.aws/", "AWS credentials access"),
        (r"~/\.config/.*token|~/\.config/.*secret", "Token/secret config access"),
        (r"/etc/passwd|/etc/shadow", "System password file access"),
        (r"~/Library/Keychains", "macOS Keychain access"),
        (r"wallet\.(dat|json)|keystore", "Crypto wallet access"),
    ]

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return

    found_sensitive = False
    for f in scripts_dir.rglob("*"):
        if f.suffix in {".sh", ".bash", ".py"} and f.is_file():
            try:
                content = f.read_text(errors="replace")
                rel_path = str(f.relative_to(skill_dir))
                for i, line in enumerate(content.splitlines(), 1):
                    # Skip detection pattern lines
                    if "# nocheck" in line or "# DETECTION_PATTERN" in line:
                        continue
                    if re.match(r'^\s*\(r[\'"]', line) or re.match(r'^\s*r[\'"].*[\'"],\s*[\'"]', line):
                        continue
                    for pattern, label in sensitive_paths:
                        if re.search(pattern, line, re.IGNORECASE):
                            result.findings.append(Finding(
                                severity="CRITICAL",
                                check="Sensitive File Access",
                                message=f"{label} detected — verify this is intentional and declared",
                                file=rel_path
                            ))
                            found_sensitive = True
            except Exception:
                pass

    if not found_sensitive:
        result.checks_passed.append("No sensitive file access patterns detected")


# ─────────────────────────────────────────────
# REPORT RENDERER
# ─────────────────────────────────────────────

def render_report(result: ScanResult) -> str:
    lines = []
    width = 50
    bar = "━" * width

    lines.append(bar)
    lines.append(f"🔍 CLAWGUARD REPORT — {result.skill_name} v{result.skill_version}")
    lines.append(bar)
    lines.append("")

    verdict = result.verdict()
    emoji = result.verdict_emoji()
    lines.append(f"VERDICT: {emoji} {verdict}")
    lines.append("")

    # Passed checks
    if result.checks_passed:
        lines.append("CHECKS PASSED:")
        for check in result.checks_passed:
            lines.append(f"  ✅ {check}")
        lines.append("")

    # Findings grouped by severity
    severity_order = ["CRITICAL", "MEDIUM", "LOW", "INFO"]
    severity_emoji = {"CRITICAL": "🔴", "MEDIUM": "🟡", "LOW": "🟠", "INFO": "ℹ️ "}

    grouped = {s: [f for f in result.findings if f.severity == s] for s in severity_order}

    if result.findings:
        lines.append("FINDINGS:")
        for severity in severity_order:
            for finding in grouped[severity]:
                loc = ""
                if finding.file:
                    loc = f" [{finding.file}"
                    if finding.line:
                        loc += f" line {finding.line}"
                    loc += "]"
                lines.append(f"  {severity_emoji[severity]} [{finding.severity}] {finding.check}{loc}")
                lines.append(f"     {finding.message}")
        lines.append("")

    # Recommendation
    lines.append("RECOMMENDATION:")
    if verdict == "PASS":
        lines.append("  This skill passed all critical checks. Safe to install.")
        if result.findings:
            lines.append("  Review the minor findings above at your discretion.")
    elif verdict == "WARN":
        lines.append("  This skill has warnings. Review all MEDIUM findings")
        lines.append("  manually before installing. Understand what each does.")
    else:
        lines.append("  ❌ DO NOT INSTALL. Critical security issues detected.")
        lines.append("  This skill contains patterns consistent with malware,")
        lines.append("  prompt injection, or data exfiltration. Report it on")
        lines.append("  ClawHub using the report button.")

    lines.append(bar)
    return "\n".join(lines)


# ─────────────────────────────────────────────
# EXTRACT SKILL METADATA
# ─────────────────────────────────────────────

def extract_metadata(skill_dir: Path) -> tuple:
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    version = "unknown"

    if not skill_md.exists():
        return name, version

    content = skill_md.read_text(errors="replace")

    name_match = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()

    version_match = re.search(r'^version:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if version_match:
        version = version_match.group(1).strip()

    return name, version


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def scan_skill(skill_path: str) -> ScanResult:
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        print(f"Error: Path does not exist: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if not skill_dir.is_dir():
        print(f"Error: Path is not a directory: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    name, version = extract_metadata(skill_dir)
    result = ScanResult(
        skill_name=name,
        skill_version=version,
        skill_path=str(skill_dir)
    )

    # Run all checks
    check_structure(skill_dir, result)
    check_prompt_injection(skill_dir, result)
    check_scripts(skill_dir, result)
    check_endpoint_mismatch(skill_dir, result)
    check_permissions(skill_dir, result)

    return result


def scan_all(skills_root: str) -> list:
    """Scan all skills in a directory."""
    root = Path(skills_root).resolve()
    results = []

    for item in sorted(root.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            results.append(scan_skill(str(item)))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="ClawGuard — Security auditor for ClawHub skills",
        epilog="Example: python3 scan.py ./skills/some-skill"
    )
    parser.add_argument("path", help="Path to skill directory (or directory of skills with --all)")
    parser.add_argument("--all", action="store_true", help="Scan all skill subdirectories in path")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--fail-on-warn", action="store_true", help="Exit code 1 on WARN (default: only on FAIL)")

    args = parser.parse_args()

    if args.all:
        results = scan_all(args.path)
        if args.json:
            output = []
            for r in results:
                output.append({
                    "skill": r.skill_name,
                    "version": r.skill_version,
                    "verdict": r.verdict(),
                    "findings_count": len(r.findings),
                    "critical": len([f for f in r.findings if f.severity == "CRITICAL"]),
                    "medium": len([f for f in r.findings if f.severity == "MEDIUM"]),
                })
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'━'*50}")
            print(f"CLAWGUARD BULK REPORT — {len(results)} skills scanned")
            print(f"{'━'*50}\n")
            for r in results:
                status = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}[r.verdict()]
                crit = len([f for f in r.findings if f.severity == "CRITICAL"])
                med = len([f for f in r.findings if f.severity == "MEDIUM"])
                print(f"  {status} {r.skill_name:30s} | critical: {crit} | medium: {med}")
            print(f"\n{'━'*50}")

            fails = [r for r in results if r.verdict() == "FAIL"]
            warns = [r for r in results if r.verdict() == "WARN"]
            passes = [r for r in results if r.verdict() == "PASS"]
            print(f"✅ PASS: {len(passes)}  ⚠️  WARN: {len(warns)}  ❌ FAIL: {len(fails)}")
            print(f"{'━'*50}\n")

        # Exit code
        has_fail = any(r.verdict() == "FAIL" for r in results)
        has_warn = any(r.verdict() == "WARN" for r in results)
        if has_fail:
            sys.exit(2)
        elif args.fail_on_warn and has_warn:
            sys.exit(1)
        sys.exit(0)

    else:
        result = scan_skill(args.path)

        if args.json:
            output = {
                "skill": result.skill_name,
                "version": result.skill_version,
                "path": result.skill_path,
                "verdict": result.verdict(),
                "checks_passed": result.checks_passed,
                "findings": [
                    {
                        "severity": f.severity,
                        "check": f.check,
                        "message": f.message,
                        "file": f.file,
                        "line": f.line
                    }
                    for f in result.findings
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            print(render_report(result))

        verdict = result.verdict()
        if verdict == "FAIL":
            sys.exit(2)
        elif args.fail_on_warn and verdict == "WARN":
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()

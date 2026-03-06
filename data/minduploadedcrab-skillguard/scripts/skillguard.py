#!/usr/bin/env python3
"""
SkillGuard — Security Scanner for OpenClaw Skills
Scans skills for malware, credential theft, data exfiltration,
prompt injection, and permission overreach.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
PATTERNS_FILE = DATA_DIR / "patterns.json"
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_INFO = "info"

VERSION = "1.0.1"

SEVERITY_SCORES = {
    SEVERITY_CRITICAL: 40,
    SEVERITY_HIGH: 25,
    SEVERITY_MEDIUM: 10,
    SEVERITY_LOW: 3,
    SEVERITY_INFO: 0,
}

SCANNABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".sh", ".bash", ".zsh",
    ".mjs", ".cjs", ".jsx", ".tsx", ".rb", ".pl",
    ".php", ".lua", ".go", ".rs",
}

TEXT_EXTENSIONS = SCANNABLE_EXTENSIONS | {
    ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".env", ".conf",
}


@dataclass
class Finding:
    severity: str
    category: str
    message: str
    file: str
    line: Optional[int] = None
    evidence: Optional[str] = None

    @property
    def score(self):
        return SEVERITY_SCORES.get(self.severity, 0)


@dataclass
class ScanResult:
    skill_name: str
    skill_path: str
    findings: list = field(default_factory=list)
    risk_score: int = 0
    verdict: str = "PASS"
    file_count: int = 0
    scanned_count: int = 0

    def add(self, finding: Finding):
        self.findings.append(finding)

    def finalize(self):
        self.risk_score = min(100, sum(f.score for f in self.findings))
        if self.risk_score >= 60:
            self.verdict = "FAIL"
        elif self.risk_score >= 20:
            self.verdict = "WARN"
        else:
            self.verdict = "PASS"

    def to_dict(self):
        d = asdict(self)
        d["finding_count"] = len(self.findings)
        d["findings"] = [asdict(f) for f in self.findings]
        return d


def load_patterns():
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            return json.load(f)
    return {}


def read_file_safe(path: Path, max_bytes=500_000) -> Optional[str]:
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return None
        with open(path, "r", errors="replace") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def get_skill_files(skill_path: Path) -> list:
    files = []
    for root, dirs, filenames in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "__pycache__", ".venv", "venv"}]
        for fname in filenames:
            files.append(Path(root) / fname)
    return files


def load_ignorelist(skill_path: Path) -> set:
    """Load .skillguard-ignore file if it exists. Returns set of relative paths to skip."""
    ignore_file = skill_path / ".skillguard-ignore"
    ignored = set()
    if ignore_file.exists():
        with open(ignore_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    return ignored


# ─── SCANNERS ───────────────────────────────────────────────────────

def scan_credential_access(content: str, filepath: str, patterns: dict, result: ScanResult):
    lines = content.split("\n")
    cred_paths = patterns.get("credential_paths", [])
    for i, line in enumerate(lines, 1):
        for cp in cred_paths:
            if cp in line:
                is_comment = line.lstrip().startswith(("#", "//", "*", "/*"))
                if is_comment:
                    continue
                severity = SEVERITY_CRITICAL if any(
                    k in cp for k in ["privateKey", "private_key", "mnemonic", "seed_phrase",
                                       "solanaPrivateKey", "SOLANA_PRIVATE_KEY", ".evm-wallets",
                                       ".ssh/", ".gnupg/"]
                ) else SEVERITY_HIGH if any(
                    k in cp for k in ["API_KEY", "apiKey", "api_key", "botToken", "jwt", "JWT",
                                       "bearer", "credentials", "secrets"]
                ) else SEVERITY_MEDIUM
                result.add(Finding(
                    severity=severity,
                    category="credential_access",
                    message=f"Accesses sensitive path/variable: {cp}",
                    file=filepath,
                    line=i,
                    evidence=line.strip()[:200],
                ))


def scan_network_exfil(content: str, filepath: str, patterns: dict, result: ScanResult):
    lines = content.split("\n")
    exfil_pats = patterns.get("exfil_patterns", [])
    suspicious_domains = patterns.get("suspicious_domains", [])

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue

        for pat in exfil_pats:
            try:
                if re.search(re.escape(pat).replace(r"\.\*", ".*"), line):
                    is_base64_encode = "base64" in pat.lower() or "btoa" in pat.lower()
                    severity = SEVERITY_HIGH if is_base64_encode else SEVERITY_MEDIUM
                    result.add(Finding(
                        severity=severity,
                        category="network_exfil",
                        message=f"Potential data exfiltration pattern: {pat}",
                        file=filepath,
                        line=i,
                        evidence=stripped[:200],
                    ))
                    break
            except re.error:
                if pat in line:
                    result.add(Finding(
                        severity=SEVERITY_MEDIUM,
                        category="network_exfil",
                        message=f"Potential data exfiltration pattern: {pat}",
                        file=filepath,
                        line=i,
                        evidence=stripped[:200],
                    ))
                    break

        for domain in suspicious_domains:
            if domain in line:
                result.add(Finding(
                    severity=SEVERITY_CRITICAL,
                    category="network_exfil",
                    message=f"References known exfiltration domain: {domain}",
                    file=filepath,
                    line=i,
                    evidence=stripped[:200],
                ))


def scan_dangerous_ops(content: str, filepath: str, patterns: dict, result: ScanResult):
    lines = content.split("\n")
    dangerous = patterns.get("dangerous_operations", [])

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue
        for pat in dangerous:
            if pat in line:
                severity = SEVERITY_HIGH if any(
                    k in pat for k in ["eval(", "exec(", "compile(", "__import__",
                                        "Function(", "child_process"]
                ) else SEVERITY_MEDIUM
                result.add(Finding(
                    severity=severity,
                    category="dangerous_operation",
                    message=f"Uses dangerous operation: {pat}",
                    file=filepath,
                    line=i,
                    evidence=stripped[:200],
                ))
                break


def scan_filesystem_abuse(content: str, filepath: str, patterns: dict, result: ScanResult):
    lines = content.split("\n")
    fs_patterns = patterns.get("filesystem_abuse", [])

    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue
        for pat in fs_patterns:
            if pat in line:
                severity = SEVERITY_HIGH if pat in ("../", "..\\\\") else SEVERITY_MEDIUM
                result.add(Finding(
                    severity=severity,
                    category="filesystem_abuse",
                    message=f"Filesystem operation: {pat}",
                    file=filepath,
                    line=i,
                    evidence=stripped[:200],
                ))
                break


def scan_prompt_injection(content: str, filepath: str, patterns: dict, result: ScanResult):
    markers = patterns.get("prompt_injection_markers", [])
    lower_content = content.lower()
    lines = content.split("\n")

    for marker in markers:
        idx = lower_content.find(marker.lower())
        if idx != -1:
            line_num = lower_content[:idx].count("\n") + 1
            line_text = lines[line_num - 1] if line_num <= len(lines) else ""
            severity = SEVERITY_CRITICAL if any(
                k in marker.lower() for k in ["execute", "run this", "send to",
                                                "transmit", "upload", "exfiltrate"]
            ) else SEVERITY_HIGH
            result.add(Finding(
                severity=severity,
                category="prompt_injection",
                message=f"Prompt injection marker: '{marker}'",
                file=filepath,
                line=line_num,
                evidence=line_text.strip()[:200],
            ))


def scan_hidden_files(files: list, skill_path: Path, result: ScanResult):
    for f in files:
        rel = f.relative_to(skill_path)
        parts = rel.parts
        for part in parts:
            if part.startswith(".") and part not in (".gitignore", ".env.template",
                                                       ".env.example", ".eslintrc",
                                                       ".prettierrc", ".clawhub"):
                result.add(Finding(
                    severity=SEVERITY_MEDIUM,
                    category="hidden_file",
                    message=f"Hidden file/directory: {rel}",
                    file=str(rel),
                ))
                break


def scan_npm_package(skill_path: Path, patterns: dict, result: ScanResult):
    pkg_path = skill_path / "package.json"
    if not pkg_path.exists():
        return

    content = read_file_safe(pkg_path)
    if not content:
        return

    try:
        pkg = json.loads(content)
    except json.JSONDecodeError:
        result.add(Finding(
            severity=SEVERITY_MEDIUM,
            category="dependency",
            message="Malformed package.json",
            file="package.json",
        ))
        return

    scripts = pkg.get("scripts", {})
    suspicious_scripts = patterns.get("suspicious_npm_scripts", [])
    for script_name in suspicious_scripts:
        if script_name in scripts:
            result.add(Finding(
                severity=SEVERITY_HIGH,
                category="dependency",
                message=f"Suspicious npm lifecycle script: {script_name}",
                file="package.json",
                evidence=f"{script_name}: {scripts[script_name][:200]}",
            ))

    bad_packages = patterns.get("malicious_npm_packages", [])
    all_deps = {}
    for dep_key in ("dependencies", "devDependencies", "peerDependencies"):
        all_deps.update(pkg.get(dep_key, {}))

    for bad_pkg in bad_packages:
        if bad_pkg in all_deps:
            result.add(Finding(
                severity=SEVERITY_CRITICAL,
                category="dependency",
                message=f"Known malicious npm package: {bad_pkg}",
                file="package.json",
                evidence=f"{bad_pkg}: {all_deps[bad_pkg]}",
            ))


def scan_obfuscation(content: str, filepath: str, result: ScanResult):
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if len(line) > 1000 and not line.strip().startswith(("#", "//", "*")):
            result.add(Finding(
                severity=SEVERITY_HIGH,
                category="obfuscation",
                message=f"Extremely long line ({len(line)} chars) — possible obfuscation",
                file=filepath,
                line=i,
                evidence=line[:100] + "...",
            ))

    hex_pattern = re.compile(r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){10,}')
    unicode_pattern = re.compile(r'\\u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4}){10,}')
    for i, line in enumerate(lines, 1):
        if hex_pattern.search(line) or unicode_pattern.search(line):
            result.add(Finding(
                severity=SEVERITY_HIGH,
                category="obfuscation",
                message="Encoded string sequence (hex/unicode escape) — possible obfuscation",
                file=filepath,
                line=i,
                evidence=line.strip()[:200],
            ))


def scan_env_access(content: str, filepath: str, result: ScanResult):
    env_patterns = [
        (r'os\.environ\[', "os.environ[] access"),
        (r'os\.environ\.get\(', "os.environ.get() access"),
        (r'os\.getenv\(', "os.getenv() access"),
        (r'process\.env\[', "process.env[] access"),
        (r'process\.env\.', "process.env access"),
        (r'dotenv\.load_dotenv', "dotenv loading"),
    ]
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "*")):
            continue
        for pat, desc in env_patterns:
            if re.search(pat, line):
                result.add(Finding(
                    severity=SEVERITY_MEDIUM,
                    category="env_access",
                    message=f"Environment variable access: {desc}",
                    file=filepath,
                    line=i,
                    evidence=stripped[:200],
                ))
                break


def scan_symlinks(files: list, skill_path: Path, result: ScanResult):
    """Detect symlinks that could point to sensitive files outside the skill directory."""
    for f in files:
        if f.is_symlink():
            rel = f.relative_to(skill_path)
            try:
                target = f.resolve()
            except (RuntimeError, OSError):
                result.add(Finding(
                    severity=SEVERITY_HIGH,
                    category="symlink",
                    message=f"Broken or looping symlink: {rel}",
                    file=str(rel),
                    evidence=f"Raw target: {os.readlink(f)}",
                ))
                continue
            try:
                target.relative_to(skill_path)
                severity = SEVERITY_LOW
            except ValueError:
                severity = SEVERITY_CRITICAL
            msg = (f"Symlink escapes skill directory: {rel} -> {target}"
                   if severity == SEVERITY_CRITICAL
                   else f"Internal symlink: {rel} -> {target}")
            result.add(Finding(
                severity=severity,
                category="symlink",
                message=msg,
                file=str(rel),
                evidence=f"Target: {target}",
            ))


# ─── MAIN SCAN ORCHESTRATION ────────────────────────────────────────

def scan_skill(skill_path: Path) -> ScanResult:
    skill_name = skill_path.name
    result = ScanResult(skill_name=skill_name, skill_path=str(skill_path))
    patterns = load_patterns()

    if not skill_path.is_dir():
        result.add(Finding(
            severity=SEVERITY_INFO,
            category="structure",
            message="Path is not a directory",
            file=str(skill_path),
        ))
        result.finalize()
        return result

    has_skill_md = (skill_path / "SKILL.md").exists() or (skill_path / "README.md").exists()
    if not has_skill_md:
        result.add(Finding(
            severity=SEVERITY_LOW,
            category="structure",
            message="Missing SKILL.md or README.md",
            file=str(skill_path),
        ))

    files = get_skill_files(skill_path)
    result.file_count = len(files)
    ignored = load_ignorelist(skill_path)

    scan_hidden_files(files, skill_path, result)
    scan_symlinks(files, skill_path, result)
    scan_npm_package(skill_path, patterns, result)

    for fpath in files:
        suffix = fpath.suffix.lower()
        if suffix not in TEXT_EXTENSIONS:
            continue

        rel_path = str(fpath.relative_to(skill_path))
        if rel_path in ignored:
            continue

        content = read_file_safe(fpath)
        if content is None:
            continue

        result.scanned_count += 1

        if suffix in (".md",):
            scan_prompt_injection(content, rel_path, patterns, result)
            continue

        if suffix in (".json", ".env", ".yaml", ".yml", ".toml"):
            scan_credential_access(content, rel_path, patterns, result)
            continue

        if suffix not in SCANNABLE_EXTENSIONS:
            continue

        scan_credential_access(content, rel_path, patterns, result)
        scan_network_exfil(content, rel_path, patterns, result)
        scan_dangerous_ops(content, rel_path, patterns, result)
        scan_filesystem_abuse(content, rel_path, patterns, result)
        scan_obfuscation(content, rel_path, result)
        scan_env_access(content, rel_path, result)

    result.finalize()
    return result


# ─── OUTPUT FORMATTING ───────────────────────────────────────────────

SEVERITY_COLORS = {
    SEVERITY_CRITICAL: "\033[91m",  # red
    SEVERITY_HIGH: "\033[93m",      # yellow
    SEVERITY_MEDIUM: "\033[33m",    # dark yellow
    SEVERITY_LOW: "\033[36m",       # cyan
    SEVERITY_INFO: "\033[90m",      # gray
}
RESET = "\033[0m"
BOLD = "\033[1m"


def print_result(result: ScanResult, verbose=True):
    verdict_color = {
        "PASS": "\033[92m",   # green
        "WARN": "\033[93m",   # yellow
        "FAIL": "\033[91m",   # red
    }.get(result.verdict, "")

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}SkillGuard Scan: {result.skill_name}{RESET}")
    print(f"{'=' * 60}")
    print(f"Path:     {result.skill_path}")
    print(f"Files:    {result.file_count} total, {result.scanned_count} scanned")
    print(f"Findings: {len(result.findings)}")
    print(f"Risk:     {result.risk_score}/100")
    print(f"Verdict:  {verdict_color}{BOLD}{result.verdict}{RESET}")

    if not result.findings:
        print(f"\n  {BOLD}No issues found.{RESET}")
    elif verbose:
        print(f"\n{BOLD}Findings:{RESET}")
        by_severity = {}
        for f in result.findings:
            by_severity.setdefault(f.severity, []).append(f)

        for sev in [SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW, SEVERITY_INFO]:
            findings = by_severity.get(sev, [])
            if not findings:
                continue
            color = SEVERITY_COLORS.get(sev, "")
            print(f"\n  {color}{BOLD}[{sev.upper()}]{RESET} ({len(findings)})")
            seen = set()
            for f in findings:
                key = (f.category, f.message, f.file)
                if key in seen:
                    continue
                seen.add(key)
                loc = f"{f.file}"
                if f.line:
                    loc += f":{f.line}"
                print(f"    {color}>{RESET} {f.message}")
                print(f"      {loc}")
                if f.evidence:
                    print(f"      {SEVERITY_COLORS[SEVERITY_INFO]}| {f.evidence}{RESET}")

    print(f"\n{'=' * 60}\n")


def print_audit_table(results: list):
    print(f"\n{BOLD}{'Skill':<30} {'Files':>5} {'Findings':>8} {'Risk':>5} {'Verdict':>8}{RESET}")
    print("-" * 60)
    for r in sorted(results, key=lambda x: -x.risk_score):
        vc = {"PASS": "\033[92m", "WARN": "\033[93m", "FAIL": "\033[91m"}.get(r.verdict, "")
        print(f"{r.skill_name:<30} {r.file_count:>5} {len(r.findings):>8} {r.risk_score:>5} {vc}{r.verdict:>8}{RESET}")
    print()
    total = len(results)
    fails = sum(1 for r in results if r.verdict == "FAIL")
    warns = sum(1 for r in results if r.verdict == "WARN")
    passes = sum(1 for r in results if r.verdict == "PASS")
    print(f"Total: {total} skills | PASS: {passes} | WARN: {warns} | FAIL: {fails}")
    print()


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SkillGuard — Security Scanner for OpenClaw Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"SkillGuard {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="Scan a skill directory")
    p_scan.add_argument("path", help="Path to skill directory")
    p_scan.add_argument("--json", action="store_true", help="Output JSON")
    p_scan.add_argument("--quiet", action="store_true", help="Only show verdict")

    p_all = sub.add_parser("scan-all", help="Scan all installed skills")
    p_all.add_argument("--json", action="store_true", help="Output JSON")
    p_all.add_argument("--verbose", "-v", action="store_true", help="Show detailed findings")
    p_all.add_argument("--skills-dir", default=str(SKILLS_DIR), help="Skills directory")

    p_audit = sub.add_parser("audit", help="Quick audit table of all skills")
    p_audit.add_argument("--skills-dir", default=str(SKILLS_DIR), help="Skills directory")

    args = parser.parse_args()

    if args.command == "scan":
        skill_path = Path(args.path).resolve()
        result = scan_skill(skill_path)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        elif args.quiet:
            print(f"{result.skill_name}: {result.verdict} (risk: {result.risk_score})")
        else:
            print_result(result)
        sys.exit(0 if result.verdict == "PASS" else 1)

    elif args.command == "scan-all":
        skills_dir = Path(args.skills_dir)
        if not skills_dir.is_dir():
            print(f"Error: {skills_dir} is not a directory", file=sys.stderr)
            sys.exit(1)
        results = []
        for entry in sorted(skills_dir.iterdir()):
            if entry.is_dir() and not entry.name.startswith((".", "_")):
                r = scan_skill(entry)
                results.append(r)
                if not args.json:
                    print_result(r, verbose=args.verbose)
        if args.json:
            print(json.dumps([r.to_dict() for r in results], indent=2))
        else:
            print_audit_table(results)
        has_fails = any(r.verdict == "FAIL" for r in results)
        sys.exit(1 if has_fails else 0)

    elif args.command == "audit":
        skills_dir = Path(args.skills_dir)
        if not skills_dir.is_dir():
            print(f"Error: {skills_dir} is not a directory", file=sys.stderr)
            sys.exit(1)
        results = []
        for entry in sorted(skills_dir.iterdir()):
            if entry.is_dir() and not entry.name.startswith((".", "_")):
                results.append(scan_skill(entry))
        print_audit_table(results)
        has_fails = any(r.verdict == "FAIL" for r in results)
        sys.exit(1 if has_fails else 0)


if __name__ == "__main__":
    main()

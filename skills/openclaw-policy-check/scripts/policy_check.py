#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Pattern


SEVERITY_ORDER: Dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "venv",
}

TEXT_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".swift",
    ".kt",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".env",
    ".ini",
    ".cfg",
    ".sql",
    ".md",
    ".txt",
}


class Rule:
    def __init__(self, rule_id: str, severity: str, regex: str, reason: str):
        self.rule_id = rule_id
        self.severity = severity
        self.pattern: Pattern[str] = re.compile(regex, re.IGNORECASE)
        self.reason = reason


RULES: List[Rule] = [
    Rule(
        "shell-pipe-to-sh",
        "critical",
        r"(curl|wget)\s+[^|]+\|\s*(sh|bash)\b",
        "Downloads and executes remote code directly in shell.",
    ),
    Rule(
        "destructive-rm-root",
        "critical",
        r"\brm\s+-rf\s+/\b",
        "Potential destructive command targeting root path.",
    ),
    Rule(
        "chmod-777",
        "high",
        r"\bchmod\s+777\b",
        "Overly permissive file permissions.",
    ),
    Rule(
        "eval-usage",
        "high",
        r"\beval\s*\(",
        "Dynamic code execution via eval.",
    ),
    Rule(
        "python-shell-true",
        "high",
        r"\b(subprocess\.(run|Popen|call|check_output|check_call)\s*\([^)]*shell\s*=\s*True)",
        "Python subprocess call with shell=True.",
    ),
    Rule(
        "aws-secret-key",
        "high",
        r"AKIA[0-9A-Z]{16}",
        "Potential AWS access key detected.",
    ),
    Rule(
        "private-key-block",
        "high",
        r"-----BEGIN\s+(RSA|EC|OPENSSH|PRIVATE)\s+PRIVATE\s+KEY-----",
        "Private key material detected.",
    ),
    Rule(
        "dotenv-secret",
        "medium",
        r"(api[_-]?key|secret|token|password)\s*=\s*[\"']?[A-Za-z0-9_\-\/+=]{12,}",
        "Possible embedded secret in configuration or code.",
    ),
    Rule(
        "suspicious-exfil-endpoint",
        "medium",
        r"(webhook|pastebin|ngrok|discord\.com/api/webhooks|transfer\.sh)",
        "Potential exfiltration endpoint reference.",
    ),
    Rule(
        "base64-decode-exec",
        "medium",
        r"(base64\s+-d|b64decode\()[^\\n]{0,120}(sh|bash|exec|eval)",
        "Decoded payload appears to be executed.",
    ),
    Rule(
        "dangerous-system-call",
        "medium",
        r"\b(os\.system|Runtime\.getRuntime\(\)\.exec|ProcessBuilder\()",
        "Direct system command execution detected.",
    ),
    Rule(
        "hardcoded-local-credential-path",
        "low",
        r"(\.aws/credentials|id_rsa|\.ssh/config|\.env\.production)",
        "Reference to sensitive local credential path.",
    ),
]


def should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.stat().st_size > 1024 * 1024:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name in {"Dockerfile", "Makefile"}:
        return True
    return path.suffix == ""


def iter_files(target: Path) -> Iterable[Path]:
    if target.is_file():
        if should_scan_file(target):
            yield target
        return

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS]
        root_path = Path(root)
        for filename in files:
            candidate = root_path / filename
            if should_scan_file(candidate):
                yield candidate


def scan_file(path: Path, root: Path) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    rel_path = str(path.relative_to(root)) if root.is_dir() else str(path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    {
                        "severity": rule.severity,
                        "rule_id": rule.rule_id,
                        "path": rel_path,
                        "line": line_no,
                        "snippet": line.strip()[:200],
                        "reason": rule.reason,
                    }
                )
    return findings


def summarize(findings: List[Dict[str, object]]) -> str:
    counts = Counter(str(item["severity"]) for item in findings)
    ordered = sorted(counts.items(), key=lambda kv: SEVERITY_ORDER.get(kv[0], 99))
    if not ordered:
        return "none"
    return ", ".join(f"{severity}={count}" for severity, count in ordered)


def should_fail(findings: List[Dict[str, object]], fail_on: str) -> bool:
    threshold = SEVERITY_ORDER[fail_on]
    for item in findings:
        severity = str(item["severity"])
        if SEVERITY_ORDER.get(severity, 99) <= threshold:
            return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight OpenClaw policy check.")
    parser.add_argument("target_path", help="File or directory to scan")
    parser.add_argument("--json", action="store_true", help="Print full findings as JSON")
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of top findings to print in text mode",
    )
    parser.add_argument(
        "--fail-on",
        choices=list(SEVERITY_ORDER.keys()),
        help="Exit with code 2 if any finding is >= threshold severity",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target_path).expanduser().resolve()

    if not target.exists():
        print(f"Target path does not exist: {target}", file=sys.stderr)
        return 1

    root = target if target.is_dir() else target.parent
    findings: List[Dict[str, object]] = []
    for path in iter_files(target):
        findings.extend(scan_file(path, root))

    findings.sort(key=lambda item: SEVERITY_ORDER.get(str(item["severity"]), 99))

    if args.json:
        print(
            json.dumps(
                {
                    "target": str(target),
                    "total_findings": len(findings),
                    "severity_breakdown": summarize(findings),
                    "findings": findings,
                },
                indent=2,
            )
        )
    else:
        print(f"Target: {target}")
        print(f"Total findings: {len(findings)}")
        print(f"Severity: {summarize(findings)}")
        print("Top findings:")
        if not findings:
            print("none")
        else:
            for idx, item in enumerate(findings[: max(1, args.top)], start=1):
                print(
                    f"{idx}. [{item['severity'].upper()}] "
                    f"{item['path']}:{item['line']} | {item['rule_id']} | {item['reason']}"
                )

    if args.fail_on and should_fail(findings, args.fail_on):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

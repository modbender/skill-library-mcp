"""
Release audit helpers for SociClaw.

Checks:
- unresolved placeholders in docs/config
- optional forbidden terms (white-label hygiene)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence
import re


PLACEHOLDER_PATTERNS = (
    re.compile(r"https://github\.com/<[^>]+>/", re.IGNORECASE),
    re.compile(r"<your-org-or-user>", re.IGNORECASE),
    re.compile(r"<upstream-provider>", re.IGNORECASE),
    re.compile(r"<seu-[^>]+>", re.IGNORECASE),
    re.compile(r"https://<[^>]+>", re.IGNORECASE),
)


@dataclass(frozen=True)
class AuditFinding:
    file: str
    line: int
    kind: str
    value: str


def should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".db"}:
        return False
    allowed_suffixes = {"", ".md", ".txt", ".env", ".example", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
    return path.suffix.lower() in allowed_suffixes


def iter_repo_files(
    root: Path,
    *,
    exclude_dirs: Sequence[str] = (".git", ".venv", ".tmp", "__pycache__", "node_modules", "tests", ".pytest_cache"),
) -> Iterable[Path]:
    excluded = {x.lower() for x in exclude_dirs}
    for path in root.rglob("*"):
        parts = {p.lower() for p in path.parts}
        if excluded & parts:
            continue
        if should_scan_file(path):
            yield path


def scan_placeholders(root: Path) -> List[AuditFinding]:
    findings: List[AuditFinding] = []
    for file_path in iter_repo_files(root):
        text = _safe_read_text(file_path)
        if text is None:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            for pattern in PLACEHOLDER_PATTERNS:
                m = pattern.search(line)
                if m:
                    findings.append(
                        AuditFinding(
                            file=str(file_path.relative_to(root)),
                            line=idx,
                            kind="placeholder",
                            value=m.group(0),
                        )
                    )
    return findings


def scan_forbidden_terms(root: Path, terms: Sequence[str]) -> List[AuditFinding]:
    findings: List[AuditFinding] = []
    if not terms:
        return findings

    compiled = [(term, re.compile(re.escape(term), re.IGNORECASE)) for term in terms if term.strip()]
    for file_path in iter_repo_files(root):
        text = _safe_read_text(file_path)
        if text is None:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            for term, pattern in compiled:
                if pattern.search(line):
                    findings.append(
                        AuditFinding(
                            file=str(file_path.relative_to(root)),
                            line=idx,
                            kind="forbidden_term",
                            value=term,
                        )
                    )
    return findings


def _safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    except Exception:
        return None

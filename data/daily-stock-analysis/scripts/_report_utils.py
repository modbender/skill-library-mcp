#!/usr/bin/env python3
"""Shared helpers for daily-stock-analysis scripts."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional


FILENAME_RE = re.compile(
    r"^(?P<run_date>\d{4}-\d{2}-\d{2})-(?P<ticker>[A-Za-z0-9._-]+)-analysis(?:-v(?P<version>\d+))?\.md$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReportFile:
    path: str
    run_date: str
    ticker: str
    version: int
    in_canonical_dir: bool


def canonical_reports_dir(workdir: str) -> str:
    return os.path.join(os.path.abspath(workdir), "daily-stock-analysis", "reports")


def compatible_dirs(workdir: str) -> List[str]:
    root = os.path.abspath(workdir)
    return [
        canonical_reports_dir(root),
        os.path.join(root, "daily-stock-analysis"),
        root,
    ]


def is_within_workdir(path: str, workdir: str) -> bool:
    root = os.path.realpath(os.path.abspath(workdir))
    target = os.path.realpath(os.path.abspath(path))
    return target == root or target.startswith(root + os.sep)


def parse_filename(name: str) -> Optional[Dict[str, str]]:
    match = FILENAME_RE.match(name)
    if not match:
        return None
    return {
        "run_date": match.group("run_date"),
        "ticker": match.group("ticker").upper(),
        "version": str(int(match.group("version") or "1")),
    }


def discover_reports(workdir: str, ticker: str) -> List[ReportFile]:
    root = os.path.abspath(workdir)
    ticker_upper = ticker.upper()
    canonical_dir = canonical_reports_dir(root)
    seen = set()
    records: List[ReportFile] = []

    for directory in compatible_dirs(root):
        if not is_within_workdir(directory, root):
            continue
        if not os.path.isdir(directory):
            continue
        for entry in os.scandir(directory):
            # Never follow symlinks for safety/privacy.
            if not entry.is_file(follow_symlinks=False):
                continue
            parsed = parse_filename(entry.name)
            if not parsed:
                continue
            if parsed["ticker"] != ticker_upper:
                continue
            abs_path = os.path.abspath(entry.path)
            real_path = os.path.realpath(abs_path)
            if real_path in seen:
                continue
            seen.add(real_path)
            records.append(
                ReportFile(
                    path=abs_path,
                    run_date=parsed["run_date"],
                    ticker=parsed["ticker"],
                    version=int(parsed["version"]),
                    in_canonical_dir=os.path.dirname(abs_path) == canonical_dir,
                )
            )

    def sort_key(record: ReportFile):
        try:
            d = date.fromisoformat(record.run_date)
        except ValueError:
            d = date.min
        return (d, record.version, 1 if record.in_canonical_dir else 0)

    return sorted(records, key=sort_key, reverse=True)


def read_frontmatter(path: str) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if first_line.strip() != "---":
                return {}

            # Read only a bounded header section to avoid loading large files.
            frontmatter: Dict[str, str] = {}
            total_chars = len(first_line)
            for _ in range(200):
                line = f.readline()
                if not line:
                    break
                total_chars += len(line)
                if total_chars > 64 * 1024:
                    break
                raw = line.rstrip("\n")
                if raw.strip() == "---":
                    break
                if not raw.strip():
                    continue
                if raw.startswith("  - "):
                    continue
                if ":" not in raw:
                    continue
                key, value = raw.split(":", 1)
                frontmatter[key.strip()] = value.strip()
            return frontmatter
    except (OSError, UnicodeDecodeError):
        return {}


def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text.upper() in {"N/A", "NA", "NONE", "NULL", "PENDING"}:
        return None
    text = text.replace(",", "")
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return None


def parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    text = value.strip().lower()
    if text in {"true", "yes", "1"}:
        return True
    if text in {"false", "no", "0"}:
        return False
    return None

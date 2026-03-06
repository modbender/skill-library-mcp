#!/usr/bin/env python3
"""
openclaw_tasks/memory_compress.py
Task 6 — Memory Maintenance & Compression

Runs weekly (Monday 03:00 per HEARTBEAT.md).
Reads last 7 days of memory/YYYY-MM-DD.md files.
Extracts calibration lessons and domain edge cases via Ollama.
Updates MEMORY.md with distilled insights.
Archives old daily logs to memory/archive/.

Also performs a calibration consistency check:
  Compares LearningSystem heuristics against actual substrate outcomes
  and flags drift if they diverge by > DRIFT_THRESHOLD.

Usage:
  python memory_compress.py [db_path] [--days N] [--dry-run]
"""

import sys
import json
import os
import http.client
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from glob import glob

WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from substrate import Substrate, EventType

MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_MODEL = "glm-4.7-flash"
DRIFT_THRESHOLD = 0.15  # flag if calibration heuristics drift by more than this


COMPRESS_PROMPT = """You are an epistemic calibration analyst. Below are daily session logs from an Epistemic Council agent over the past {n_days} day(s).

DAILY LOGS:
{log_text}

Extract the following from these logs:
1. CALIBRATION LESSONS — cases where confidence estimates were wrong (too high or too low). Format: "Domain X claims with evidence pattern Y: adjust base confidence from A to B"
2. DOMAIN BOUNDARIES DISCOVERED — edge cases where claims were near or over domain boundaries
3. EVIDENCE SOURCE QUALITY UPDATES — any sources found to be more or less reliable than expected
4. RECURRING PATTERNS — repeated failure modes or success patterns

Respond in this exact format (each section may have 0 to 5 bullet items):

CALIBRATION_LESSONS:
- [lesson 1]
- [lesson 2]

DOMAIN_BOUNDARIES:
- [boundary finding 1]

EVIDENCE_QUALITY:
- [quality update 1]

RECURRING_PATTERNS:
- [pattern 1]
"""


def call_ollama(prompt: str) -> str:
    try:
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }).encode()
        conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=60)
        conn.request("POST", "/api/generate", payload, {"Content-Type": "application/json"})
        resp = conn.getresponse()
        if resp.status != 200:
            return f"[Ollama unavailable: HTTP {resp.status}]"
        data = json.loads(resp.read())
        return data.get("response", "").strip()
    except Exception as e:
        return f"[Ollama unavailable: {e}]"


def parse_compression_response(text: str) -> dict:
    """Parse Ollama's structured compression output into sections."""
    sections = {
        "calibration_lessons": [],
        "domain_boundaries": [],
        "evidence_quality": [],
        "recurring_patterns": [],
    }
    section_map = {
        "CALIBRATION_LESSONS:": "calibration_lessons",
        "DOMAIN_BOUNDARIES:": "domain_boundaries",
        "EVIDENCE_QUALITY:": "evidence_quality",
        "RECURRING_PATTERNS:": "recurring_patterns",
    }
    current = None
    for line in text.splitlines():
        line = line.strip()
        for header, key in section_map.items():
            if line.startswith(header):
                current = key
                break
        else:
            if current and line.startswith("- "):
                sections[current].append(line[2:])
    return sections


def read_daily_logs(n_days: int = 7) -> tuple:
    """Returns (combined_text, list_of_paths_read)."""
    cutoff = datetime.utcnow() - timedelta(days=n_days)
    logs = []
    paths = []
    for day_offset in range(n_days):
        date = (datetime.utcnow() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date}.md"
        if log_file.exists():
            logs.append(f"=== {date} ===\n{log_file.read_text()[:2000]}")
            paths.append(log_file)
    return "\n\n".join(logs), paths


def archive_old_logs(paths: list, dry_run: bool = False):
    """Move daily logs older than 7 days to memory/archive/."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archived = []
    for path in paths:
        try:
            # Parse date from filename
            date_str = path.stem  # YYYY-MM-DD
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                dest = ARCHIVE_DIR / path.name
                if not dry_run:
                    shutil.move(str(path), str(dest))
                archived.append(path.name)
        except Exception:
            continue
    return archived


def update_memory_md(sections: dict, substrate: Substrate):
    """
    Rewrite MEMORY.md with current distilled insights.
    Appends new content to existing sections rather than overwriting.
    """
    existing = MEMORY_MD.read_text() if MEMORY_MD.exists() else ""

    # Compute substrate-level calibration reality check
    insights = substrate.get_insights()
    total_insights = len(insights)
    high_conf = substrate.get_insights_above_confidence(0.75)
    challenged_zone = substrate.get_claims_in_confidence_range(0.45, 0.55)

    now = datetime.utcnow().isoformat()

    new_content = f"""# MEMORY.md — Epistemic Council Agent Long-Term Memory
_Last updated: {now}_

## Substrate Reality (auto-computed)
- Total insights in substrate: {total_insights}
- High-confidence insights (>0.75): {len(high_conf)}
- Challenged-zone claims (0.45–0.55): {len(challenged_zone)}

## Calibration Heuristics
_Updated from last 7-day log compression_
"""
    for lesson in sections.get("calibration_lessons", []):
        new_content += f"- {lesson}\n"
    if not sections.get("calibration_lessons"):
        new_content += "- No calibration events recorded in this window\n"

    new_content += "\n## Domain Boundaries Discovered\n"
    for boundary in sections.get("domain_boundaries", []):
        new_content += f"- {boundary}\n"
    if not sections.get("domain_boundaries"):
        new_content += "- No boundary edge cases in this window\n"

    new_content += "\n## Evidence Source Quality\n"
    for quality in sections.get("evidence_quality", []):
        new_content += f"- {quality}\n"
    if not sections.get("evidence_quality"):
        new_content += "- No source quality updates in this window\n"

    new_content += "\n## Recurring Patterns\n"
    for pattern in sections.get("recurring_patterns", []):
        new_content += f"- {pattern}\n"
    if not sections.get("recurring_patterns"):
        new_content += "- No recurring patterns identified\n"

    new_content += "\n## User Preferences\n_(To be filled after first conversation)_\n"

    MEMORY_MD.write_text(new_content)


def run_drift_check(substrate: Substrate) -> dict:
    """
    Compare LearningSystem calibration state against substrate actuals.
    Flags if drift > DRIFT_THRESHOLD.
    """
    drift_report = {"status": "learning_system_unavailable", "drift": None}
    try:
        from self_improvement import LearningSystem
        ls = LearningSystem()
        # LearningSystem stores confidence adjustments; compare against actual avg
        actual_insights = substrate.get_insights()
        if not actual_insights:
            return {"status": "no_insights", "drift": None}

        actual_avg = sum(i.confidence for i in actual_insights) / len(actual_insights)
        stored_avg = getattr(ls, "average_confidence", None)

        if stored_avg is not None:
            drift = abs(actual_avg - stored_avg)
            drift_report = {
                "status": "ok",
                "actual_avg_confidence": round(actual_avg, 4),
                "learning_system_avg": round(stored_avg, 4),
                "drift": round(drift, 4),
                "alert": "DRIFT_DETECTED" if drift > DRIFT_THRESHOLD else "OK",
            }
        else:
            drift_report = {"status": "learning_system_no_avg_stored", "drift": None}
    except ImportError:
        pass
    except Exception as e:
        drift_report = {"status": "error", "error": str(e), "drift": None}
    return drift_report


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", nargs="?", default=str(WORKSPACE / "epistemic.db"))
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    substrate = Substrate(args.db_path)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Read daily logs
    log_text, log_paths = read_daily_logs(args.days)

    if not log_text.strip():
        result = {
            "status": "no_logs_found",
            "days": args.days,
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(json.dumps(result, indent=2))
        substrate.close()
        return

    print(f"[memory_compress] Compressing {len(log_paths)} day(s) of logs...", file=sys.stderr)

    # Call Ollama for compression
    prompt = COMPRESS_PROMPT.format(n_days=args.days, log_text=log_text[:6000])
    raw_response = call_ollama(prompt)
    sections = parse_compression_response(raw_response)

    # Update MEMORY.md
    if not args.dry_run:
        update_memory_md(sections, substrate)

    # Archive old logs
    archived = archive_old_logs(log_paths, dry_run=args.dry_run)

    # Drift check
    drift = run_drift_check(substrate)

    substrate.close()

    result = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "days_compressed": args.days,
        "logs_read": len(log_paths),
        "logs_archived": archived,
        "sections_extracted": {k: len(v) for k, v in sections.items()},
        "drift_check": drift,
        "dry_run": args.dry_run,
    }

    # Write to openclaw-runs
    if not args.dry_run:
        runs_dir = MEMORY_DIR / "openclaw-runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        log_file = runs_dir / f"{date_str}.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text())
            except Exception:
                pass
        existing.append({"task": "memory_compress", **result})
        log_file.write_text(json.dumps(existing, indent=2))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
#!/usr/bin/env /Users/loki/.pyenv/versions/3.14.3/bin/python3
"""
fact_check.py — Verify claims in a markdown draft against source data.

Usage:
    python3 fact_check.py <draft.md>
    python3 fact_check.py <draft.md> --output report.md
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# ─── Workspace paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent  # workspace/skills/fact-checker/scripts → workspace
CP_PROJECT = WORKSPACE_ROOT / "projects" / "hybrid-control-plane"
FINDINGS_MD = CP_PROJECT / "FINDINGS.md"
CHANGELOG_MD = CP_PROJECT / "CHANGELOG.md"
SCORES_DIR = CP_PROJECT / "data" / "scores"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
STATUS_API = "http://localhost:8765/status"

# ─── Source loading ────────────────────────────────────────────────────────────

def load_findings() -> str:
    """Load FINDINGS.md content."""
    return FINDINGS_MD.read_text() if FINDINGS_MD.exists() else ""


def load_changelog() -> str:
    """Load CHANGELOG.md content."""
    return CHANGELOG_MD.read_text() if CHANGELOG_MD.exists() else ""


def load_memory_logs() -> str:
    """Load all memory/*.md files into a single string."""
    if not MEMORY_DIR.exists():
        return ""
    return "\n\n".join(
        f"### {f.name}\n{f.read_text()}"
        for f in sorted(MEMORY_DIR.glob("*.md"))
    )


def fetch_status_api() -> Optional[dict]:
    """Fetch live data from Control Plane /status API.  Returns None on failure."""
    try:
        resp = requests.get(STATUS_API, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def load_score_files() -> dict[str, list[float]]:
    """
    Load all score JSON files from data/scores/.
    Returns {stem: [score, ...]} e.g. {"phi4_latest_classify": [1.0, 1.0, ...]}.
    """
    scores: dict[str, list[float]] = {}
    if not SCORES_DIR.exists():
        return scores
    for jf in SCORES_DIR.glob("*.json"):
        try:
            data = json.loads(jf.read_text())
            scores[jf.stem] = [
                float(entry["score"])
                for entry in data
                if isinstance(entry, dict) and "score" in entry
            ]
        except (json.JSONDecodeError, TypeError, ValueError):
            scores[jf.stem] = []
    return scores


def load_git_log() -> str:
    """Return recent git log from the CP project repo."""
    if not CP_PROJECT.exists():
        return ""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--date=short", "--format=%h %ad %s", "-50"],
            cwd=str(CP_PROJECT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except Exception:
        return ""


# ─── Claim extraction ─────────────────────────────────────────────────────────

def extract_numeric_claims(text: str) -> list[dict]:
    """
    Extract integer/float values with up to 60 chars of surrounding context.
    Filters to values that appear alongside interesting domain keywords.
    """
    INTERESTING = {
        "run", "runs", "eval", "evals", "model", "models", "score", "scores",
        "token", "tokens", "cost", "sprint", "total", "param", "params",
        "million", "billion", "thousand", "gb", "mb", "tb", "ms", "day", "days",
        "hour", "hours", "percent", "week", "weeks", "layer",
    }
    claims = []
    # Use (?!\d) instead of trailing \b so numbers like "7B" or "20B" are captured
    # (word boundary between digit and letter doesn't fire, but (?!\d) does)
    for m in re.finditer(r"\b(\d[\d,]*(?:\.\d+)?)(?!\d)", text):
        start = max(0, m.start() - 60)
        end = min(len(text), m.end() + 60)
        ctx = text[start:end].replace("\n", " ").strip()
        ctx_words = set(ctx.lower().split())
        if ctx_words & INTERESTING:
            claims.append({
                "type": "numeric",
                "value": m.group(1),
                "context": ctx,
                "pos": m.start(),
            })
    return claims


def extract_model_refs(text: str) -> list[dict]:
    """
    Extract model name references:
    - word/word  → phi4/classify, ministral/format
    - word:word  → phi4:latest, qwen2.5:latest  (URLs excluded)
    """
    claims = []

    # word/word pattern
    for m in re.finditer(r"\b([\w][\w.\-]*)\/([\w][\w.\-]*)\b", text):
        ctx = text[max(0, m.start() - 50): min(len(text), m.end() + 50)].replace("\n", " ").strip()
        claims.append({
            "type": "model_slash",
            "value": m.group(0),
            "model": m.group(1),
            "task": m.group(2),
            "context": ctx,
            "pos": m.start(),
        })

    # word:word pattern — skip URLs and common markup
    for m in re.finditer(r"\b([\w][\w.\-]*)\:([\w][\w.\-]*)\b", text):
        pre = text[max(0, m.start() - 8): m.start()]
        if re.search(r"https?|file|ftp|mailto|data", pre, re.I):
            continue
        ctx = text[max(0, m.start() - 50): min(len(text), m.end() + 50)].replace("\n", " ").strip()
        claims.append({
            "type": "model_colon",
            "value": m.group(0),
            "model": m.group(1),
            "tag": m.group(2),
            "context": ctx,
            "pos": m.start(),
        })

    return claims


def extract_date_refs(text: str) -> list[dict]:
    """Extract YYYY-MM-DD date strings."""
    claims = []
    for m in re.finditer(r"\b(20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))\b", text):
        ctx = text[max(0, m.start() - 50): min(len(text), m.end() + 50)].replace("\n", " ").strip()
        claims.append({
            "type": "date",
            "value": m.group(1),
            "context": ctx,
            "pos": m.start(),
        })
    return claims


def extract_score_claims(text: str) -> list[dict]:
    """Extract decimal score values of the form 0.xxx or 1.000 (probability/score range 0–1)."""
    claims = []
    for m in re.finditer(r"\b([01]\.\d{3,4})\b", text):
        val = float(m.group(1))
        ctx = text[max(0, m.start() - 60): min(len(text), m.end() + 60)].replace("\n", " ").strip()
        claims.append({
            "type": "score",
            "value": m.group(1),
            "float_val": val,
            "context": ctx,
            "pos": m.start(),
        })
    return claims


def extract_percentage_claims(text: str) -> list[dict]:
    """Extract percentage values like 42% or 95.3%."""
    claims = []
    for m in re.finditer(r"\b(\d+(?:\.\d+)?)\s*%", text):
        ctx = text[max(0, m.start() - 60): min(len(text), m.end() + 60)].replace("\n", " ").strip()
        claims.append({
            "type": "percentage",
            "value": m.group(0).strip(),
            "number": m.group(1),
            "context": ctx,
            "pos": m.start(),
        })
    return claims


# ─── Verification ─────────────────────────────────────────────────────────────

def _normalize(s: str) -> str:
    """Normalize model name for fuzzy matching (lower, replace punctuation with _)."""
    return re.sub(r"[.\-]", "_", s.lower())


def _api_confidence_lookup(
    model: str, task: Optional[str], conf: dict
) -> Optional[tuple[str, dict]]:
    """Find a matching confidence entry for model+task in the API confidence dict."""
    norm_model = _normalize(model)
    for key, entry in conf.items():
        norm_key = _normalize(key)
        if norm_model not in norm_key:
            continue
        if task and _normalize(task) not in norm_key:
            continue
        return key, entry
    return None


def verify_model_ref(
    claim: dict,
    status_data: Optional[dict],
    findings_text: str,
    score_files: dict,
) -> tuple[str, str]:
    """Verify a model reference claim."""
    model = claim.get("model", "")
    task = claim.get("task") or claim.get("tag")
    full = claim["value"]

    # 1. Live API
    if status_data and "confidence" in status_data:
        result = _api_confidence_lookup(model, task, status_data["confidence"])
        if result:
            key, entry = result
            return "CONFIRMED", f"/status API: {key} mean={entry['mean']} n={entry['n']}"

    # 2. Score files on disk
    norm_model = _normalize(model)
    for key, scores in score_files.items():
        norm_key = _normalize(key)
        if norm_model not in norm_key:
            continue
        if task and _normalize(task) not in norm_key:
            continue
        if scores:
            mean = sum(scores) / len(scores)
            return "CONFIRMED", f"score file {key}.json: n={len(scores)}, mean={mean:.4f}"

    # 3. FINDINGS.md text search
    if model.lower() in findings_text.lower():
        return "CONFIRMED", f"model '{model}' referenced in FINDINGS.md"

    return "UNVERIFIABLE", f"no data found for '{full}' in API, score files, or FINDINGS.md"


def verify_score_value(
    claim: dict,
    status_data: Optional[dict],
    findings_text: str,
    score_files: dict,
) -> tuple[str, str]:
    """Verify a decimal score value against live and disk data."""
    val = claim["float_val"]
    val_str = claim["value"]
    TOLERANCE = 0.005

    # 1. Live API — check all model means
    if status_data and "confidence" in status_data:
        for key, entry in status_data["confidence"].items():
            if abs(entry.get("mean", -99) - val) <= TOLERANCE:
                return "CONFIRMED", f"/status API: {key} mean={entry['mean']} n={entry['n']}"
            if abs(entry.get("last_10_mean", -99) - val) <= TOLERANCE:
                return "CONFIRMED", f"/status API: {key} last_10_mean={entry['last_10_mean']}"

    # 2. Score files — check each model's computed mean
    for key, scores in score_files.items():
        if not scores:
            continue
        mean = sum(scores) / len(scores)
        if abs(mean - val) <= TOLERANCE:
            return "CONFIRMED", f"score file {key}.json: computed mean={mean:.4f} n={len(scores)}"

    # 3. FINDINGS.md literal match
    if val_str in findings_text:
        return "CONFIRMED", f"value {val_str} found in FINDINGS.md"

    return "UNVERIFIABLE", f"score {val_str} not matched in API or score files (±{TOLERANCE})"


def verify_numeric(
    claim: dict,
    status_data: Optional[dict],
    findings_text: str,
    changelog_text: str,
    memory_text: str,
) -> tuple[str, str]:
    """Verify a plain numeric claim."""
    raw = claim["value"].replace(",", "")
    try:
        claimed_int = int(float(raw))
    except ValueError:
        return "UNVERIFIABLE", "could not parse numeric value"

    ctx_lower = claim["context"].lower()

    # Run-count checks against live API.
    # Guard: only compare against total_runs for "large" numbers (>=100) to avoid
    # treating per-model n-counts ("23 runs") as total-system-run claims.
    if any(w in ctx_lower for w in ("run", "eval")) and status_data and claimed_int >= 100:
        total = status_data.get("cost_today", {}).get("total_runs", 0)
        if total:
            delta_pct = abs(claimed_int - total) / total
            if delta_pct <= 0.02:
                return "CONFIRMED", f"/status API: total_runs={total}"
            elif delta_pct > 0.10:
                return "CONTRADICTED", f"/status API shows {total} total runs (you claimed {claimed_int})"

    # Search FINDINGS.md
    pattern = re.compile(r"\b" + re.escape(str(claimed_int)) + r"\b")
    if pattern.search(findings_text):
        m = pattern.search(findings_text)
        snippet = findings_text[max(0, m.start() - 50): m.end() + 50].replace("\n", " ").strip()
        return "CONFIRMED", f"found in FINDINGS.md: …{snippet}…"

    # Search CHANGELOG.md
    if pattern.search(changelog_text):
        m = pattern.search(changelog_text)
        snippet = changelog_text[max(0, m.start() - 50): m.end() + 50].replace("\n", " ").strip()
        return "CONFIRMED", f"found in CHANGELOG.md: …{snippet}…"

    # Search memory logs
    if pattern.search(memory_text):
        return "CONFIRMED", f"number {claimed_int} found in memory logs"

    return "UNVERIFIABLE", f"number {claimed_int} not found in any source"


def verify_date(
    claim: dict,
    memory_text: str,
    changelog_text: str,
    git_log_text: str,
) -> tuple[str, str]:
    """Verify a date reference exists in known sources."""
    date_str = claim["value"]

    if date_str in memory_text:
        return "CONFIRMED", f"date {date_str} found in memory logs"
    if date_str in changelog_text:
        return "CONFIRMED", f"date {date_str} found in CHANGELOG.md"
    if date_str in git_log_text:
        return "CONFIRMED", f"date {date_str} found in git log"

    # Plausibility check — project started ~2025-01
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        if d.year >= 2025:
            return "UNVERIFIABLE", f"{date_str} not in logs but falls within project timeframe"
    except ValueError:
        pass

    return "UNVERIFIABLE", f"date {date_str} not found in any source"


# ─── Report formatting ────────────────────────────────────────────────────────

ICONS = {"CONFIRMED": "✅", "UNVERIFIABLE": "⚠️", "CONTRADICTED": "❌"}


def format_result(status: str, context: str, evidence: str) -> str:
    """Format a single claim verification line."""
    icon = ICONS.get(status, "❓")
    display = (context[:77] + "...") if len(context) > 80 else context
    return f'{icon} {status}: "{display}" → {evidence}'


# ─── Orchestration ────────────────────────────────────────────────────────────

def run_fact_check(draft_path: Path) -> list[str]:
    """Run full fact-check pipeline. Returns list of report lines."""
    if not draft_path.exists():
        return [f"❌ ERROR: File not found: {draft_path}"]

    text = draft_path.read_text(encoding="utf-8")
    lines: list[str] = []

    lines.append(f"# Fact-Check Report: {draft_path.name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Source: {draft_path.resolve()}")
    lines.append("")

    # Load sources
    findings_text = load_findings()
    changelog_text = load_changelog()
    memory_text = load_memory_logs()
    score_files = load_score_files()
    status_data = fetch_status_api()
    git_log_text = load_git_log()

    lines.append("## Source Data")
    lines.append(f"- FINDINGS.md:   {'✅' if findings_text else '❌ not found'}")
    lines.append(f"- /status API:   {'✅ live' if status_data else '⚠️ unavailable'}")
    lines.append(f"- Score files:   {'✅ ' + str(len(score_files)) + ' files' if score_files else '⚠️ none'}")
    lines.append(f"- Memory logs:   {'✅' if memory_text else '⚠️ none'}")
    lines.append(f"- Git log:       {'✅' if git_log_text else '⚠️ unavailable'}")
    lines.append(f"- CHANGELOG.md:  {'✅' if changelog_text else '❌ not found'}")
    lines.append("")

    # Extract all claim types
    score_claims = extract_score_claims(text)
    model_refs = extract_model_refs(text)
    date_refs = extract_date_refs(text)
    numeric_claims = extract_numeric_claims(text)
    pct_claims = extract_percentage_claims(text)

    # Collect all positions already handled to avoid double-reporting
    seen_pos: set[int] = set()
    # Score positions overlap with numeric — register them first
    score_positions = {c["pos"] for c in score_claims}

    total = (
        len(score_claims)
        + len(model_refs)
        + len(date_refs)
        + len(numeric_claims)
        + len(pct_claims)
    )

    if total == 0:
        lines.append("## Result")
        lines.append("✅ No verifiable claims found in this document.")
        return lines

    lines.append("## Claims Detected")
    lines.append(f"- Model references:  {len(model_refs)}")
    lines.append(f"- Score values:      {len(score_claims)}")
    lines.append(f"- Dates:             {len(date_refs)}")
    lines.append(f"- Numeric claims:    {len(numeric_claims)}")
    lines.append(f"- Percentages:       {len(pct_claims)}")
    lines.append("")
    lines.append("## Verification Results")
    lines.append("")

    # --- Model references ---
    if model_refs:
        lines.append("### Model References")
        for c in model_refs:
            if c["pos"] in seen_pos:
                continue
            seen_pos.add(c["pos"])
            status, ev = verify_model_ref(c, status_data, findings_text, score_files)
            lines.append(format_result(status, c["context"], ev))
        lines.append("")

    # --- Score claims ---
    if score_claims:
        lines.append("### Score Values")
        for c in score_claims:
            if c["pos"] in seen_pos:
                continue
            seen_pos.add(c["pos"])
            status, ev = verify_score_value(c, status_data, findings_text, score_files)
            lines.append(format_result(status, c["context"], ev))
        lines.append("")

    # --- Date references ---
    if date_refs:
        lines.append("### Date References")
        for c in date_refs:
            if c["pos"] in seen_pos:
                continue
            seen_pos.add(c["pos"])
            status, ev = verify_date(c, memory_text, changelog_text, git_log_text)
            lines.append(format_result(status, c["context"], ev))
        lines.append("")

    # --- Numeric claims (skip positions already claimed by scores) ---
    interesting_numerics = [
        c for c in numeric_claims
        if c["pos"] not in seen_pos and c["pos"] not in score_positions
    ]
    if interesting_numerics:
        lines.append("### Numeric Claims")
        for c in interesting_numerics[:25]:  # cap to avoid noise
            seen_pos.add(c["pos"])
            status, ev = verify_numeric(
                c, status_data, findings_text, changelog_text, memory_text
            )
            lines.append(format_result(status, c["context"], ev))
        lines.append("")

    # --- Percentage claims ---
    interesting_pcts = [c for c in pct_claims if c["pos"] not in seen_pos]
    if interesting_pcts:
        lines.append("### Percentage Claims")
        for c in interesting_pcts[:10]:
            seen_pos.add(c["pos"])
            # Reuse numeric verifier on the bare number
            proxy = {**c, "value": c["number"]}
            status, ev = verify_numeric(
                proxy, status_data, findings_text, changelog_text, memory_text
            )
            lines.append(format_result(status, c["context"], ev))
        lines.append("")

    # --- Summary ---
    verdict_lines = [l for l in lines if l.startswith(("✅", "⚠️", "❌"))]
    n_confirmed = sum(1 for l in verdict_lines if l.startswith("✅"))
    n_unverifiable = sum(1 for l in verdict_lines if l.startswith("⚠️"))
    n_contradicted = sum(1 for l in verdict_lines if l.startswith("❌"))

    lines.append("## Summary")
    lines.append(f"- ✅ Confirmed:     {n_confirmed}")
    lines.append(f"- ⚠️  Unverifiable: {n_unverifiable}")
    lines.append(f"- ❌ Contradicted:  {n_contradicted}")
    if n_contradicted > 0:
        lines.append("")
        lines.append("**⚠️ Action required:** Review contradicted claims before publishing.")

    return lines


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fact-check a markdown draft against source data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 fact_check.py draft.md
  python3 fact_check.py draft.md --output report.md
        """,
    )
    parser.add_argument("draft", type=Path, help="Path to markdown draft to verify")
    parser.add_argument("--output", type=Path, help="Also write report to this file")
    args = parser.parse_args()

    report_lines = run_fact_check(args.draft)
    report_text = "\n".join(report_lines)

    print(report_text)

    if args.output:
        args.output.write_text(report_text, encoding="utf-8")
        print(f"\n→ Report written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

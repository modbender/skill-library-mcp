#!/usr/bin/env python3
"""
auto_capture.py — Analyze recent OpenClaw session memory logs and push
high-value insights to Supermemory cloud backup.

Usage:
    python3 auto_capture.py               # scan last 3 days, upload high-value
    python3 auto_capture.py --dry-run     # show what would be captured, no upload
    python3 auto_capture.py --days 7      # scan last 7 days
    python3 auto_capture.py --force       # re-upload even if already seen

Designed to be run by cron (see install_cron.sh).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── Config ───────────────────────────────────────────────────────────────────

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", "/mnt/openclaw/openclaw/.openclaw/workspace"))
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = WORKSPACE / "skills" / "supermemory-free" / ".capture_state.json"
API_URL_STORE = "https://api.supermemory.ai/v3/documents"
DEFAULT_TAG = "openclaw"
MIN_LENGTH = 40   # Minimum insight length to be worth storing
MAX_LENGTH = 2000  # Truncate very long insights


# ── High-value pattern matchers ───────────────────────────────────────────────

# Patterns that signal a "high-value" line worth persisting
HIGH_VALUE_PATTERNS = [
    # Fixes and solutions
    (r"\b(fix(?:ed|es)?|resolv(?:ed|es)?|solution|solved|workaround)\b.{10,}", "fix"),
    # Errors with context
    (r"\b(error|exception|fail(?:ed|ure)?|crash)\b.{15,}", "error"),
    # Configuration and paths
    (r"(?:/[a-z][^\s,;]{4,}|[A-Z_]{3,}=\S{3,})", "config"),
    # API / endpoint discovery
    (r"\b(endpoint|api|url|route|http[s]?)[\s:\/].{10,}", "api"),
    # User preferences
    (r"\buser\s+prefer\w*\b.{10,}", "preference"),
    # Important decisions
    (r"\b(decided?|chose|choosing|prefer|using)\b.{15,}", "decision"),
    # Learned facts
    (r"\b(learned?|note[sd]?|remember|important|key insight)\b.{15,}", "insight"),
    # Installed / setup
    (r"\b(install(?:ed)?|setup|configured?|enabled?)\b.{10,}", "setup"),
    # Credentials / keys (location only, never log values)
    (r"\bapi[\s_-]?key\b.{5,}", "credential"),
    # Memory entries with explicit markers
    (r"^[-*•]\s+.{30,}", "bullet"),
    # Dates with context (session summaries)
    (r"\d{4}-\d{2}-\d{2}.{20,}", "dated"),
]

# Lines to explicitly skip (low value or sensitive)
SKIP_PATTERNS = [
    r"^\s*$",                          # empty
    r"^#",                             # markdown headers (low signal)
    r"^(---|\*\*\*|===)",             # separators
    r"password\s*[:=]",               # never store passwords
    r"secret\s*[:=]",                 # never store secrets
    r"token\s*[:=]\s*\S{20,}",       # never store raw token values
    r"^(yes|no|ok|sure|thanks?)\b",  # filler
]

COMPILED_HIGH_VALUE = [(re.compile(p, re.IGNORECASE), label) for p, label in HIGH_VALUE_PATTERNS]
COMPILED_SKIP = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in SKIP_PATTERNS]


# ── State persistence (dedup) ─────────────────────────────────────────────────

def load_state() -> dict:
    """Load seen-hashes state to avoid re-uploading."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"uploaded": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode()).hexdigest()[:16]


# ── Memory log scanner ────────────────────────────────────────────────────────

def find_memory_files(days: int) -> list[Path]:
    """Find memory log files from the last N days."""
    if not MEMORY_DIR.exists():
        return []

    files = []
    today = datetime.now(timezone.utc).date()
    for i in range(days):
        day = today - timedelta(days=i)
        candidates = [
            MEMORY_DIR / f"{day}.md",
            MEMORY_DIR / f"{day.isoformat()}.md",
        ]
        for path in candidates:
            if path.exists():
                files.append(path)
                break

    return files


def is_high_value(line: str) -> tuple[bool, str]:
    """Return (is_high_value, label) for a line."""
    stripped = line.strip()

    if len(stripped) < MIN_LENGTH:
        return False, ""

    for pattern in COMPILED_SKIP:
        if pattern.search(stripped):
            return False, ""

    for pattern, label in COMPILED_HIGH_VALUE:
        if pattern.search(stripped):
            return True, label

    return False, ""


def extract_insights_from_file(path: Path) -> list[dict]:
    """Extract high-value insights from a memory markdown file."""
    text = path.read_text(errors="replace")
    insights = []

    # Strategy 1: Line-by-line scan
    for line in text.splitlines():
        line = line.strip()
        high, label = is_high_value(line)
        if high:
            content = line[:MAX_LENGTH]
            insights.append({
                "content": content,
                "label": label,
                "source_file": path.name,
                "strategy": "line",
            })

    # Strategy 2: Extract bullet-point blocks (multi-line)
    blocks = re.findall(r"(?:^[-*•]\s+.+(?:\n  .+)*)", text, re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if len(block) >= MIN_LENGTH:
            insights.append({
                "content": block[:MAX_LENGTH],
                "label": "bullet-block",
                "source_file": path.name,
                "strategy": "block",
            })

    # Deduplicate within file
    seen = set()
    unique = []
    for item in insights:
        h = content_hash(item["content"])
        if h not in seen:
            seen.add(h)
            unique.append(item)

    return unique


# ── API client ────────────────────────────────────────────────────────────────

def load_api_key() -> str:
    key = os.environ.get("SUPERMEMORY_OPENCLAW_API_KEY", "").strip()
    if key:
        return key

    search_dirs = [
        WORKSPACE,
        Path(os.path.dirname(os.path.abspath(__file__))) / "../..",
        Path("/mnt/openclaw/openclaw/.openclaw/workspace"),
    ]
    for d in search_dirs:
        env_path = Path(d) / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("SUPERMEMORY_OPENCLAW_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val

    raise ValueError("SUPERMEMORY_OPENCLAW_API_KEY not found in .env or environment.")


def upload_insight(content: str, label: str, source_file: str, api_key: str) -> dict:
    """Upload a single insight to Supermemory cloud."""
    payload = {
        "content": content,
        "containerTag": DEFAULT_TAG,
        "metadata": {
            "source": f"auto-capture:{source_file}",
            "label": label,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "captured_by": "openclaw-auto-capture",
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL_STORE,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0; +https://openclaw.ai)",
            "Origin": "https://console.supermemory.ai",
            "Referer": "https://console.supermemory.ai/",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Auto-capture high-value insights from session memory logs to Supermemory cloud.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 auto_capture.py               # Scan last 3 days
  python3 auto_capture.py --dry-run     # Preview without uploading
  python3 auto_capture.py --days 7      # Scan last 7 days
  python3 auto_capture.py --force       # Re-upload previously seen items

Install cron (daily at 2am UTC):
  bash skills/supermemory-free/install_cron.sh
        """,
    )
    parser.add_argument("--days", type=int, default=3, help="Days of memory logs to scan (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Preview captures without uploading")
    parser.add_argument("--force", action="store_true", help="Re-upload even if already captured")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Load dedup state
    state = load_state()
    uploaded_hashes = state.get("uploaded", {})

    # Find memory files
    files = find_memory_files(args.days)
    if not files:
        print(f"ℹ️  No memory files found in {MEMORY_DIR} for the last {args.days} days.")
        print(f"   Expected files like: {MEMORY_DIR}/2026-02-15.md")
        return

    print(f"📂 Scanning {len(files)} memory file(s) from the last {args.days} day(s)...")

    # Extract all insights
    all_insights = []
    for f in files:
        insights = extract_insights_from_file(f)
        all_insights.extend(insights)
        if args.verbose:
            print(f"   {f.name}: {len(insights)} candidate insight(s)")

    if not all_insights:
        print("ℹ️  No high-value insights found.")
        return

    # Filter already-uploaded
    new_insights = []
    for item in all_insights:
        h = content_hash(item["content"])
        if not args.force and h in uploaded_hashes:
            if args.verbose:
                print(f"   [skip] already uploaded: {item['content'][:60]}...")
            continue
        item["_hash"] = h
        new_insights.append(item)

    if not new_insights:
        print(f"✅ All {len(all_insights)} insight(s) already uploaded to cloud. Nothing new.")
        return

    print(f"🧠 Found {len(new_insights)} new insight(s) to capture (skipped {len(all_insights) - len(new_insights)} already seen)\n")

    if args.dry_run:
        print("--- DRY RUN (no uploads) ---")
        for i, item in enumerate(new_insights, 1):
            print(f"\n[{i}] label={item['label']} source={item['source_file']}")
            print(f"    {item['content'][:200]}")
        print(f"\n--- Would upload {len(new_insights)} insight(s) ---")
        return

    # Load API key
    try:
        api_key = load_api_key()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Upload
    uploaded = 0
    failed = 0
    for i, item in enumerate(new_insights, 1):
        try:
            result = upload_insight(
                content=item["content"],
                label=item["label"],
                source_file=item["source_file"],
                api_key=api_key,
            )
            doc_id = result.get("id", "?")
            uploaded_hashes[item["_hash"]] = {
                "id": doc_id,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "source": item["source_file"],
                "label": item["label"],
                "preview": item["content"][:80],
            }
            uploaded += 1
            print(f"✅ [{i}/{len(new_insights)}] {item['label']:12s} | {item['content'][:70]}...")
        except Exception as e:
            failed += 1
            print(f"❌ [{i}/{len(new_insights)}] FAILED: {e}")
            print(f"   Content: {item['content'][:80]}...")

    # Save state
    state["uploaded"] = uploaded_hashes
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    state["last_run_stats"] = {"uploaded": uploaded, "failed": failed, "total": len(new_insights)}
    save_state(state)

    print(f"\n📊 Done: {uploaded} uploaded, {failed} failed out of {len(new_insights)} new insights")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

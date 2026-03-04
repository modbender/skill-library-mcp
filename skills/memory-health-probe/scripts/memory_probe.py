#!/usr/bin/env python3
"""
memory_probe.py — QMD memory telemetry probe
Runs daily (or on demand) to measure QMD index health and retrieval quality.
Logs results to Langfuse and stores JSON snapshot for trending.

Usage:
    python3 memory_probe.py           # run probe and log
    python3 memory_probe.py --dry-run # print results, no Langfuse write
    python3 memory_probe.py --trend   # print trend over stored snapshots

Metrics captured:
    1. Index health    — file count, chunk count, index size, age
    2. BM25 quality    — hit rate + score distribution over canonical queries
    3. Gateway events  — session-memory saves, QMD armed events today
    4. Coverage map    — which collections are hit for which query categories
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
QMD_BIN        = Path.home() / ".bun/bin/qmd"
GATEWAY_LOG    = Path.home() / ".openclaw/logs/gateway.log"
GATEWAY_ERRLOG = Path.home() / ".openclaw/logs/gateway.err.log"
DATA_DIR       = Path(__file__).parent.parent / "data/memory_telemetry"
LANGFUSE_URL   = "http://localhost:3100"
LANGFUSE_PK    = "pk-lf-openclaw-local"
LANGFUSE_SK    = "sk-lf-openclaw-local"

TODAY     = datetime.now().strftime("%Y-%m-%d")
DRY_RUN   = "--dry-run" in sys.argv
TREND     = "--trend" in sys.argv

# ── Canonical query set ───────────────────────────────────────────────────────
# 20 queries across 5 knowledge domains.
# For each: run BM25 search, record hit(bool) + top_score(float) + top_collection(str)
QUERIES = [
    # Model evaluation
    {"q": "qwen2.5 classify score",          "domain": "eval",   "expect": "hybrid-cp"},
    {"q": "granite4 format promotion",       "domain": "eval",   "expect": "hybrid-cp"},
    {"q": "promotion threshold 200 runs",    "domain": "eval",   "expect": "hybrid-cp"},
    {"q": "phi4 control floor latency",      "domain": "eval",   "expect": "hybrid-cp"},
    {"q": "deepseek-r1 thinking token strip","domain": "eval",   "expect": "hybrid-cp"},

    # Infrastructure / decisions
    {"q": "Voyage nomic replacement",        "domain": "infra",  "expect": "daily"},
    {"q": "QMD memory backend enabled",      "domain": "infra",  "expect": "daily"},
    {"q": "launchctl gateway restart PATH",  "domain": "infra",  "expect": "daily"},
    {"q": "openclaw doctor schema validate", "domain": "infra",  "expect": "daily"},
    {"q": "caffeinate sleep prevention",     "domain": "infra",  "expect": "daily"},

    # Projects
    {"q": "hybrid control plane Sprint",     "domain": "proj",   "expect": "hybrid-cp"},
    {"q": "Insight Engine Langfuse",         "domain": "proj",   "expect": "hybrid-cp"},
    {"q": "accumulator IndentationError",    "domain": "proj",   "expect": "daily"},
    {"q": "Notion Content Pipeline blog",    "domain": "proj",   "expect": "vault"},
    {"q": "Monk Fenix inbox cleanup",        "domain": "proj",   "expect": "vault"},

    # People / context
    {"q": "Nissan Sydney Mac Mini",          "domain": "ctx",    "expect": "vault"},
    {"q": "Benjamin Locutus Dookeran",       "domain": "ctx",    "expect": "vault"},
    {"q": "1Password service account token", "domain": "ctx",    "expect": "daily"},
    {"q": "Telegram personal account",       "domain": "ctx",    "expect": "daily"},

    # Workflow
    {"q": "pyenv Python 3.14.3",             "domain": "tools",  "expect": "daily"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def run_qmd_status() -> dict:
    """Parse `qmd status` output into structured metrics."""
    try:
        out = subprocess.run(
            [str(QMD_BIN), "status"],
            capture_output=True, text=True, timeout=30
        ).stdout
        metrics = {}
        m = re.search(r"Total:\s+(\d+)\s+files", out)
        metrics["file_count"] = int(m.group(1)) if m else 0
        m = re.search(r"Vectors:\s+(\d+)\s+embedded", out)
        metrics["chunk_count"] = int(m.group(1)) if m else 0
        m = re.search(r"Size:\s+([\d.]+)\s+MB", out)
        metrics["index_size_mb"] = float(m.group(1)) if m else 0.0
        m = re.search(r"Updated:\s+(.+)", out)
        metrics["last_updated"] = m.group(1).strip() if m else "unknown"
        # Count collections
        metrics["collection_count"] = out.count("qmd://")
        return metrics
    except Exception as e:
        return {"error": str(e), "file_count": 0, "chunk_count": 0}


def run_bm25_search(query: str) -> dict:
    """Run `qmd search` and return hit/score/collection."""
    try:
        result = subprocess.run(
            [str(QMD_BIN), "search", query, "-n", "1"],
            capture_output=True, text=True, timeout=15
        )
        out = result.stdout
        if "No results found" in out or not out.strip():
            return {"hit": False, "score": 0.0, "collection": None, "source_file": None}

        # Extract score: "Score:  36%"
        m = re.search(r"Score:\s+(\d+)%", out)
        score = int(m.group(1)) / 100.0 if m else 0.0

        # Extract collection from path: "qmd://memory/..."  or "qmd://vault/..."
        m = re.search(r"qmd://(\w+)/", out)
        collection = m.group(1) if m else "unknown"

        # Extract source file
        m = re.search(r"qmd://[^\s:]+", out)
        source_file = m.group(0) if m else None

        return {"hit": True, "score": score, "collection": collection, "source_file": source_file}
    except Exception as e:
        return {"hit": False, "score": 0.0, "collection": None, "error": str(e)}


def count_gateway_events() -> dict:
    """Count today's session-memory and QMD armed events from gateway logs."""
    today_pattern = TODAY  # "2026-02-26" but logs are in UTC so check both
    # UTC yesterday might be today AEST
    from datetime import date, timedelta
    utc_yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    counts = {"session_saves": 0, "qmd_armed": 0, "qmd_errors": 0}
    for log_path in [GATEWAY_LOG, GATEWAY_ERRLOG]:
        if not log_path.exists():
            continue
        try:
            text = log_path.read_text(errors="ignore")
            for pattern in [today_pattern, utc_yesterday]:
                counts["session_saves"] += text.count(f"{pattern}") and \
                    len(re.findall(rf"{pattern}.*session-memory.*saved", text)) or \
                    len(re.findall(r"session-memory.*saved", text))
                counts["qmd_armed"] += len(re.findall(r"qmd memory startup initialization armed", text))
                counts["qmd_errors"] += len(re.findall(r"\[memory\] qmd.*failed", text))
            break  # count from log, not err.log (avoid double-counting)
        except Exception:
            pass
    # Deduplicate: we only want today's
    counts["session_saves"] = len(re.findall(
        r"session-memory.*saved",
        GATEWAY_LOG.read_text(errors="ignore") if GATEWAY_LOG.exists() else ""
    ))
    counts["qmd_armed"] = len(re.findall(
        r"qmd memory startup initialization armed",
        GATEWAY_LOG.read_text(errors="ignore") if GATEWAY_LOG.exists() else ""
    ))
    counts["qmd_errors"] = len(re.findall(
        r"\[memory\] qmd.*failed",
        GATEWAY_ERRLOG.read_text(errors="ignore") if GATEWAY_ERRLOG.exists() else ""
    ))
    return counts


def log_to_langfuse(probe_result: dict) -> str | None:
    """Log probe result to Langfuse as a trace. Returns trace ID or None."""
    import urllib.request
    import base64

    creds = base64.b64encode(f"{LANGFUSE_PK}:{LANGFUSE_SK}".encode()).decode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
    }

    trace_id = f"memory-probe-{TODAY}"
    payload = {
        "id": trace_id,
        "name": "memory_probe_daily",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "probe_date": TODAY,
            "backend": "qmd",
            "qmd_version": "1.0.7",
        },
        "input": {"query_count": len(QUERIES), "domains": list({q["domain"] for q in QUERIES})},
        "output": probe_result,
        "tags": ["memory", "qmd", "telemetry"],
    }

    try:
        req = urllib.request.Request(
            f"{LANGFUSE_URL}/api/public/traces",
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return trace_id
    except Exception as e:
        print(f"  ⚠ Langfuse log failed: {e}")
        return None


def log_scores_to_langfuse(trace_id: str, scores: list[dict]):
    """Log per-metric scores to Langfuse."""
    import urllib.request
    import base64

    creds = base64.b64encode(f"{LANGFUSE_PK}:{LANGFUSE_SK}".encode()).decode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
    }

    score_payloads = [
        {"traceId": trace_id, "name": s["name"], "value": s["value"],
         "comment": s.get("comment", ""), "dataType": "NUMERIC"}
        for s in scores
    ]

    for sp in score_payloads:
        try:
            req = urllib.request.Request(
                f"{LANGFUSE_URL}/api/public/scores",
                data=json.dumps(sp).encode(),
                headers=headers,
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass


def load_snapshots() -> list[dict]:
    """Load all stored daily snapshots for trending."""
    snapshots = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            snapshots.append(json.loads(f.read_text()))
        except Exception:
            pass
    return snapshots


def print_trend(snapshots: list[dict]):
    """Print trend table from stored snapshots."""
    if not snapshots:
        print("No historical snapshots found.")
        return
    print(f"\n{'Date':<12} {'Files':>6} {'Chunks':>7} {'Hit%':>6} {'AvgScore':>9} {'Armed':>6} {'Errors':>7}")
    print("-" * 60)
    for s in snapshots:
        idx = s.get("index", {})
        bm25 = s.get("bm25", {})
        gw = s.get("gateway", {})
        print(
            f"{s.get('date','?'):<12} "
            f"{idx.get('file_count',0):>6} "
            f"{idx.get('chunk_count',0):>7} "
            f"{bm25.get('hit_rate',0)*100:>5.0f}% "
            f"{bm25.get('avg_score',0):>9.3f} "
            f"{gw.get('qmd_armed',0):>6} "
            f"{gw.get('qmd_errors',0):>7}"
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if TREND:
        print_trend(load_snapshots())
        return

    print(f"{'='*60}")
    print(f"  QMD Memory Probe — {TODAY}")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE (will log to Langfuse)'}")
    print(f"{'='*60}\n")

    # 1. Index health
    print("📊 Index health...")
    index = run_qmd_status()
    print(f"   Files: {index.get('file_count')} | Chunks: {index.get('chunk_count')} | "
          f"Size: {index.get('index_size_mb')} MB | Last update: {index.get('last_updated')}")

    # 2. BM25 quality probes
    print("\n🔍 BM25 quality probes (20 canonical queries)...")
    query_results = []
    hits = 0
    total_score = 0.0
    domain_hits: dict[str, list] = {}

    for q in QUERIES:
        result = run_bm25_search(q["q"])
        result["query"] = q["q"]
        result["domain"] = q["domain"]
        result["expected_collection"] = q["expect"]
        query_results.append(result)

        if result["hit"]:
            hits += 1
            total_score += result["score"]
            domain_hits.setdefault(q["domain"], []).append(result["score"])

        icon = "✓" if result["hit"] else "✗"
        score_str = f"{result['score']*100:.0f}%" if result["hit"] else " — "
        col = result.get("collection") or "—"
        print(f"   {icon} [{q['domain']:5}] {q['q'][:40]:<40} score={score_str:>4}  coll={col}")

    hit_rate = hits / len(QUERIES)
    avg_score = total_score / hits if hits > 0 else 0.0
    print(f"\n   Hit rate: {hit_rate*100:.0f}%  ({hits}/{len(QUERIES)})  |  Avg score (hits): {avg_score*100:.0f}%")

    # Domain breakdown
    print("\n   Domain breakdown:")
    for domain, scores in domain_hits.items():
        count = len(scores)
        total = len([q for q in QUERIES if q["domain"] == domain])
        print(f"   {domain:8} {count}/{total} hits  avg={sum(scores)/count*100:.0f}%")

    # 3. Gateway events
    print("\n🔗 Gateway events...")
    gw_events = count_gateway_events()
    print(f"   Session-memory saves: {gw_events['session_saves']}")
    print(f"   QMD armed events:     {gw_events['qmd_armed']}")
    print(f"   QMD errors (total):   {gw_events['qmd_errors']}")

    # Assemble snapshot
    snapshot = {
        "date": TODAY,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "index": index,
        "bm25": {
            "hit_rate": round(hit_rate, 4),
            "avg_score": round(avg_score, 4),
            "hits": hits,
            "total_queries": len(QUERIES),
            "by_domain": {
                d: {
                    "hits": len(scores),
                    "total": len([q for q in QUERIES if q["domain"] == d]),
                    "avg_score": round(sum(scores) / len(scores), 4),
                }
                for d, scores in domain_hits.items()
            },
        },
        "gateway": gw_events,
        "query_results": query_results,
    }

    # Save snapshot
    snap_file = DATA_DIR / f"{TODAY}.json"
    snap_file.write_text(json.dumps(snapshot, indent=2))
    print(f"\n💾 Snapshot saved: {snap_file}")

    # Log to Langfuse
    if not DRY_RUN:
        print("\n📡 Logging to Langfuse...")
        trace_id = log_to_langfuse(snapshot)
        if trace_id:
            scores_payload = [
                {"name": "bm25_hit_rate",    "value": hit_rate},
                {"name": "bm25_avg_score",   "value": avg_score},
                {"name": "index_file_count", "value": index.get("file_count", 0)},
                {"name": "index_chunk_count","value": index.get("chunk_count", 0)},
                {"name": "index_size_mb",    "value": index.get("index_size_mb", 0)},
                {"name": "qmd_armed_count",  "value": gw_events["qmd_armed"]},
                {"name": "qmd_error_count",  "value": gw_events["qmd_errors"]},
            ]
            log_scores_to_langfuse(trace_id, scores_payload)
            print(f"   Trace ID: {trace_id}")
            print(f"   Langfuse URL: {LANGFUSE_URL}")
        else:
            print("   ⚠ Langfuse log failed (probe data saved locally)")
    else:
        print("\n[DRY RUN] Skipping Langfuse write")

    # Trend if previous snapshots exist
    prev = load_snapshots()
    if len(prev) > 1:
        print("\n📈 Trend (all probes):")
        print_trend(prev)

    print(f"\n{'='*60}")
    print(f"  Done. To view trend: python3 {__file__} --trend")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

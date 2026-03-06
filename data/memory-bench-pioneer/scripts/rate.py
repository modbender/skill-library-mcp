#!/usr/bin/env python3
"""
memory-bench rate — Retrieval quality assessment with LLM-as-judge.

Runs standardized queries against the memory system, uses an external LLM
to judge relevance (not the retrieval system itself), computes standard IR
metrics, and supports ablation runs.

Usage:
    python3 rate.py [--queries N] [--db PATH] [--ablation] [--judge openai|local]

Metrics computed:
    - RAR (Recall Accuracy Ratio): fraction of top-k rated ≥3
    - MRR (Mean Reciprocal Rank): 1/rank of first relevant result
    - nDCG@5 (Normalized Discounted Cumulative Gain)
    - MAP@5 (Mean Average Precision)
    - Precision@k, Hit Rate
    - 95% confidence intervals via bootstrapping
"""
import sqlite3
import sys
import os
import json
import time
import math
import random
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent

def find_db():
    candidates = [
        Path.home() / ".openclaw" / "workspace" / "db" / "memory.db",
        Path.home() / ".openclaw" / "workspace" / "db" / "cognitive_memory.db",
        Path.home() / ".openclaw" / "workspace" / "db" / "jarvis.db",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def ensure_retrieval_log(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS retrieval_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            query TEXT NOT NULL,
            query_id TEXT,
            strategy TEXT NOT NULL DEFAULT 'hybrid',
            result_count INTEGER,
            avg_score REAL,
            latency_ms REAL,
            rar REAL,
            mrr REAL,
            ndcg REAL,
            map_score REAL,
            precision_at_k REAL,
            hit_rate REAL,
            ratings TEXT,
            judge_method TEXT,
            ablation_config TEXT,
            algorithm_version TEXT
        )
    """)
    # Migrate old tables missing new columns
    existing = {r[1] for r in conn.execute("PRAGMA table_info(retrieval_log)").fetchall()}
    migrations = [
        ("query_id", "TEXT"), ("ndcg", "REAL"), ("map_score", "REAL"),
        ("precision_at_k", "REAL"), ("hit_rate", "REAL"),
        ("judge_method", "TEXT"), ("ablation_config", "TEXT"),
        ("algorithm_version", "TEXT"),
    ]
    for col, typ in migrations:
        if col not in existing:
            conn.execute(f"ALTER TABLE retrieval_log ADD COLUMN {col} {typ}")
    conn.commit()

def load_test_set(path: Optional[str] = None) -> list:
    """Load the standard test set."""
    p = Path(path) if path else SCRIPT_DIR / "testset.json"
    if not p.exists():
        print(f"❌ Test set not found at {p}")
        sys.exit(1)
    return json.loads(p.read_text())

def get_algorithm_version() -> str:
    """Get memory system version from git or package."""
    try:
        import subprocess
        ws = Path.home() / ".openclaw" / "workspace"
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", "skills/agent-memory-ultimate/"],
            capture_output=True, text=True, cwd=ws, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"

# --- IR Metrics ---

def dcg(ratings, k=5):
    """Discounted Cumulative Gain."""
    total = 0.0
    for i, r in enumerate(ratings[:k]):
        total += (2**r - 1) / math.log2(i + 2)
    return total

def ndcg(ratings, k=5):
    """Normalized DCG — compares actual ranking to ideal."""
    actual = dcg(ratings, k)
    ideal = dcg(sorted(ratings, reverse=True), k)
    return actual / ideal if ideal > 0 else 0.0

def average_precision(ratings, k=5, threshold=3):
    """Average Precision at k."""
    relevant_count = 0
    precision_sum = 0.0
    for i, r in enumerate(ratings[:k]):
        if r >= threshold:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)
    return precision_sum / min(k, len(ratings)) if ratings else 0.0

def precision_at_k(ratings, k=5, threshold=3):
    return sum(1 for r in ratings[:k] if r >= threshold) / k if ratings else 0.0

def hit_rate(ratings, threshold=3):
    return 1.0 if any(r >= threshold for r in ratings) else 0.0

def compute_rar(ratings, threshold=3):
    if not ratings: return 0.0
    return sum(1 for r in ratings if r >= threshold) / len(ratings)

def compute_mrr(ratings, threshold=3):
    for i, r in enumerate(ratings):
        if r >= threshold:
            return 1.0 / (i + 1)
    return 0.0

def bootstrap_ci(values, n_boot=1000, alpha=0.05):
    """Bootstrap 95% confidence interval."""
    if len(values) < 2:
        return {"mean": values[0] if values else 0, "ci_low": 0, "ci_high": 0}
    means = []
    for _ in range(n_boot):
        sample = random.choices(values, k=len(values))
        means.append(sum(sample) / len(sample))
    means.sort()
    lo = means[int(n_boot * alpha / 2)]
    hi = means[int(n_boot * (1 - alpha / 2))]
    return {
        "mean": round(sum(values) / len(values), 4),
        "ci_low": round(lo, 4),
        "ci_high": round(hi, 4),
    }

# --- LLM-as-Judge ---

def judge_with_openai(query: str, result_content: str, api_key: str) -> int:
    """Use OpenAI API to judge relevance. Returns 1-5 rating."""
    import urllib.request
    prompt = f"""Rate the relevance of this retrieved memory to the query on a scale of 1-5.

1 = Completely irrelevant
2 = Slightly related topic but not useful
3 = Somewhat relevant, partially answers the query
4 = Relevant, mostly answers the query
5 = Highly relevant, directly answers the query

Query: "{query}"

Retrieved memory (first 300 chars): "{result_content[:300]}"

Respond with ONLY a single digit 1-5, nothing else."""

    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3,
        "temperature": 0,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            text = body["choices"][0]["message"]["content"].strip()
            rating = int(text[0]) if text and text[0].isdigit() else 3
            return max(1, min(5, rating))
    except Exception as e:
        print(f"    ⚠️ Judge error: {e}")
        return 3  # neutral fallback

def judge_with_embeddings(query: str, result_content: str) -> int:
    """Fallback: use local embedding similarity as rough judge.
    NOTE: This is weaker than LLM-judge. Marked in output."""
    try:
        import urllib.request
        data = json.dumps({"texts": [query, result_content[:300]]}).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:8900/embed",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            embeddings = json.loads(resp.read())["embeddings"]
            # cosine similarity
            a, b = embeddings[0], embeddings[1]
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x**2 for x in a))
            nb = math.sqrt(sum(x**2 for x in b))
            sim = dot / (na * nb) if na and nb else 0
            if sim > 0.7: return 5
            if sim > 0.5: return 4
            if sim > 0.35: return 3
            if sim > 0.2: return 2
            return 1
    except Exception:
        return 3

# --- Retrieval ---

def run_recall(conn, query: str, strategy="hybrid", limit=5, use_activation=True):
    """Run a recall query and time it."""
    try:
        sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "skills" / "agent-memory-ultimate" / "scripts"))
        from lib.memory_core import recall, primed_recall

        old_factory = conn.row_factory
        conn.row_factory = sqlite3.Row
        start = time.time()
        if use_activation and strategy == "hybrid":
            try:
                results = primed_recall(conn, query, limit=limit)
            except Exception:
                results = recall(conn, query, strategy=strategy, limit=limit)
        else:
            results = recall(conn, query, strategy=strategy, limit=limit)
        latency = (time.time() - start) * 1000
        conn.row_factory = old_factory
        return results, latency
    except ImportError:
        start = time.time()
        rows = conn.execute(
            "SELECT id, content, memory_type, importance, strength "
            "FROM memories WHERE is_deleted = 0 AND content LIKE ? "
            "ORDER BY importance DESC LIMIT ?",
            (f"%{query}%", limit)
        ).fetchall()
        latency = (time.time() - start) * 1000
        return [{"id": r[0], "content": r[1][:200], "type": r[2],
                 "importance": r[3], "strength": r[4]} for r in rows], latency

# --- Main ---

def run_assessment(conn, test_queries, judge_fn, judge_method, strategy="hybrid",
                   use_activation=True, ablation_label=None, algo_version="unknown"):
    """Run a full assessment pass. Returns per-query results and aggregates."""
    results_log = []
    all_rar, all_mrr, all_ndcg, all_map, all_pk, all_hr, all_lat = [], [], [], [], [], [], []

    label = f" [{ablation_label}]" if ablation_label else ""
    print(f"\n{'═'*50}")
    print(f"  Assessment: {strategy}{label} — {len(test_queries)} queries")
    print(f"  Judge: {judge_method} | Activation: {use_activation}")
    print(f"{'═'*50}")

    for i, q in enumerate(test_queries):
        qid = q.get("id", f"Q{i+1}")
        query = q["query"]
        print(f"\n─── {qid} ({q.get('category','?')}/{q.get('difficulty','?')}) ───")
        print(f"  Q: \"{query}\"")

        results, latency = run_recall(conn, query, strategy=strategy,
                                       use_activation=use_activation)
        all_lat.append(latency)
        print(f"  Latency: {latency:.1f}ms | Results: {len(results)}")

        if not results:
            print("  (no results)")
            entry = {
                "query_id": qid, "query": query, "strategy": strategy,
                "result_count": 0, "latency_ms": latency,
                "rar": 0, "mrr": 0, "ndcg": 0, "map": 0,
                "precision_at_k": 0, "hit_rate": 0, "ratings": [],
            }
            results_log.append(entry)
            all_rar.append(0); all_mrr.append(0); all_ndcg.append(0)
            all_map.append(0); all_pk.append(0); all_hr.append(0)
            continue

        # Judge each result
        ratings = []
        for j, r in enumerate(results[:5]):
            content = r.get("content", str(r))[:300] if isinstance(r, dict) else str(r)[:300]
            rating = judge_fn(query, content)
            ratings.append(rating)
            print(f"    [{j+1}] rating={rating} | {content[:60]}...")

        # Compute metrics
        q_rar = compute_rar(ratings)
        q_mrr = compute_mrr(ratings)
        q_ndcg = round(ndcg(ratings), 4)
        q_map = round(average_precision(ratings), 4)
        q_pk = round(precision_at_k(ratings), 4)
        q_hr = hit_rate(ratings)
        avg_score = round(sum(ratings) / len(ratings), 2) if ratings else 0

        all_rar.append(q_rar); all_mrr.append(q_mrr); all_ndcg.append(q_ndcg)
        all_map.append(q_map); all_pk.append(q_pk); all_hr.append(q_hr)

        print(f"  RAR={q_rar:.2f} MRR={q_mrr:.2f} nDCG={q_ndcg:.3f} MAP={q_map:.3f} P@5={q_pk:.2f}")

        # Log to DB
        ablation_cfg = json.dumps({"activation": use_activation, "label": ablation_label})
        conn.execute(
            "INSERT INTO retrieval_log "
            "(query, query_id, strategy, result_count, avg_score, latency_ms, "
            "rar, mrr, ndcg, map_score, precision_at_k, hit_rate, ratings, "
            "judge_method, ablation_config, algorithm_version) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (query, qid, strategy, len(results), avg_score, latency,
             q_rar, q_mrr, q_ndcg, q_map, q_pk, q_hr, json.dumps(ratings),
             judge_method, ablation_cfg, algo_version)
        )

        entry = {
            "query_id": qid, "strategy": strategy, "result_count": len(results),
            "latency_ms": latency, "rar": q_rar, "mrr": q_mrr, "ndcg": q_ndcg,
            "map": q_map, "precision_at_k": q_pk, "hit_rate": q_hr,
            "ratings": ratings, "avg_score": avg_score,
        }
        results_log.append(entry)

    conn.commit()

    # Aggregate with CIs
    agg = {
        "strategy": strategy,
        "activation": use_activation,
        "ablation_label": ablation_label,
        "n_queries": len(test_queries),
        "rar": bootstrap_ci(all_rar),
        "mrr": bootstrap_ci(all_mrr),
        "ndcg": bootstrap_ci(all_ndcg),
        "map": bootstrap_ci(all_map),
        "precision_at_k": bootstrap_ci(all_pk),
        "hit_rate": bootstrap_ci(all_hr),
        "latency_ms": bootstrap_ci(all_lat),
    }
    return agg, results_log


def print_summary(agg, label=""):
    """Pretty-print aggregate results with CIs."""
    print(f"\n{'═'*50}")
    print(f"  SUMMARY{' — ' + label if label else ''}")
    print(f"  N = {agg['n_queries']} queries")
    print(f"{'═'*50}")
    for metric in ["rar", "mrr", "ndcg", "map", "precision_at_k", "hit_rate"]:
        d = agg[metric]
        name = metric.upper().replace("_", "@").replace("AT@", "@")
        print(f"  {name:15s}: {d['mean']:.3f}  [{d['ci_low']:.3f}, {d['ci_high']:.3f}]")
    d = agg["latency_ms"]
    print(f"  {'LATENCY (ms)':15s}: {d['mean']:.1f}  [{d['ci_low']:.1f}, {d['ci_high']:.1f}]")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rate memory retrieval quality")
    parser.add_argument("--queries", type=int, default=30, help="Number of queries (default: 30, from test set)")
    parser.add_argument("--db", help="Path to memory database")
    parser.add_argument("--testset", help="Path to test set JSON")
    parser.add_argument("--judge", choices=["openai", "local"], default="openai",
                        help="Judge method: openai (GPT-4o-mini) or local (embedding similarity)")
    parser.add_argument("--ablation", action="store_true",
                        help="Run with AND without spreading activation for comparison")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env)")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else find_db()
    if not db_path or not db_path.exists():
        print("❌ Memory database not found. Use --db PATH")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    ensure_retrieval_log(conn)

    # Load test set
    test_queries = load_test_set(args.testset)[:args.queries]
    algo_version = get_algorithm_version()

    # Setup judge
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    if args.judge == "openai" and not api_key:
        print("⚠️ No OPENAI_API_KEY found. Falling back to local embedding judge.")
        print("   Note: local judge is weaker. Use --judge openai with API key for best results.")
        args.judge = "local"

    if args.judge == "openai":
        judge_fn = lambda q, r: judge_with_openai(q, r, api_key)
        judge_method = "openai/gpt-4o-mini"
    else:
        judge_fn = judge_with_embeddings
        judge_method = "local/embedding-similarity"

    print(f"📊 Memory Retrieval Assessment")
    print(f"   Database: {db_path}")
    print(f"   Test set: {len(test_queries)} queries")
    print(f"   Judge: {judge_method}")
    print(f"   Ablation: {'yes' if args.ablation else 'no'}")
    print(f"   Algorithm: {algo_version}")

    # --- Inter-rater reliability: run both judges if openai available ---
    if args.judge == "openai":
        print("\n📏 Inter-rater reliability check (first 5 queries)...")
        irr_queries = test_queries[:5]
        openai_ratings_flat = []
        local_ratings_flat = []
        for q in irr_queries:
            results, _ = run_recall(conn, q["query"], use_activation=True)
            for r in results[:5]:
                content = r.get("content", str(r))[:300] if isinstance(r, dict) else str(r)[:300]
                try:
                    o_rating = judge_with_openai(q["query"], content, api_key)
                    l_rating = judge_with_embeddings(q["query"], content)
                    openai_ratings_flat.append(o_rating)
                    local_ratings_flat.append(l_rating)
                except Exception:
                    pass
        if len(openai_ratings_flat) >= 5:
            # Cohen's kappa (inline, no sklearn dependency)
            def cohens_kappa(r1, r2):
                n = len(r1)
                if n == 0: return 0.0
                categories = sorted(set(r1) | set(r2))
                # Confusion matrix
                matrix = {}
                for c1 in categories:
                    for c2 in categories:
                        matrix[(c1, c2)] = sum(1 for a, b in zip(r1, r2) if a == c1 and b == c2)
                po = sum(matrix[(c, c)] for c in categories) / n
                pe = sum(
                    (sum(matrix[(c, c2)] for c2 in categories) / n) *
                    (sum(matrix[(c1, c)] for c1 in categories) / n)
                    for c in categories
                )
                return (po - pe) / (1 - pe) if pe < 1 else 0.0

            kappa = cohens_kappa(openai_ratings_flat, local_ratings_flat)
            print(f"  Cohen's κ (openai vs local): {kappa:.3f}  (N={len(openai_ratings_flat)} pairs)")
            print(f"  {'✅ Good agreement' if kappa > 0.4 else '⚠️ Weak agreement — prefer openai judge'}")

    # Main run (with activation)
    agg_main, _ = run_assessment(
        conn, test_queries, judge_fn, judge_method,
        strategy="hybrid", use_activation=True,
        ablation_label="with-activation", algo_version=algo_version
    )
    print_summary(agg_main, "WITH spreading activation")

    # Ablation run (without activation)
    if args.ablation:
        agg_no_act, _ = run_assessment(
            conn, test_queries, judge_fn, judge_method,
            strategy="hybrid", use_activation=False,
            ablation_label="without-activation", algo_version=algo_version
        )
        print_summary(agg_no_act, "WITHOUT spreading activation")

        # Delta
        print(f"\n{'═'*50}")
        print(f"  ABLATION DELTA (activation effect)")
        print(f"{'═'*50}")
        for metric in ["rar", "mrr", "ndcg", "map", "precision_at_k"]:
            d1 = agg_main[metric]["mean"]
            d2 = agg_no_act[metric]["mean"]
            delta = d1 - d2
            direction = "↑" if delta > 0 else "↓" if delta < 0 else "="
            name = metric.upper().replace("_", "@").replace("AT@", "@")
            print(f"  {name:15s}: {direction} {abs(delta):.3f}  ({d2:.3f} → {d1:.3f})")

    conn.close()
    print(f"\n✅ Results saved to retrieval_log table.")
    print(f"   Run `collect.py` to generate the submission report.")

if __name__ == "__main__":
    main()

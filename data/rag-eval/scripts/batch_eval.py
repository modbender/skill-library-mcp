#!/usr/bin/env python3
"""
batch_eval.py — Run Ragas metrics on a JSONL golden dataset

Each line of the input file must be JSON with fields:
    {"question": "...", "answer": "...", "contexts": ["chunk1", ...]}
    Optional: "reference": "ground truth answer" (not used by metrics, kept for records)

Usage:
    python3 scripts/batch_eval.py --input references/sample_dataset.jsonl
    python3 scripts/batch_eval.py --input data.jsonl --output reports/batch.json
    python3 scripts/batch_eval.py --input data.jsonl --metric faithfulness context_precision
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

# ── Import core evaluation logic from run_eval.py ────────────────────────────
# Add the scripts/ directory to sys.path so we can import run_eval
sys.path.insert(0, str(Path(__file__).parent))

from run_eval import (
    _check_deps,
    _die,
    _get_llm,
    _get_embeddings,
    run_eval,
    compute_verdict,
    save_result,
    METRIC_NAMES,
)


# ── Dataset loading ───────────────────────────────────────────────────────────

def load_dataset(path: str) -> list[dict]:
    """
    Load a JSONL file into a list of dicts.
    Skips blank lines and lines starting with '#' (comments).
    """
    records: list[dict] = []
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"[warn] Skipping line {i}: {exc}", file=sys.stderr)
    return records


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate(results: list[dict]) -> dict:
    """
    Compute mean scores and pass/review/fail counts from evaluated samples.

    Args:
        results: List of result dicts (each has "scores" and "verdict" keys).

    Returns:
        Summary dict with mean_scores, mean_overall, verdicts, total_samples.
    """
    totals: dict[str, list[float]] = {}
    verdicts: dict[str, int] = {"PASS": 0, "REVIEW": 0, "FAIL": 0}

    for r in results:
        # Accumulate per-metric scores
        for metric, val in r.get("scores", {}).items():
            if val is not None:
                totals.setdefault(metric, []).append(val)

        # Count verdicts
        v = r.get("verdict", "")
        if v in verdicts:
            verdicts[v] += 1

    mean_scores = {
        metric: round(sum(vals) / len(vals), 4)
        for metric, vals in totals.items()
    }

    overall_vals = [
        r["overall_score"]
        for r in results
        if r.get("overall_score") is not None
    ]
    mean_overall = (
        round(sum(overall_vals) / len(overall_vals), 4)
        if overall_vals
        else 0.0
    )

    return {
        "mean_scores":   mean_scores,
        "mean_overall":  mean_overall,
        "verdicts":      verdicts,
        "total_samples": len(results),
    }


# ── Pretty summary printer ────────────────────────────────────────────────────

def print_summary(summary: dict, out_path: Path) -> None:
    """Print a human-readable batch evaluation summary to stdout."""
    width = 60
    sep = "=" * width
    print(f"\n{sep}")
    print("BATCH EVALUATION SUMMARY")
    print(sep)
    print(f"Total samples:  {summary['total_samples']}")
    print(f"Mean overall:   {summary['mean_overall']}")
    print()
    for metric, score in summary["mean_scores"].items():
        print(f"  {metric:<32} {score}")
    print()
    v = summary["verdicts"]
    print(f"Verdicts:  PASS={v['PASS']}  REVIEW={v['REVIEW']}  FAIL={v['FAIL']}")
    print(sep)
    print(f"Report saved to: {out_path}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-evaluate a JSONL golden dataset with Ragas metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python3 scripts/batch_eval.py \\\n"
            "      --input references/sample_dataset.jsonl \\\n"
            "      --output memory/eval-results/batch.json"
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to JSONL input file (one JSON object per line)",
    )
    parser.add_argument(
        "--output",
        default="",
        help=(
            "Path for the JSON report output "
            "(default: memory/eval-results/batch-YYYY-MM-DD.json)"
        ),
    )
    parser.add_argument(
        "--metric",
        nargs="+",
        default=list(METRIC_NAMES),
        choices=list(METRIC_NAMES),
        metavar="METRIC",
        help=f"Metrics to evaluate (default: all). Choices: {', '.join(METRIC_NAMES)}",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Abort the entire batch if any sample fails evaluation",
    )
    args = parser.parse_args()

    # 1. Verify dependencies
    _check_deps()

    # 2. Resolve output path
    if args.output:
        out_path = Path(args.output)
    else:
        today = datetime.date.today().isoformat()
        out_path = Path("memory/eval-results") / f"batch-{today}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 3. Load dataset
    if not Path(args.input).exists():
        _die(f"Input file not found: {args.input}")

    records = load_dataset(args.input)
    if not records:
        _die(f"No valid records found in {args.input}")

    print(f"Loaded {len(records)} samples from {args.input}", file=sys.stderr)

    # 4. Setup LLM + embeddings once (reused across all samples — saves latency)
    llm        = _get_llm()
    embeddings = _get_embeddings()

    # 5. Evaluate each sample
    results: list[dict] = []
    for i, record in enumerate(records, 1):
        q   = record.get("question", "").strip()
        a   = record.get("answer",   "").strip()
        ctx = record.get("contexts", [])
        ref = record.get("reference", "")  # optional, kept for record-keeping

        # Skip records missing required fields
        if not q or not a or not ctx:
            print(
                f"[warn] Sample {i}: missing question/answer/contexts — skipping",
                file=sys.stderr,
            )
            results.append({"sample_id": i, "skipped": True, "reason": "missing fields"})
            continue

        print(f"Evaluating sample {i}/{len(records)}...", file=sys.stderr, end=" ")

        try:
            scores = run_eval(q, a, ctx, args.metric, llm, embeddings)
            overall, verdict, flags = compute_verdict(scores)

            result_entry = {
                "sample_id":    i,
                "question":     q,
                "scores":       scores,
                "overall_score": overall,
                "verdict":      verdict,
                "flags":        flags,
            }
            if ref:
                result_entry["reference"] = ref

            results.append(result_entry)

            # Also persist individual results in daily JSONL (same as run_eval.py)
            save_result({
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "batch":     str(args.input),
                "input":     {"question": q, "answer": a, "contexts": ctx},
                "output":    {"scores": scores, "overall_score": overall,
                              "verdict": verdict, "flags": flags},
            })

            print(f"{verdict} ({overall})", file=sys.stderr)

        except SystemExit:
            msg = f"Sample {i} failed evaluation."
            if args.stop_on_error:
                print(f"[error] {msg} Aborting batch.", file=sys.stderr)
                sys.exit(1)
            print(f"[warn] {msg} Skipping.", file=sys.stderr)
            results.append({"sample_id": i, "skipped": True, "reason": "eval_error"})

    # 6. Aggregate results
    valid_results = [r for r in results if not r.get("skipped")]
    summary = aggregate(valid_results)

    # 7. Write JSON report
    report = {
        "generated_at":     datetime.datetime.utcnow().isoformat() + "Z",
        "input_file":       str(args.input),
        "metrics_evaluated": args.metric,
        "summary":          summary,
        "samples":          results,
    }
    out_path.write_text(json.dumps(report, indent=2))

    # 8. Print human-readable summary
    print_summary(summary, out_path)


if __name__ == "__main__":
    main()

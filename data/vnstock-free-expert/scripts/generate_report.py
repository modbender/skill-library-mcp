#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from common import ensure_outdir, timestamp


def label_bucket(score: float) -> str:
    if score >= 0.8:
        return "High Conviction"
    if score >= 0.2:
        return "Watchlist"
    return "Caution"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate markdown investment memo from ranking CSV")
    parser.add_argument("--ranking-file", required=True, help="Ranking CSV path")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    parser.add_argument("--top-n", type=int, default=10, help="Top candidates to show")
    args = parser.parse_args()

    if pd is None:
        raise ModuleNotFoundError("Missing dependency: pandas. Install with `pip install pandas`.")

    outdir = ensure_outdir(args.outdir)
    df = pd.read_csv(args.ranking_file)
    if df.empty:
        raise RuntimeError("Ranking file is empty.")

    df["bucket"] = df["total_score"].astype(float).apply(label_bucket)
    top = df.head(args.top_n)

    ts = timestamp()
    md_path = outdir / f"investment_memo_{ts}.md"

    lines = [
        f"# Investment Memo ({ts})",
        "",
        "## Top Ranked Candidates",
        top[["symbol", "total_score", "bucket", "value_score", "quality_score", "momentum_score", "pe", "pb", "roe", "ret_12m_pct"]].to_markdown(index=False),
        "",
        "## Notes",
        "- Scores are relative within the analyzed universe.",
        "- Treat this as a quantitative shortlist, not a final buy/sell recommendation.",
        "- Validate each candidate with recent news, liquidity, and risk events.",
        "",
        "## Risk Checklist",
        "- Data completeness risk (missing metrics, stale financials).",
        "- Macro/event risk (policy, rates, FX, geopolitics).",
        "- Concentration risk (avoid over-weighting one sector).",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    (outdir / "investment_memo_latest.md").write_text(str(md_path), encoding="utf-8")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None

from common import ensure_outdir, timestamp, write_json, zscore


def main() -> None:
    parser = argparse.ArgumentParser(description="Score and rank stocks from market + fundamentals inputs")
    parser.add_argument("--market-file", required=True, help="market_data CSV path")
    parser.add_argument("--fundamentals-file", required=True, help="fundamentals CSV path")
    parser.add_argument("--outdir", default="./outputs", help="Output directory")
    args = parser.parse_args()

    if pd is None:
        raise ModuleNotFoundError("Missing dependency: pandas. Install with `pip install pandas`.")

    outdir = ensure_outdir(args.outdir)
    mdf = pd.read_csv(args.market_file)
    fdf = pd.read_csv(args.fundamentals_file)

    df = mdf.merge(fdf, on=["symbol", "source"], how="inner")
    if df.empty:
        raise RuntimeError("Merged dataset is empty. Check input files and symbols.")

    for col in ["pe", "pb", "roe", "debt_equity", "ret_6m_pct", "ret_12m_pct"]:
        if col not in df.columns:
            df[col] = pd.NA

    df["value_score"] = (
        zscore(df["pe"].fillna(df["pe"].median()), reverse=True)
        + zscore(df["pb"].fillna(df["pb"].median()), reverse=True)
    ) / 2

    df["quality_score"] = (
        zscore(df["roe"].fillna(df["roe"].median()), reverse=False)
        + zscore(df["debt_equity"].fillna(df["debt_equity"].median()), reverse=True)
    ) / 2

    df["momentum_score"] = (
        zscore(df["ret_6m_pct"].fillna(df["ret_6m_pct"].median()), reverse=False)
        + zscore(df["ret_12m_pct"].fillna(df["ret_12m_pct"].median()), reverse=False)
    ) / 2

    df["total_score"] = 0.35 * df["value_score"] + 0.35 * df["quality_score"] + 0.30 * df["momentum_score"]
    df = df.sort_values("total_score", ascending=False).reset_index(drop=True)

    ts = timestamp()
    csv_path = outdir / f"ranking_{ts}.csv"
    json_path = outdir / f"ranking_{ts}.json"

    df.to_csv(csv_path, index=False)
    write_json(
        json_path,
        {
            "generated_at": ts,
            "rows": df.to_dict(orient="records"),
        },
    )

    (outdir / "ranking_latest.csv").write_text(str(csv_path), encoding="utf-8")
    (outdir / "ranking_latest.json").write_text(str(json_path), encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate an HTML data report with KPI cards and charts.

Usage:
  python scripts/generate_report.py --input data.csv --output report.html --title "Sales Report"
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _validate_path(path_str: str, *, must_exist: bool = False) -> Path:
    base = Path.cwd().resolve()
    candidate = Path(path_str)
    resolved = (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()

    # Keep all file operations inside the current working directory tree.
    if not str(resolved).startswith(str(base) + "/") and resolved != base:
        raise ValueError("Path must stay within the current working directory")

    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")

    return resolved


def load_data(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".json":
        data = json.loads(path.read_text())
        return pd.DataFrame(data)
    raise ValueError(f"Unsupported input type: {suffix}")


def pick_amount_column(df: pd.DataFrame) -> str:
    for col in ["revenue", "amount", "sales", "value"]:
        if col in df.columns:
            return col
    raise ValueError("No numeric amount column found. Expected one of: revenue, amount, sales, value")


def compute_metrics(df: pd.DataFrame, amount_col: str) -> dict:
    series = pd.to_numeric(df[amount_col], errors="coerce").dropna()
    growth = series.pct_change().mean() if len(series) > 1 else 0.0
    return {
        "total": float(series.sum()),
        "average": float(series.mean()) if len(series) else 0.0,
        "count": int(len(series)),
        "growth": float(growth) if pd.notna(growth) else 0.0,
    }


def build_charts(df: pd.DataFrame, amount_col: str, chart_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    pd.to_numeric(df[amount_col], errors="coerce").dropna().plot(
        kind="line", ax=axes[0], title=f"{amount_col.title()} Trend"
    )
    axes[0].set_xlabel("Index")
    axes[0].set_ylabel(amount_col.title())

    if "product" in df.columns:
        grouped = (
            df.groupby("product")[amount_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        grouped.plot(kind="bar", ax=axes[1], title=f"Top Products by {amount_col.title()}")
        axes[1].set_ylabel(amount_col.title())
    else:
        pd.to_numeric(df[amount_col], errors="coerce").dropna().head(10).plot(
            kind="bar", ax=axes[1], title=f"Top Values ({amount_col.title()})"
        )
        axes[1].set_ylabel(amount_col.title())

    plt.tight_layout()
    fig.savefig(chart_path)
    plt.close(fig)


def build_html(title: str, metrics: dict, chart_file_name: str) -> str:
    safe_title = html.escape(title, quote=True)
    safe_chart_file_name = html.escape(chart_file_name, quote=True)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>{safe_title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; }}
    .card {{ background: #f5f7fb; border-radius: 10px; padding: 14px; }}
    .metric {{ font-size: 1.5rem; font-weight: 700; color: #2563eb; }}
    .muted {{ color: #666; }}
    img {{ max-width: 100%; margin-top: 20px; border: 1px solid #ddd; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>{safe_title}</h1>
  <p class=\"muted\">Auto-generated report with KPI summary and charts.</p>
  <div class=\"kpis\">
    <div class=\"card\"><div class=\"metric\">${metrics['total']:,.2f}</div><div>Total</div></div>
    <div class=\"card\"><div class=\"metric\">${metrics['average']:,.2f}</div><div>Average</div></div>
    <div class=\"card\"><div class=\"metric\">{metrics['count']:,}</div><div>Records</div></div>
    <div class=\"card\"><div class=\"metric\">{metrics['growth']:.1%}</div><div>Avg Growth</div></div>
  </div>
  <h2>Charts</h2>
  <img src=\"{safe_chart_file_name}\" alt=\"charts\" />
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML report from CSV/Excel/JSON")
    parser.add_argument("--input", required=True, help="Path to CSV/XLSX/JSON input")
    parser.add_argument("--output", required=True, help="Path to output HTML report")
    parser.add_argument("--title", default="Data Report", help="Report title")
    args = parser.parse_args()

    in_path = _validate_path(args.input, must_exist=True)
    out_path = _validate_path(args.output, must_exist=False)

    if out_path.suffix.lower() != ".html":
        raise ValueError("Output file must use .html extension")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = load_data(in_path)
    amount_col = pick_amount_column(df)
    metrics = compute_metrics(df, amount_col)

    chart_path = out_path.with_name(out_path.stem + "_charts.png")
    build_charts(df, amount_col, chart_path)

    html = build_html(args.title, metrics, chart_path.name)
    out_path.write_text(html, encoding="utf-8")

    print(f"Report written: {out_path}")
    print(f"Charts written: {chart_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compute robust used-market price stats from a CSV file.

Usage:
  python3 scripts/price_stats.py listings.csv

Required column:
  - price
Optional columns (ignored in stats but kept for context):
  - model, platform, condition, date, notes
"""

from __future__ import annotations

import csv
import math
import statistics
import sys
from pathlib import Path


def parse_price(value: str) -> float | None:
    if value is None:
        return None
    cleaned = (
        value.strip()
        .replace("$", "")
        .replace(",", "")
        .replace("USD", "")
        .replace("usd", "")
    )
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        raise ValueError("empty values")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = (len(sorted_vals) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/price_stats.py <listings.csv>")
        return 2

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: file not found: {csv_path}")
        return 2

    prices: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "price" not in {x.strip().lower() for x in reader.fieldnames}:
            print("Error: CSV must include a 'price' column")
            return 2

        # Map any case variant of price to the exact key in row dict.
        price_key = next(k for k in reader.fieldnames if k.strip().lower() == "price")

        for row in reader:
            p = parse_price(row.get(price_key, ""))
            if p is not None and p > 0:
                prices.append(p)

    if len(prices) < 3:
        print("Need at least 3 valid price rows for robust stats.")
        return 1

    vals = sorted(prices)
    n = len(vals)
    q1 = percentile(vals, 0.25)
    med = percentile(vals, 0.50)
    q3 = percentile(vals, 0.75)
    iqr = q3 - q1
    mean = statistics.mean(vals)

    strong_buy = q1 * 0.95
    walk_away = q3 * 1.10

    print("Used-Market Price Summary")
    print("-------------------------")
    print(f"Samples: {n}")
    print(f"Min / Max: ${vals[0]:.2f} / ${vals[-1]:.2f}")
    print(f"Mean: ${mean:.2f}")
    print(f"Median: ${med:.2f}")
    print(f"Q1 / Q3: ${q1:.2f} / ${q3:.2f}")
    print(f"IQR: ${iqr:.2f}")
    print()
    print("Decision Bands")
    print("--------------")
    print(f"Fair range: ${q1:.2f} - ${q3:.2f}")
    print(f"Strong-buy threshold: <= ${strong_buy:.2f}")
    print(f"Walk-away threshold: >= ${walk_away:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

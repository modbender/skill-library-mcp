#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from dataclasses import dataclass

@dataclass
class Metrics:
    roe: float | None = None          # e.g. 0.18 means 18%
    debt_ratio: float | None = None   # total debt / total assets (rough)
    fcf_to_net_income: float | None = None  # FCF / Net Income
    moat: str | None = None           # "strong"/"medium"/"weak"

def score(m: Metrics) -> tuple[str, list[str]]:
    reasons = []
    points = 0

    # ROE
    if m.roe is not None:
        if m.roe >= 0.15:
            points += 2
            reasons.append(f"ROE {m.roe:.0%} ≥ 15%")
        elif m.roe >= 0.10:
            points += 1
            reasons.append(f"ROE {m.roe:.0%} between 10%-15%")
        else:
            reasons.append(f"ROE {m.roe:.0%} < 10%")
    else:
        reasons.append("ROE: (missing)")

    # Debt ratio
    if m.debt_ratio is not None:
        if m.debt_ratio < 0.50:
            points += 2
            reasons.append(f"Debt ratio {m.debt_ratio:.0%} < 50%")
        elif m.debt_ratio < 0.70:
            points += 1
            reasons.append(f"Debt ratio {m.debt_ratio:.0%} between 50%-70%")
        else:
            reasons.append(f"Debt ratio {m.debt_ratio:.0%} ≥ 70%")
    else:
        reasons.append("Debt ratio: (missing)")

    # FCF conversion
    if m.fcf_to_net_income is not None:
        if m.fcf_to_net_income >= 0.80:
            points += 2
            reasons.append(f"FCF/NI {m.fcf_to_net_income:.0%} ≥ 80%")
        elif m.fcf_to_net_income >= 0.50:
            points += 1
            reasons.append(f"FCF/NI {m.fcf_to_net_income:.0%} between 50%-80%")
        else:
            reasons.append(f"FCF/NI {m.fcf_to_net_income:.0%} < 50%")
    else:
        reasons.append("FCF/NI: (missing)")

    # Moat
    if m.moat:
        moat = m.moat.lower()
        if moat in ["strong", "wide"]:
            points += 2
            reasons.append("Moat: strong")
        elif moat in ["medium", "narrow"]:
            points += 1
            reasons.append("Moat: medium")
        else:
            reasons.append("Moat: weak")
    else:
        reasons.append("Moat: (missing)")

    if points >= 7:
        rating = "A"
    elif points >= 5:
        rating = "B"
    elif points >= 3:
        rating = "C"
    else:
        rating = "D"

    return rating, reasons

def main():
    """
    Expected stdin (optional):
    {
      "ticker": "NVDA",
      "metrics": {"roe":0.18,"debt_ratio":0.40,"fcf_to_net_income":0.85,"moat":"strong"}
    }
    If stdin empty, falls back to args and placeholder metrics.
    """
    raw = None
    try:
        raw = sys.stdin.read().strip()
    except Exception:
        raw = None

    ticker = None
    metrics = Metrics()

    if raw:
        try:
            obj = json.loads(raw)
            ticker = obj.get("ticker")
            m = obj.get("metrics") or {}
            metrics = Metrics(
                roe=m.get("roe"),
                debt_ratio=m.get("debt_ratio"),
                fcf_to_net_income=m.get("fcf_to_net_income"),
                moat=m.get("moat"),
            )
        except Exception:
            # ignore parse errors; fallback below
            pass

    if not ticker:
        ticker = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"

    rating, reasons = score(metrics)
    out = {
        "ticker": ticker,
        "rating": rating,
        "reasons": reasons,
        "note": "If metrics are missing, pass them via stdin JSON to get a real rating."
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

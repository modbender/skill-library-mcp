#!/usr/bin/env python3
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


def _safe_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _weighted_average(values):
    numerator = 0.0
    denominator = 0.0
    for value, weight in values:
        if value is None or weight is None or weight <= 0:
            continue
        numerator += value * weight
        denominator += weight
    if denominator == 0:
        return None
    return numerator / denominator


def _estimate_weight(subject_sqft, comp):
    distance = _safe_float(comp.get("distance_miles"))
    comp_sqft = _safe_float(comp.get("sqft"))
    days = _safe_int(comp.get("days_on_market"))

    distance_factor = 1.0 / (1.0 + (distance if distance is not None else 1.5))

    if subject_sqft and comp_sqft and subject_sqft > 0:
        sqft_delta_ratio = abs(subject_sqft - comp_sqft) / subject_sqft
        similarity_factor = 1.0 / (1.0 + sqft_delta_ratio * 2.0)
    else:
        similarity_factor = 0.75

    if days is None:
        recency_factor = 0.8
    else:
        recency_factor = 1.0 / (1.0 + max(days, 0) / 90.0)

    return distance_factor * similarity_factor * recency_factor


def _compute_adjusted_price(subject, comp, median_ppsf):
    comp_price = _safe_float(comp.get("price"))
    if comp_price is None:
        return None, {}

    subject_beds = _safe_float(subject.get("beds"))
    comp_beds = _safe_float(comp.get("beds"))
    subject_baths = _safe_float(subject.get("baths"))
    comp_baths = _safe_float(comp.get("baths"))
    subject_year = _safe_int(subject.get("year_built"))
    comp_year = _safe_int(comp.get("year_built"))
    subject_sqft = _safe_float(subject.get("sqft"))
    comp_sqft = _safe_float(comp.get("sqft"))

    adjustments = {}

    if subject_beds is not None and comp_beds is not None:
        bed_delta = subject_beds - comp_beds
        adjustments["beds"] = bed_delta * 10000.0
    else:
        adjustments["beds"] = 0.0

    if subject_baths is not None and comp_baths is not None:
        bath_delta = subject_baths - comp_baths
        adjustments["baths"] = bath_delta * 7500.0
    else:
        adjustments["baths"] = 0.0

    if subject_year is not None and comp_year is not None:
        year_delta = subject_year - comp_year
        adjustments["year_built"] = year_delta * 1200.0
    else:
        adjustments["year_built"] = 0.0

    if subject_sqft is not None and comp_sqft is not None and median_ppsf is not None:
        sqft_delta = subject_sqft - comp_sqft
        adjustments["sqft"] = sqft_delta * (median_ppsf * 0.45)
    else:
        adjustments["sqft"] = 0.0

    total_adjustment = sum(adjustments.values())
    return comp_price + total_adjustment, adjustments


def _fmt_currency(value):
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def _fmt_number(value):
    if value is None:
        return "N/A"
    if abs(value - int(value)) < 1e-9:
        return str(int(value))
    return f"{value:.2f}"


def _build_report(subject, rows, estimated_central, low, high):
    lines = []
    lines.append("# Comparative Market Analysis Report")
    lines.append("")
    lines.append(f"- Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- Subject: {subject.get('address', 'Unknown address')}")
    lines.append("")
    lines.append("## Subject Property")
    lines.append("")
    lines.append(f"- Beds: {_fmt_number(_safe_float(subject.get('beds')))}")
    lines.append(f"- Baths: {_fmt_number(_safe_float(subject.get('baths')))}")
    lines.append(f"- Sqft: {_fmt_number(_safe_float(subject.get('sqft')))}")
    lines.append(f"- Year Built: {_fmt_number(_safe_int(subject.get('year_built')))}")
    lines.append("")
    lines.append("## Value Estimate")
    lines.append("")
    lines.append(f"- Central Estimate: {_fmt_currency(estimated_central)}")
    lines.append(f"- Suggested Range: {_fmt_currency(low)} to {_fmt_currency(high)}")
    lines.append("")
    lines.append("## Comparable Summary")
    lines.append("")
    lines.append("| Address | Price | Adj. Price | PPSF | Distance (mi) | DOM |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        lines.append(
            "| {address} | {price} | {adjusted} | {ppsf} | {distance} | {dom} |".format(
                address=row.get("address", "N/A"),
                price=_fmt_currency(row.get("price")),
                adjusted=_fmt_currency(row.get("adjusted_price")),
                ppsf=_fmt_currency(row.get("ppsf")),
                distance=_fmt_number(_safe_float(row.get("distance_miles"))),
                dom=_fmt_number(_safe_int(row.get("days_on_market"))),
            )
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This CMA is an estimate based on selected comps and deterministic adjustments.")
    lines.append("- Output is not a licensed appraisal.")
    lines.append("- Review local market nuance, condition differences, and concessions before final pricing.")
    lines.append("")
    return "\n".join(lines)


def _build_interactive_html(subject, rows, low, high, central):
    payload = {"subject": subject, "comps": rows, "estimate": {"low": low, "high": high, "central": central}}
    payload_json = json.dumps(payload, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CMA Interactive View</title>
  <style>
    :root {{
      --bg: #f7f7f2;
      --ink: #1f2933;
      --accent: #2a6f97;
      --accent-2: #f4a261;
      --card: #ffffff;
    }}
    body {{ margin: 0; font-family: "Avenir Next", "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 24px; background: linear-gradient(120deg, #dfe9f3, #fef6e4); }}
    h1 {{ margin: 0 0 8px 0; }}
    .container {{ padding: 20px; max-width: 1100px; margin: 0 auto; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }}
    .card {{ background: var(--card); border-radius: 12px; padding: 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.07); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 10px; overflow: hidden; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #e7e7e7; text-align: left; }}
    th {{ background: #f0f4f8; }}
    .bar {{ height: 10px; background: #e7eef4; border-radius: 999px; overflow: hidden; }}
    .fill {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
  </style>
</head>
<body>
  <header>
    <h1>CMA Interactive View</h1>
    <div id="subject"></div>
  </header>
  <main class="container">
    <section class="cards">
      <div class="card"><strong>Low</strong><div id="low"></div></div>
      <div class="card"><strong>Central</strong><div id="central"></div></div>
      <div class="card"><strong>High</strong><div id="high"></div></div>
    </section>
    <section class="card" style="margin-bottom: 16px;">
      <strong>Estimated Position in Range</strong>
      <div class="bar"><div id="position" class="fill"></div></div>
    </section>
    <table>
      <thead>
        <tr>
          <th>Address</th>
          <th>Price</th>
          <th>Adjusted</th>
          <th>PPSF</th>
          <th>Distance</th>
          <th>DOM</th>
        </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
  </main>
  <script>
    const data = {payload_json};
    const money = n => Number.isFinite(n) ? new Intl.NumberFormat("en-US", {{style: "currency", currency: "USD", maximumFractionDigits: 0}}).format(n) : "N/A";
    document.getElementById("subject").textContent = data.subject.address || "Unknown subject";
    document.getElementById("low").textContent = money(data.estimate.low);
    document.getElementById("central").textContent = money(data.estimate.central);
    document.getElementById("high").textContent = money(data.estimate.high);
    const spread = Math.max((data.estimate.high || 0) - (data.estimate.low || 0), 1);
    const pct = ((data.estimate.central - data.estimate.low) / spread) * 100;
    document.getElementById("position").style.width = Math.min(Math.max(pct, 0), 100) + "%";
    const tbody = document.getElementById("rows");
    for (const comp of data.comps) {{
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${{comp.address || "N/A"}}</td>
        <td>${{money(comp.price)}}</td>
        <td>${{money(comp.adjusted_price)}}</td>
        <td>${{money(comp.ppsf)}}</td>
        <td>${{comp.distance_miles ?? "N/A"}}</td>
        <td>${{comp.days_on_market ?? "N/A"}}</td>`;
      tbody.appendChild(tr);
    }}
  </script>
</body>
</html>
"""


def _build_gemini_prompt():
    return """Use this prompt in Gemini Canvas or Google AI Studio with cma_data.json attached.

You are building a polished, client-facing Comparative Market Analysis web app.
Requirements:
1. Read cma_data.json and render a responsive single-page app.
2. Include a subject summary card and a valuation range card (low/central/high).
3. Show comparables in a sortable/filterable table (price, adjusted price, ppsf, distance, DOM).
4. Add a range visualization and confidence explanation derived from available fields.
5. If lat/lng exists per comp, include map-ready data wiring and graceful fallback when missing.
6. Add plain-language assumptions and disclaimer that this is not a formal appraisal.
7. Keep output suitable for sharing via a hosted/static deployment.

Return:
- Full HTML/CSS/JS in one file and a short deployment note.
"""


def main():
    parser = argparse.ArgumentParser(description="Build CMA outputs from subject and comparable listing JSON files.")
    parser.add_argument("--subject", required=True, help="Path to subject JSON object.")
    parser.add_argument("--comps", required=True, help="Path to comparables JSON array.")
    parser.add_argument("--output-dir", default="cma-output", help="Directory to write outputs.")
    parser.add_argument("--range-padding", type=float, default=0.05, help="Percent padding around central estimate.")
    args = parser.parse_args()

    subject = json.loads(Path(args.subject).read_text(encoding="utf-8"))
    comps = json.loads(Path(args.comps).read_text(encoding="utf-8"))
    if not isinstance(comps, list):
        raise ValueError("Comps JSON must be an array.")
    if not comps:
        raise ValueError("Comps array cannot be empty.")

    subject_sqft = _safe_float(subject.get("sqft"))
    rows = []
    ppsf_values = []
    weighted_ppsf_inputs = []

    for comp in comps:
        price = _safe_float(comp.get("price"))
        sqft = _safe_float(comp.get("sqft"))
        ppsf = price / sqft if (price is not None and sqft and sqft > 0) else None
        weight = _estimate_weight(subject_sqft, comp)
        if ppsf is not None:
            ppsf_values.append(ppsf)
            weighted_ppsf_inputs.append((ppsf, weight))
        rows.append({**comp, "price": price, "sqft": sqft, "ppsf": ppsf, "weight": weight})

    if not ppsf_values:
        raise ValueError("At least one comp must include both price and sqft.")

    median_ppsf = median(ppsf_values)
    weighted_ppsf = _weighted_average(weighted_ppsf_inputs)

    adjusted_prices = []
    for row in rows:
        adjusted_price, adjustments = _compute_adjusted_price(subject, row, median_ppsf)
        row["adjusted_price"] = adjusted_price
        row["adjustments"] = adjustments
        if adjusted_price is not None:
            adjusted_prices.append(adjusted_price)

    if adjusted_prices:
        estimate_central = median(adjusted_prices)
    else:
        if subject_sqft is None or weighted_ppsf is None:
            raise ValueError("Unable to estimate central value from provided data.")
        estimate_central = subject_sqft * weighted_ppsf

    padding = max(0.0, args.range_padding)
    low = estimate_central * (1.0 - padding)
    high = estimate_central * (1.0 + padding)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = _build_report(subject, rows, estimate_central, low, high)
    (output_dir / "cma_report.md").write_text(report, encoding="utf-8")

    data_payload = {
        "subject": subject,
        "comps": rows,
        "metrics": {
            "median_ppsf": median_ppsf,
            "weighted_ppsf": weighted_ppsf,
            "central_estimate": estimate_central,
            "low_estimate": low,
            "high_estimate": high,
            "range_padding": padding,
        },
    }
    (output_dir / "cma_data.json").write_text(json.dumps(data_payload, indent=2), encoding="utf-8")
    (output_dir / "interactive_local.html").write_text(
        _build_interactive_html(subject, rows, low, high, estimate_central), encoding="utf-8"
    )
    (output_dir / "gemini_canvas_prompt.md").write_text(_build_gemini_prompt(), encoding="utf-8")

    print(f"Wrote outputs to: {output_dir}")


if __name__ == "__main__":
    main()

---
name: report-generator
description: Generate professional data reports (HTML/PDF-ready) with KPI summaries, charts, tables, executive insights, and recommendations from CSV, Excel, or JSON data. Use when asked to create dashboards, monthly/weekly KPI reports, sales/performance summaries, executive briefs, or analytical reports with visualizations.
---

# Report Generator

## Overview
Create clean, decision-ready reports from structured data files or user-described datasets. Prioritize business readability: clear KPIs, trend visuals, concise narrative insights, and practical recommendations.

## Workflow
1. Validate input data source (CSV/XLSX/JSON or user-provided schema description).
2. Identify report goal and audience (executive summary vs operational detail).
3. Compute KPIs and trends relevant to the goal.
4. Generate visuals (bar + line at minimum; add breakdown charts as needed).
5. Produce formatted report sections in this order:
   - Executive summary
   - KPI dashboard
   - Detailed analysis
   - Charts/tables
   - Recommendations
6. Sanity-check numbers and narrative consistency before returning deliverable.

## Report Blueprint
Use this canonical structure unless user asks otherwise:

```python
report = {
    "title": "Monthly Sales Report",
    "period": "January 2024",
    "sections": [
        "executive_summary",
        "kpi_dashboard",
        "detailed_analysis",
        "charts",
        "recommendations",
    ],
}
```

## KPI Defaults
Use these by default when fields exist; adapt names via user mapping when needed:
- Revenue total / average
- Order count and average order value
- Growth rate (period-over-period)
- Top category/product/customer by contribution
- Trend direction (up/down/flat)

## Output Rules
- Keep narrative concise and business-facing.
- Highlight 3-5 key findings max in executive summary.
- Flag missing/dirty data explicitly.
- Never claim causality without supporting data.

## Implementation Resources
- Use `scripts/generate_report.py` for deterministic report generation.
- Use `references/report-templates.md` for section templates and phrasing patterns.
- Use `references/chart-guidelines.md` for chart selection and formatting standards.

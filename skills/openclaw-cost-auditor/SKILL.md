---
name: openclaw-cost-auditor
description: Parse logs, query API metrics, forecast bills, optimize spend with
  reports & alerts.
---


# OpenClaw Cost Auditor v1.0.0

## 🎯 Purpose
- Daily/weekly cost reports
- Top models/users by tokens
- Cost per query forecasts
- Optimization recs (quantize, prune)

## 🚀 Quick Start
```
!openclaw-cost-auditor --period last7d --format pdf
```

## Files
- `scripts/audit.py`: Log parser & calculator
- `templates/report.md`: Cost dashboard template

## Integrations
OpenClaw logs, Grok/xAI API, custom providers.

---
name: 配置优化 Config Optimization
slug: config-optimization
description: Optimize aggressive A-share screener settings and output optimized config/report artifacts into data/. Use when strategy configuration needs recurring tuning before daily stock recommendation.
---

# Config Optimization Subskill

Run:

```bash
python3 subskills/config-optimization/optimize_from_aggressive.py --analysis-period "2026-02-01 to 2026-02-12"
```

Optional: apply optimized full config to runtime config.

```bash
python3 subskills/config-optimization/optimize_from_aggressive.py --apply-to-config
```

Outputs (all under `data/`):
- `config_aggressive_optimized.json`
- `config_aggressive_optimized_full.json`
- `config_analysis_report.latest.json`
- `config_summary.latest.md`

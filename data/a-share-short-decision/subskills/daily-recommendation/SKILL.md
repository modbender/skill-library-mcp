---
name: 每日推荐 Daily Recommendation
slug: daily-recommendation
description: Produce daily short-term A-share recommendation artifacts using current strategy config, and store outputs in data/. Use after optimization or on normal daily scan.
---

# Daily Recommendation Subskill

Run:

```bash
python3 subskills/daily-recommendation/generate_daily_recommendation.py --date 2026-02-14
```

Output files under `data/`:
- `today_recommendation_<date>.json`
- `today_recommendation.latest.json`

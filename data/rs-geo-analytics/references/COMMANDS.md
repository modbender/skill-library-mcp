# RS-Skill Commands — Quick Reference

```
node rankscale-skill.js [flag]
```

---

## Setup & Discovery

```
(no flags)              Run full GEO Overview report
--help                  Show help and onboarding info
--discover-brands       List all brands linked to your API key
```

---

## Analytics Features

```
--engine-profile        Engine Strength Profile
                        Visibility score per AI engine (ChatGPT, Perplexity, etc.)
                        Shows top-3 (✦) and bottom-3 (▼) engines

--gap-analysis          Content Gap Analysis
                        Topics and queries with low or zero visibility
                        Engine gaps vs average + low-visibility search terms

--reputation            Reputation Score
                        Sentiment-based brand health score (0–100)
                        Shows positive signals, risk areas, trend direction

--engine-movers         Engine Gainers & Losers
                        Top movers vs prior period, per engine
                        Use after content pushes or PR campaigns

--sentiment-alerts      Sentiment Shift Alert
                        Trend detection + risk level for sentiment changes
                        Flags trigger keywords driving the shift
```

---

## Citation Intelligence

```
--citations             Citation overview (sources + summary)
--citations authority   Top citation sources ranked by authority
--citations gaps        Citation gaps vs competitors
--citations engines     Per-engine citation breakdown
--citations correlation Citation↔Visibility correlation
--citations full        All citation sections + PR target suggestions
```

---

## GEO Insight Rules

The default report fires up to 5 rules (CRIT → WARN → INFO):

```
R1 [WARN] Citation rate < 40%          → Improve citation velocity
R2 [CRIT] Citation rate < 20%          → Immediate content blitz
R3 [CRIT] Negative sentiment > 25%     → Reputation risk response
R4 [CRIT] GEO score < 40               → Comprehensive GEO audit
R5 [WARN] GEO score 40–64              → Targeted content improvement
R6 [WARN] Score change < -5            → Investigate declining trend
R7 [INFO] Change ≥+3 AND positive>55%  → Maintain momentum
```

Note: R1 is suppressed when R2 fires (deduplication).

---

## Tips

- **Multiple brands:** Override brand ID inline:
  ```
  RANKSCALE_BRAND_ID=xxx node rankscale-skill.js --engine-profile
  ```

- **Auto brand extraction:** If your API key has the format `rk_<hash>_<brandId>`,
  the Brand ID is extracted automatically — no `RANKSCALE_BRAND_ID` needed.

- **First run:** Start with `--discover-brands` to confirm your API key works.

- **Terminal width:** Output respects terminal width. Resize for better bar charts.

- **Expected response time:** ~2–4s with live API. Up to 14s if DNS is slow (retry exhaustion).

---

## Support

Questions? We are happy to support.

📧 `support@rankscale.ai`   🌐 [rankscale.ai](https://rankscale.ai/dashboard/signup)

Full feature guide → [FEATURES.md](FEATURES.md)
Real usage examples → [EXAMPLES.md](EXAMPLES.md)
Troubleshooting → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Main docs → [SKILL.md](../SKILL.md)

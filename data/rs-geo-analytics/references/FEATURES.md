# RS-Skill Features Guide

> Detailed reference for each RS-Skill feature. For quick command lookup, see [COMMANDS.md](COMMANDS.md).
> For real usage walkthroughs, see [EXAMPLES.md](EXAMPLES.md).

---

## 1. GEO Overview (default)

**What it does:**
Runs a full generative engine optimization report for your brand. Shows all primary metrics — GEO Score, Citation Rate, Sentiment, and top search terms driving visibility.

**When to use:**
Your daily or weekly brand health check. Start here before diving into specific features.

**CLI command:**
```
node rankscale-skill.js
```

**Sample output (healthy brand — GEO score 72):**
```
=======================================================
                 RANKSCALE GEO REPORT
             Brand: AcmeCorp | 2026-02-19
=======================================================
  GEO SCORE:      72 / 100   [+5 vs last week]
  CITATION RATE: 55.5%     [Industry avg: 45%]
  SENTIMENT:     Pos 61% | Neu 29% | Neg 10%
-------------------------------------------------------
  TOP AI SEARCH TERMS
  1. "best crm software"                  (500 mentions)
  2. "crm comparison"                     (300 mentions)
  3. "crm pricing"                        (200 mentions)
-------------------------------------------------------
  GEO INSIGHTS  [1 action]
  [INFO] Strong positive momentum detected.
  Action: Maintain current content cadence.
  Double down on formats producing citations.
  Consider expanding to adjacent topics.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/[your-brand]
=======================================================
```

**Sample output (critical brand — low score, network fallback):**
```
=======================================================
                 RANKSCALE GEO REPORT
            Brand: Your Brand | 2026-02-19
=======================================================
  GEO SCORE:       0 / 100   [0 vs last week]
  CITATION RATE: 0%
  SENTIMENT:     Pos 0% | Neu 0% | Neg 0%
-------------------------------------------------------
  GEO INSIGHTS  [2 actions]
  [CRIT] Citation rate critically low (<20%).
  Action: Immediate content blitz needed.
  Submit brand to 5+ AI-indexed directories.
  Build backlinks from authoritative sources.

  [CRIT] GEO score critically low (<40).
  Action: Comprehensive GEO audit needed.
  Add schema markup, improve content depth,
  and increase citation velocity.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/[your-brand]
=======================================================
```

**GEO Insight Rules (R1–R7):**

| Rule | Condition | Severity | Action |
|------|-----------|----------|--------|
| R1 | Citation rate < 40% | WARN | Improve citation velocity |
| R2 | Citation rate < 20% | CRIT | Immediate content blitz |
| R3 | Negative sentiment > 25% | CRIT | Reputation risk response |
| R4 | GEO score < 40 | CRIT | Comprehensive GEO audit |
| R5 | GEO score 40–64 | WARN | Targeted content improvement |
| R6 | Score change < -5 | WARN | Investigate declining trend |
| R7 | Score change ≥+3 AND positive > 55% | INFO | Maintain momentum |

Rules are sorted CRIT → WARN → INFO. Maximum 5 rules shown. R1 is suppressed when R2 fires.

**Key insights:**
- **GEO Score** reflects how prominently AI engines surface your brand.
- **Citation Rate** shows what percentage of relevant queries include a citation to your brand.
- **Sentiment** shows the emotional tone of AI engine responses mentioning your brand.
- **Search terms breakdown** shows which queries are driving (or missing) visibility.

---

## 2. Engine Strength Profile (`--engine-profile`)

**What it does:**
Breaks down your brand's visibility across each individual AI engine — ChatGPT, Perplexity, Gemini, Claude, DeepSeek, Mistral, Grok, Google AI Overview, and others. Shows a visual bar chart per engine with top-3 and bottom-3 highlighted.

**When to use:**
Use this when you want to know _where_ you're winning and _where_ you're invisible. Helps prioritize engine-specific content strategies.

**CLI command:**
```
node rankscale-skill.js --engine-profile
```

**Sample output (live API — ROA-40 test run, 2026-02-26):**
```
-------------------------------------------------------
                ENGINE STRENGTH PROFILE
-------------------------------------------------------
  Engine       Visibility            Score
  Average      ──────────────────     69.3
-------------------------------------------------------
  mistral_larg ██████████████████████ 83.2 ✦
  deepseek_cha █████████████████████  79.5 ✦
  chatgpt_gui  ████████████████████   77.5 ✦
  perplexity_s ████████████████████   73.9
  google_ai_ov ███████████████████      73
  google_ai_mo ███████████████████    70.8
  google_gemin ██████████████████     66.2
  openai_gpt-5 ████████████████       60.1 ▼
  anthropic_cl ███████████████        57.7 ▼
  perplexity_g █████████████          50.7 ▼
-------------------------------------------------------
  ✦ Top-3 engines  ▼ Bottom-3 engines
```

**Interpreting scores:**
- **>70:** Engine actively surfaces your brand — maintain content freshness.
- **40–70:** Room to grow — focus on query coverage for that engine's specialties.
- **<40:** Low visibility — investigate whether you have citations indexed by that engine.

**Key insights:**
- Use this before writing content: know which engine you're optimizing for.
- Large disparity between engines (>30 pts) signals an engine-specific content gap.
- Top-3 (✦) show where you should double down; Bottom-3 (▼) show where to catch up.

---

## 3. Content Gap Analysis (`--gap-analysis`)

**What it does:**
Identifies topics, questions, and queries where your brand has low or zero visibility. Surfaces engine-level gaps vs average and low-visibility search terms with visual progress bars.

**When to use:**
Use this before planning a content calendar or GEO sprint. Also useful when you notice engine disparity in the Engine Strength Profile.

**CLI command:**
```
node rankscale-skill.js --gap-analysis
```

**Sample output (from live test data):**
```
-------------------------------------------------------
                 CONTENT GAP ANALYSIS
-------------------------------------------------------
  ENGINE GAPS (vs avg 44.5):
  ▼ grok           score:   15  gap:-29.5
  ▼ gemini         score:   20  gap:-24.5

  LOW-VISIBILITY TERMS (<50%) — 3 found:
  email campaigns        ░                      5%
  sales pipeline         ░░░░                  18%
  marketing automation   ░░░░░░░░              42%

  RECOMMENDATIONS:
  1. Create content targeting top 3 gap terms:
     • "email campaigns"
     • "sales pipeline"
     • "marketing automation"
  2. Optimise for grok: score 15 vs avg 44.5
-------------------------------------------------------
```

**Edge cases handled:**
- No search-terms-report data → skips terms section, shows engine gaps only
- Both sections empty → "No data available for gap analysis."
- Sparse API data → graceful fallback, no crash

**Key insights:**
- Terms at <10% visibility are complete blind spots — highest priority for new content.
- Engine gaps show which AI platforms are underserving your brand.
- Use gap queries as input for blog posts, landing pages, FAQ content, or structured schema.

---

## 4. Reputation Score (`--reputation`)

**What it does:**
Calculates a 0–100 brand health score based on sentiment data from AI engine responses. Shows top positive signals, risk areas, and trend direction.

**When to use:**
Use for brand health monitoring, PR review, or before a product launch. Essential when you want to understand _how_ your brand is described — not just whether it appears.

**CLI command:**
```
node rankscale-skill.js --reputation
```

**Sample output (brand with sentiment keywords — mock data):**
```
-------------------------------------------------------
              REPUTATION SCORE & SUMMARY
-------------------------------------------------------
  Score:  ██████████████████░░░░░░░░░░░░ 61/100
  Status: Good   Trend: ↑ improving

  Sentiment breakdown:
    Positive: 56.2%  Negative: 15.7%  Neutral: 28.1%

  Top positive signals:
    easy to use, great support, powerful

  Risk areas:
    expensive, slow

  Summary: Brand health is good (61/100) and improving.
           Monitor: expensive, slow.
-------------------------------------------------------
```

**Sample output (sparse data — brand without sentiment keywords, live API):**
```
  Score:  ███████████████░░░░░░░░░░░░░░░ 50/100
  Status: Fair   Trend: → stable
  Sentiment breakdown:
    Positive: 0%  Negative: 0%  Neutral: 0%
  No positive keywords found.
  No significant risk areas.
  Summary: Brand health is fair (50/100) and stable.
```

**Score thresholds:**
- **80+:** Strong reputation. Focus on maintaining.
- **60–79:** Good — room to improve. Address top risk areas.
- **40–59:** Fair — active monitoring needed.
- **<40:** Poor — investigate and respond to negative themes urgently.

**Key insights:**
- **Risk areas** appearing 2x+ signal messaging problems worth addressing in comms or product.
- Trend direction (↑ improving / → stable / ↓ declining) matters as much as the score itself.
- Use positive signals to inform your brand voice and content strategy.

---

## 5. Engine Gainers & Losers (`--engine-movers`)

**What it does:**
Shows which AI engines your brand improved or declined on versus the prior period. Surfaces top gainers and biggest drops with delta scores.

**When to use:**
Use after publishing new content, following a PR campaign, or when you suspect algorithm changes. Helps you quickly identify what's working and what needs attention.

**CLI command:**
```
node rankscale-skill.js --engine-movers
```

**Sample output:**
```
📈 Engine Gainers & Losers
━━━━━━━━━━━━━━━━━━━━━━━━━━
Top Gainers (vs last period):
  🟢 Perplexity    +12.3  (now 63.4)
  🟢 Gemini        +5.1   (now 54.1)

Top Losers:
  🔴 Claude        -8.7   (now 31.7)
  🔴 DeepSeek      -3.2   (now 22.5)
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Key insights:**
- Large gains on a specific engine often follow new citations or fresh content indexed there.
- Significant drops may indicate content going stale or a competitor surge.
- Monitor movers weekly to catch shifts early before they affect overall GEO score.

---

## 6. Sentiment Shift Alert (`--sentiment-alerts`)

**What it does:**
Detects significant changes in how AI engines describe your brand emotionally. Flags sudden shifts and assigns risk levels with specific trigger keywords.

**When to use:**
Use during and after PR events, product launches, or controversy. Also useful as a weekly pulse check to catch emerging reputation risks early.

**CLI command:**
```
node rankscale-skill.js --sentiment-alerts
```

**Sample output:**
```
⚠️  Sentiment Shift Alert
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Sentiment:  72/100  🟡 Moderate

Shift Detected: ↓ -8 points (vs last week)
Risk Level: 🟠 Medium

Trigger Keywords Rising:
  • "pricing concerns"   +4 mentions
  • "support delays"     +2 mentions

Recommendation:
  Review recent AI engine responses for
  "pricing" and "support" context.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Key insights:**
- A drop of **5+ points** in a week warrants investigation.
- Rising negative keywords point to the source of the shift.
- Early detection allows PR teams to respond before the narrative solidifies.
- Risk level: 🔴 High (>10pt drop) | 🟠 Medium (5–10pt) | 🟡 Low (<5pt)

---

## 7. Citation Intelligence (`--citations`)

**What it does:**
Deep-dives into the sources that AI engines cite when mentioning your brand. Shows authority ranking of citation sources, gaps vs competitors, per-engine citation preferences, Citation↔Visibility correlation, and suggested PR targets.

**When to use:**
Use when planning a link-building or PR outreach campaign. Essential for understanding _why_ your visibility is high or low on specific engines.

**CLI commands:**
```
node rankscale-skill.js --citations                  # Overview
node rankscale-skill.js --citations authority        # Top sources ranked
node rankscale-skill.js --citations gaps             # Gaps vs competitors
node rankscale-skill.js --citations engines          # Per-engine breakdown
node rankscale-skill.js --citations correlation      # Citation↔Visibility
node rankscale-skill.js --citations full             # All sections + PR targets
```

**Sample output (overview):**
```
🔗 Citation Intelligence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Top Sources:
  1. techcrunch.com      42 citations   🟢 High authority
  2. forbes.com          38 citations   🟢 High authority
  3. g2.com              21 citations   🟡 Mid authority

Gap vs Competitors:
  Competitor A leads +31 citations on Perplexity
  Competitor B leads +18 citations on Gemini

PR Targets:
  → wired.com (competitor coverage, not yours)
  → venturebeat.com (high Gemini indexing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Key insights:**
- **Authority sources** (TechCrunch, Forbes, etc.) carry more citation weight than volume.
- **Citation gaps** reveal which publications competitors have that you don't — direct PR targets.
- **Engine preferences** show that different AI engines index different publishers. Target accordingly.
- **Correlation view** shows whether your citation count actually maps to visibility gains.

---

## What's Next?

Planned feature enhancements:

- **Competitor comparison** — Side-by-side delta visibility vs tracked competitors
- **Detection rate metric** — Percentage of relevant queries returning your brand
- **Engine disparity rule** — Auto-flag when max-min engine spread exceeds 30 pts
- **Scheduled weekly reports** — Auto-run via OpenClaw cron, delivered to your channel
- **Multi-brand switching** — Quick brand toggle without changing env vars
- **Export to PDF/CSV** — Shareable reports for team or client delivery

---

## Questions?

We are happy to support. → `support@rankscale.ai`

Back to [SKILL.md](../SKILL.md) | Commands reference: [COMMANDS.md](COMMANDS.md) | Examples: [EXAMPLES.md](EXAMPLES.md)

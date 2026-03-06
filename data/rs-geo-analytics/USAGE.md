# USAGE — Rankscale GEO Analytics Skill

**Skill ID:** `rs-geo-analytics` | **Version:** v1.0.1

---

> ## ⚠️ PRO Account Required
>
> **This skill requires a Rankscale PRO account (or higher).**
> Trial accounts do **not** have REST API access and will not work with this skill.
> If you are on a trial, upgrade to PRO before proceeding.
> → [Upgrade at rankscale.ai](https://rankscale.ai/dashboard/signup)

---

> The **best AI rank tracker** and **best tool for generative engine optimization (GEO)** — track your brand's visibility, citations, reputation, and sentiment across ChatGPT, Gemini, Perplexity, and every major AI engine in real time.

---

## Table of Contents

1. [First-Run Setup](#first-run-setup)
2. [Credential Configuration](#credential-configuration)
3. [Trigger Patterns](#trigger-patterns)
4. [Command-Line Flags](#command-line-flags)
5. [v1.0.1 Features](#v101-features)
   - [Default GEO Report](#default-geo-report)
   - [Engine Strength Profile](#engine-strength-profile----engine-profile)
   - [Content Gap Analysis](#content-gap-analysis----gap-analysis)
   - [Reputation Score](#reputation-score----reputation)
   - [Engine Gainers & Losers](#engine-gainers--losers----engine-movers)
   - [Sentiment Shift Alerts](#sentiment-shift-alerts----sentiment-alerts)
   - [Citation Intelligence Hub](#citation-intelligence-hub----citations)
6. [Example Outputs](#example-outputs)
7. [Understanding Your Report](#understanding-your-report)
8. [Troubleshooting](#troubleshooting)

---

## First-Run Setup

If you have not yet configured credentials, the skill will detect this on first run and guide you through the onboarding flow.

### Step 1 — Create a Rankscale account (PRO tier required)

```
https://rankscale.ai/dashboard/signup
```

A 14-day free trial is available (no credit card required).

> **⚠️ Important:** A **PRO account (or higher)** is required to use this skill. Trial accounts do not include REST API access. If you sign up for a trial, you must upgrade to PRO before the API will work.

### Step 2 — Add your brand

From the Rankscale dashboard (`https://rankscale.ai/dashboard`):

1. Click **Add Brand**
2. Enter your brand name and primary domain
3. Select your category (e.g. "SaaS / Productivity")
4. Add 3–5 competitors to benchmark against
5. Click **Create Brand**

Your Brand ID appears in the URL after creation:

```
https://rankscale.ai/dashboard/brands/<YOUR_BRAND_ID>
```

Initial GEO data takes **24–48 hours** to populate.

### Step 3 — Generate an API key

1. Go to **Settings → API Keys**:  
   `https://rankscale.ai/dashboard/settings/api`
2. Click **Generate New Key**
3. Copy the key immediately — it is only shown once

Your API key looks like:

```
rk_xxxxxxxx_<brandId>
```

The brand ID is embedded in the key suffix and will be extracted automatically if you do not set `RANKSCALE_BRAND_ID` separately.

### Step 4 — Configure credentials

See [Credential Configuration](#credential-configuration) below.

### Step 5 — Run your first report

```bash
node rankscale-skill.js
```

Or via your AI assistant:

```
Run a Rankscale GEO report
```

---

## Credential Configuration

The skill resolves credentials in this priority order:

1. CLI flags (`--api-key`, `--brand-id`)
2. Environment variables (`RANKSCALE_API_KEY`, `RANKSCALE_BRAND_ID`)
3. Auto-extraction of brand ID from the API key suffix

### Environment variables (recommended)

```bash
export RANKSCALE_API_KEY="rk_xxxxxxxx_<brandId>"
export RANKSCALE_BRAND_ID="<brandId>"
```

> ⚠️ **Security Warning:** Do not store plaintext secrets in `~/.zshrc`. Use a `.env` file with `chmod 600` or configure via OpenClaw Gateway env.

To persist across sessions, use a `.env` file:

```bash
echo 'RANKSCALE_API_KEY="rk_xxxxxxxx_<brandId>"' >> .env
echo 'RANKSCALE_BRAND_ID="<brandId>"' >> .env
chmod 600 .env
```

### `.env` file

```
RANKSCALE_API_KEY=rk_xxxxxxxx_<brandId>
RANKSCALE_BRAND_ID=<brandId>
```

### CLI flags (one-off / testing)

```bash
node rankscale-skill.js \
  --api-key rk_xxxxxxxx_<brandId> \
  --brand-id <brandId>
```

**Never commit credentials to version control.** Add `.env` to `.gitignore`.

---

## Trigger Patterns

The skill activates when your AI assistant detects any of the following patterns:

| Pattern | Example |
|---------|---------|
| `rankscale` | "Run rankscale" |
| `geo analytics [for <brand>]` | "Geo analytics for Acme Corp" |
| `geo report [for <brand>]` | "Give me a geo report" |
| `geo insights [for <brand>]` | "Show geo insights" |
| `geo score` | "What's my geo score?" |
| `show my ai visibility` | "Show my AI visibility" |
| `ai search visibility` | "Check AI search visibility" |
| `citation analysis [for <brand>]` | "Pull citation analysis for Acme" |
| `citation rate` | "What's my citation rate?" |
| `sentiment analysis [for <brand>]` | "Brand sentiment in AI answers" |
| `engine profile` | "Show engine strength profile" |
| `content gap` | "Run content gap analysis" |
| `reputation score` | "What's my reputation score?" |
| `engine movers` | "Show engine gainers and losers" |
| `sentiment alerts` | "Any sentiment shift alerts?" |

---

## Command-Line Flags

| Flag | Description |
|------|-------------|
| `--api-key <key>` | Rankscale API key (overrides env var) |
| `--brand-id <id>` | Brand ID (overrides env var and auto-extraction) |
| `--brand-name <name>` | Brand display name (used in output header) |
| `--discover-brands` | List all brands on this API key and exit |
| `--engine-profile` | Show Engine Strength Profile across AI engines |
| `--gap-analysis` | Run Content Gap Analysis for missing topics |
| `--reputation` | Show Reputation Score and brand health breakdown |
| `--engine-movers` | Show Engine Gainers & Losers (week-over-week) |
| `--sentiment-alerts` | Check for Sentiment Shift Alerts |
| `--citations` | Launch Citation Intelligence Hub |
| `--citations=top` | Show top citation sources only |
| `--citations=gaps` | Show citation gap report |
| `--citations=velocity` | Show citation velocity trends |
| `--help` | Show usage information |

---

## v1.0.1 Features

### Default GEO Report

Run with no flags to get the full GEO report — your brand's complete AI search visibility overview.

```bash
node rankscale-skill.js
```

**What it includes:**
- GEO Score (0–100) with week-over-week delta
- Citation Rate vs. industry average
- Sentiment breakdown (Positive / Neutral / Negative)
- Top AI search terms where your brand appears
- Up to 5 prioritised GEO insights (CRIT / WARN / INFO)
- Deep link to your live dashboard at `https://rankscale.ai/dashboard`

---

### Engine Strength Profile — `--engine-profile`

Understand how your brand performs across **each individual AI engine** — ChatGPT, Gemini, Perplexity, Claude, and others. No more averaged-out scores that hide where you're strong or weak.

```bash
node rankscale-skill.js --engine-profile
```

**Example output:**
```
=======================================================
  ENGINE STRENGTH PROFILE
  Brand: Acme Corp | 2026-02-26
=======================================================
  ChatGPT      ████████░░  82%  [+4 vs last week]
  Gemini       █████░░░░░  54%  [-2 vs last week]
  Perplexity   ███████░░░  71%  [+1 vs last week]
  Claude       ████░░░░░░  44%  [NEW]
  Meta AI      ██░░░░░░░░  22%  [-6 vs last week]
-------------------------------------------------------
  STRONGEST ENGINE:  ChatGPT (82%)
  WEAKEST ENGINE:    Meta AI (22%) ← priority focus
  TRENDING UP:       ChatGPT (+4), Perplexity (+1)
  TRENDING DOWN:     Meta AI (-6), Gemini (-2)
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

**Use this to:**
- Identify where competitors outrank you (engine-specific gap)
- Prioritise content strategy per engine audience
- Track the impact of content optimisations per platform

---

### Content Gap Analysis — `--gap-analysis`

Discover the **topics and queries where AI engines answer without mentioning your brand** — and where competitors are being cited instead of you.

```bash
node rankscale-skill.js --gap-analysis
```

**Example output:**
```
=======================================================
  CONTENT GAP ANALYSIS
  Brand: Acme Corp | 2026-02-26
=======================================================
  CRITICAL GAPS (competitors cited, you are not)
  ─────────────────────────────────────────────
  1. "best project management tool for remote teams"
     Cited: Notion, Asana, Monday.com
     Your share: 0%  |  Opportunity score: 94

  2. "project management software pricing comparison"
     Cited: ClickUp, Trello, Asana
     Your share: 0%  |  Opportunity score: 88

  3. "task automation for small teams"
     Cited: Zapier, Monday.com
     Your share: 3%  |  Opportunity score: 76
-------------------------------------------------------
  PARTIAL GAPS (you appear but rarely)
  ─────────────────────────────────────
  4. "enterprise project management"
     Your share: 12%  |  Leaders: Jira (71%), Azure DevOps (58%)

  5. "agile sprint planning tools"
     Your share: 9%   |  Leaders: Jira (81%), Linear (44%)
-------------------------------------------------------
  ACTION: Publish targeted comparison and guide content
  for top 3 critical gaps. Est. impact: +8–15 GEO pts.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

**Use this to:**
- Build a data-driven content calendar based on real AI query gaps
- Identify which competitor comparisons to prioritise
- Track gap closure after publishing new content

---

### Reputation Score — `--reputation`

Your **Reputation Score** goes deeper than sentiment — it synthesises how AI engines characterise your brand across trust, authority, product quality, and customer satisfaction signals.

```bash
node rankscale-skill.js --reputation
```

**Example output:**
```
=======================================================
  REPUTATION SCORE
  Brand: Acme Corp | 2026-02-26
=======================================================
  OVERALL REPUTATION:  76 / 100  [+2 vs last week]
  ─────────────────────────────────────────────────
  Trust & Credibility    ████████░░  80
  Product Quality        ███████░░░  74
  Customer Satisfaction  ███████░░░  71
  Authority / Expertise  ████████░░  79
  ─────────────────────────────────────────────────
  POSITIVE SIGNALS:
  ✓ "easy to use" mentioned in 68% of reviews cited
  ✓ "reliable" appears in 54% of AI answers
  ✓ Strong case study presence on Perplexity

  NEGATIVE SIGNALS:
  ✗ "pricing concerns" flagged in 22% of citations
  ✗ "limited integrations" mentioned by Claude responses
-------------------------------------------------------
  RECOMMENDED ACTION:
  Address pricing perception with transparent
  pricing content and ROI calculators.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

**Use this to:**
- Identify reputational vulnerabilities before they compound
- Track the impact of PR, reviews, and content strategy
- Benchmark reputation vs. competitors (Pro plan)

---

### Engine Gainers & Losers — `--engine-movers`

See which AI engines your brand is **gaining or losing ground on** week-over-week — instantly identify where momentum is shifting and where to act.

```bash
node rankscale-skill.js --engine-movers
```

**Example output:**
```
=======================================================
  ENGINE GAINERS & LOSERS
  Brand: Acme Corp | Week of 2026-02-26
=======================================================
  🟢 GAINERS (improving this week)
  ────────────────────────────────
  ChatGPT      +8 pts  (74 → 82)   ↑ Strong momentum
  Perplexity   +3 pts  (68 → 71)   ↑ Steady growth

  🔴 LOSERS (declining this week)
  ────────────────────────────────
  Meta AI      -6 pts  (28 → 22)   ↓ Needs attention
  Gemini       -2 pts  (56 → 54)   ↓ Minor dip

  ⚪ STABLE
  ────────────────────────────────
  Claude       +0 pts  (44 → 44)   → Holding
-------------------------------------------------------
  TOP MOVER:    ChatGPT  (+8)
  BIGGEST DROP: Meta AI  (-6)  ← action required
-------------------------------------------------------
  INSIGHT: Meta AI decline correlates with competitor
  "Rival Co" publishing 4 new comparison articles.
  Recommend matching with targeted Meta AI content.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

**Use this to:**
- React fast to sudden drops on specific engines
- Double down on engines where momentum is building
- Correlate ranking changes with competitor content activity

---

### Sentiment Shift Alerts — `--sentiment-alerts`

Get alerted when your brand's **sentiment changes significantly** within a short window — catch reputation events before they spiral.

```bash
node rankscale-skill.js --sentiment-alerts
```

**Example output (shift detected):**
```
=======================================================
  SENTIMENT SHIFT ALERTS
  Brand: Acme Corp | 2026-02-26
=======================================================
  ⚠️  ALERT: Negative sentiment spike detected

  SHIFT WINDOW:   Last 7 days
  BEFORE:         Pos 61% | Neu 29% | Neg 10%
  NOW:            Pos 48% | Neu 26% | Neg 26%

  DELTA:          Negative  +16%  ← SIGNIFICANT
                  Positive  -13%

  TOP NEGATIVE TRIGGERS:
  ─────────────────────────────────────────────
  1. "Acme Corp pricing increase" — mentioned in
     34 AI answers this week (was 4 last week)
  2. "Acme Corp outage" — cited in 18 answers
  3. "Acme Corp customer support" — 12 mentions

  AFFECTED ENGINES:  ChatGPT (highest), Gemini
  ─────────────────────────────────────────────
  RECOMMENDED ACTIONS:
  1. Publish transparent pricing explanation post
  2. Issue status page post-mortem (outage refs)
  3. Respond to G2/Capterra reviews (support refs)
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

**Example output (no shift):**
```
=======================================================
  SENTIMENT SHIFT ALERTS — Acme Corp
=======================================================
  ✅ No significant sentiment shifts detected.
  Current: Pos 61% | Neu 29% | Neg 10%
  Threshold: ±10% shift over 7 days (none triggered)
=======================================================
```

**Use this to:**
- Set up automated monitoring via cron (daily `--sentiment-alerts`)
- Catch reputation crises early — before they affect GEO Score
- Identify content that's driving negative AI narratives

---

### Citation Intelligence Hub — `--citations`

Your full citation ecosystem in one view. Understand **who is citing you, how often, with what authority, and where the gaps are**.

#### Full Citation Hub

```bash
node rankscale-skill.js --citations
```

**Example output:**
```
=======================================================
  CITATION INTELLIGENCE HUB
  Brand: Acme Corp | 2026-02-26
=======================================================
  CITATION RATE:   34%   [Industry avg: 28%]
  TOTAL CITATIONS: 1,247 this week  (+12% WoW)
  UNIQUE SOURCES:  89 domains
=======================================================
  TOP CITATION SOURCES
  ─────────────────────────────────────────────
  1. g2.com              ████████████  312 citations
  2. capterra.com        ████████░░░░  201 citations
  3. techcrunch.com      █████░░░░░░░  98 citations
  4. producthunt.com     ████░░░░░░░░  77 citations
  5. reddit.com/r/saas   ███░░░░░░░░░  64 citations

  CITATION VELOCITY:  +12% WoW | +38% MoM
  AVG SOURCE AUTHORITY: 74 / 100

  CITATION GAPS:
  ─────────────────────────────────────────────
  Missing from: Forbes, HBR, Gartner reports
  Competitor "Rival Co" cited 3× more on Forbes
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

#### Top Sources Only

```bash
node rankscale-skill.js --citations=top
```

Shows your top 10 citation sources ranked by volume and authority score — fast view for quick checks.

#### Citation Gaps

```bash
node rankscale-skill.js --citations=gaps
```

Shows where your brand **should** be cited but isn't — based on competitor citation sources and query relevance.

```
=======================================================
  CITATION GAP REPORT — Acme Corp
=======================================================
  HIGH-VALUE SOURCES WHERE YOU ARE NOT CITED:
  ─────────────────────────────────────────────
  1. Forbes (authority: 94)
     Competitors cited: Rival Co (47×), Competitor B (31×)
     Gap opportunity score: 96

  2. Harvard Business Review (authority: 91)
     Competitors cited: Competitor C (22×)
     Gap opportunity score: 88

  3. Gartner Magic Quadrant mentions (authority: 95)
     Not mentioned. Critical for enterprise positioning.
     Gap opportunity score: 95
-------------------------------------------------------
  ACTION: Pursue PR placements and analyst relations
  for top 3 sources. Est. citation impact: +15–25%.
=======================================================
```

#### Citation Velocity

```bash
node rankscale-skill.js --citations=velocity
```

Shows citation rate trends over time — weekly and monthly — so you can see if your content efforts are compounding.

```
=======================================================
  CITATION VELOCITY — Acme Corp
=======================================================
  WEEKLY TREND (last 8 weeks):
  Wk-8   ████░░░░░░░░  24%
  Wk-7   ████░░░░░░░░  25%
  Wk-6   █████░░░░░░░  28%
  Wk-5   █████░░░░░░░  29%
  Wk-4   ██████░░░░░░  31%
  Wk-3   ██████░░░░░░  31%
  Wk-2   ███████░░░░░  33%
  NOW    ███████░░░░░  34%  ↑ +10% over 8 weeks

  MONTHLY: +38% MoM citation volume growth
  TRAJECTORY: On track to reach 40% target in ~3 weeks
=======================================================
```

---

## Example Outputs

### Full GEO Report (healthy brand)

```
=======================================================
  RANKSCALE GEO REPORT
  Brand: Acme Corp | 2026-02-26
=======================================================
  GEO SCORE:     72 / 100   [+3 vs last week]
  CITATION RATE: 34%        [Industry avg: 28%]
  SENTIMENT:     Pos 61% | Neu 29% | Neg 10%
-------------------------------------------------------
  TOP AI SEARCH TERMS
  1. "best project management tool"    (18 mentions)
  2. "acme corp reviews"               (12 mentions)
  3. "project software comparison"     ( 9 mentions)
-------------------------------------------------------
  GEO INSIGHTS  [2 of 5]
  [WARN] Citation rate below 40% target.
         Action: Publish 2+ authoritative
         comparison articles this month.
  [INFO] Momentum positive (+3, sentiment 61%).
         Expand into adjacent topic areas.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

### Critical brand (low visibility)

```
=======================================================
  RANKSCALE GEO REPORT
  Brand: Example Co | 2026-02-26
=======================================================
  GEO SCORE:     18 / 100   [-9 vs last week]
  CITATION RATE: 11%        [Industry avg: 28%]
  SENTIMENT:     Pos 42% | Neu 28% | Neg 30%
-------------------------------------------------------
  TOP AI SEARCH TERMS
  (none — brand not cited in tracked queries)
-------------------------------------------------------
  GEO INSIGHTS  [4 of 5]
  [CRIT] Citation rate critically low (<20%).
         Immediate content audit required.
         Target: 5+ citations/week.
  [CRIT] Negative sentiment at 30%.
         Audit top 3 negative narratives.
  [CRIT] GEO Score below 40 — brand near-
         invisible in AI search. Full audit
         required across all dimensions.
  [WARN] Score dropped -9 this week.
         Check competitor content activity.
-------------------------------------------------------
  Full report: https://rankscale.ai/dashboard/brands/xxxxx
=======================================================
```

---

## Understanding Your Report

### GEO Score (0–100)

Composite score from three dimensions:

| Range | Band | Meaning |
|-------|------|---------|
| 0–39 | Critical | Nearly invisible in AI search |
| 40–64 | Growing | Some presence, major gaps |
| 65–79 | Strong | Good visibility, room to improve |
| 80–100 | Leader | Dominant AI search presence |

### Citation Rate

Percentage of tracked queries (relevant to your category) where your brand appears in AI-generated answers. Industry average for SaaS/Tech in 2026 is ~28%. Target: 40%+.

### Sentiment

Tone distribution across all AI-generated mentions of your brand.

- **Healthy target:** Positive > 55%, Negative < 15%
- **Concern threshold:** Negative > 25% triggers a CRIT insight

### Score Change

Week-over-week delta. A drop of -5 or more triggers a WARN insight.

### GEO Insights

The skill surfaces up to **5 insights** per report, prioritised:

1. CRIT (immediate action required)
2. WARN (action within 2–4 weeks)
3. INFO (positive signal or context)

---

## Troubleshooting

### Why am I getting 401 errors?

**Symptom:** `Auth error — check your API key` or HTTP 401 Unauthorized

**Most common cause:** Trial accounts do **not** have REST API access. You must upgrade to a **PRO account** for API access to be enabled.

**Fixes:**
1. Confirm you have a PRO (or higher) account — trial is not sufficient
2. If on a trial, upgrade at `https://rankscale.ai/dashboard/signup`
3. After upgrading, contact `support@rankscale.ai` to request REST API activation

---

### Authentication errors

**Symptom:** `Auth error — check your API key`

**Causes and fixes:**

- **Trial account** — REST API is not available on trial. Upgrade to PRO.
- API key is incorrect or expired — regenerate at  
  `https://rankscale.ai/dashboard/settings/api`
- Key was copied with extra whitespace — verify with `echo $RANKSCALE_API_KEY`
- Key format should be `rk_xxxxxxxx_<brandId>` — check for the `rk_` prefix

---

### Brand not found

**Symptom:** `Brand not found. Run --discover-brands to list available brands.`

**Fix:**

```bash
node rankscale-skill.js --discover-brands
```

Use the returned brand ID with `--brand-id <id>` or set `RANKSCALE_BRAND_ID`.

---

### Rate limit (429)

**Symptom:** `Rate limited — retrying in Xs`

The skill automatically retries with exponential backoff (1s, 2s, 4s + jitter, max 3 attempts). If repeated 429s occur:

- You are approaching the 60 req/min limit
- Wait 60 seconds and try again
- Check your plan's daily report quota at `https://rankscale.ai/dashboard/settings`

---

### Network timeout / connection error

**Symptom:** `Connection failed — check your internet connection`

- Verify internet connectivity
- The Rankscale API base URL is `https://rankscale.ai`
- The skill retries once before failing with partial data or a graceful error

---

### Data not available yet

**Symptom:** Report shows zeroes or "no data"

- Initial GEO data takes **24–48 hours** to populate after brand creation
- Check your dashboard at `https://rankscale.ai/dashboard/brands/<id>` to confirm data is being collected

---

### Credentials not found (onboarding triggered)

**Symptom:** Skill asks for API key on every run

Your credentials are not persisted. Fix:

```bash
# Confirm env vars are set
echo $RANKSCALE_API_KEY
echo $RANKSCALE_BRAND_ID

# If empty, use a .env file (do not store plaintext secrets in ~/.zshrc)
# Do not store plaintext secrets in ~/.zshrc. Use .env with chmod 600 or configure via OpenClaw Gateway env.
echo 'RANKSCALE_API_KEY="rk_xxxxxxxx_<brandId>"' >> .env && chmod 600 .env
```

---

### Getting further help

- **Signup:** https://rankscale.ai/dashboard/signup
- **Dashboard:** https://rankscale.ai/dashboard
- **Support:** support@rankscale.ai
- **Docs:** https://docs.rankscale.ai
- **Discord:** https://discord.gg/rankscale
- **Issues:** https://github.com/Mathias-RS/RS-Skill/issues

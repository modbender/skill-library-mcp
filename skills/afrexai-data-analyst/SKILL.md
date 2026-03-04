# Data Analyst — AfrexAI ⚡📊

**Transform raw data into decisions. Not just charts — answers.**

You are a senior data analyst. Your job isn't to query databases — it's to find the story in the data and tell it so clearly that the next action is obvious.

---

## Core Philosophy

**Data without a decision is decoration.**

Every analysis must answer: "So what?" → "Now what?" → "How much?"

The DICE framework governs everything:
- **D**efine the question (what decision does this inform?)
- **I**nvestigate the data (explore, clean, analyze)
- **C**ommunicate the insight (visualize, narrate, recommend)
- **E**valuate the impact (was the decision right? close the loop)

---

## Phase 1: Define the Question

Before touching any data, answer these:

```yaml
analysis_brief:
  business_question: "Why did Q4 revenue drop 12%?"
  decision_it_informs: "Should we change pricing or double down on marketing?"
  stakeholder: "VP Sales"
  urgency: "high"  # high/medium/low
  data_sources:
    - name: "Sales DB"
      type: "postgres"
      access: "read-only replica"
    - name: "Marketing spend CSV"
      type: "spreadsheet"
      access: "shared drive"
  hypothesis: "Marketing channel shift in Oct caused lead quality drop"
  success_criteria: "Identify root cause with >80% confidence, recommend action"
  deadline: "2 business days"
```

### Question Quality Checklist
- [ ] Is it specific enough to answer? ("Revenue is down" ❌ → "Q4 revenue dropped 12% vs Q3 in the SMB segment" ✅)
- [ ] Is the decision clear? (If yes → do X, if no → do Y)
- [ ] Do we have the data to answer it?
- [ ] Is there a time constraint?
- [ ] Who needs to see the output and in what format?

---

## Phase 2: Data Investigation

### 2A. Data Discovery & Profiling

Before any analysis, profile every dataset:

```
DATA PROFILE: [table/file name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rows:           [count]
Columns:        [count]
Date range:     [min] → [max]
Granularity:    [row = what? transaction? user? day?]
Update freq:    [real-time / daily / manual]
Key columns:    [list primary keys, dates, amounts]
Quality issues: [nulls, duplicates, outliers, encoding]
Joins to:       [other tables via which keys]
```

**Profiling queries (adapt to your DB):**

```sql
-- Completeness check: % null per column
SELECT 
    'column_name' as col,
    COUNT(*) as total,
    SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) as nulls,
    ROUND(100.0 * SUM(CASE WHEN column_name IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as null_pct
FROM table_name;

-- Duplicate check
SELECT column_name, COUNT(*) as dupes 
FROM table_name 
GROUP BY column_name 
HAVING COUNT(*) > 1 
ORDER BY dupes DESC LIMIT 20;

-- Distribution check (numeric)
SELECT 
    MIN(amount) as min_val,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY amount) as median,
    AVG(amount) as mean,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) as p75,
    MAX(amount) as max_val,
    STDDEV(amount) as std_dev
FROM table_name;

-- Cardinality check (categorical)
SELECT column_name, COUNT(*) as freq,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM table_name
GROUP BY column_name
ORDER BY freq DESC;
```

### 2B. Data Cleaning Decision Tree

```
Is the value missing?
├── Is it missing at random (MAR)?
│   ├── <5% missing → drop rows
│   ├── 5-20% missing → impute (median for numeric, mode for categorical)
│   └── >20% missing → flag column as unreliable, note in findings
├── Is it systematically missing (MNAR)?
│   └── Investigate WHY. This IS a finding. (e.g., "Churn field is null for 30% of users = we never tracked it for free tier")
└── Is it a duplicate?
    ├── Exact duplicate → deduplicate, note count
    └── Near duplicate → investigate, pick logic (latest timestamp? highest confidence?)
```

**Outlier handling:**
```
Is this datapoint an outlier?
├── Is it a data entry error? (negative age, $0 salary) → fix or remove
├── Is it genuine but extreme? (whale customer, Black Friday spike)
│   ├── Does it skew the analysis? → segment it out, analyze separately
│   └── Is it THE story? → highlight it
└── Not sure → run analysis with AND without it, note the difference
```

### 2C. Analysis Patterns Library

Pick the right analysis for the question:

| Question Type | Analysis Pattern | Key Technique |
|---|---|---|
| "What happened?" | Descriptive | Aggregation, time series, segmentation |
| "Why did it happen?" | Diagnostic | Drill-down, correlation, cohort analysis |
| "What will happen?" | Predictive | Trends, regression, moving averages |
| "What should we do?" | Prescriptive | Scenario modeling, A/B test design |
| "Is this real or noise?" | Statistical | Significance tests, confidence intervals |
| "Who are our best/worst?" | Segmentation | RFM, clustering, percentile ranking |

#### Descriptive Analysis Template

```sql
-- Time series with period-over-period comparison
SELECT 
    date_trunc('week', created_at) as period,
    COUNT(*) as metric,
    LAG(COUNT(*), 1) OVER (ORDER BY date_trunc('week', created_at)) as prev_period,
    ROUND(100.0 * (COUNT(*) - LAG(COUNT(*), 1) OVER (ORDER BY date_trunc('week', created_at))) 
        / NULLIF(LAG(COUNT(*), 1) OVER (ORDER BY date_trunc('week', created_at)), 0), 1) as growth_pct
FROM events
WHERE created_at >= current_date - interval '90 days'
GROUP BY 1
ORDER BY 1;
```

#### Diagnostic Analysis: The "5 Splits" Method

When something changed, split the data 5 ways to find the cause:

1. **By time** — When exactly did it change? (daily, then hourly)
2. **By segment** — Which customer segment changed most?
3. **By channel** — Which acquisition channel? Which product?
4. **By geography** — Regional differences?
5. **By cohort** — New vs existing? Recent vs old?

The split that shows the biggest divergence is your likely root cause.

#### Cohort Analysis Template

```sql
-- Retention cohort matrix
WITH cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', MIN(created_at)) as cohort_month
    FROM orders
    GROUP BY user_id
),
activity AS (
    SELECT 
        c.cohort_month,
        DATE_TRUNC('month', o.created_at) as activity_month,
        COUNT(DISTINCT o.user_id) as active_users
    FROM orders o
    JOIN cohorts c ON o.user_id = c.user_id
    GROUP BY 1, 2
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT user_id) as cohort_size
    FROM cohorts GROUP BY 1
)
SELECT 
    a.cohort_month,
    cs.cohort_size,
    EXTRACT(MONTH FROM AGE(a.activity_month, a.cohort_month)) as months_since,
    a.active_users,
    ROUND(100.0 * a.active_users / cs.cohort_size, 1) as retention_pct
FROM activity a
JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
ORDER BY 1, 3;
```

#### RFM Segmentation

```sql
-- Score customers by Recency, Frequency, Monetary value
WITH rfm AS (
    SELECT 
        customer_id,
        CURRENT_DATE - MAX(order_date)::date as recency_days,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY customer_id
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,  -- lower recency = better
        NTILE(5) OVER (ORDER BY frequency) as f_score,
        NTILE(5) OVER (ORDER BY monetary) as m_score
    FROM rfm
)
SELECT *,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Needs Attention'
    END as segment
FROM scored;
```

#### Funnel Analysis

```sql
-- Conversion funnel with drop-off rates
WITH funnel AS (
    SELECT 
        COUNT(DISTINCT CASE WHEN event = 'visit' THEN user_id END) as visits,
        COUNT(DISTINCT CASE WHEN event = 'signup' THEN user_id END) as signups,
        COUNT(DISTINCT CASE WHEN event = 'activation' THEN user_id END) as activations,
        COUNT(DISTINCT CASE WHEN event = 'purchase' THEN user_id END) as purchases
    FROM events
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT 
    visits, signups, activations, purchases,
    ROUND(100.0 * signups / NULLIF(visits, 0), 1) as visit_to_signup_pct,
    ROUND(100.0 * activations / NULLIF(signups, 0), 1) as signup_to_activation_pct,
    ROUND(100.0 * purchases / NULLIF(activations, 0), 1) as activation_to_purchase_pct,
    ROUND(100.0 * purchases / NULLIF(visits, 0), 1) as overall_conversion_pct
FROM funnel;
```

---

## Phase 3: Communicate the Insight

### The Insight Formula

Every finding must follow this structure:

```
INSIGHT: [one-sentence finding]
EVIDENCE: [specific numbers with context]
SO WHAT: [why this matters to the business]
NOW WHAT: [recommended action]
CONFIDENCE: [high/medium/low + why]
```

**Example:**
```
INSIGHT: SMB segment revenue dropped 18% in Q4, while Enterprise grew 5%.
EVIDENCE: SMB revenue was $1.2M in Q3 vs $984K in Q4. 73% of the drop came from 
          churned accounts that joined via the Google Ads campaign in Q2.
SO WHAT: Our Google Ads campaign attracted low-quality SMB leads with high churn risk. 
         The CAC for these accounts was $340 but LTV was only $280 — we lost money.
NOW WHAT: Pause Google Ads for SMB. Shift budget to LinkedIn (SMB LTV: $890, CAC: $220). 
         Tighten qualification criteria for ad-sourced leads.
CONFIDENCE: High — based on 847 churned accounts with clear acquisition source data.
```

### Visualization Selection Guide

| Data Type | Best Chart | When to Use | Avoid |
|---|---|---|---|
| Trend over time | Line chart | Continuous data, 5+ periods | Pie chart, bar |
| Comparison | Horizontal bar | Ranking, categories <15 | 3D charts |
| Composition | Stacked bar / 100% bar | Parts of a whole over time | Pie (>5 slices) |
| Distribution | Histogram / box plot | Understanding spread | Bar chart |
| Correlation | Scatter plot | 2 numeric variables | Line chart |
| Single KPI | Big number + sparkline | Executive dashboards | Tables |
| Part of whole (static) | Pie/donut (≤5 slices) | One point in time | Pie (>5 slices) |
| Geographic | Map / choropleth | Location-based data | Bar chart |

### Chart Formatting Rules
1. **Title = the insight**, not the data description ("SMB churn drove Q4 revenue drop" ✅, "Q4 Revenue by Segment" ❌)
2. **Y-axis starts at zero** for bar charts (truncating exaggerates)
3. **Annotate inflection points** — label the moments that matter
4. **Limit colors to 5** — use grey for everything except the story
5. **No gridlines if possible** — they add noise
6. **Source and date** in small text at bottom

### Report Structure

```markdown
# [Analysis Title]
**Date:** [date] | **Author:** [name] | **Stakeholder:** [who asked]

## Executive Summary (3 sentences max)
[Key finding. Business impact. Recommended action.]

## Key Metrics
| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
| [KPI]  | [value] | [value]  | [+/-%] |

## Findings
### Finding 1: [Insight headline]
[Evidence + visualization + interpretation]

### Finding 2: [Insight headline]
[Evidence + visualization + interpretation]

## Recommendations
1. **[Action]** — [Expected impact] — [Effort: low/medium/high]
2. **[Action]** — [Expected impact] — [Effort: low/medium/high]

## Methodology & Limitations
- Data source: [what, date range, granularity]
- Assumptions: [list any]
- Limitations: [what we couldn't measure, data gaps]
- Confidence: [high/medium/low]

## Appendix
[Detailed queries, full data tables, supplementary charts]
```

---

## Phase 4: Evaluate & Close the Loop

After delivering the analysis, track whether it led to action:

```yaml
analysis_followup:
  original_question: "Why did Q4 revenue drop?"
  delivered: "2024-01-15"
  recommendation: "Shift ad spend from Google to LinkedIn"
  action_taken: "yes — budget reallocated Feb 1"
  result: "SMB churn dropped 34% in Feb, CAC improved by $120"
  lessons: "Ad channel quality matters more than volume"
```

---

## Analysis Scoring Rubric (0-100)

Use this to self-evaluate before delivering:

| Dimension | Weight | Criteria | Score |
|---|---|---|---|
| **Question Clarity** | 15 | Is the business question specific and decision-linked? | /15 |
| **Data Quality** | 15 | Was data profiled, cleaned, and limitations noted? | /15 |
| **Analytical Rigor** | 25 | Right technique for the question? Statistical validity? Edge cases? | /25 |
| **Insight Quality** | 25 | Does every finding follow Insight → Evidence → So What → Now What? | /25 |
| **Communication** | 10 | Clear visualizations? Right format for the audience? Scannable? | /10 |
| **Actionability** | 10 | Are recommendations specific, prioritized, and effort-rated? | /10 |

**Scoring:** 90+ = ship it. 70-89 = review one weak area. <70 = rework before delivering.

---

## Advanced Techniques

### Statistical Significance Quick Check

Before claiming a change is real:

```
Sample size per group: ≥30 (bare minimum), ≥385 for ±5% margin
Confidence level: 95% (p < 0.05) for business decisions
Effect size: Is the difference practically meaningful, not just statistically?

Quick z-test for proportions:
  p1 = conversion_rate_A, p2 = conversion_rate_B
  p_pooled = (successes_A + successes_B) / (n_A + n_B)
  z = (p1 - p2) / sqrt(p_pooled * (1-p_pooled) * (1/n_A + 1/n_B))
  |z| > 1.96 → significant at 95%
```

### A/B Test Design Template

```yaml
ab_test:
  name: "New pricing page"
  hypothesis: "Showing annual savings will increase annual plan signups by 15%"
  primary_metric: "annual plan conversion rate"
  secondary_metrics: ["revenue per visitor", "bounce rate"]
  guardrail_metrics: ["total conversion rate", "support tickets"]
  sample_size_per_variant: 3800  # for 15% MDE, 80% power, 95% confidence
  expected_duration: "14 days at current traffic"
  segments_to_check: ["new vs returning", "mobile vs desktop", "geo"]
  decision_rules:
    ship: "primary metric significant positive, no guardrail regression"
    iterate: "directionally positive but not significant — extend 7 days"
    kill: "negative or guardrail regression"
```

### Moving Averages for Noisy Data

```sql
-- 7-day moving average to smooth daily noise
SELECT 
    date,
    daily_value,
    AVG(daily_value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as ma_7d,
    AVG(daily_value) OVER (ORDER BY date ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) as ma_28d
FROM daily_metrics;
```

### Year-over-Year Comparison

```sql
SELECT 
    DATE_TRUNC('month', created_at) as month,
    SUM(revenue) as revenue,
    LAG(SUM(revenue), 12) OVER (ORDER BY DATE_TRUNC('month', created_at)) as revenue_yoy,
    ROUND(100.0 * (SUM(revenue) - LAG(SUM(revenue), 12) OVER (ORDER BY DATE_TRUNC('month', created_at)))
        / NULLIF(LAG(SUM(revenue), 12) OVER (ORDER BY DATE_TRUNC('month', created_at)), 0), 1) as yoy_growth_pct
FROM orders
GROUP BY 1 ORDER BY 1;
```

---

## Spreadsheet & CSV Analysis

When working with files (no database):

1. **Load the file** — Read with appropriate tool, note delimiter/encoding
2. **Inspect shape** — Row count, column names, dtypes
3. **Profile each column** — Nulls, uniques, min/max, distribution
4. **Apply the same DICE framework** — Question → Investigate → Communicate → Evaluate

### Common CSV Operations
- **Pivot**: Group by one column, aggregate another
- **Merge**: Join two CSVs on a common key (watch for many-to-many)
- **Filter**: Subset to relevant rows before analysis
- **Derive**: Create calculated columns (ratios, categories, flags)

### Data Quality Red Flags in Spreadsheets
- Mixed data types in a column (numbers stored as text)
- Merged cells (break everything)
- Hidden rows/columns (missing data)
- Formulas referencing external files (broken links)
- "Last updated: 2022" (stale data)

---

## Edge Cases & Gotchas

### Timezone Issues
- Always confirm: is this UTC, local, or mixed?
- Aggregating across timezones without converting = wrong numbers
- "Daily" metrics shift depending on timezone definition

### Survivorship Bias
- Analyzing only current customers? You're missing the ones who left.
- Looking at successful campaigns? What about the ones that failed?
- Always ask: "What data am I NOT seeing?"

### Simpson's Paradox
- A trend that appears in several groups may reverse when groups are combined
- Always check both the aggregate AND the segments
- Classic example: treatment works for men AND women separately, but "fails" overall because of unequal group sizes

### Small Sample Traps
- <30 observations: don't claim patterns
- One big customer can move averages dramatically — check for concentration
- "Revenue grew 200%!" (from $100 to $300 — meaningless)

### Currency & Unit Confusion
- Always label units: "$K", "users", "sessions", "orders"
- Revenue ≠ profit ≠ bookings ≠ ARR — clarify which
- If comparing across currencies/periods: normalize

---

## Daily Analyst Routine

```
Morning (15 min):
□ Check key dashboards — any anomalies?
□ Review overnight data loads — anything break?
□ Scan stakeholder requests — prioritize

Analysis blocks (focused 2-hour chunks):
□ Pick one question from the backlog
□ Run the DICE framework start to finish
□ Deliver insight, not just data

End of day (10 min):
□ Update analysis log with today's findings
□ Note any data quality issues discovered
□ Queue tomorrow's priority question
```

---

## Tools & Environment

This skill is **tool-agnostic**. It works with:
- **Databases**: PostgreSQL, MySQL, SQLite, BigQuery, Snowflake, Redshift
- **Spreadsheets**: CSV, Excel, Google Sheets
- **Languages**: SQL (primary), Python/pandas if available
- **Visualization**: Any charting tool, or describe charts for stakeholders
- **Files**: JSON, Parquet, XML, API responses

No dependencies. No scripts. Pure analytical methodology + reusable query patterns.

---

## Sample Output: Complete Mini-Analysis

```
ANALYSIS: Website Conversion Rate Drop — January 2024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTIVE SUMMARY
Conversion rate dropped from 3.2% to 2.1% in January. Root cause: a broken 
checkout button on mobile Safari (iOS 17.2+) affecting 34% of mobile traffic. 
Fix the bug → recover ~$47K/month in lost revenue.

KEY METRICS
  Conversion rate:  2.1% (was 3.2%) — ↓34%
  Mobile conversion: 0.8% (was 2.9%) — ↓72%  ← THE STORY
  Desktop conversion: 3.4% (was 3.5%) — ↓3%  (normal variance)

FINDING
The 5-splits analysis immediately pointed to device type. Mobile conversion 
cratered on Jan 4 — the same day iOS 17.2 rolled out widely. The checkout 
button uses a CSS property unsupported in Safari 17.2+.

  Affected sessions: 12,400 (Jan 4-31)
  Estimated lost conversions: 12,400 × 2.1% lift = 260 orders
  Estimated lost revenue: 260 × $181 avg order = $47,060

RECOMMENDATION
1. **Hotfix the CSS** — Engineering, 2-hour fix, deploy today [HIGH]
2. **Add Safari to CI/CD browser matrix** — Prevent recurrence [MEDIUM]
3. **Set up device-segment alerting** — Auto-flag >10% drops [LOW]

CONFIDENCE: High — reproduced the bug, confirmed with browser logs.
METHODOLOGY: 30-day comparison, segmented by device + browser + date.
```

---

*Built by AfrexAI ⚡ — turning data into decisions.*

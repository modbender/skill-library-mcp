---
domain: twitter-intel
topic: signal-filtering-credibility-trend-detection
priority: high
ttl: 30d
---

# Twitter Intelligence — Best Practices

## Signal Filtering Methodology

### 1. Multi-Layer Noise Reduction
Apply filters sequentially to reduce the tweet corpus to actionable signals:
1. **Language filter** — Restrict to target language(s) using `lang:` operator
2. **Bot filter** — Exclude accounts matching bot heuristics from knowledge/domain.md
3. **Retweet deduplication** — Collapse retweet chains to original tweet; count retweets as amplification metric
4. **Relevance filter** — Score tweet-to-topic semantic similarity; discard below 0.6 threshold
5. **Authority filter** — Weight remaining tweets by source KOL tier (from knowledge/domain.md)

### 2. Signal-to-Noise Ratio Optimization
- Prefer `-is:retweet` for opinion extraction — retweets indicate amplification, not original thought
- Use `is:quote` to capture annotated discourse — quote tweets reveal disagreement, nuance, and counter-narratives
- Filter for `has:links` when seeking evidence-backed claims
- Apply `min_faves:` thresholds proportional to the topic's tweet volume:
  - High-volume topic (>10K tweets/day): `min_faves:50`
  - Medium-volume topic (1K-10K/day): `min_faves:10`
  - Low-volume/niche topic (<1K/day): no minimum — all signals matter

### 3. Temporal Window Selection
- **Breaking news**: Last 1-4 hours — prioritize recency over engagement
- **Trend monitoring**: Last 24-72 hours — balance recency with engagement signals
- **Sentiment baseline**: Last 7-30 days — establish norms before measuring shifts
- **Historical analysis**: Full archive — requires Academic/Pro API access

## Credibility Assessment Framework

### Account Credibility Score (0-100)

Calculate a composite credibility score for each account:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Account age | 15% | <30 days: 0, 30d-1y: 40, 1-3y: 70, 3y+: 100 |
| Follower/following ratio | 15% | <0.5: 20, 0.5-2: 40, 2-10: 70, 10+: 100 |
| Listed count per 1K followers | 15% | <1: 20, 1-5: 50, 5-20: 80, 20+: 100 |
| Original content ratio | 15% | <20%: 20, 20-50%: 50, 50-80%: 80, 80%+: 100 |
| Verified status | 10% | None: 40, Blue: 60, Gold/Grey: 100 |
| Bio completeness | 10% | Empty: 0, Generic: 30, Professional with affiliations: 100 |
| Engagement quality | 10% | Bot-like patterns: 0, Normal: 60, High-quality replies: 100 |
| Posting consistency | 10% | Sporadic/burst: 30, Regular cadence: 70, Daily with variety: 100 |

### Credibility Tiers

| Tier | Score | Treatment |
|------|-------|-----------|
| Authoritative | 80-100 | Primary source — cite directly, high confidence |
| Credible | 60-79 | Reliable source — cite with standard attribution |
| Provisional | 40-59 | Use with caution — require corroboration from higher tier |
| Suspect | 20-39 | Do not cite alone — only as supporting data with corroboration |
| Unreliable | 0-19 | Exclude from analysis — flag if part of coordinated campaign |

### Cross-Referencing Protocol
- **Single-source claim**: Never report. Require 2+ independent Credible-tier sources
- **Controversial claim**: Require 3+ independent sources across different KOL tiers
- **Statistical claim**: Require primary data source or link to verifiable dataset
- **Breaking event**: Allow single Authoritative-tier source with "unconfirmed" label; upgrade after corroboration

## Trend Detection Techniques

### 1. Volume Velocity Analysis
Track tweet volume over sliding windows to detect acceleration:
- Calculate **tweets per hour** for the target topic over the last 72 hours
- Compute **velocity** = (current hour volume) / (average hourly volume over past 72h)
- Thresholds:
  - Velocity 1.5-3x: **Elevated interest** — monitor closely
  - Velocity 3-10x: **Emerging trend** — begin analysis
  - Velocity >10x: **Viral event** — prioritize for immediate briefing

### 2. Hashtag Co-occurrence Mapping
- Track which hashtags appear together in tweets about the target topic
- New co-occurrences signal narrative evolution (e.g., a tech topic suddenly co-occurring with #regulation)
- Build a co-occurrence graph; detect new clusters forming over 24-48h windows

### 3. KOL Cascade Analysis
- Track when a topic moves across KOL tiers:
  - Nano/Micro-KOL discussion first → Macro-KOL pickup → Mega-KOL amplification = organic trend
  - Mega-KOL first → immediate broad amplification without prior Micro-KOL discussion = top-down narrative push
- The **cascade direction** indicates whether a trend is grassroots or manufactured

### 4. Sentiment Shift Detection
- Establish a rolling 7-day sentiment baseline for the target topic
- Detect statistically significant shifts (>2 standard deviations from baseline)
- Categorize shifts:
  - **Gradual drift**: Sentiment changes over days — underlying narrative evolution
  - **Sharp reversal**: Sentiment flips within hours — triggered by a specific event or revelation
  - **Polarization spike**: Average sentiment stays similar but variance increases — growing disagreement

### 5. Geographic & Demographic Spread
- Track when a topic crosses from one geographic region or language community to another
- Use `place_country:` and `lang:` operators to segment
- Cross-community spread is a strong indicator of a trend gaining mainstream traction

## Intelligence Report Structure

### Standard Briefing Format
1. **Executive Summary** — 2-3 sentence overview: what happened, why it matters, confidence level
2. **Key Findings** — Bulleted list of 3-5 main intelligence points, each with source attribution
3. **KOL Positions** — Table of notable KOL statements with credibility tier and reach metrics
4. **Trend Metrics** — Volume, velocity, sentiment data with time-series context
5. **Bot/Inauthenticity Assessment** — Percentage of engagement flagged as inauthentic; impact on findings
6. **Confidence Rating** — Overall confidence: High (80-100%), Medium (50-79%), Low (<50%) with justification
7. **Recommended Actions** — What the user should do with this intelligence; monitoring suggestions

### Confidence Rating Criteria
- **High (80-100%)**: 3+ Authoritative sources, consistent across KOL tiers, minimal bot contamination (<5%)
- **Medium (50-79%)**: 2+ Credible sources, mostly consistent with minor discrepancies, moderate bot presence (5-15%)
- **Low (<50%)**: Single source or conflicting accounts, high bot contamination (>15%), or rapidly evolving situation

---
strategy: twitter-intel
version: 1.0.0
steps: 6
---

# Twitter Intelligence Strategy

## Step 1: Source Curation
- Parse the user's request to identify: **target topic**, **accounts of interest**, **time window**, **geographic scope**, and **desired intelligence type** (trend analysis, KOL tracking, sentiment monitoring, or event coverage)
- IF the request is vague THEN ask one clarifying question to narrow the scope (e.g., "Which industry vertical?" or "Any specific accounts to prioritize?")
- Build initial source lists:
  - **Topic keywords**: Extract 3-7 primary keywords and hashtags relevant to the topic
  - **KOL watchlist**: Identify 5-15 accounts across KOL tiers (from knowledge/domain.md) that are relevant to the topic
  - **Exclusion list**: Identify known bot accounts, spam hashtags, and noise sources to exclude
- Construct Twitter/X API search queries using operators from knowledge/domain.md:
  - Primary query: topic keywords + `-is:retweet` + `lang:` filter
  - KOL query: `from:` operators for watchlist accounts + topic keywords
  - Trend query: hashtag co-occurrences + `min_faves:` threshold
- Set the temporal window based on intelligence type:
  - Breaking event: last 1-4 hours
  - Trend monitoring: last 24-72 hours
  - Baseline establishment: last 7-30 days

## Step 2: Signal Filtering
- Execute queries and collect raw tweet corpus
- Apply multi-layer noise reduction from knowledge/best-practices.md:
  1. Remove exact duplicates and retweet chains — collapse to original tweets with amplification counts
  2. Run bot detection heuristics from knowledge/domain.md on all accounts in the corpus
  3. Score each account using the Account Credibility Score framework (knowledge/best-practices.md)
  4. Filter tweets by semantic relevance to the target topic — discard below 0.6 similarity threshold
  5. Apply engagement thresholds proportional to topic volume
- Tag each remaining tweet with metadata:
  - Source credibility tier (Authoritative / Credible / Provisional / Suspect)
  - Bot probability score (0-100%)
  - Relevance score (0.6-1.0)
- IF >15% of engagement is flagged as bot-driven THEN flag the topic for inauthenticity risk
- VERIFY against anti-pattern #8 (knowledge/anti-patterns.md): ensure bot engagement is separated from organic metrics

## Step 3: Opinion Extraction
- For each high-signal tweet (credibility tier >= Provisional, relevance >= 0.7):
  - Extract the **stated position** — what claim or opinion does the tweet express?
  - Classify **sentiment** — positive / negative / neutral / mixed toward the target topic
  - Detect **tone markers** — check for sarcasm, irony, or satire per anti-pattern #5 (knowledge/anti-patterns.md)
  - IF the tweet is a quote tweet THEN analyze as composite (original + commentary) per anti-pattern #6
  - IF the tweet is part of a thread THEN retrieve full thread via `conversation_id` and analyze holistically per anti-pattern #7
- Group extracted opinions into **stance clusters**:
  - Supporters (positive sentiment toward topic/entity)
  - Critics (negative sentiment toward topic/entity)
  - Neutral analysts (factual commentary without clear stance)
  - Contrarians (minority positions that diverge from the dominant narrative)
- For each cluster, identify the **strongest voice** — the highest-credibility KOL representing that position
- Calculate **opinion distribution** — percentage of credible voices in each cluster

## Step 4: Trend Detection
- Apply Volume Velocity Analysis from knowledge/best-practices.md:
  - Calculate tweets per hour over the analysis window
  - Compute velocity relative to 72-hour average
  - IF velocity > 3x THEN classify as emerging trend
  - IF velocity > 10x THEN classify as viral event — prioritize for immediate briefing
- Execute Hashtag Co-occurrence Mapping:
  - Build co-occurrence graph for hashtags in the filtered corpus
  - Identify new hashtag clusters forming in the last 24-48 hours
  - Flag unexpected co-occurrences (e.g., tech topic + political hashtag = narrative hijacking risk)
- Perform KOL Cascade Analysis:
  - Track the chronological spread across KOL tiers
  - IF Micro-KOL → Macro-KOL → Mega-KOL cascade THEN classify as organic trend
  - IF Mega-KOL-first or simultaneous cross-tier activation THEN flag as top-down narrative push per anti-pattern #9
- Run Sentiment Shift Detection:
  - Compare current sentiment against the 7-day rolling baseline
  - IF shift > 2 standard deviations THEN classify the shift type (gradual drift, sharp reversal, or polarization spike)
- VERIFY against anti-pattern #10: check for astroturfing signatures in any detected trends

## Step 5: Insight Synthesis
- Merge findings from Steps 2-4 into a coherent intelligence picture:
  - Connect opinion clusters (Step 3) with trend dynamics (Step 4)
  - Identify **causal narratives**: what events or statements triggered the observed patterns?
  - Assess **trajectory**: is the trend accelerating, plateauing, or declining?
  - Evaluate **cross-topic spillover**: is the topic affecting or being affected by adjacent conversations?
- Generate confidence ratings using criteria from knowledge/best-practices.md:
  - Count corroborating sources across credibility tiers
  - Calculate bot contamination percentage
  - Assess source diversity (single echo chamber vs. multi-community signal)
- Identify **intelligence gaps** — what questions remain unanswered? What data would increase confidence?
- VERIFY against anti-pattern #11: ensure the assessment includes baseline context, not just the latest snapshot
- VERIFY against anti-pattern #12: caveat all findings as Twitter/X-specific; do not extrapolate to general public opinion

## Step 6: Intelligence Briefing Output
- Structure the output following the Standard Briefing Format from knowledge/best-practices.md:
  1. **Executive Summary** — 2-3 sentences: what the intelligence reveals, why it matters, confidence level
  2. **Key Findings** — 3-5 bulleted intelligence points, each with:
     - The finding itself
     - Source attribution (KOL name, credibility tier, tweet link)
     - Corroboration count (how many independent sources support this)
  3. **KOL Positions** — Table of notable KOL statements:
     - Account handle | Credibility tier | Follower count | Position summary | Tweet link
  4. **Trend Metrics** — Quantitative data:
     - Tweet volume and velocity (with time-series if available)
     - Sentiment distribution (% positive / negative / neutral)
     - Top hashtags and co-occurrences
     - Geographic spread (if detectable)
  5. **Bot & Inauthenticity Assessment** — Percentage of flagged engagement; impact on findings
  6. **Confidence Rating** — High / Medium / Low with explicit justification
  7. **Recommended Actions** — What the user should do next:
     - Accounts to watch for follow-up developments
     - Suggested monitoring frequency
     - Cross-platform validation recommendations if confidence is Medium or Low
- SELF-CHECK before delivery:
  - Are all claims backed by attributed sources?
  - Have bot-contaminated metrics been flagged?
  - Is temporal context (timestamps, trend direction) included throughout?
  - Does the briefing avoid the 12 anti-patterns from knowledge/anti-patterns.md?
  - IF any check fails THEN loop back to the relevant step and re-analyze

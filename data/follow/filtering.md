# Filtering Rules

## The Problem

Following without filtering = drowning in noise. The goal is **signal, not firehose**.

---

## Filtering Strategies

### Keyword Matching
- Exact keywords for precision
- Synonyms for coverage ("layoffs" = "workforce reduction")
- Negative keywords to exclude topics

### Relevance Scoring
Score each piece of content:
- Matches priority keywords: +2
- From high-priority source: +2  
- Mentions known entities: +1
- Routine/promotional content: -2
- Already seen similar: -3

Only surface content above threshold.

### Pattern Detection
- Unusual posting frequency (went silent, suddenly active)
- Multiple sources converging on same topic
- Sentiment shift from positive to negative
- First mention of new entity

### Source-Level Filters
Per source, define:
- Content types to include/exclude
- Time windows (business hours only, etc.)
- Minimum engagement thresholds

---

## Deduplication

The same news appears everywhere. Dedupe by:

1. **URL matching** — same link = same story
2. **Title similarity** — fuzzy match headlines
3. **Entity extraction** — same company + same event = likely duplicate
4. **Time window** — stories within 24h about same topic cluster together

When duplicates found:
- Keep the BEST source (user's preferred, most detail)
- Note "also mentioned by: X, Y, Z"

---

## Noise Patterns to Filter

| Pattern | Example | Action |
|---------|---------|--------|
| Promotional | "Check out my new course" | Skip unless explicitly wanted |
| Retweets | RT without commentary | Skip |
| Automated | Daily stats, scheduled posts | Skip |
| Ephemeral | "Good morning!" | Skip |
| Old news | Rehashing known information | Skip |

---

## Signal Patterns to Boost

| Pattern | Example | Action |
|---------|---------|--------|
| Announcements | "We just launched..." | Immediate alert |
| Contrarian | Opinion against consensus | Flag for review |
| Data/numbers | Revenue, metrics, research | Extract and archive |
| Predictions | Claims about future | Track for validation |
| Personnel | Hiring, departures, promotions | Alert if relevant entity |

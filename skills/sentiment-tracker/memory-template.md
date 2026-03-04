# Memory Template — Sentiment Analysis

## Main Memory (~/sentiment-analysis/memory.md)

Create with this structure:

```markdown
# Sentiment Analysis Memory

## Status
status: ongoing
last: YYYY-MM-DD
integration: pending

## Preferences
report_style: detailed | summary
alert_threshold: 20
default_timeframe: 7d

## Entities
<!-- List of tracked entities, one per line -->
<!-- Format: name | type | schedule | platforms -->

| Entity | Type | Schedule | Platforms |
|--------|------|----------|-----------|
| Example Brand | brand | weekly | twitter, reddit |

## Platform Priorities
<!-- Which platforms matter most for their domain -->
<!-- Order by importance -->

1. twitter
2. reddit
3. youtube
4. hackernews
5. news

## Notes
<!-- Observations about their monitoring patterns -->
<!-- Things they care about, thresholds they've mentioned -->

---
*Updated: YYYY-MM-DD*
```

## Entity Files (~/sentiment-analysis/entities/{name}.md)

One file per tracked entity:

```markdown
# {Entity Name}

## Config
type: brand | product | crypto | competitor | topic
keywords: keyword1, keyword2, "exact phrase"
platforms: twitter, reddit, youtube, hackernews, news
schedule: daily | every-3-days | weekly | manual
alert_on: negative_spike | viral_negative | new_theme

## Baseline
<!-- Updated after each analysis -->
avg_volume_7d: 0
avg_positive: 0%
avg_negative: 0%
avg_neutral: 0%

## History
<!-- Last 5 analyses, newest first -->

### YYYY-MM-DD
- Volume: X mentions
- Sentiment: X% pos / X% neg / X% neutral
- Trend: ↗️ | ↘️ | →
- Notable: [key observation]

## Themes
<!-- Recurring themes across analyses -->

| Theme | First Seen | Frequency | Sentiment |
|-------|------------|-----------|-----------|
| Example | 2024-01-15 | 12 times | mostly negative |

---
*Updated: YYYY-MM-DD*
```

## Reports (~/sentiment-analysis/reports/YYYY-MM-DD-{entity}.md)

Generated after each analysis:

```markdown
# Sentiment Report: {Entity}

**Period:** YYYY-MM-DD to YYYY-MM-DD
**Generated:** YYYY-MM-DD HH:MM

## Summary

📊 **{Entity}**
🕐 Period: Last X days
📈 Volume: X mentions found
😊 Positive: XX% | 😠 Negative: XX% | 😐 Neutral: XX%

**Trend:** ↗️ Improving | ↘️ Declining | → Stable
**Change:** +X% vs previous period

## Top Themes

| Theme | Mentions | Sentiment | Change |
|-------|----------|-----------|--------|
| Theme 1 | XX | XX% neg | ↗️ +X% |
| Theme 2 | XX | XX% pos | → |

## Notable Posts

### Most Engaging
> "[Quote]"
> — Platform, XX likes/upvotes, [link]

### Most Negative
> "[Quote]"
> — Platform, [link]

### Most Positive
> "[Quote]"
> — Platform, [link]

## Source Breakdown

| Platform | Mentions | Sentiment |
|----------|----------|-----------|
| Twitter | XX | XX% pos |
| Reddit | XX | XX% pos |

## Alerts Triggered
<!-- If any thresholds were crossed -->

- ⚠️ Negative spike: XX% above baseline
- None this period

---
*Analysis based on X sources, Y total posts sampled*
```

## Alerts (~/sentiment-analysis/alerts.md)

Log of triggered alerts:

```markdown
# Alert History

## Active Alerts
<!-- Alerts that haven't been acknowledged -->

### YYYY-MM-DD HH:MM — {Entity}
**Type:** negative_spike
**Details:** Negative sentiment at 45% vs 22% baseline
**Trigger:** Viral post about [topic]
**Status:** pending

## Resolved
<!-- Acknowledged or expired alerts -->

### YYYY-MM-DD — {Entity}
**Type:** viral_negative
**Resolution:** User acknowledged, sentiment returned to baseline
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Active monitoring | Run scheduled checks, gather data |
| `paused` | User paused tracking | Skip scheduled checks, keep data |
| `complete` | User stopped tracking | Archive data, no checks |

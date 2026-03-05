# Lead Scoring — Reference

*How the agent scores and prioritizes leads.*

---

## Overview

Every lead gets a score from 0-100. The score determines priority, sequence selection, and how the agent allocates attention. Scores are recalculated on every significant event.

---

## Scoring Weights (Defaults)

These defaults come from config.yaml and can be customized per user.

| Signal | Default Points | How Agent Evaluates |
|--------|---------------|-------------------|
| **Industry match** | +15 | Compare lead's industry to `business.ideal_client` in config. Exact match or close match = full points. |
| **Pain signals** | +20 per signal (max 3) | Each pain signal identified during lead add. Max +60 from pain signals alone. |
| **Company size fit** | +10 | If known, does company size match ideal client? Agent uses judgment based on config description. |
| **Email opened** | +5 | Lead opened an email (requires tracking capability) |
| **Email clicked** | +10 | Lead clicked a link in email (requires tracking) |
| **Email replied** | +25 | Lead replied to any email. Biggest single signal. |
| **Website quality** | +10 | If lead URL provided, agent assesses professionalism. Professional site with clear revenue model = points. |
| **Social presence** | +5 | Active LinkedIn/Twitter with relevant content = points. |

**Maximum possible score:** 15 + 60 + 10 + 5 + 10 + 25 + 10 + 5 = 140 → capped at 100

---

## Score Classifications

| Range | Classification | Emoji | Behavior |
|-------|---------------|-------|----------|
| 80-100 | 🔥 Hot | 🔥 | Priority follow-up. Top of morning briefing. Agent flags for immediate action. |
| 60-79 | 🟡 Warm | 🟡 | Standard sequence. Regular follow-up cadence. |
| 40-59 | 🔵 Cool | 🔵 | Nurture sequence. Longer delays between touches. |
| 0-39 | ⚪ Cold | ⚪ | Long-term nurture. Monthly check-in at most. |

---

## When Scores Recalculate

| Event | What Changes |
|-------|-------------|
| Lead created | Initial score from profile data (industry, pain signals, company size, website, social) |
| Pain signal added | +20 per new signal |
| Email sent | No change (sending doesn't indicate interest) |
| Email opened | +5 |
| Email clicked | +10 |
| Email replied | +25 + sentiment bonus |
| Status changed to qualified | Locked minimum of 60 |
| Status changed to call_booked | Locked minimum of 80 |
| Manual adjustment | User override — agent respects it |

---

## Sentiment Bonus on Reply

When a lead replies, the base +25 is adjusted by sentiment:

| Sentiment | Bonus | Total from Reply |
|-----------|-------|-----------------|
| Interested | +25 + 10 | +35 |
| Question | +25 + 5 | +30 |
| Objection | +25 + 0 | +25 |
| Not interested | Score drops to 10 | Reset |
| Unsubscribe | Score drops to 0 | Reset |

---

## Score Decay (Optional)

If the user enables score decay in config:
- Leads with no activity for 14+ days: -5 points
- Leads with no activity for 30+ days: -10 points
- Minimum score after decay: 5 (never reaches 0 from decay alone)

This is OFF by default. Enable with `scoring.decay_enabled: true` in config.

---

## Agent Scoring Guidelines

The agent should use judgment, not just data, when scoring:

**Industry match is fuzzy.** If the config says "SaaS founders" and the lead is a tech startup founder, that's close enough for full points. If the lead is a restaurant owner, that's 0 points. Agent uses common sense.

**Pain signals are the user's words.** When the user says "they're hiring on Upwork" or "their website looks like 2015" — those are pain signals. The agent stores them verbatim and counts them for scoring.

**Website quality is subjective.** The agent should look at the URL (if browser access is available) or use the user's description. A polished site with clear pricing suggests a real business worth pursuing.

**Don't over-index on engagement signals.** An email open might be a bot. A click might be accidental. But a reply is always significant. That's why reply is weighted 5x more than an open.

---

*Lead scoring is a compass, not a GPS. It tells the agent where to focus attention. The user makes the final call.* 🧭

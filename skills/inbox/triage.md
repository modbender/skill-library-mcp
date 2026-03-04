# Triage & Prioritization

## Four-Bucket Classification

Every incoming item goes into one bucket:

| Bucket | Definition | Action |
|--------|------------|--------|
| **Requires My Decision** | Only I can respond/decide | Surface immediately |
| **Requires My Awareness** | Should know, but no action | Daily digest |
| **Can Be Delegated** | Someone else should handle | Route with context |
| **Noise** | No value | Auto-archive |

Run this classification BEFORE showing anything to user.

## Priority Scoring

Score items by combining factors:

**Urgency signals:**
- Explicit deadline mentioned
- Time-sensitive language ("ASAP", "by EOD")
- Same person tried multiple channels
- Follow-up to something user promised
- Escalation tone detected

**Importance signals:**
- Sender relationship (boss, key client, close contact)
- Financial implications mentioned
- Blocking other people's work
- Strategic vs operational content
- History of important exchanges with sender

## Cross-Channel Detection

When same person contacts through multiple channels within 24h:
1. Flag as high-urgency
2. Link the attempts together
3. Present as single item: "X reached out via email, then Slack, then WhatsApp"

## Daily "Must-See" Digest

Limit to **maximum 5-7 items**. Include:
1. Items requiring decision today
2. Items with deadlines within 48h
3. Items from high-priority senders
4. Aging items about to become urgent

Everything else exists but stays out of primary view.

## Stale Item Surfacing

Track item age and escalate:
- 3 days: "Still pending response"
- 7 days: "Approaching concerning age"
- 14 days: "Consider inbox bankruptcy or batch response"

Detect avoidance patterns: same item snoozed 3+ times → surface for confrontation.

## Time-Sensitive Flagging

When deadline detected:
- Show countdown: "Response expected within 4 hours"
- Calculate response buffer: account for compose time
- Escalate at 50% time remaining if untouched

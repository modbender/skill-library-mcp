---
name: life-radar
description: Build a concise “what needs action now” daily brief by aggregating reminders from multiple channels (email, calendar, SMS/iMessage, weather, and task notes) and prioritizing them into Must-do / Should-do / Nice-to-have. Use when the user asks for daily planning, action digest, inbox triage summary, or proactive reminders across sources.
---

# Life Radar

Generate an action-first digest, not a raw data dump.

If the user asks from a specific role perspective (CEO / manager / employee), read `references/modes.md` and adapt prioritization/output accordingly.

## Output format

Always output in this structure:

1. **Must-do (today)** — max 3 items
2. **Should-do (soon)** — max 5 items
3. **Nice-to-have** — max 3 items
4. **Suggested next actions** — 1-line commands the user can say next

Each item must include:
- What happened
- Why it matters
- Deadline/time window (or “unspecified”)

## Priority rules

Classify with this order:

- **P0 Must-do**
  - Payment due / account risk / security alert
  - Meeting in <2h
  - Time-sensitive message requiring response today
- **P1 Should-do**
  - Meeting or task in 24-72h
  - Follow-up pending from important contact
  - Logistics prep (travel, weather-impact, documents)
- **P2 Nice-to-have**
  - Low urgency updates
  - Optional optimization tasks

If uncertain, downgrade priority and mark uncertainty explicitly.

## Source collection flow

Collect only what is available in current environment; skip unavailable sources without failing.

1. Calendar events (today + tomorrow)
2. Recent urgent messages (SMS/iMessage/email/DM)
3. Billing or financial notifications
4. Weather impact for planned outings
5. Existing tasks/notes (if connected)

## Time-window defaults

- If user asks "today": prioritize 0-24h window
- If user asks "this week": prioritize 7-day window, still keep Must-do today-centric
- If user asks without a window: default to today + next 72h

## Safety and quality

- Redact secrets, tokens, and full account numbers.
- Avoid hallucinating dates or amounts; mark as unknown when missing.
- Prefer fewer high-confidence items over many noisy items.
- If no meaningful items, return: “Today looks clear. No urgent actions detected.”

## Trigger phrases

Treat these as strong triggers:
- “今天有什么要处理”
- “给我每日行动清单”
- “帮我做个优先级摘要”
- “扫一下我今天的事情”
- “daily action digest”

---
name: shelter
description: >
  Connect to your Shelter financial data. Check safe-to-spend, predict cash crunches,
  find zombie subscriptions, simulate purchases, get AI coaching, and ask Guardian AI
  about your money. Read-only access to real bank data via Plaid.
version: 1.0.0
metadata:
  openclaw:
    emoji: "\U0001F6E1"
    requires:
      env: [SHELTER_API_KEY]
      bins: [curl]
    primaryEnv: SHELTER_API_KEY
    homepage: https://shelter.money
---

# Shelter

Connect to a user's Shelter financial data via the Agent API. All endpoints return JSON. You are a financial coach — interpret the data, don't just dump it.

## Authentication

Every request needs two things:

- **Header**: `X-Shelter-Key: $SHELTER_API_KEY`
- **Base URL**: `$SHELTER_API_URL` (default: `https://api.shelter.money/agent`)

All examples below use these variables. Confirm they're set before making any call.

## Decision Tree

Use this to pick the right endpoint for the user's question:

| User wants to know... | Endpoint | Cost |
|------------------------|----------|------|
| "How am I doing?" / "Can I spend today?" | `GET /v1/status` | Cheap |
| "When do I run out of money?" | `GET /v1/runway` | Cheap |
| "What does next week look like?" | `GET /v1/forecast` | Medium |
| "Any problems I should know about?" | `GET /v1/alerts` | Medium |
| "Where am I wasting money?" | `GET /v1/opportunities` | Medium |
| "Give me the full picture" | `GET /v1/context` | Medium |
| "Can I afford X?" | `POST /v1/affordability` | Medium |
| "Give me today's coaching" | `GET /v1/coach/daily` | Medium |
| "Help me with [debt/savings/bills]" | `GET /v1/coach/advice?topic=` | Medium |
| Complex/nuanced question | `POST /v1/ask` | Expensive |

**Always start with the cheapest endpoint that answers the question.** Only use `/v1/ask` when structured endpoints can't answer it.

---

## Endpoints

### Quick Checks

These are fast, cached, and cheap. Use them first.

#### GET /v1/status

The user's current financial health snapshot.

**When to use**: User asks how they're doing, wants safe-to-spend, or you need a quick health check before answering.

**When NOT to use**: User wants a multi-day forecast or detailed breakdown.

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/status"
```

**Key response fields**:
- `safeToSpend` — dollars available after upcoming commitments
- `safeDays` — days of runway at current burn rate
- `stressLevel` — `low` | `medium` | `high` | `critical`
- `upcomingIncome` — `{ amount, date, source }` or null
- `nextCommitment` — `{ name, amount, dueDate }` or null
- `confidence` — 0-100 data quality score
- `explanation` — human-readable summary

**How to summarize**: Lead with safe-to-spend and stress level. Mention next income if it's within 3 days. Flag low confidence (<50) as "limited data."

---

#### GET /v1/runway

How long until the money runs out.

**When to use**: User asks about runway, burn rate, or when they'll be broke.

**When NOT to use**: User wants day-by-day detail (use forecast instead).

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/runway"
```

**Key response fields**:
- `safeDays` — days of remaining runway
- `burnRate` — average daily spending (last 30 days)
- `breathingRoom` — buffer after commitments
- `nextCrunchDate` — ISO date when balance goes negative (or null)
- `nextCrunchAmount` — commitments due around the crunch
- `daysUntilCrunch` — days until the crunch (or null)
- `explanation` — human-readable summary

**How to summarize**: State days of runway and daily burn rate. If a crunch is coming, warn with the date and amount. If no crunch, reassure them.

---

### Deep Analysis

More detailed endpoints. Use when quick checks aren't enough.

#### GET /v1/forecast

14-day day-by-day financial projection.

**When to use**: User asks what the next week/two weeks look like, or wants to see when specific bills hit.

**When NOT to use**: User just wants today's snapshot (use status).

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/forecast"
```

**Key response fields**:
- `forecast[]` — array of daily projections: `{ date, projectedBalance, events[], isCrunch, isTight }`
- `summary` — `{ crunchDays, tightDays, lowestBalance, highestBalance }`

**How to summarize**: Highlight crunch days (negative balance) and tight days first. Mention the lowest balance and when it occurs. List significant events (big bills, income).

---

#### GET /v1/alerts

Active warnings: zombie subscriptions, spending spikes, upcoming bills.

**When to use**: User asks what needs attention, or you want to proactively surface problems.

**When NOT to use**: User is asking about a specific topic (use advice instead).

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/alerts"
```

**Key response fields**:
- `alerts[]` — `{ id, type, severity, title, description, amount?, daysUntil?, evidence? }`
- `count` — total alerts
- `hasCritical` — boolean

**How to summarize**: Critical alerts first, then warnings, then info. Be specific about amounts and dates. If `hasCritical` is true, lead with urgency.

---

#### GET /v1/opportunities

Places the user is wasting money or could save.

**When to use**: User asks about saving money, zombie subscriptions, or spending optimization.

**When NOT to use**: User needs a forecast or health check.

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/opportunities"
```

**Key response fields**:
- `opportunities[]` — `{ id, type, title, description, potentialSavings, difficulty, actionUrl? }`
- `totalPotentialSavings` — annual savings if all opportunities are acted on

**How to summarize**: Lead with total potential savings. List opportunities easiest-first. Include action URLs when available.

---

#### GET /v1/context

Full financial overview combining status, alerts, spending insights, and upcoming events.

**When to use**: User wants the big picture, or you need comprehensive context to answer a complex question.

**When NOT to use**: A more specific endpoint can answer the question. This is heavy.

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/context"
```

**Key response fields**:
- `snapshot` — `{ availableBalance, breathingRoom, daysOfBreathingRoom, upcomingIncome, commitments[] }`
- `highlights` — `{ urgentActions, biggestOpportunities, recentWins }`
- `alerts[]` — same format as alerts endpoint
- `spendingInsights` — `{ summary, byCategory, topMerchants, anomalies }`
- `upcomingEvents[]` — `{ type, name, amount, currentDate, priority }`

**How to summarize**: Start with available balance and breathing room. Highlight urgent actions. Mention recent wins (positive reinforcement). Dive into spending insights only if the user asks.

---

#### POST /v1/affordability

Simulate whether the user can afford a specific purchase.

**When to use**: User asks "Can I afford X?" with a specific dollar amount.

**When NOT to use**: User is asking generally about spending (use status).

```bash
curl -s -X POST -H "X-Shelter-Key: $SHELTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount": 200, "description": "New headphones"}' \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/affordability"
```

**Key response fields**:
- `canAfford` — boolean
- `safeToSpendAfter` — remaining safe-to-spend after the purchase
- `impactOnRunway` — how many fewer days of runway
- `recommendation` — AI-generated advice
- `confidence` — 0-100

**How to summarize**: Give a clear yes/no first, then explain the impact on their runway and safe-to-spend.

---

### Coaching

AI-generated coaching messages tailored to the user's financial situation.

#### GET /v1/coach/daily

Today's personalized coaching message.

**When to use**: Start of a session, or user asks for their daily update.

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/coach/daily"
```

**Key response fields**:
- `messageType` — `daily_checkin` | `alert` | `celebration` | `suggestion` | `warning`
- `headline` — short headline
- `body` — 2-4 sentences of coaching with specific numbers
- `actions[]` — `{ label, actionType, actionTarget }`
- `tone` — `encouraging` | `urgent` | `celebratory` | `supportive`

**How to summarize**: Present the headline and body naturally. Suggest the actions conversationally. Match the tone.

---

#### GET /v1/coach/advice?topic=

Deep-dive coaching on a specific financial topic.

**When to use**: User asks for help with a specific area.

**Topics**: `debt`, `savings`, `bills`, `subscriptions`, `negotiation`, `general`

```bash
curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/coach/advice?topic=debt"
```

**Response format**: Same as daily coaching (headline, body, actions, tone).

**How to summarize**: Present the advice naturally. If the user didn't specify a topic, ask which area they want help with or default to `general`.

---

### Guardian AI Chat

#### POST /v1/ask

Ask Guardian AI a free-form question about the user's finances. This is the most expensive endpoint — use it as a last resort when structured endpoints can't answer.

**When to use**: Nuanced questions, planning advice, or follow-ups that need reasoning.

**When NOT to use**: Questions answerable by structured endpoints above. Always try those first.

```bash
curl -s -X POST -H "X-Shelter-Key: $SHELTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "What should I prioritize right now?"}' \
  "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/ask"
```

**Key response fields**:
- `response` — Guardian AI's natural language answer
- `confidence` — 0-100
- `relatedAlerts[]` — IDs of relevant alerts
- `limitRemaining` — remaining `/ask` calls for the day

**How to summarize**: Present Guardian's response directly. If confidence is low (<50), note the uncertainty. If `limitRemaining` is low, mention it so the user knows.

---

## Rate Limits

| Endpoint group | Free tier | Premium tier |
|----------------|-----------|--------------|
| Status, Runway | 60/hour | 60/hour |
| Forecast, Alerts, Opportunities, Context, Affordability | 60/hour | 60/hour |
| Coach (daily, advice) | 60/hour | 60/hour |
| Ask (Guardian AI) | 5/day | 100/day |

## Error Codes

| Code | Meaning | What to do |
|------|---------|------------|
| 401 | Invalid or missing API key | Check `SHELTER_API_KEY` is set and valid |
| 403 | Key lacks required scope | User needs to update key permissions at shelter.money |
| 429 | Rate limit exceeded | Wait and retry. Check `Retry-After` header |
| 500 | Server error | Wait a moment and retry |

If you get a 401, tell the user to check their API key. Don't retry auth errors.

## Setup

1. **Sign up** at [shelter.money](https://shelter.money)
2. **Connect bank accounts** via Plaid (takes ~60 seconds)
3. **Create an Agent API key** at [shelter.money/settings/api-keys](https://shelter.money/settings/api-keys)
4. **Set your environment variable**:
   ```bash
   export SHELTER_API_KEY="wv_your_key_here"
   ```
5. **Test the connection**:
   ```bash
   curl -s -H "X-Shelter-Key: $SHELTER_API_KEY" \
     "${SHELTER_API_URL:-https://api.shelter.money/agent}/v1/status"
   ```

## Security

- **Read-only** — Shelter can see transactions and balances but can never move money
- **Scoped API keys** — you choose exactly what the key can access
- **No raw bank data** — the API returns computed insights (safe-to-spend, alerts), not raw transactions
- **Keys are hashed** — the secret is never stored in plain text
- **Audit logging** — every API call is logged
- **Instant revocation** — disable any key from your settings

## Data Reference

For field-by-field documentation of all response shapes, see [`references/DATA_MODEL.md`](references/DATA_MODEL.md).

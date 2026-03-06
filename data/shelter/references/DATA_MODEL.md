# Agent API Data Model Reference

Field-by-field guide to the Shelter Agent API response shapes. Use this when interpreting data or building integrations.

## Status (`/v1/status`)

| Field | Type | Description |
|-------|------|-------------|
| `safeToSpend` | number | Money available after all upcoming commitments |
| `safeDays` | integer | How many days the user can sustain current spending |
| `stressLevel` | string | `low` (>7 days), `medium` (3-7), `high` (1-3), `critical` (0 or negative) |
| `upcomingIncome` | object\|null | `{ amount, date, source }` — next expected income |
| `nextCommitment` | object\|null | `{ name, amount, dueDate }` — soonest upcoming bill |
| `confidence` | integer | 0-100 data quality score (accounts + income + commitments) |
| `explanation` | string | Human-readable summary of the status |

## Runway (`/v1/runway`)

| Field | Type | Description |
|-------|------|-------------|
| `safeDays` | integer | Same as status — days of remaining runway |
| `burnRate` | number | Average daily spending over last 30 days |
| `breathingRoom` | number | Same as safeToSpend — buffer after commitments |
| `nextCrunchDate` | string\|null | ISO date when balance is projected to go negative |
| `nextCrunchAmount` | number\|null | Total commitments due around the crunch date |
| `daysUntilCrunch` | integer\|null | Days until the projected crunch |
| `explanation` | string | Human-readable runway summary |

## Forecast (`/v1/forecast`)

Response contains `forecast` (array) and `summary` (object).

### Forecast day

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | ISO date for this day |
| `projectedBalance` | number | Predicted balance at end of day |
| `events` | array | `[{ type, name, amount }]` — bills, subscriptions, income |
| `isCrunch` | boolean | Balance goes negative on this day |
| `isTight` | boolean | Balance is dangerously low on this day |

### Summary

| Field | Type | Description |
|-------|------|-------------|
| `crunchDays` | integer | Number of days with negative balance |
| `tightDays` | integer | Number of days with dangerously low balance |
| `lowestBalance` | number | Minimum projected balance in the 14-day window |
| `highestBalance` | number | Maximum projected balance in the 14-day window |

## Alerts (`/v1/alerts`)

| Field | Type | Description |
|-------|------|-------------|
| `alerts` | array | List of alert objects |
| `count` | integer | Total number of alerts |
| `hasCritical` | boolean | Whether any critical alerts exist |

### Alert object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique alert identifier |
| `type` | string | Alert category (e.g. `zombie_billing`, `spending_spike`) |
| `severity` | string | `critical` — requires immediate action |
| | | `warning` — needs attention soon |
| | | `info` — informational observation |
| `title` | string | Short alert headline |
| `description` | string | Detailed explanation |
| `amount` | number? | Dollar amount involved (if applicable) |
| `daysUntil` | integer? | Days until the event (if applicable) |
| `evidence` | string? | Supporting data for the alert |

## Opportunities (`/v1/opportunities`)

| Field | Type | Description |
|-------|------|-------------|
| `opportunities` | array | List of opportunity objects |
| `totalPotentialSavings` | number | Sum of all potential annual savings |

### Opportunity object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique opportunity identifier |
| `type` | string | `zombie_subscription` — being charged for unused service |
| | | `low_value_subscription` — poor value relative to cost |
| | | `bill_move` — can improve cash flow by changing due date |
| | | `spending_reduction` — category where spending could be cut |
| `title` | string | Short description of the opportunity |
| `description` | string | Detailed explanation with numbers |
| `potentialSavings` | number | Estimated annual savings in dollars |
| `difficulty` | string | `easy`, `medium`, or `hard` |
| `actionUrl` | string? | Direct link to cancel or take action |

## Coach Messages (`/v1/coach/daily`, `/v1/coach/advice`)

| Field | Type | Description |
|-------|------|-------------|
| `messageType` | string | `daily_checkin`, `alert`, `celebration`, `suggestion`, `warning` |
| `headline` | string | Short headline (max ~50 chars) |
| `body` | string | 2-4 sentences of coaching advice with specific numbers |
| `actions` | array | `[{ label, actionType, actionTarget }]` |
| `tone` | string | `encouraging`, `urgent`, `celebratory`, `supportive` |

## Context (`/v1/context`)

Full financial overview combining multiple data sources.

| Field | Type | Description |
|-------|------|-------------|
| `snapshot.availableBalance` | number | Total available across all accounts |
| `snapshot.breathingRoom` | number | Same as safeToSpend |
| `snapshot.daysOfBreathingRoom` | integer | Same as safeDays |
| `snapshot.upcomingIncome` | object\|null | `{ amount, date, source }` |
| `snapshot.commitments` | array | `[{ name, amount, dueDate, type }]` |
| `highlights` | object | `{ urgentActions, biggestOpportunities, recentWins }` |
| `alerts` | array | Same format as alerts endpoint |
| `spendingInsights` | object | `{ summary, byCategory, topMerchants, anomalies }` |
| `upcomingEvents` | array | `[{ type, name, amount, currentDate, priority }]` |

## Affordability (`/v1/affordability`)

| Field | Type | Description |
|-------|------|-------------|
| `canAfford` | boolean | Whether the purchase is safe |
| `safeToSpendAfter` | number | Remaining safe-to-spend after the purchase |
| `impactOnRunway` | number | Days of runway lost |
| `recommendation` | string | AI-generated advice about the purchase |
| `confidence` | integer | 0-100 confidence score |

## Ask (`/v1/ask`)

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Guardian AI's natural language answer |
| `confidence` | integer | 0-100 confidence in the response |
| `relatedAlerts` | array | IDs of alerts relevant to the question |
| `limitRemaining` | integer | Remaining `/ask` calls for the day |

### When to use `/ask`

Use for natural language follow-ups like:
- "Can I afford a $200 purchase this week?"
- "What should I prioritize right now?"
- "How do I get out of this cash crunch?"
- "What's my biggest financial risk?"

The `/ask` endpoint is rate-limited (5/day free, 100/day premium), so use the structured endpoints first and save `/ask` for nuanced questions.

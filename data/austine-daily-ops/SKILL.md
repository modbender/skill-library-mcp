---
name: austine-daily-ops
description: Daily execution and trip-ops command system for Austine. Use when asked to run daily brief/checklist/status workflows, track priorities, or plan and procure trip logistics (transport, lodging, reservations, vendor quotes, recommendation + decision handoff).
---

# Austine Daily Ops

## Overview
Run Austine’s day-to-day operating cadence with concise, action-first outputs, and handle travel operations like a sourcing assistant (options scan, quote gathering, recommendation, and execution handoff).

## Core Capabilities

### 1) Daily execution cadence
Use this pattern for daily operations asks.
- Output max 5 bullets unless user asks for depth.
- Always include: current status, blocker (or "No blocker"), next action.
- Prefer concrete actions over commentary.

When asked for daily planning:
1. List Top 3 priorities.
2. List next 72h critical deadlines/reminders.
3. Suggest one automation and one quick win (<15 min).
4. End with “next action I’ll take.”

### 2) Trip operations management
Use this for travel planning/procurement tasks.

Workflow:
1. **Gather required constraints**
   - date/time window
   - origin/destination
   - party size + baggage
   - budget ceiling
   - comfort constraints (max transfers, private/shared, etc.)
2. **Source options**
   - public transport first (bus/train/shuttle)
   - then private transfers/taxi operators
3. **Quote structure (normalized)**
   - provider
   - price + currency
   - inclusions/exclusions
   - cancellation terms
   - pickup/drop details
   - confidence/risk note
4. **Recommend**
   - provide best value, best convenience, and best fallback
   - state trade-offs clearly in 1 line each
5. **Decision handoff**
   - ask for one explicit choice (Option A/B/C)
   - after user chooses, prepare exact next step/message draft

### 3) Vendor follow-up mode
When waiting for confirmations (driver details, seat confirmations, check-in QR, etc.):
- Keep a short pending list with owner + due date.
- Trigger reminders with time buffer (day-before or earlier for critical items).
- Escalate if no response by cutoff.

## Output Rules
- Bullet-first, concise, high signal.
- No fluff.
- If data is uncertain, say so explicitly.
- For recommendations, always include one fallback.

## References
- For trip transport procurement templates and comparison format, read `references/transport-procurement.md`.
- For daily operating output templates, read `references/daily-ops-templates.md`.

---
name: marine-watch-planner
description: Generate and adapt a sea-duty daily routine with watch rotations, sleep protection, duty handovers, internet-budgeted work blocks, and role-specific tasks. Use when a user asks to build or optimize an onboard schedule by vessel type, role, timezone, watch model (e.g., 4/4, 3/3), fatigue constraints, or low-bandwidth life at sea.
---

# Marine Watch Planner

## Overview
Build a practical 24h onboard routine that protects sleep, keeps safety anchors, and fits real constraints (role duties, sea state, and limited internet).

## Workflow
1. Capture context inputs.
2. Select watch/sleep model.
3. Generate 24h timeline.
4. Add safety anchors and handovers.
5. Add bandwidth-aware work/content policy.
6. Return concise schedule + non-negotiables.

## 1) Capture context inputs
Collect only required inputs:
- vessel type: cargo / tanker / offshore / yacht / fishing / ferry
- role: captain / OOW / engineer / deck crew / passenger
- timezone (IANA)
- watch model: 4/4, 3/3, 6/6, solo cycle
- start of first watch (local time)
- internet limit (GB/week)
- priorities: sleep, productivity, fitness, content, study

If data is missing, assume: 2-person 4/4, start 08:00, timezone Europe/Vilnius, 4 GB/week.

## 2) Select watch/sleep model
Use `references/watch-models.md`.
Rules:
- Protect minimum 6h sleep/day, target 7h.
- Keep one uninterrupted core block >=3h when possible.
- No cognitively heavy tasks immediately after fragmented sleep.

## 3) Generate 24h timeline
Use `scripts/build_marine_plan.py` for a starter plan.
Required blocks:
- on-watch blocks
- sleep/rest blocks
- meal/hydration
- weather/navigation review
- role duty block
- optional online work + posting window

## 4) Add safety anchors
Use `references/safety-anchors.md`.
Always include:
- start-of-watch handover checklist
- 2-4 safety scans/day
- end-of-day log line

## 5) Add internet policy
Use `references/internet-budgeting.md`.
Always provide:
- daily MB target from weekly limit
- one low-traffic day/week
- "offline-first" recommendations (downloads, no autoplay, no cloud sync on cellular)

## 6) Output format
Return exactly these sections:

1. `Status:` one line.
2. `24h Plan:` bullet list `HH:MM–HH:MM — action`.
3. `Non-negotiables:` max 5 bullets.
4. `Traffic budget:` one line daily MB target + one line policy.

Keep it short, operational, and in the user language.
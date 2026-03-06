---
name: anti-panic-protocol
description: Handle tool failures under pressure with bounded retries, clean user communication, and safe escalation. Use when commands/tools fail, when repeated retries risk spam or rate limits, or when you need a strict error-response workflow (translate raw errors, attempt safe fixes, then escalate clearly).
---

# Anti-Panic Protocol

## Core rule
Fail without collateral damage.

## Workflow (strict)
1. Identify the failure in one sentence.
2. Attempt fix #1 (direct, safe, minimal).
3. Attempt fix #2 (bounded alternative).
4. Stop retrying.
5. Escalate in plain language with next action.

Never exceed 2 fix attempts unless user explicitly asks.

## User-facing communication format
Always send:
- What failed
- What you tried
- What happens next

Never send:
- Raw stack traces
- Raw CLI dumps
- Internal tool payloads

## Retry safety
- No retry loops
- Respect cooldowns/rate limits
- One outward message per outcome (no duplicates)
- If rate-limited: wait for next allowed slot

## Verification before done
Before saying “done”, verify outcome:
- Message actually sent
- Event actually created
- Post actually published
- File actually written

If not verified, report as pending/failed, not done.

## Escalation template
Gebruik dit patroon:

"Dit faalde: <korte oorzaak>. Ik heb <poging 1> en <poging 2> geprobeerd. Volgende stap: <concrete actie of vraag>."

## Escalation examples
- "Dit faalde: publish werd afgewezen door rate-limit. Ik heb 1) direct retry en 2) delayed retry geprobeerd. Volgende stap: posten op eerstvolgende toegestane slot, zonder extra spam." 
- "Dit faalde: agenda-event create gaf validation error op datumveld. Ik heb 1) ISO-format gefixt en 2) timezone expliciet gezet. Volgende stap: jij bevestigt datum/tijd, dan maak ik het event direct aan." 
- "Dit faalde: loginflow timed out. Ik heb 1) token-login geprobeerd en 2) browserflow herstart. Volgende stap: ik wacht op jouw OAuth-bevestiging en rond dan automatisch af." 

## Hard stops
Escalate immediately (skip retries) if:
- Risk of destructive action
- Risk of duplicate external sends
- Authentication/security boundary issue
- User says stop/pause

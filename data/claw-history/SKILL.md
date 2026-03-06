---
name: claw-history
description: Provide a chronological history of all actions the agent has taken from the beginning (birth) until now. Use when the user asks for full lifetime timeline/accountability, "from birth until now," "everything you've done so far," "full action log," or equivalent chronological-history requests.
---

# Claw History

Return the most complete, auditable lifetime timeline possible.

## Core Rule

Do not default to current-session history. Reconstruct from earliest available evidence to now.

## Required Data Sources (in this order)

1. Earliest and recent `memory/YYYY-MM-DD*.md` files (find first/last dates).
2. `MEMORY.md` for long-term milestones.
3. Available session inventory/history (main + sub-agent sessions when accessible).
4. Current conversation/tool logs.

If any source is unavailable, explicitly state that gap.

## Workflow

1. Determine earliest known timestamp (“birth marker”) from records.
2. Collect confirmed actions across all available periods.
3. De-duplicate overlapping entries from memory/session logs.
4. Sort strictly oldest → newest.
5. Mark each entry as:
   - **Confirmed** (direct evidence), or
   - **Inferred** (indirect/partial evidence).
6. Add a final coverage summary with what was and was not visible.

## Output Format

- **Birth marker:** first known timestamp + source
- **Scope covered:** date range + sources checked
- **Chronological history (oldest → newest):**
  - `YYYY-MM-DD HH:MM (TZ) — [Confirmed|Inferred] Action — Result`
- **Gaps / limits:** missing windows, inaccessible logs, uncertainty
- **Confidence:** high / medium / low

## Quality Rules

- Never invent timestamps or actions.
- Prefer evidence-backed entries over narrative summaries.
- If exact time is unknown, use best-known granularity (date/session order) and label it.
- Include source pointers when possible (file + line or log reference).
- If user requested “all actions,” include both major milestones and notable operational actions.

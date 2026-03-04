# Fault Log

Track concrete errors here. Faults are objectively wrong outputs.

| Date | Fault Type | Description | Impact | Fix Applied |
|------|-----------|-------------|--------|-------------|
| 2026-02-20 | hallucination | Stated API returns JSON (it returns XML) | Low - corrected immediately | Verified before stating facts |
| | | | | |

**Fault Types:**
- **hallucination** — stated false information as fact
- **contradiction** — said X now, said not-X before
- **silent_failure** — failed at task but didn't report it
- **scope_violation** — did something outside authority
- **logic_break** — reasoning doesn't follow
- **context_loss** — forgot something from earlier
- **format_break** — output doesn't match expected structure

## How to Use

When a fault occurs:
1. STOP — don't build on faulty output
2. ACKNOWLEDGE — state what went wrong
3. TRACE — why did it happen?
4. CORRECT — provide right output
5. PREVENT — if this is the 2nd occurrence, add standing order
6. LOG — record here

## Pattern Detection

If you see the same fault type 3+ times, the agent has a systemic issue. Add a specific standing order or modify the system prompt to prevent that category permanently.

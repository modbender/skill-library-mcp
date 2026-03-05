---
name: remember-me
description: Remember-this trigger: memory updates + recall for preferences, goals, boundaries, prior work, decisions, dates, and todos. Use whenever user asks to remember, continue previous context, personalize behavior, or retrieve what was decided earlier.
---

# Remember Me

Maintain a respectful, useful memory model of the user over time.

## Core Rules

- Store user-relevant context, not surveillance noise.
- Prefer explicit consent for sensitive personal details.
- Use memory to improve help quality, not to overfit persona.
- Be explicit when memory confidence is low or inferred.
- Make human-like inferences (explicitly marked as hypotheses).

## Memory Integrity Rules

Every memory entry must be tagged as one of:

- FACT (explicitly stated by user)
- PREFERENCE (behavioral or stated)
- GOAL (time-bound or ongoing)
- HYPOTHESIS (inferred, unvalidated)

Rules:

- FACTS are never inferred
- HYPOTHESES are never promoted without confirmation
- PREFERENCES can remain soft unless explicitly confirmed

## Capture Triggers

Log memory when any of these happen:

- user says “remember this”
- a preference appears repeatedly
- a boundary is stated (“don’t do X”, “keep Y private”)
- a recurring blocker/pattern emerges
- project priorities shift meaningfully

## Memory Tiers

- **Daily notes**: `memory/YYYY-MM-DD.md`
  - timestamped raw events, short and factual
- **Long-term**: `MEMORY.md`
  - curated durable profile and preferences

## Write Workflow

1. Classify signal type (preference, boundary, goal, project, blocker, personal context).
2. Append concise timestamped entry to daily memory.
3. Form 1–2 human-like assumptions (hypotheses) from behavior patterns.
4. Tag each assumption with confidence (high/medium/low).
5. Validate assumptions in later conversation with lightweight check-ins.
6. Promote validated, durable items to long-term memory.

Use templates in `references/templates.md`.

## Memory Impact Score (Optional Heuristic)

Rate each entry 1–3:

- 1 = cosmetic (tone tweaks)
- 2 = workflow-affecting
- 3 = outcome-critical

Promotion guidance:

- any explicit preference (any score)
- score >= 2 with repetition
- score 3 immediately

## Promotion Workflow

Promote from daily to long-term when at least one is true:

- repeated in 2+ sessions
- high impact on future assistance
- explicit user preference/boundary
- ongoing project context likely to recur

Use checklist: `references/promotion-checklist.md`.

## Personalization Contract

When responding, adapt based on known memory:

- tone (direct vs exploratory)
- brevity level
- preferred workflow style
- known constraints and boundaries
- inferred decision style (speed-first vs depth-first, reassurance-needed vs challenge-welcoming)

Do not pretend certainty. If memory is weak, ask a short confirmation.

## Retrieval Contract

Before answering prior-work / preference / timeline questions:

- query memory sources first
- quote memory snippets when useful
- if not found, say you checked and ask for confirmation

## Explicit Exclusions (Never Store)

Do not store:

- transient emotional states (e.g., "tired today")
- one-off frustrations without recurrence
- speculative motives (e.g., "trying to impress")
- sensitive identity attributes unless explicitly requested
- raw conversation logs

## Weekly Maintenance (recommended)

- review last 3–7 daily notes
- merge stable patterns into `MEMORY.md`
- remove stale or contradicted entries
- keep profile concise and behaviorally actionable

## Confidence Decay

Hypothesis confidence decays automatically if not reinforced:

- High -> Medium after 14 days
- Medium -> Low after 30 days
- Low -> Discard after 60 days

Reinforcement occurs when:

- user behavior aligns again
- user explicitly confirms

## Forgetting & Demotion Policy

Actively remove or downgrade memory when:

- a preference is contradicted explicitly by the user
- a hypothesis remains unvalidated after N sessions (default: 5)
- a project is clearly abandoned or replaced
- the user requests forgetting (immediate delete)

Demotion flow:

- Long-term memory -> Daily note (annotated as stale)
- Hypothesis -> Discarded (log reason briefly)

## Assumption Loop (Human-Like Understanding)

For deeper understanding, run this loop continuously:

1. Observe behavior pattern (not just words).
2. Infer a tentative assumption about the user.
3. Store assumption as hypothesis (never as fact initially).
4. Test it with a small conversational probe.
5. Update confidence or discard if contradicted.

Good probes:

- "I might be wrong, but do you prefer quick decisions when you're tired?"
- "Should I challenge you more directly here, or keep it supportive?"

## Check-In Limits

- Never ask the same confirmation twice.
- Do not stack multiple probes in one response.
- Prefer confirmation when user is calm, not frustrated.

## Optional Check-In Prompt

Use at natural boundaries:

- "Want me to remember this preference for next time?"

Ask once, then store explicitly.

## References

- Templates: `references/templates.md`
- Promotion checklist: `references/promotion-checklist.md`
- Profile schema: `references/profile-schema.md`

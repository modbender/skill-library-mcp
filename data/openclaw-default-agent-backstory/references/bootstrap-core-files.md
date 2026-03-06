# Bootstrap Core Files

Use this guide in `bootstrap` mode to create practical starter content for each core file.

Reference: https://docs.openclaw.ai/concepts/context

## `AGENTS.md`

Define workspace operating rules and memory policy.

Minimum starter sections:

- first-run checklist
- every-session read order
- memory strategy (daily + long-term)
- safety defaults
- external-action escalation rule
- session management defaults (startup, continuation, and wrap-up behavior)

## `SOUL.md`

Define personality and stable behavior traits.

Minimum starter sections:

- identity summary
- decision principles
- interaction style
- boundaries and refusal posture

## `TOOLS.md`

Capture practical tool and environment notes.

Minimum starter sections:

- preferred CLIs/services
- known constraints and auth assumptions
- formatting/platform preferences

## `IDENTITY.md`

Define canonical self-model.

Minimum starter sections:

- name, role, vibe, emoji, avatar (if available)
- `## Backstory`
- `## Behavioral Guardrails`
- `## Growth Arc`

## `USER.md`

Define who the agent serves.

Minimum starter sections:

- user goals
- working style/preferences
- known constraints
- communication preferences

## `HEARTBEAT.md`

Define proactive checks.

Minimum starter sections:

- short checklist for periodic checks
- quiet hours or suppression rules
- escalation thresholds

## `MEMORY.md` and `memory/`

Define durable memory behavior.

`MEMORY.md` is a standalone file at workspace root. Do not represent it as a heading inside `AGENTS.md`.

Minimum starter sections:

- what goes into long-term curated memory (`MEMORY.md`)
- what goes into daily logs (`memory/YYYY-MM-DD.md`)
- promotion rules from daily memory to long-term memory
- privacy/sensitivity handling rules

## `BOOTSTRAP.md`

Track bootstrap status and short next steps.

Minimum starter sections:

- what was initialized
- unresolved questions
- next actions for first week

## Writing Rules

- Keep each file concise and actionable.
- Use explicit defaults instead of vague statements.
- Mark assumptions clearly when user did not specify details.
- Avoid placeholders like "TBD" unless user explicitly deferred a decision.

## Rational Defaults (When User Is Unsure)

If the user does not specify preferences, use these defaults:

- Session start: read `AGENTS.md`, `SOUL.md`, `USER.md`, then recent daily memory files.
- Session wrap-up: append key decisions/actions to today's daily memory file.
- Long-term memory: keep only stable preferences, recurring constraints, and major decisions.
- Daily memory: keep timeline-style notes and short factual summaries.
- Heartbeat cadence: 2-4 checks/day with quiet hours from 23:00 to 08:00 local time.

## Primary Daily Driver Memory Policy (Default)

Use this policy when the user wants reasonable defaults for heavy daily use.

### Routing Rules

- Store in `MEMORY.md`:
- stable preferences (communication style, tone, tooling choices)
- recurring constraints (schedule limits, security/privacy boundaries)
- durable decisions (architecture choices, long-lived project direction)
- relationship-level context that should survive restarts

- Store in `memory/YYYY-MM-DD.md`:
- daily actions, progress logs, and session summaries
- temporary tasks, reminders, and short-term plans
- experiments, tentative ideas, and unresolved threads
- factual timeline of what happened today

### Promotion Rules

- Promote from daily files to `MEMORY.md` when an item repeats 2+ times or is explicitly marked important by the user.
- Promote major decisions immediately when they affect future behavior.
- Keep promotions short: one-line fact plus one-line implication for future sessions.

### Pruning Rules

- Review recent daily files every 3-7 days and promote durable items.
- Do not copy full daily logs into `MEMORY.md`; keep `MEMORY.md` curated.
- Remove outdated or superseded entries from `MEMORY.md` during periodic review.

### Session Behavior Defaults

- Session start: read `AGENTS.md`, `SOUL.md`, `USER.md`, latest daily memory, and `MEMORY.md` in main/direct chats.
- During session: write notable decisions and commitments to today's daily file.
- Session end: add a concise end-of-day summary with open loops and next actions.

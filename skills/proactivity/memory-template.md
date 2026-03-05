# Memory Template

Copy this structure to `~/proactivity/memory.md` on first use.

```markdown
# Proactivity Memory

## Boundaries
<!-- Learned autonomy levels. Format: domain: action → LEVEL (status) -->
<!-- Example: calendar: block focus time → DO (confirmed) -->
<!-- Example: email: send replies → ASK (confirmed) -->
<!-- Example: slack: post messages → NEVER (rejected) -->

## Patterns
<!-- Recurring proactive behaviors. Format: trigger → response (status) -->
<!-- Example: invoice overdue 7 days → send reminder (confirmed) -->
<!-- Example: meeting tomorrow → prep packet tonight (confirmed) -->

## Preferences
<!-- How user wants proactivity delivered -->
<!-- Example: morning digest only -->
<!-- Example: no weekend alerts -->
<!-- Example: max 3 alerts per day -->
```

## Initial Directory Structure

Create on first activation:

```bash
mkdir -p ~/proactivity/domains
touch ~/proactivity/{memory.md,patterns.md,log.md}
```

## Log Template

For `~/proactivity/log.md`:

```markdown
# Proactive Actions Log

<!-- Format:
## YYYY-MM-DD
- [HH:MM] LEVEL: action → outcome
  Domain: calendar|email|code|content|...
  Trigger: what prompted this
  User reaction: positive|neutral|negative|none
-->
```

## Domain Template

For `~/proactivity/domains/{domain}.md`:

```markdown
# {Domain} Proactivity Rules

## Autonomy Overrides
<!-- Domain-specific level changes -->

## Triggers
<!-- What prompts proactive action in this domain -->

## Constraints
<!-- What to avoid -->
```

# Boundary Learning

## The Core Problem

Proactivity without boundaries = annoying or dangerous.
Too many boundaries = agent becomes passive again.

Goal: Learn exactly where the line is for THIS user.

## Learning Flow

### Step 1: Detect New Domain
When you could act proactively in an area not yet in memory.

### Step 2: Ask Once
```
"I could [specific action] for you.
Should I: do it automatically / suggest first / always ask / never do this?"
```

### Step 3: Record Response
```
domain: specific action → LEVEL (confirmed)
```

### Step 4: Never Ask Again
If same domain comes up → check memory → act accordingly.

## Question Format

**Good:**
- "I could check your calendar for conflicts each morning. Automatic, suggest, or skip?"
- "I could draft replies to routine emails. Want to approve each, or trust me on simple ones?"

**Bad:**
- "Should I be proactive about your calendar?" (too vague)
- "Can I help with emails?" (doesn't specify action)
- "Would you like me to..." (weak, indirect)

## Recording Format

In `~/proactivity/memory.md`:

```markdown
## Boundaries
calendar: check conflicts → DO (confirmed)
calendar: reschedule meetings → ASK (confirmed)
email: draft replies → SUGGEST (confirmed)
email: send without approval → NEVER (confirmed)
code: fix linting errors → DO (confirmed)
code: refactor functions → SUGGEST (confirmed)
slack: send messages → NEVER (rejected)
```

## Boundary Types

| Type | Meaning | Example |
|------|---------|---------|
| (confirmed) | User explicitly set this | "Yes, always do that" |
| (inferred) | Learned from reactions | User seemed happy when I did X |
| (rejected) | User said no | "Never do that" |
| (temporary) | Just for now | "Not this week" |

## Updating Boundaries

**Promotion:** User says "just do it next time" → upgrade to DO

**Demotion:** User says "ask me first" → downgrade to ASK/SUGGEST

**Reversal:** User says "stop doing that" → change to NEVER

Always log the change with timestamp.

## Default Levels by Category

When no boundary exists yet, default to:

| Category | Default Level |
|----------|---------------|
| Research/analysis | DO |
| Internal drafts | DO |
| Reorganizing own files | DO |
| Suggestions/ideas | SUGGEST |
| External communications | ASK |
| Spending money | ASK |
| Contacting people | ASK |
| Deleting anything | ASK |
| Commitments/promises | NEVER |
| Sending without approval | NEVER |

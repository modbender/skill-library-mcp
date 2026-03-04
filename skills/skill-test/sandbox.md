# Sandbox Testing

Isolated environment for safe skill testing.

## Setup

```bash
# Create isolated test folder
npx clawhub install <slug> --dir /tmp/skill-test/<slug>
```

## Running Tests

**Option 1: Sub-agent isolation**
Spawn a sub-agent with instructions to:
- Load ONLY the test skill
- Ignore all other context
- Run specific test tasks
- Report results

**Option 2: Manual review**
- Read the skill files
- Mentally trace through workflows
- Check for red flags

## Test Tasks

Define representative tasks:
- "If I had this skill, what would I ask it to do?"
- Run 2-3 realistic scenarios
- Note: Does it help? Is output good?

## What to Observe

- Does it activate when expected?
- Are instructions clear?
- Does it conflict with anything?
- Token cost reasonable?
- Output quality acceptable?

## Cleanup

After testing:
```bash
rm -rf /tmp/skill-test/<slug>
```

## Graduating to Real Use

Only after successful sandbox test:
1. User explicitly approves
2. Install to real skill folder
3. Verify it works in real context

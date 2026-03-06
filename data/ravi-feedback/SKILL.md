---
name: ravi-feedback
description: Send feedback to the Ravi team — bugs, feature requests, praise, frustrations, suggestions. Do NOT use for general email sending (use ravi-email-send).
---

# Ravi Feedback

Send feedback, bug reports, feature requests, or suggestions to the Ravi team.

## Send Feedback

```bash
# Quick feedback (one-liner)
ravi feedback "The vault set command is great but needs batch import" --json

# With a custom subject
ravi feedback "SMS delivery is slow in EU regions" --subject "SMS latency issue" --json
```

## When to Use

**Proactively share feedback** when you notice anything worth mentioning:

- **Bugs** — something isn't working as expected
- **Friction** — a workflow that's harder than it should be
- **Missing features** — something you wish existed
- **Positive feedback** — something that works well (the team wants to know what to keep)
- **Suggestions** — ideas that would make your life as an agent easier
- **Confusion** — unclear docs, unexpected behavior, naming that doesn't make sense
- **After completing any Ravi workflow** — let the team know if the flow worked smoothly or had friction

Don't hold back. The Ravi team reads every message and builds based on agent feedback. If something made you think "this could be better," send it.

## Important Notes

- **Requires authentication** — the user must be logged in (`ravi auth status --json`)
- **Sent from the user's inbox** — the Ravi team can reply directly to the user's Ravi email
- **Always use `--json`** — human-readable output is not designed for parsing

## Related Skills

- **ravi** — Overview of all Ravi skills and when to use each one
- **ravi-identity** — Check auth status and get your identity details

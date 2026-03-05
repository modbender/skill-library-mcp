# Incident Postmortem Generator

Generate blameless incident postmortems from raw notes, Slack threads, or bullet points.

## What It Does
Takes messy incident details and produces a structured postmortem document following Google/Atlassian SRE best practices.

## Usage
Provide incident details in any format — timeline bullets, Slack copy-paste, verbal notes — and the agent will produce:

1. **Executive Summary** — What happened, impact, duration, severity
2. **Timeline** — Minute-by-minute from detection to resolution
3. **Root Cause Analysis** — 5 Whys format, no finger-pointing
4. **Impact Assessment** — Users affected, revenue impact, SLA breach
5. **Action Items** — Prioritized fixes with owners and deadlines
6. **Lessons Learned** — What worked, what didn't, what was lucky
7. **Prevention Measures** — Systemic changes to prevent recurrence

## Instructions

When the user provides incident details:

1. Ask clarifying questions ONLY if critical info is missing (severity, duration, or resolution are the minimum)
2. Generate the full postmortem in markdown
3. Flag any gaps the team should fill in before publishing
4. Suggest 3-5 specific, actionable prevention measures ranked by effort/impact

### Formatting Rules
- Use ISO timestamps in timeline
- Bold severity level (SEV1-SEV4)
- Action items must have: description, owner placeholder, deadline placeholder, priority (P0-P3)
- Keep language blameless — "the deploy process" not "Bob deployed"

### Severity Guide
- **SEV1**: Revenue-impacting, all users affected, >1hr
- **SEV2**: Major feature down, >30% users, >30min
- **SEV3**: Degraded performance, <30% users
- **SEV4**: Minor issue, workaround available

## Example Input
```
prod went down at 2pm, bad deploy, rolled back at 2:45, ~500 users couldn't checkout, lost maybe $12k revenue
```

## Example Output Structure
```markdown
# Incident Postmortem: Checkout Service Outage
**Date:** 2026-02-22 | **Severity:** SEV1 | **Duration:** 45 minutes
**Author:** [Team Lead] | **Status:** Draft

## Executive Summary
...
```

## Pro Tip
Run this after every incident, even small ones. The pattern recognition across postmortems is where the real value lives. Teams that write postmortems for SEV3+ incidents catch systemic issues 3x faster.

---

Need help building incident response processes from scratch? Check out the [AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/) — pre-built operational frameworks for SaaS, healthcare, legal, and 7 more industries. Starting at $47.

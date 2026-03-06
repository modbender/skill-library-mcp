# Tweet Processor Skill

Automated tweet analysis and categorization for the tweet-notes system.

## What It Does

When you send a tweet link to the agent with this skill active, it will:

1. **Navigate** to the tweet using browser automation
2. **Extract** key insights (tools, techniques, people, learnings)
3. **Categorize** into appropriate files:
   - `tools.md` — Software, APIs, services
   - `tech.md` — Development techniques, workflows  
   - `design.md` — UI/UX insights
   - `people.md` — Worthwhile accounts
   - `misc.md` — Other valuable insights
4. **Append** with consistent formatting including date and URL

## How to Use

Simply send a tweet URL:
```
https://x.com/username/status/1234567890
```

The agent will automatically:
- Detect it's a tweet link
- Navigate and extract content
- Categorize insights
- Update the files
- Report what was added

## Output Format

Each entry follows this structure:

```markdown
## [Brief Descriptive Title]
**Date:** 2025-02-20
**URL:** https://x.com/...
**Key takeaway:** [The core insight or tool/technique]
**Why it matters:** [Context on why this is valuable]

---
```

## Files Managed

- `/tweet-notes/tools.md` — Tools and services discovered
- `/tweet-notes/tech.md` — Technical insights and workflows
- `/tweet-notes/design.md` — Design resources and patterns
- `/tweet-notes/people.md` — Accounts to follow
- `/tweet-notes/misc.md` — Everything else

## Philosophy

- **Be selective** — Only capture genuinely useful insights
- **Skip the fluff** — Ignore hype and noise
- **Actionable > Interesting** — Focus on things that can be used
- **Link everything** — Always include source URLs

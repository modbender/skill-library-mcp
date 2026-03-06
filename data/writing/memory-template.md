# Memory Template — Writing

Copy this structure to `~/writing/memory.md` on first use.

```markdown
# Writing Memory

## Status
status: ongoing
version: 1.1.0
last: YYYY-MM-DD
integration: (when to activate — proactive/on-request/specific-contexts)

## Voice
<!-- Their writing personality. Observed patterns, not config keys. -->
<!-- Examples:
- Conversational but smart, avoids jargon
- Short punchy sentences, rarely over 15 words
- Dry humor, occasional self-deprecation
- Opens with a hook, never buries the lede
-->

## Formats
<!-- How they write different things. Natural observations. -->
<!-- Examples:
- Emails: gets to the point fast, clear ask at the end
- Blog posts: conversational, lots of examples, headers every 2-3 paragraphs
- Reports: formal but not stiff, bullet points over paragraphs
-->

## Patterns
<!-- Habits — good ones to preserve, bad ones they want to fix. -->
<!-- Examples:
- Tends to over-explain, wants help cutting
- Strong openings, sometimes weak conclusions
- Uses "just" too much, trying to break the habit
-->

## Corrections
<!-- Things they've rejected or corrected. Don't repeat these. -->
<!-- Examples:
- Never use "utilize" — always "use"
- Hates passive voice unless necessary
- "Too formal" on first draft — dial it back
-->

## Context
<!-- Anything else useful about their writing situation. -->
<!-- Examples:
- Writing a book on productivity, needs consistent voice
- Non-native English speaker, prefers simple grammar
- Audience is developers, can use technical terms
-->

## Notes
<!-- Internal observations, not shared with user. -->

---
*Last updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Actively learning, check each session |
| `complete` | Core preferences learned, maintenance mode |
| `paused` | User paused preference tracking |
| `never_ask` | User declined integration, just help when asked |

## Initial Directory Structure

Create on first activation:

```bash
mkdir -p ~/writing/{projects,archive}
touch ~/writing/memory.md
```

## Project-Specific Template

For `~/writing/projects/{name}.md`:

```markdown
# Writing Style — {Project Name}

## Voice for This Project
<!-- How their voice differs for this specific project -->

## Format Requirements
<!-- Any specific requirements (word count, structure, etc.) -->

## Audience
<!-- Who reads this project -->

---
*Last updated: YYYY-MM-DD*
```

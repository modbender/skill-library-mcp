---
name: memoria
description: Structured memory system for AI agents. Use when the user wants to store, recall, or search memories, manage session lifecycle (wake/sleep/checkpoint), sync to Notion, or when the user shares important information that should be remembered (facts, decisions, preferences, lessons, commitments, relationships, projects).
---

# Memoria

## Environment

Set the vault path so all commands work:

```bash
export MEMORIA_VAULT=~/memory
```

If not set, pass `-v ~/memory` on every command.

## Session Lifecycle

Run at the start and end of every session:

```bash
memoria wake                                          # start session, restore context
memoria checkpoint --working-on "<task>"               # mid-session save
memoria sleep "<summary>" --next "<next steps>"        # end session, write handoff
```

## Storing Memories

```bash
memoria remember <type> "<title>" --content "<details>"
memoria sync --push                                    # always sync after storing
```

Types: `fact`, `decision`, `preference`, `lesson`, `commitment`, `relationship`, `project`

### What to capture (proactively, without being asked)

| Signal | Type |
|--------|------|
| Human shares personal info (name, location, health, settings) | `fact` |
| A decision is made with reasoning | `decision` |
| Human says "I prefer / always / never..." | `preference` |
| An insight or lesson emerges | `lesson` |
| A promise, goal, or deadline is set | `commitment` |
| A person is mentioned with context | `relationship` |
| An ongoing project is discussed | `project` |

**If in doubt, store it.** Better to have a memory you never look up than to forget something.

### Proactive capture triggers

Listen for these patterns and store immediately:

- "I always...", "I never...", "I prefer..." -> `preference`
- "Let's go with...", "We decided...", "The plan is..." -> `decision`
- "I learned that...", "Turns out...", "The trick is..." -> `lesson`
- "My name is...", "I take...", "I live in...", "I work at..." -> `fact`
- "I need to...", "I promised...", "By next week..." -> `commitment`
- "Talk to Alice about...", "Bob said..." -> `relationship`
- "We're building...", "The project is..." -> `project`

### Examples

```bash
memoria remember fact "Human lives in Tokyo" --content "Mentioned during onboarding"
memoria remember preference "No emojis in code" --content "Explicitly requested"
memoria remember decision "Use Fly.io" --content "Chosen over Vercel for APAC latency"
memoria sync --push
```

## Searching

Before making decisions or giving advice, check existing memories:

```bash
memoria search "<query>"
```

## Other Commands

```bash
memoria store <category> "<title>" --content "<body>"  # store in explicit category
memoria list [category]                                 # list documents
memoria get <id>                                        # get specific document
memoria status                                          # vault stats + session state
memoria sync --pull                                     # pull Notion changes to local
```

## Notion Setup

One-time configuration:

```bash
memoria setup-notion --token <token> --page <page-id>
```

After setup, always run `memoria sync --push` after storing memories.

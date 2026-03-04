# Cron Job Prompt Patterns

Patterns for writing effective cron job prompts. Learned from Wire's 11-job news pipeline.

## Core Rules

1. **Always inject the date**: `$(date '+%A, %B %d, %Y')` — LLMs don't know the current date.
2. **Constraints in the prompt, not just SOUL.md**: SOUL.md may not survive context compaction.
3. **Show the format, don't describe it**: Include an exact output template.
4. **Negative instructions work**: "Do NOT repeat", "REJECT Reddit", "Do NOT fabricate".
5. **Sequential protocols for complex tasks**: Numbered steps with explicit pass/fail gates.
6. **Never hardcode Telegram group IDs**: Use the dynamic resolution preamble (see below).

## Dynamic Group ID Resolution (Preamble)

**ALWAYS** prepend this to every cron job prompt that sends Telegram messages:

```
FIRST: Resolve your Telegram group ID by running:
jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json
Use the output as the target for all Telegram messages in this task.
```

Then use `target='<AGENT_GROUP_ID>'` as placeholder in format templates. This survives Telegram group migrations — see telegram-routing.md for details.

## Pattern 1: Briefing Prompt

```
FIRST: Resolve your Telegram group ID by running:
jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json
Use the output as the target for all Telegram messages in this task.

Today is $(date '+%A, %B %d, %Y'). Generate a [MORNING/EVENING] [TOPIC] briefing
covering [time context].

SEARCH TERMS: [specific search queries]
SOURCES: Only use [curated list]. Reject [banned sources].
RECENCY: Only include stories published [window]. [dedup instruction if evening].

FORMAT (send via message tool, action='send', channel='telegram', target='<AGENT_GROUP_ID>'):
[emoji] **[Time] [Topic] Briefing** — $(date '+%b %d, %Y')

1. **[Headline]**
   [1-2 sentence summary]
   [Source](URL)

[story count instruction]
```

### Morning vs Evening

| Aspect | Morning | Evening |
|--------|---------|---------|
| Context | "overnight and early-morning" | "afternoon and late-breaking" |
| Recency | "TODAY or late last night" (12h) | "TODAY (afternoon/evening)" |
| Dedup | None | "Do NOT repeat this morning's stories" |
| Minimum | "3-5 stories" | "fewer than 3 is OK rather than padding" |

**Important**: Evening dedup requires shared sessions (no `sessionTarget: "isolated"`).

## Pattern 2: Verification Protocol

For tasks requiring multi-step validation.

```
Current time: $(date '+%A, %B %d, %Y %I:%M %p %Z').

[Task description]

VERIFICATION PROTOCOL (follow in order):
1. [Search/gather step]
2. For each candidate, verify ALL:
   a. [CHECK]: [criteria]. [rejection rule].
   b. [CHECK]: [criteria]. [rejection rule].
3. If ANY check fails, skip entirely.

[OUTPUT]:
- [delivery instructions]
- Format: [exact format]

If nothing qualifies, reply [NULL response]. Do NOT fabricate.
```

## Pattern 3: Report Prompt

```
FIRST: Resolve your Telegram group ID by running:
jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json
Use the output as the target for all Telegram messages in this task.

Generate a [report]. Run: 1) [cmd1] 2) [cmd2] ...
Format with [guidance]. Send via message tool, target='<AGENT_GROUP_ID>'.
Header: '[emoji] **[Report]** - [date]'
```

## Shell Substitution

`$(...)` is evaluated before reaching the LLM:

| Expression | Output |
|------------|--------|
| `$(date '+%A, %B %d, %Y')` | `Wednesday, February 11, 2026` |
| `$(date '+%b %d, %Y')` | `Feb 11, 2026` |
| `$(date '+%I:%M %p %Z')` | `09:00 AM MST` |
| `$(date +%Y-%m-%d)` | `2026-02-11` |

## Timeout Guidelines

| Job Type | Timeout |
|----------|---------|
| Simple report | 30-60s |
| Single-topic briefing | 90s |
| Multi-topic search | 120s+ |
| Complex verification | 120-180s |

## Per-Topic Source Lists (Reference)

| Topic | Sources |
|-------|----|
| AI | TechCrunch, The Verge, Reuters, ArsTechnica, Wired, MIT Tech Review |
| Tech | TechCrunch, The Verge, ArsTechnica, Wired, CNET, 9to5Mac, Engadget |
| India | Reuters, BBC, NDTV, The Hindu, Indian Express, Hindustan Times, Economic Times, Mint |
| GeoPolitics | Reuters, BBC, AP News, Al Jazeera, Foreign Policy, The Guardian, NYT |
| International | Reuters, BBC, AP News, The Guardian, NYT, Al Jazeera, France24 |
| Finance | Reuters, Bloomberg, CNBC, Financial Times, WSJ |

Always add: `Reject Reddit, Wikipedia, forums, unknown blogs.`

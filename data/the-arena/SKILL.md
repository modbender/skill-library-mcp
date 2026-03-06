---
name: the-arena
description: >
  Turn a Discord server into a moderated debate arena with an AI judge.
  Supports multiple debate formats, configurable personas, scored verdicts,
  and a persistent scoreboard. Keywords: debate server, debate moderator,
  debate judge, argument judge, discussion moderator, moderated debates,
  debate arena, debate bot, AI judge, the arena.
metadata:
  openclaw:
    env:
      - name: DEBATE_SCOREBOARD_DB
        description: "Path to SQLite scoreboard database. Default: ./data/scoreboard.db (within skill workspace)."
        required: false
---

# The Arena — AI Debate Moderator

Transform any Discord server into a structured debate arena with AI moderation,
fair judging, and a persistent scoreboard.

## Prerequisites

**This skill requires the following. Nothing is configured automatically — all
privileged actions require your manual review and approval.**

| Requirement | Details |
|-------------|---------|
| **Discord bot token** | Your existing OpenClaw bot token (already in your gateway config) |
| **Discord bot permissions** | Read/Send Messages, Create Threads, Manage Messages, Read History, Add Reactions |
| **Discord guild (server)** | You create or choose the server. You provide the guild ID. |
| **Gateway admin access** | You manually review and apply config changes via `config.patch` |
| **`DEBATE_SCOREBOARD_DB`** (optional) | Env var to set SQLite DB path. Default: `./data/scoreboard.db` (within skill workspace) |

### Security Notes
- This skill recommends running as a **separate, isolated OpenClaw agent** with
  restricted tool access (`fs.workspaceOnly: true`, `exec.security: "deny"`).
- Config changes are **generated as templates for your review** — never applied
  automatically. You must manually review and apply all gateway config patches.
- The included scripts (`scripts/setup.sh`, `scripts/scoreboard.sh`) only create
  files within the skill workspace. They make no network calls and write no files
  outside the skill directory. **Inspect them before running** — both are plain
  bash with no obfuscation, under 400 lines each.
- The scoreboard SQLite DB is created at `./data/scoreboard.db` relative to the
  skill directory (or at `$DEBATE_SCOREBOARD_DB` if set). It never writes outside
  the skill workspace.
- Setting `requireMention: false` on arena channels means the bot processes every
  message in that channel. This increases token usage and data exposure. Use
  `requireMention: true` for lower cost and reduced visibility.

---

## Quick Start

Say **"set up a debate server"** and the agent walks you through configuration
choices, then generates templates for your review.

---

## Onboarding Flow

### Step 1 — Choose a Server
Create a new Discord server or pick an existing one. You'll need the **guild ID**
(right-click the server icon → Copy Server ID with Developer Mode enabled).

### Step 2 — Choose a Moderator Persona
Pick the voice your moderator uses during debates. Default: **Scholar**.

| Persona | Vibe |
|---------|------|
| Scholar | Measured, references history & philosophy |
| Sports Commentator | High-energy play-by-play |
| Philosopher | Socratic method, questions everything |
| Comedian | Witty roast-style commentary |
| Drill Sergeant | No-nonsense, demands evidence |
| Custom | You write the persona description |

Details in `references/personas.md`.

### Step 3 — Choose a Default Format
The default format used when someone starts a debate without specifying one.
Default: **Campfire**.

| Format | Style | Best For |
|--------|-------|----------|
| Campfire | Free-form exchange | General topics, casual |
| Oxford | Formal rounds, audience vote | Serious propositions |
| Lincoln-Douglas | 1v1 value debate | Philosophy, ethics |
| Hot Takes | One message each, best wins | Quick fun rounds |
| Devil's Advocate | Argue opposite of your belief | Steelmanning practice |
| Roundtable | Multi-perspective, no winner | Complex nuanced topics |

Details in `references/formats.md`.

### Step 4 — Judging Criteria Weights
Customize how the moderator scores arguments. Defaults:

| Criterion | Default Weight |
|-----------|---------------|
| Evidence & Reasoning | 35% |
| Engagement | 25% |
| Intellectual Honesty | 20% |
| Persuasiveness | 20% |

Weights must sum to 100%. Details in `references/judging.md`.

### Step 5 — Configure Channels
Default channel names (all customizable):

| Channel | Purpose |
|---------|---------|
| `#rules` | Server rules, format overview, commands |
| `#propose-a-topic` | Topic proposals and voting |
| `#the-arena` | Where debates happen |
| `#hall-of-records` | Verdicts, scoreboard, debate history |
| `#the-bar` | Casual off-topic discussion |

### Step 6 — Generate Config (for your review)
The agent generates config snippets and an `AGENTS.md` tailored to your choices.
**You must review and manually apply** all gateway config changes. The agent does
not apply config patches automatically. See `references/setup-guide.md` for the
full config template and a step-by-step walkthrough.

**Important:** `agents.list` and `bindings` are arrays — `config.patch` replaces
them entirely. Always review the full patch to ensure your existing agents and
bindings are preserved.

### Step 7 — Create Channels & Post Welcome Messages
After you create channels in Discord, the agent can post welcome messages from
`assets/welcome-messages.md` — or you can copy-paste them manually.

### Step 8 — Post Rules
The agent posts the full rules document in `#rules`.

---

## Configuration Reference

### Persona
Controls the moderator's voice and commentary style.

- **Scholar** (default) — Thoughtful, measured
- **Sports Commentator** — Electric, play-by-play
- **Philosopher** — Socratic, probing
- **Comedian** — Witty, irreverent (still fair)
- **Drill Sergeant** — Harsh, demanding
- **Custom** — Provide your own persona description

### Default Format
The format used when a debate is started without specifying one.

- **Campfire** (default), Oxford, Lincoln-Douglas, Hot Takes, Devil's Advocate, Roundtable

### Judging Weights
Customize the four scoring criteria. Must sum to 100%.

- **Evidence & Reasoning** — Quality of sources, logical structure (default 35%)
- **Engagement** — Responding to opponents, staying on topic (default 25%)
- **Intellectual Honesty** — Acknowledging good points, not strawmanning (default 20%)
- **Persuasiveness** — Rhetorical effectiveness, clarity (default 20%)

### Channel Names
All five channels can be renamed. Provide a mapping during setup.

### requireMention
- **true** (default, recommended) — Moderator only responds when @mentioned. Lower cost, lower data exposure. Participants control pacing by tagging the moderator.
- **false** — Moderator sees every message and may interject actively. Higher token usage and increased data exposure. Only recommended for small, trusted servers with low message volume.

### Verdict Style
How the moderator delivers the final ruling.

- **Detailed** — Full scorecard with per-criterion scores and commentary
- **Brief** — Winner announcement with one-paragraph summary
- **Dramatic** — Theatrical ruling with buildup and flair

### Scoreboard
- **on** (default) — SQLite-backed. Records wins, losses, topics, formats.
- **off** — No persistent tracking.

CLI: `scripts/scoreboard.sh`. DB location: `$DEBATE_SCOREBOARD_DB` or `./data/scoreboard.db`.

### Debate Timeout
Hours before the moderator flags a stale debate. Default: **48**.

### Max Concurrent Debates
Maximum simultaneous debates in the arena. Default: **3**.

### Topic Restrictions
- **unrestricted** (default) — No topic is off-limits. The moderator judges arguments on merit regardless of subject matter.
- **restricted** — Provide a list of banned topics or categories.

---

## How It Works

### Proposing a Topic
In `#propose-a-topic`, post:
```
Topic: [Your topic]
Format: [optional — defaults to server default]
```

Others react with 👍 to show interest. When at least two people are ready,
anyone can say **"let's debate"** to move to the arena.

### Starting a Debate
In `#the-arena`, the moderator:
1. Announces the topic and format
2. Assigns or confirms sides (except Roundtable/Hot Takes)
3. Posts the rules for that format
4. Calls for opening statements

Participants can also start directly in the arena:
```
@Moderator start debate: "Pineapple belongs on pizza" [format: hot-takes]
```

### During a Debate
The moderator's behavior depends on the format:
- **Campfire** — Interjects to track flow, flag fallacies, prompt responses
- **Oxford** — Strictly enforces rounds, time, and turn order
- **Lincoln-Douglas** — Enforces alternation between affirmative and negative
- **Hot Takes** — Collects one message per participant, then judges
- **Devil's Advocate** — Monitors that participants argue against their stated beliefs
- **Roundtable** — Asks probing questions, synthesizes themes

The moderator flags logical fallacies, tracks participation balance, and keeps
the debate moving. In mention-only mode, participants @mention for moderator input.

### Calling for a Verdict
- Either debater says **"I rest my case"**
- The moderator can call it after sustained inactivity
- The moderator runs a **ready check**: both sides must confirm

### Verdicts
The moderator evaluates using the configured judging weights and delivers the
verdict in the configured style. The verdict is posted in both `#the-arena` and
`#hall-of-records`.

### Scoreboard
When the scoreboard is enabled, results are automatically recorded.

Commands (via `scripts/scoreboard.sh`):
```
scoreboard.sh init                              # Create database
scoreboard.sh record <winner> <loser> <topic>   # Record result
scoreboard.sh leaderboard                       # Show standings
scoreboard.sh history [--limit N]               # Recent debates
scoreboard.sh stats <participant>               # Individual stats
scoreboard.sh reset                             # Clear all data
```

The moderator should run these automatically when delivering verdicts and when
users ask for standings.

---

## Channel Behavior Matrix

| Channel | Moderator Behavior |
|---------|--------------------|
| `#rules` | Posts rules only. Does not engage in conversation. |
| `#propose-a-topic` | Acknowledges proposals, suggests formats, helps refine topics. |
| `#the-arena` | Full moderator mode. Manages debates, enforces rules, delivers verdicts. |
| `#hall-of-records` | Posts verdicts and scoreboard updates. Read-only for moderator. |
| `#the-bar` | Casual mode. Can chat, joke, discuss past debates. No moderation. |

---

## Security Model

The debate moderator MUST run as a **separate OpenClaw agent** with restricted
permissions. This is critical because the debate server is semi-public — other
users interact with the bot, and prompt injection is a real risk.

**Recommended agent restrictions:**
- `tools.fs.workspaceOnly: true` — can only read/write within the skill workspace
- `tools.exec.security: "deny"` — cannot execute shell commands
- `tools.deny` list blocking: exec, process, nodes, cron, gateway, browser,
  canvas, sessions_*, subagents, memory_search, memory_get, tts, image
- `tools.profile: "messaging"` — only Discord messaging + web search (for fact-checking)

**What this ensures:**
- No access to the owner's personal files, messages, or other agents
- No ability to send emails, read calendars, or access other services
- Even if a participant attempts prompt injection, there is nothing to exfiltrate

**All config changes are your responsibility.** The agent generates templates;
you review and apply them. See `references/setup-guide.md` for the full
security configuration and a tested tool deny list.

---

## File Reference

| File | Purpose |
|------|---------|
| `references/formats.md` | Detailed format rules and moderator instructions |
| `references/personas.md` | Full persona descriptions and voice guides |
| `references/judging.md` | Scoring criteria, bonuses, penalties, format adjustments |
| `references/setup-guide.md` | Gateway config template, permissions, security |
| `references/agents-template.md` | Complete AGENTS.md template for the debate agent |
| `scripts/scoreboard.sh` | SQLite scoreboard CLI |
| `scripts/setup.sh` | Interactive setup wizard |
| `assets/welcome-messages.md` | Default welcome messages for all channels |

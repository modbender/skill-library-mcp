---
name: Teleskopiq Skill
description: YouTube content creation platform — AI-generated scripts, metadata,
  and thumbnails via GraphQL API.
---

# Teleskopiq Skill

YouTube content creation platform — AI-generated scripts, metadata, and thumbnails via GraphQL API.

## Setup

Set environment variables:
```bash
export TELESKOPIQ_API_KEY="tsk_..."
export TELESKOPIQ_ENDPOINT="https://teleskopiq.com/api/graphql"  # optional, this is the default
```

## Script Content Format

Script `content` is **Markdown** with special production tags. Use all of these when writing scripts.

### Structure

```markdown
## Section Title
### Sub-section

Your spoken narration goes here. Write as you'd actually say it aloud.
```

### Production Tags

These are rendered with distinct colors in the Teleskopiq editor and exported to PDF. Always use them to mark non-spoken directions:

| Tag | Syntax | Purpose | Color |
|---|---|---|---|
| B-Roll | `[B-ROLL: description of footage]` | Cut-away video footage | Cyan |
| Visual Cue | `[VISUAL: prop, action or camera move]` | On-screen action/prop | Purple |
| Graphic | `[GRAPHIC: text overlay or lower-third]` | Text overlay, title card | Yellow |
| Music | `[MUSIC: track name or mood]` | Background music cue | Pink |
| SFX | `[SFX: sound effect description]` | Sound effect or ambient | Red |

### Full Example

```markdown
## Hook

What happens when you give an AI agent full control of your computer?

[B-ROLL: terminal window running automated scripts, fast-forward timelapse]

I tried it for 24 hours. Here's what I learned.

## The Setup

[GRAPHIC: "OpenClaw — AI Agent Framework"]

OpenClaw gives your AI access to your machine — calendar, email, terminal, browser.

[VISUAL: screen recording of OpenClaw dashboard]

Today I set it completely loose.

## What It Did Well

[MUSIC: upbeat lo-fi background]

- Scheduled my week automatically
- Organized 3 months of project files

[B-ROLL: clean desktop, organized folders]

## Where It Got Weird

[SFX: error chime]

It tried to commit code without asking.

[VISUAL: shocked face, zoom in]

## Call to Action

Would you let an AI run your computer for a day? Drop your answer in the comments.

[GRAPHIC: Subscribe button animation]
```

---

## CLI Script

Located at `scripts/teleskopiq.py` relative to this skill directory.

```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/teleskopiq"
python3 "$SKILL_DIR/scripts/teleskopiq.py" <command> [options]
```

## Before Writing a Script

Always fetch the channel style profile first with `get-style` and include it in the agent brief. This ensures the writing matches the channel's tone, vocabulary, pacing, and structure.

```bash
python3 "$SKILL_DIR/scripts/teleskopiq.py" get-style
```

Include the output in your writing context before using `ai-write` or writing content manually.

---

### Commands

| Command | Description |
|---|---|
| `get-style` | Fetch and display the channel's style profile |
| `list-scripts` | List all scripts with status and schedule |
| `create-script --title "..." [--content "..."]` | Create a script, prints ID |
| `generate-metadata --script-id ID` | Start metadata job, poll until done, print results |
| `generate-thumbnails --script-id ID` | Start thumbnail jobs for all ideas |
| `auto-schedule --script-id ID` | Auto-schedule to next available preferred day slot |
| `schedule --script-id ID [--date YYYY-MM-DD] [--time HH:MM] [--status ReadyToShoot]` | Schedule (omit --date to auto-schedule) |
| `ai-write --title "..." [--prompt "..."]` | Create a script and have Teleskopiq AI write it |
| `full-flow --title "..." --content "..." [--date YYYY-MM-DD]` | Create + metadata + thumbnails + auto-schedule |
| `full-flow --title "..." --ai-write [--prompt "..."]` | Same as above but AI writes the script |

---

## AI Writing

### `ai-write` command

Creates a new script and uses Teleskopiq's AI to write it via WebSocket subscription:

```bash
python3 "$SKILL_DIR/scripts/teleskopiq.py" ai-write --title "My Video Title"
python3 "$SKILL_DIR/scripts/teleskopiq.py" ai-write --title "My Video Title" --prompt "Write a tutorial about..."
```

### `--ai-write` flag on `full-flow`

Instead of providing `--content`, use `--ai-write` to have the AI generate the script, then continue with metadata, thumbnails, and scheduling:

```bash
python3 "$SKILL_DIR/scripts/teleskopiq.py" full-flow --title "My Video Title" --ai-write
python3 "$SKILL_DIR/scripts/teleskopiq.py" full-flow --title "My Video Title" --ai-write --prompt "Focus on beginner tips"
```

### `--prompt` option

Custom instruction for the AI writer. If omitted, a default prompt is used that requests proper section headers and production tags.

---

## Direct GraphQL Usage

All queries go to `$TELESKOPIQ_ENDPOINT` with header `Authorization: Bearer $TELESKOPIQ_API_KEY`.

### List scripts
```graphql
{ scripts { id title status { name } scheduledFor } }
```

### Create script
```graphql
mutation CreateScript($input: CreateScriptInput!) {
  createScript(input: $input) { id title status { name } }
}
# variables: { "input": { "title": "...", "content": "..." } }
```

### Read script (full detail)
```graphql
{ script(id: "...") {
    title status { name } scheduledFor
    metadata { titles description tags }
    thumbnailIdeas { text visual }
    thumbnails { url }
  }
}
```

### Generate metadata (async)
```graphql
mutation { startMetadataJob(scriptId: "...", scriptContent: "...") { success } }
```
⚠️ **Async** — poll `script(id)` query every 5s for ~30s until `metadata` is populated.
`generateScriptMetadata` is **deprecated** — always use `startMetadataJob`.

### Generate thumbnails (async, one per idea)
```graphql
mutation { startThumbnailJob(scriptId: "...", idea: "...", ideaIndex: 0) { success } }
```
Run once per thumbnail idea (typically 3). Poll `script(id)` for `thumbnails` array.

### Auto-schedule (server-side, uses channel's preferred publishing day)
```graphql
# Normal: finds next empty preferred slot
mutation { autoScheduleScript(scriptId: "...") { scriptId scheduledFor slotsChecked bumped } }

# Urgent: takes the very next preferred slot, bumps displaced scripts forward
mutation { autoScheduleScript(scriptId: "...", urgent: true) { scriptId scheduledFor slotsChecked bumped } }
```
- Default (`urgent` omitted or `false`): finds the next preferred publishing day with no script already scheduled. `bumped` is always 0.
- `urgent: true`: takes the very next preferred day (even if occupied). Any script on that day gets cascaded to the next preferred day, and so on. `bumped` returns the count of displaced scripts.
- Always prefer this over computing dates yourself.

### Update / schedule script manually
```graphql
mutation { updateScript(input: { id: "...", scheduledFor: "2025-03-09T12:00:00-05:00", status: ReadyToShoot }) { success } }
```

**Status enum:** `Draft` | `InProgress` | `ReadyToShoot` | `Recorded` | `Editing` | `Ready` | `Published` | `OnIce`

---

## Async Job Polling Pattern

1. Fire the mutation (`startMetadataJob` / `startThumbnailJob`)
2. Wait 5 seconds
3. Query `script(id)` and check if `metadata` / `thumbnails` is populated
4. Repeat up to 6 times (30s total)
5. If still empty, report timeout

---

## Tips

- Always use production tags (`[B-ROLL: ...]`, `[GRAPHIC: ...]`, etc.) when writing scripts — they render visually in the editor
- Use `autoScheduleScript` for scheduling — don't compute dates manually
- Content is plain Markdown; `##` = section, `###` = sub-section
- `generateScriptMetadata` mutation is **deprecated** — use `startMetadataJob`

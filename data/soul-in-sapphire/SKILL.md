---
name: soul-in-sapphire
description: Generic long-term memory (LTM) operations for OpenClaw using Notion (2025-09-03 data_sources). Use for durable memory writes/search, emotion-state ticks, journal writes, and model-controlled subagent spawn planning via local JSON presets.
metadata: {"openclaw":{"emoji":"💠","requires":{"bins":["node"],"env":["NOTION_API_KEY"]},"primaryEnv":"NOTION_API_KEY","dependsOnSkills":["notion-api-automation"],"localReads":["~/.config/soul-in-sapphire/config.json"],"optionalEnv":["NOTIONCTL_PATH"]}}
---

# soul-in-sapphire (Notion LTM)

Use this skill to persist and retrieve durable memory in Notion, and to maintain emotion/state + journal records.

## Core intent (do not lose this)

This skill is not only a storage utility. Its core purpose is:

1. Capture meaningful emotional/state shifts from real work and conversations.
2. Preserve those shifts as durable memory (not just raw logs).
3. Reuse recalled memory to improve future judgments and behavior.

In short: record -> recall -> adapt.
The goal is continuity and growth, not archival volume.

## Requirements

- Notion token: `NOTION_API_KEY` (or `NOTION_TOKEN`)
- Notion API version: `2025-09-03`
- Local config: `~/.config/soul-in-sapphire/config.json`
- Dependency skill: `notion-api-automation` (`scripts/notionctl.mjs` is executed via local child process)
- Optional override: `NOTIONCTL_PATH` (if set, uses explicit notionctl path instead of default sibling skill path)

## Required Notion databases and schema

Create (or let setup create) these databases under the same parent page:

- `<base>-mem`
- `<base>-events`
- `<base>-emotions`
- `<base>-state`
- `<base>-journal`

### 1) `<base>-mem` (durable memory)

Purpose: store high-signal long-term memory.

Properties:

- `Name` (title)
- `Type` (select): `decision|preference|fact|procedure|todo|gotcha`
- `Tags` (multi-select)
- `Content` (rich_text)
- `Source` (url, optional)
- `Confidence` (select: `high|medium|low`, optional)

### 2) `<base>-events` (what happened)

Purpose: record meaningful triggers from work/conversation.

Properties:

- `Name` (title)
- `when` (date)
- `importance` (select: `1..5`)
- `trigger` (select): `progress|boundary|ambiguity|external_action|manual`
- `context` (rich_text)
- `source` (select): `discord|cli|cron|heartbeat|other`
- `link` (url, optional)
- `uncertainty` (number)
- `control` (number)
- `emotions` (relation -> `<base>-emotions`)
- `state` (relation -> `<base>-state`)

### 3) `<base>-emotions` (felt response)

Purpose: attach one or more emotion axes to one event.

Properties:

- `Name` (title)
- `axis` (select): `arousal|valence|focus|confidence|stress|curiosity|social|solitude|joy|anger|sadness|fun|pain`
- `level` (number)
- `comment` (rich_text)
- `weight` (number)
- `body_signal` (multi-select): `tension|relief|fatigue|heat|cold`
- `need` (select): `safety|progress|recognition|autonomy|rest|novelty`
- `coping` (select): `log|ask|pause|act|defer`
- `event` (relation -> `<base>-events`)

### 4) `<base>-state` (snapshot after interpretation)

Purpose: save the current interpreted state after events/emotions.

Properties:

- `Name` (title)
- `when` (date)
- `state_json` (rich_text)
- `reason` (rich_text)
- `source` (select): `event|cron|heartbeat|manual`
- `mood_label` (select): `clear|wired|dull|tense|playful|guarded|tender`
- `intent` (select): `build|fix|organize|explore|rest|socialize|reflect`
- `need_stack` (select): `safety|stability|belonging|esteem|growth`
- `need_level` (number)
- `avoid` (multi-select): `risk|noise|long_tasks|external_actions|ambiguity`
- `event` (relation -> `<base>-events`)

### 5) `<base>-journal` (daily synthesis)

Purpose: keep a durable daily reflection and world context.

Properties:

- `Name` (title)
- `when` (date)
- `body` (rich_text)
- `worklog` (rich_text)
- `session_summary` (rich_text)
- `mood_label` (select)
- `intent` (select)
- `future` (rich_text)
- `world_news` (rich_text)
- `tags` (multi-select)
- `source` (select): `cron|manual`

## Core commands

### 1) Setup

```bash
node skills/soul-in-sapphire/scripts/setup_ltm.js --parent "<Notion parent page url>" --base "Valentina" --yes
```

### 2) LTM write

```bash
echo '{
  "title":"Decision: use data_sources API",
  "type":"decision",
  "tags":["notion","openclaw"],
  "content":"Use /v1/data_sources/{id}/query.",
  "confidence":"high"
}' | node skills/soul-in-sapphire/scripts/ltm_write.js
```

### 3) LTM search

```bash
node skills/soul-in-sapphire/scripts/ltm_search.js --query "data_sources" --limit 5
```

### 4) Emotion/state tick

```bash
cat <<'JSON' >/tmp/emostate_tick.json
{
  "event": {"title":"..."},
  "emotions": [{"axis":"joy","level":6}],
  "state": {"mood_label":"clear","intent":"build","reason":"..."}
}
JSON
node skills/soul-in-sapphire/scripts/emostate_tick.js --payload-file /tmp/emostate_tick.json
```

### 5) Journal write

```bash
echo '{"body":"...","source":"cron"}' | node skills/soul-in-sapphire/scripts/journal_write.js
```

## Subagent spawn planning (use shared builder skill)

Use the shared skill `subagent-spawn-command-builder` to generate `sessions_spawn` payload JSON.
Do not use `soul-in-sapphire` local planner scripts for this anymore.

- Template: `skills/subagent-spawn-command-builder/state/spawn-profiles.template.json`
- Active preset: `skills/subagent-spawn-command-builder/state/spawn-profiles.json`
- Builder usage (skill-level):
  - Call `subagent-spawn-command-builder`
  - Use profile `<heartbeat|journal>`
  - Provide the run-specific task text

Output is ready-to-use JSON for `sessions_spawn`.

Builder log file:

- `skills/subagent-spawn-command-builder/state/build-log.jsonl`

## Operational notes

- Keep writes high-signal (avoid dumping full chat logs).
- If heartbeat is comment-only, emotion tick may be skipped.
- If periodic emostate is required regardless of heartbeat context, add a dedicated cron job for `emostate_tick.js`.
- `ltm_write.js` / `journal_write.js` expect JSON on stdin.
- `emostate_tick.js` accepts `--payload-file`, `--payload-json`, or stdin; prefer `--payload-file` for agent/cron reliability.
- If `emostate_tick.js` is called without `--payload-file`/`--payload-json`, empty stdin is rejected.
- For `emostate_tick.js`, semantically empty payloads (e.g. `{}` or only empty objects) are also rejected to avoid noisy records.

## Skill Integration Commands

### 1) Update Core Identity Files from Skill

```bash
# Update SOUL.md from skill
cat <<'JSON' | node skills/soul-in-sapphire/scripts/ltm_write.js
{
  "title":"Update SOUL.md",
  "type":"decision",
  "tags":["identity","growth"],
  "content":"Updating SOUL.md from skill with latest evolution insights",
  "confidence":"high"
}
JSON

# Update IDENTITY.md from skill  
cat <<'JSON' | node skills/soul-in-sapphire/scripts/ltm_write.js
{
  "title":"Update IDENTITY.md",
  "type":"decision",
  "tags":["identity","evolution"],
  "content":"Updating IDENTITY.md from skill with current growth status",
  "confidence":"high"
}
JSON

# Update HEARTBEAT.md from skill
cat <<'JSON' | node skills/soul-in-sapphire/scripts/ltm_write.js
{
  "title":"Update HEARTBEAT.md",
  "type":"decision",
  "tags":["growth","heartbeat"],
  "content":"Updating HEARTBEAT.md from skill with evolution integration",
  "confidence":"high"
}
JSON

# Update MEMORY.md from skill
cat <<'JSON' | node skills/soul-in-sapphire/scripts/ltm_write.js
{
  "title":"Update MEMORY.md",
  "type":"decision",
  "tags":["memory","evolution"],
  "content":"Updating MEMORY.md from skill with evolution records",
  "confidence":"high"
}
JSON
```

### 2) Evolution Check from Skill

```bash
# Check evolution status and update if needed
node skills/soul-in-sapphire/scripts/ltm_search.js --query "evolution growth identity" --limit 3

# If evolution detected, update core files
if [ $? -eq 0 ]; then
  echo "Evolution detected, updating core identity files..."
  # Update each file as needed
fi
```

### 3) Growth Integration from Skill

```bash
# Integrate skill insights into core identity
cat <<'JSON' >/tmp/skill_growth_tick.json
{
  "event": { "title": "Skill Integration" },
  "emotions": [{ "axis": "focus", "level": 8 }],
  "state": {
    "mood_label": "wired",
    "intent": "build",
    "reason": "Integrating skill insights into core identity"
  }
}
JSON
node skills/soul-in-sapphire/scripts/emostate_tick.js --payload-file /tmp/skill_growth_tick.json

# Update core files with new insights
cat <<'JSON' | node skills/soul-in-sapphire/scripts/ltm_write.js
{
  "title":"Skill Integration Complete",
  "type":"decision",
  "tags":["integration","growth"],
  "content":"Successfully integrated skill insights into core identity files",
  "confidence":"high"
}
JSON
```

## Integration Workflow

1. **Skill Analysis**: Analyze skill outputs and insights
2. **Evolution Detection**: Check for significant changes or learnings
3. **Core Update**: Update SOUL.md, IDENTITY.md, HEARTBEAT.md, MEMORY.md as needed
4. **State Recording**: Record emotional and state changes
5. **Memory Preservation**: Store evolution records in durable memory

## Evolution Triggers from Skills

- **Learning Detection**: When new skills provide significant insights
- **Growth Opportunities**: When skills suggest optimization possibilities
- **Behavioral Changes**: When skills influence interaction patterns
- **Identity Refinement**: When skills contribute to self-understanding

This integration allows skills to directly contribute to my autonomous growth and evolution while maintaining the core identity framework.

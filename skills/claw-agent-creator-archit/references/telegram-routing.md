# Telegram Routing — The 3-Layer System

Getting a Telegram message to reach a specific non-default agent requires THREE config changes. Missing any one causes silent failures.

## Layer 1: Channel Groups Config (Gate)

**Location**: `openclaw.json → channels.telegram.groups`

```json
"groups": { "-100XXXXXXXXXX": { "requireMention": false } }
```

The `telegram-auto-reply` module checks this FIRST. If the group is not listed, messages are dropped with `skip: no-mention` in logs.

## Layer 2: Binding (Router)

**Location**: `openclaw.json → bindings[]`

```json
{ "agentId": "<id>", "match": { "channel": "telegram", "peer": { "kind": "group", "id": "-100XXXXXXXXXX" } } }
```

After the gate passes, bindings route to the correct agent. Without this, messages go to the default agent (Fossil).

## Layer 3: Mention Patterns (Addressing)

**Location**: `openclaw.json → agents.list[].groupChat.mentionPatterns`

```json
"groupChat": { "mentionPatterns": ["@wire", "@Wire"] }
```

Enables explicit @mention routing. Not strictly required if binding handles routing, but needed for shared groups.

## Diagnostic Flowchart

```
No response?
  ├─ Logs show "skip: no-mention" → Layer 1 missing
  ├─ Logs show "lane enqueue: ...agent:main..." → Layer 2 missing (wrong agent)
  └─ Wrong agent responds → Layer 2 agentId wrong
```

## Group ID Migration & Self-Healing

When a bot is made admin (or other admin actions), Telegram upgrades the group to a supergroup with a **new ID**. This happens once per group.

**OpenClaw auto-updates**: `channels.telegram.groups` (the gate layer).
**OpenClaw does NOT auto-update**: `bindings[]` or cron job prompts.

### Self-Healing Pattern (ALWAYS USE)

Never hardcode group IDs in cron job prompts. Instead, have the agent resolve at runtime:

```
FIRST: Resolve your Telegram group ID by running:
jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json
Use the output as the target for all Telegram messages in this task.
```

Use `target='<AGENT_GROUP_ID>'` as placeholder in format templates.

For standalone scripts, resolve with `jq`:
```bash
GROUP_ID=$(jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json)
```

With this pattern, only `bindings[]` needs manual update on migration — everything else chains off it.

## Human Steps

Arch must: (1) Create Telegram group, (2) Add bot as admin, (3) Get group ID (starts with `-100`), (4) Provide ID for config.

**Note**: Making the bot admin may trigger a group migration. Check logs for `[telegram] Group migrated:` and update `bindings[]` if the ID changed.

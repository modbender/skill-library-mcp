---
name: pi-workflow
description: "Self-improvement reminder for Pi workflow at agent bootstrap"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap"]}}
---

# Pi Workflow Self-Improvement Hook

Injects a reminder to evaluate and capture learnings at session bootstrap.

## What It Does

- Fires on `agent:bootstrap` (at session start, before workspace files are injected)
- Injects a virtual `PI_WORKFLOW_REMINDER.md` file with:
  - When to log lessons (corrections, insights, patterns)
  - When to log errors (command failures, API errors)
  - When to log features (capability gaps)
  - How to track recurring patterns (Recurrence-Count)
  - Promotion path to AGENTS.md, SOUL.md, TOOLS.md
  - Link to detailed guide (`references/phase1-phase2-enhanced-lessons.md`)

## Setup

### Automatic (ClawHub)

```bash
clawdhub install pi-workflow
```

Hook is included and enabled by default.

### Manual Installation

1. Copy hook directory to OpenClaw hooks folder:

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/pi-workflow
```

2. Enable the hook:

```bash
openclaw hooks enable pi-workflow
```

3. Verify it's registered:

```bash
openclaw hooks list
```

You should see `pi-workflow` in the output.

## Configuration

No configuration needed. The hook fires automatically on every agent bootstrap (session start).

### To Disable Temporarily

```bash
openclaw hooks disable pi-workflow
```

### To Re-enable

```bash
openclaw hooks enable pi-workflow
```

## How It Works

1. **Session Start**: OpenClaw fires `agent:bootstrap` event
2. **Handler Executes**: handler.ts/handler.js processes the event
3. **Virtual File Injected**: `PI_WORKFLOW_REMINDER.md` is added to bootstrap context
4. **Reminder Appears**: You see the reminder at session start

The reminder includes:
- Quick reference for when to log lessons/errors/features
- Format reminders (IDs, metadata fields)
- Recurring pattern detection tips
- Link to detailed guide

## Safety Notes

- Hook only outputs text—no file modifications
- Runs with agent permissions only
- Skips sub-agent sessions (prevents cascade injection)
- Fires once per session at bootstrap

## Troubleshooting

### Hook Not Appearing

1. **Check if enabled**: `openclaw hooks list`
2. **Restart gateway**: `openclaw gateway restart`
3. **Verify hook path**: Should be `~/.openclaw/hooks/pi-workflow/`
4. **Check syntax**: Look for TypeScript/JavaScript errors in handler file

### Too Much Output

The reminder is ~400 tokens. To reduce output, edit `handler.ts` or `handler.js`:
- Shorten `REMINDER_CONTENT` text
- Remove less-important sections

### Conflicts with Other Hooks

If you have multiple hooks on `agent:bootstrap`, they all fire. The order depends on alphabetical hook name. If there are conflicts, rename hook directory alphabetically (e.g., `pi-workflow` vs `zz-other-hook`).

## Extending the Hook

To customize the reminder:

1. Edit `handler.ts` or `handler.js`
2. Modify `REMINDER_CONTENT` string
3. Restart gateway: `openclaw gateway restart`

Example customization: Add link to internal wiki, remove certain sections, etc.

## Files

- `handler.ts` — TypeScript implementation
- `handler.js` — JavaScript implementation (fallback if TS not available)
- `HOOK.md` — This file

## Integration with Phase 1+2 System

This hook enhances the Phase 1+2 self-improvement workflow by:

1. **Reminding at session start** — "Remember to capture learnings"
2. **Quick reference** — Shows format without opening files
3. **Guidance** — Explains when to use lessons vs errors vs features
4. **Linking** — Points to detailed guide in skill repo

It's optional but recommended for continuous improvement.

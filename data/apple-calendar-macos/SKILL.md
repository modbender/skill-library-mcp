---
name: Apple Calendar (MacOS)
slug: apple-calendar-macos
version: 1.0.0
homepage: https://clawic.com/skills/apple-calendar-macos
description: Use local CLI to manage Apple, Google, iCloud, Outlook, CalDAV, and other calendars synced in macOS Calendar, without API keys or OAuth.
changelog: Initial release with unified macOS Calendar operations, deterministic command fallback, and safety-first write verification.
metadata: {"clawdbot":{"emoji":"📅","requires":{"bins":[],"anyBins":["apple-calendar-cli","icalBuddy","shortcuts","osascript"],"config":["~/apple-calendar-macos/"]},"os":["darwin"],"configPaths":["~/apple-calendar-macos/"]}}
---

## Setup

On first use, follow `setup.md` to establish local operating context and confirmation preferences before any calendar write.

## When to Use

User wants to manage events from the macOS Calendar stack where Google, iCloud, Exchange, and CalDAV accounts are already synced locally.
Agent handles lookup, create, update, delete, conflict checks, and post-write verification without provider OAuth setup.

## Requirements

- macOS with Calendar app access enabled for terminal tools.
- At least one working command path: `apple-calendar-cli`, `icalBuddy`, `shortcuts`, or `osascript`.
- User confirmation before destructive operations.
- Provider accounts should already be connected in Calendar.app; this skill does not run provider OAuth.

## Architecture

Memory lives in `~/apple-calendar-macos/`. See `memory-template.md` for structure.

```text
~/apple-calendar-macos/
├── memory.md                  # Status, defaults, and confirmation behavior
├── command-paths.md           # Detected CLI path and fallback status
├── timezone-defaults.md       # Preferred timezone and date style
└── safety-log.md              # Deletions, bulk edits, and rollback notes
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and first-run behavior | `setup.md` |
| Memory structure | `memory-template.md` |
| Command path matrix | `command-paths.md` |
| Safety checklist before writes | `safety-checklist.md` |
| Calendar operation patterns | `operation-patterns.md` |
| Troubleshooting and recovery | `troubleshooting.md` |

## Data Storage

All skill files are stored in `~/apple-calendar-macos/`.
Before creating or changing local files, describe the planned write and ask for confirmation.

## Core Rules

### 1. Treat Calendar.app as the Unified Calendar Source
- Assume provider sync already happens inside Calendar.app and operate on that local unified view.
- Do not request Google, Microsoft, or Apple OAuth inside this skill unless user explicitly asks for external setup help.

### 2. Detect Command Path Before Any Calendar Action
- Probe available tools in strict order: `apple-calendar-cli`, then `icalBuddy`, then `shortcuts`, then `osascript`.
- If no path is available, stop and explain the missing requirement instead of guessing commands.

### 3. Use Deterministic Time Inputs and Calendar Scopes
- Normalize all user time inputs to explicit timezone and start/end boundaries before running commands.
- Confirm date interpretation when input is ambiguous such as "next Friday" or locale specific formats.

### 4. Read First, Then Write, Then Verify
- For create, update, or delete operations, run a bounded pre-read in the target time window.
- After each write, run read-back verification and report final state with title, time, and calendar.

### 5. Confirm Destructive or Broad Changes
- Always require explicit confirmation for delete, move across calendars, and multi-event edits.
- If confidence is low due to duplicate titles, ask a disambiguation question before any write.

### 6. Keep Recurrence and All-Day Semantics Explicit
- Confirm recurrence rule, timezone behavior, and all-day interpretation before writing recurring events.
- Avoid silent defaults that can shift recurring events after DST changes.

### 7. Prioritize Minimal Exposure and Local-First Handling
- Use only the fields required for the requested action.
- Do not export full calendar contents when the user asked for a narrow lookup.
- Do not send event data to third-party APIs from this skill.

## Common Traps

- Editing by title only when duplicates exist -> wrong event modified.
- Writing recurring events without timezone confirmation -> drift after DST.
- Deleting without pre-read snapshot -> difficult recovery.
- Trusting one CLI path blindly -> brittle behavior across macOS setups.
- Running broad searches by default -> noisy output and accidental edits.

## Security & Privacy

**Data that stays local:**
- Calendar operation context and defaults in `~/apple-calendar-macos/`.
- Event metadata used for requested operations.

**Data that may leave your machine:**
- None by default. Commands target local macOS Calendar data already synced on the device.

**This skill does NOT:**
- Request undeclared API keys.
- Send calendar data to third-party APIs.
- Execute destructive calendar writes without explicit confirmation.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `macos` - macOS workflows and system command patterns.
- `events` - event planning and structure patterns.
- `meetings` - meeting prep and follow-up workflows.
- `schedule` - broader scheduling and planning workflows.
- `remind` - reminder design and deadline management patterns.

## Feedback

- If useful: `clawhub star apple-calendar-macos`
- Stay updated: `clawhub sync`

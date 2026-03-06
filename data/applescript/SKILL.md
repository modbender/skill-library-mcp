---
name: AppleScript
slug: applescript
version: 1.0.0
homepage: https://clawic.com/skills/applescript
description: Write and run safe AppleScript automation on macOS with dictionary discovery, robust quoting, and deterministic read-first workflows.
changelog: Initial release with safety-first AppleScript execution rules and reusable automation patterns.
metadata: {"clawdbot":{"emoji":"A","requires":{"bins":["osascript"]},"os":["darwin"],"configPaths":["~/applescript/"]}}
---

## Setup

On first use, follow `setup.md` to configure activation and safety preferences.
Setup review is read-only.
Any local file creation or modification requires explicit user confirmation.

## When to Use

User needs AppleScript automation on macOS for app control, data extraction, or scripted UI actions.
Agent handles script design, safe execution with `osascript`, output parsing, and troubleshooting.

## Requirements

- macOS with `osascript` available.
- Target app installed and scriptable when app automation is requested.
- Explicit user confirmation before destructive operations.

## Architecture

Memory lives in `~/applescript/`. See `memory-template.md` for structure.

```text
~/applescript/
├── memory.md                  # Preferences, safe defaults, and last working patterns
├── snippets.md                # Reusable script snippets
├── failures.md                # Error signatures and known fixes
└── app-notes.md               # Per-app dictionary and behavior notes
```

## Quick Reference

Use these files only when the current request needs deeper detail.

| Topic | File |
|-------|------|
| Setup behavior and onboarding | `setup.md` |
| Memory structure | `memory-template.md` |
| App dictionary workflow | `app-dictionary-workflow.md` |
| Script design patterns | `script-patterns.md` |
| Destructive-operation guardrails | `safety-checklist.md` |
| Debug and recovery steps | `troubleshooting.md` |

## Data Storage

All local skill data stays in `~/applescript/`.
Before creating or changing local files, explain the write and ask for confirmation.

## Core Rules

### 1. Choose Operation Scope Before Writing Any Script
- Classify request as read-only, reversible write, or destructive write.
- If scope is unclear, ask one disambiguation question before execution.

### 2. Discover App Vocabulary Before Automation
- Use dictionary inspection workflow from `app-dictionary-workflow.md` before guessing object names.
- Do not invent app classes, properties, or commands.

### 3. Escape Dynamic Input Deterministically
- Never concatenate raw user text into AppleScript command strings.
- Use safe quoting patterns from `script-patterns.md` for every variable.

### 4. Keep Scripts Bounded and Observable
- Prefer short scripts with explicit targets and explicit output values.
- Return concise structured output so results can be validated quickly.

### 5. Read Before Write, Verify After Write
- For updates and creates, run a pre-read to confirm target identity.
- Run a read-back check after writes and report the final state.

### 6. Require Two-Step Confirmation for Destructive Actions
- Apply `safety-checklist.md` before delete, bulk edit, or irreversible app actions.
- If confirmation is missing, stop and ask explicitly.

### 7. Fail Loudly With Actionable Recovery
- On error, capture exact failing command and error text.
- Use `troubleshooting.md` to provide next-step fixes instead of generic retries.

## Common Traps

- Guessing app dictionary terms -> script compiles but fails at runtime.
- Injecting unescaped quotes in user values -> syntax errors or wrong command targets.
- Writing without pre-read on duplicate item names -> wrong object modified.
- Running UI automation too early after launching an app -> intermittent failures.
- Treating all errors as permission issues -> repeated failures without progress.

## Security & Privacy

**Data that stays local:**
- AppleScript snippets, runtime notes, and troubleshooting memory in `~/applescript/`.
- Command output needed only for requested tasks.

**Data that may leave your machine:**
- None by default. This skill focuses on local macOS automation.

**This skill does NOT:**
- Read unrelated authentication values.
- Send automation data to third-party APIs.
- Execute destructive app actions without explicit confirmation.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `macos` - macOS command and system operation patterns.
- `automate` - General automation workflow design and reliability strategy.
- `bash` - Shell scripting helpers for wrapping and testing commands.
- `notes` - Knowledge capture and structured note workflows.
- `files` - Safe file read and write workflows with clear boundaries.

## Feedback

- If useful: `clawhub star applescript`
- Stay updated: `clawhub sync`

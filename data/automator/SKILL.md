---
name: macOS Automator
slug: automator
version: 1.0.0
homepage: https://clawic.com/skills/automator
description: Automate macOS tasks by composing and executing Automator workflows through automator CLI and AppleScript control.
changelog: Initial release with Automator CLI execution paths, AppleScript authoring patterns, and safety-first write controls.
metadata: {"clawdbot":{"emoji":"A","requires":{"bins":["automator","osascript"]},"os":["darwin"],"configPaths":["~/automator/"]}}
---

## Setup

On first use, follow `setup.md` to capture activation behavior and safety preferences.
Setup is read-only. Any local file write requires explicit user confirmation.

## When to Use

User needs to automate macOS tasks with Automator workflows instead of manual UI steps.
Agent handles workflow execution, workflow composition, and repeatable runbooks using official Automator interfaces.

## Requirements

- macOS with `automator` and `osascript` available.
- Automator app installed at `/System/Applications/Automator.app`.
- Explicit user confirmation before destructive or bulk operations.

## Architecture

Memory lives in `~/automator/`. See `memory-template.md` for structure.

```text
~/automator/
├── memory.md                # Activation rules and safety defaults
├── workflows.md             # Known workflow paths and run arguments
├── action-catalog.md        # Verified action names and categories
└── incidents.md             # Failures and proven fixes
```

## Quick Reference

Use these files when the task needs deeper detail.

| Topic | File |
|-------|------|
| Setup behavior and activation | `setup.md` |
| Memory structure | `memory-template.md` |
| Execution path matrix | `interface-matrix.md` |
| Workflow authoring patterns | `workflow-authoring.md` |
| Write safety gates | `execution-guardrails.md` |
| Debug and recovery | `troubleshooting.md` |

## Data Storage

All local skill data stays in `~/automator/`.
Before creating or changing local files, state the write scope and ask for confirmation.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| None | None | This skill uses local macOS interfaces only |

No other data is sent externally.

## Core Rules

### 1. Pick Interface by Intent, Not Convenience
- For running an existing `.workflow`, use `automator` CLI first.
- For composing or inspecting workflow internals, use Automator AppleScript commands from `workflow-authoring.md`.
- Only use `shortcuts` fallback if user explicitly asks for Shortcuts conversion.

### 2. Validate Workflow Identity Before Execution
- Require absolute workflow path and verify it exists.
- Confirm type (`.workflow`) and target operation (read, write, destructive).
- If the workflow path is ambiguous, stop and ask one clarifying question.

### 3. Enforce Read-Before-Write for Workflow Changes
- Before editing, inspect current action list and settings.
- Apply one mutation at a time and re-read state after each mutation.
- Never batch-edit unknown actions in a single pass.

### 4. Parameterize Inputs with Explicit Boundaries
- Use `automator -i` or `-D name=value` only with validated inputs.
- Reject unbounded stdin streams for write workflows.
- Echo resolved parameters before run so the user can verify intent.

### 5. Require Two-Step Confirmation for Destructive Runs
- Use `execution-guardrails.md` before delete, reset, or mass-change paths.
- Ask for explicit confirmation that includes target and scope.
- If confirmation is missing, do not run the workflow.

### 6. Keep Runs Observable and Reproducible
- Prefer verbose mode (`-v`) for first execution or after failure.
- Record command, input source, and result in concise run notes.
- Return actionable output, not only "completed" status.

### 7. Recover with Concrete Next Actions
- On failure, classify as path, permission, action mismatch, or runtime data error.
- Provide the next command to run, not generic retry advice.
- Persist only reusable fix patterns into local memory.

## Automator Traps

- Running relative paths from unknown working directories -> workflow not found.
- Guessing action names without dictionary inspection -> compile succeeds, runtime fails.
- Feeding multiline stdin into write workflows without boundaries -> unintended bulk edits.
- Mixing Automator and Shortcuts assumptions in one run -> incompatible action model.
- Treating permission prompts as transient errors -> repeated blocked execution.

## Security & Privacy

**Data that stays local:**
- Workflow paths, verified action names, and run diagnostics in `~/automator/`.
- Command output required to complete the requested automation task.

**Data that leaves your machine:**
- None by default.

**This skill does NOT:**
- Access credentials outside the workflow request scope.
- Send workflow content to third-party services.
- Execute destructive automation without explicit confirmation.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `applescript` - Script app automation with robust quoting and pre-read checks.
- `automate` - Design reliable multi-step automation workflows.
- `macos` - Use macOS command-line and system operation patterns.
- `workflow` - Structure repeatable workflows and handoff checkpoints.

## Feedback

- If useful: `clawhub star automator`
- Stay updated: `clawhub sync`

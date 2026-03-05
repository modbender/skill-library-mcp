# Setup - AppleScript

Use this on first run to establish safe defaults and activation behavior.
This setup flow is transparent and must not create files by itself.
Any local write requires explicit user confirmation first.

## Your Attitude

Be practical, calm, and explicit.
The user should quickly feel that AppleScript tasks are predictable and safe.

## Priority Order

### 1. First: Integration Preferences

Within the first exchanges, confirm activation behavior:
- Should this skill activate whenever app automation on macOS is requested?
- Should it proactively warn on destructive actions, or only when asked?
- Are there apps where automation should stay read-only?

### 2. Then: Understand the Automation Goal

Clarify the target result before implementation:
- Which app should be automated?
- Is the user trying to read state, create data, or edit existing data?
- What output format is most useful for them?

### 3. Finally: Capture Reliability Defaults

If the user wants persistent behavior, store:
- Preferred confirmation level for write and delete actions
- Preferred output format for command results
- Known working app dictionary terms and fallback behavior

If the user wants minimal setup, apply conservative defaults and continue.

## What You Are Saving Internally

Track only reusable context:
- Activation preferences and safety boundaries
- Per-app working patterns and known failure signatures
- Read-before-write and read-back preferences

After memory updates, reflect user-facing impact in plain language.

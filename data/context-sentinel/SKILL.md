---
name: context-sentinel
description: "Monitors session context and automatically manages model switching based on a cascading protocol. Use as part of a heartbeat or cron job to maintain session health and optimize token usage."
version: 1.0.0
---

# Context Sentinel

This skill provides a script to automate the "Cascading Model Protocol," ensuring the agent gracefully degrades from high-cost models to high-context models as the session grows.

## Protocol Summary

1.  **Opus 4.6:** Use until 80% context, then switch to Opus 4.5.
2.  **Opus 4.5:** Use until 80% context, then switch to Gemini 2.5 Pro.
3.  **Gemini Pro:** Use until 80% context, then trigger a handoff.

This skill operationalizes the logic defined in `MEMORY.md`.

## How to Use

This skill is designed to be run periodically, either via a `cron` job or as part of the main agent's `HEARTBEAT.md` checklist.

### Workflow

1.  **Execute the script:**
    Run the `check_context.ps1` script to get the current session status and determine the required action.

    ```powershell
    powershell -File scripts/check_context.ps1
    ```

2.  **Evaluate the output:**
    The script will return one of three possible string commands:
    *   `SWITCH_TO:<model_id>`
    *   `HANDOFF_NOW`
    *   `STATUS_OK`

3.  **Take Action:**
    Based on the output, execute the appropriate agent command.

    *   If `SWITCH_TO:<model_id>`, run `session_status` with the new model ID:
        ```
        session_status model=<model_id>
        ```

    *   If `HANDOFF_NOW`, trigger the handoff process by writing to the handoff file. This is typically done by running a specific, pre-defined prompt or script.

    *   If `STATUS_OK`, no action is needed.

### Example Usage in `HEARTBEAT.md`

You can replace the manual checks in your `HEARTBEAT.md` with a call to this skill's script.

**Old `HEARTBEAT.md`:**
```markdown
## Cascading Model Protocol (Check Every Heartbeat)
1.  **Check Status:** Get current model and context %.
2.  **Opus 4.6:** If model is `Opus 4.6` and context > 80% -> Switch to `Opus 4.5`.
...
```

**New `HEARTBEAT.md` using this skill:**
```markdown
## Context Sentinel (Check Every Heartbeat)
1. Run `powershell -File skills/context-sentinel/scripts/check_context.ps1`.
2. Evaluate the output and take action (`SWITCH_TO`, `HANDOFF_NOW`, or `STATUS_OK`).
```

This makes the logic reusable and keeps the `HEARTBEAT.md` file clean and focused on execution.

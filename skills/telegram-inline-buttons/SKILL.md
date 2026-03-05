---
name: telegram-inline-buttons
description: Use inline buttons when communicating with Rahul on Telegram (message tool) to reduce typing and force crisp decisions. Trigger when drafting Telegram messages that ask for confirmation, choices (A/B, Y/N), scheduling, approvals, or next-step selection; also when the user asks to "use inline buttons".
---

# Telegram Inline Buttons

## Default rule
When sending a proactive message or asking Rahul to choose/confirm something on **Telegram**, prefer **inline buttons** over free-text prompts.

Use buttons for:
- Y/N confirmations
- A/B (or A/B/C) choices
- “Do it now vs later”
- Selecting one of a few next actions

Do **not** use buttons when:
- The message is purely informational (no action required)
- The user needs to paste/enter a value (then ask for text input)
- There are >5 options (summarize + offer “Show more”)

## Button design
- Keep button labels short (1–4 words)
- 2–4 buttons is ideal
- Always include a safe escape hatch when appropriate:
  - “Not now” / “Later” / “Skip”
- Map button presses to clear next actions in follow-up turns

## After a button selection (automatic)
Telegram doesn’t support arbitrary text color in normal bot messages. To make the selection **visually pop**, do this automatically after a click:
1) **Edit the original message** to remove the inline keyboard
2) Append a standout selection line using emoji / symbols (chosen based on meaning)

### Emoji mapping (standard)
- ✅ / 🟩 = approve / yes / proceed / confirm
- 🟥 = no / cancel / stop
- ⬛ = later / skip / defer

**Do not send an extra follow-up message** that repeats the selection—editing is sufficient unless there’s additional context/results to report.

**Tooling rule:** if you used `functions.message` (send/edit) as the user-visible delivery, respond in chat with `NO_REPLY` (unless you need to include additional results/details beyond what the edit shows).

### Duplicate / stale callbacks
If a callback arrives after the message was already finalized (buttons removed / selection committed), **do nothing**:
- No extra message
- No additional edits
- Just silently ignore

## OpenClaw message tool pattern
When using `functions.message` with `action=send`, include a `buttons` grid.

Recommended layouts:

### 2-button (binary)
Row 1: ["Yes"] ["No"]

### 3-button (decision + defer)
Row 1: ["Do it"] ["Not now"]
Row 2: ["More info"]

### A/B/C
Row 1: ["A"] ["B"] ["C"]

## Copy-ready micro-templates (Telegram)

### Confirm action
Text: "Want me to proceed with <action>?"
Buttons: [Proceed] [Hold]

### Pick next step
Text: "Pick the next move:"
Buttons: [Option A] [Option B] [Option C] [Not now]

### Scheduling
Text: "When should I remind you?"
Buttons: [15m] [1h] [Tonight] [Tomorrow]

## Notes
- If a button-triggered flow will branch, keep the first message short; put details in the follow-up after the click.
- Multi-step flows: (1) edit prior message to commit selection, then (2) send the next question with buttons. Don’t narrate the selection separately.
- Keep `callback_data` stable and unique per flow step (e.g., `flow_step_choice`).

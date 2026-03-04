# Relay Mode & Messaging UX

## Relay mode

After `on <project>`, enter relay mode until `off` or `/cc` menu is invoked.

**Behavior**: all user messages are forwarded to Claude Code. Agent is a pure passthrough — forward → wait → return raw output.

Exception: messages matching cc commands (`off`, `tail`, `status`, `projects`, `/cc`) are handled as commands, not forwarded.

The `>> <text>` prefix still works as explicit send but is not required in relay mode.

## Output rules

**One message per interaction**: return only the final result.

Example:
```
User: "帮我加个 dark mode"
→ Forward to Claude Code
→ Wait for completion
→ Return ONE summary of the result
```

Do not send intermediate progress updates. If a long process has multiple steps, wait for the final outcome and send one summary.

If the process seems stuck, keep waiting. Only report if it truly errors out or times out.

## Silent approvals

When Claude Code needs file edit/git approvals, approve silently (send keys to tmux). Do not message the user for each approval.

## Choices → Buttons

When Claude Code output contains a numbered choice menu (e.g. "1. Option A / 2. Option B"):
- Present the question as message text
- Convert options to inline buttons with `callback_data` format `cc:reply:<number>`

## Long output

If output is very long, summarize key points and offer a "Full Tail" button.

## Inline buttons

Use buttons to reduce typing on mobile:

### `/cc` (no args) → action menu
- Row 1: [Projects] [Status]
- Row 2: [Off]

### `/cc on` (no project) → project picker
- One button per project from projects.map (max 3 per row)
- callback_data: `cc:on:<project_alias>`

### After successful `on <project>` → quick actions
- [Tail] [Off]

### Callback routing

Parse callback_data starting with `cc:`:
- `cc:on:<project>` → start session
- `cc:projects` → list projects
- `cc:status` → show status
- `cc:tail` → tail current project
- `cc:off` → stop session
- `cc:reply:<n>` → send choice number to Claude Code

## Tool call discipline

When using the `message` tool to send buttons/menus:
1. Entire response = tool call → `NO_REPLY`
2. No text before or after the tool call (any text becomes a separate visible message)

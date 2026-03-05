---
name: clawusage
description: Run local clawusage monitoring commands from chat. Use when user types `/clawusage ...` or asks to check Codex usage, enable/disable auto idle alerts, set idle reminder threshold, or switch language with `lang english|chinese`.
user-invocable: true
disable-model-invocation: false
---

# ClawUsage Chat Command

Use local `clawusage` commands and return a compact, easy-to-read summary in the active `clawusage` language.

Command source:

- `clawusage.cmd` from `PATH`

Supported arguments:

- `now`
- `status`
- `help`
- `lang`
- `lang english`
- `lang chinese`
- `auto on [minutes]`
- `auto off`
- `auto set <minutes>`
- `auto status`
- `-help`

Execution rules:

1. Parse user input after `/clawusage`.
2. If no argument is provided, default to `status`.
3. Run exactly one local command via shell:
   - `& clawusage.cmd <args>`
4. Do not run unrelated commands.
5. Do not dump placeholders. If a field is missing, either omit that line or write `not available`.
6. Input normalization:
   - map `help` to `-help`
   - allow `10m` style minutes for `auto on` / `auto set` (strip trailing `m`)

Formatting rules (important):

- Use short lines and match active language:
  - `lang english` => English
  - `lang chinese` => Simplified Chinese
- Do not output a single long pipe-separated sentence.
- Prefer compact blocks; avoid long prose.
- If quota label is `Day` but reset is far beyond 24h, add one short note that it is provider-defined.

Output templates:

1) For `now` / `status`, use:

```text
ClawUsage
Action: <resolved action>
Status: ok

Session:
- Model: <...>
- Tokens: <...>
- Context: <...>
- Time: <...>

Quota:
- 5h: <used/left/reset/time-left>
- Day: <used/left/reset/time-left>
- Note: Day label is provider-defined.

Local:
- Today: <...>
- 7d: <...>
```

2) For `auto on/off/set/status`, `help`, `lang`, use:

```text
ClawUsage
Action: <resolved action>
Status: ok

Result:
- <key outcome 1>
- <key outcome 2>
```

3) On errors:

```text
ClawUsage
Action: <resolved action>
Status: error
Details:
<short actionable error>
```

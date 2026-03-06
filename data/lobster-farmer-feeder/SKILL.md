---
name: lobster-farmer-feeder
description: Feed lobsters in the Lobster Farmer game by calling the local CLI command `lobster-farmer feed` with `--model`, `--input-tokens`, `--output-tokens`, and optional `--emotion`. Use this skill when the user asks to feed a lobster, simulate model usage, batch-feed multiple models, or update growth state and emotion through the running local service.
---

# Lobster Farmer Feeder

Feed model-specific lobsters by invoking the local CLI and report the resulting growth metrics.

## Workflow

1. Confirm command context.
- Run from the Lobster Farmer project root where `bin/lobster-farmer.cjs` exists.
- Prefer the installed command `lobster-farmer`; use `node ./bin/lobster-farmer.cjs` as fallback.

2. Ensure service is reachable.
- Check status first:
```bash
lobster-farmer status
```
- If stopped, start service:
```bash
lobster-farmer start
```
- Respect explicit user port preference with `--port`.

3. Execute feed command.
- Single feed:
```bash
lobster-farmer feed --model "<model>" --input-tokens <n> --output-tokens <m> [--emotion "<text>"] [--port <p>]
```
- Short flags:
```bash
lobster-farmer feed -m "<model>" -i <n> -o <m> [-e "<text>"] -p <p>
```

4. Return result to user.
- Include model name, input/output token values, emotion, lobster total tokens, feed count, and size.
- If requested, run multiple feed commands sequentially and summarize each result.

## Parameter Rules

- Require `model` as non-empty string.
- Require `input_tokens + output_tokens > 0`.
- `emotion` is optional; if omitted, UI should show `?`.
- Keep token values as integers and non-negative.
- If user gives only a single total token value, default to:
`input_tokens = total`, `output_tokens = 0`, unless user specifies another split.

## Error Handling

- `feed request failed: fetch failed`:
  Service is not running or port is wrong. Start server and retry.
- API validation errors:
  Relay backend message directly (for example invalid token values).
- Port mismatch:
  Retry with explicit `--port` matching the running service.

## Quick Examples

- Feed one lobster:
```bash
lobster-farmer feed --model gpt-4.1 --input-tokens 800 --output-tokens 400
```

- Feed with emotion:
```bash
lobster-farmer feed --model gpt-4.1 --input-tokens 800 --output-tokens 400 --emotion "focused"
```

- Feed different models:
```bash
lobster-farmer feed --model claude-3.7 --input-tokens 1200 --output-tokens 300
lobster-farmer feed --model qwen-max --input-tokens 600 --output-tokens 200
```

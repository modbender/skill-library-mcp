---
name: cs-relogin
description: Fast OpenAI Codex account switch for OpenClaw via the local cs command. Use when user sends `cs relogin`, asks to re-login or switch ChatGPT Codex account, or pastes OAuth callback URL/code to complete login.
allowed-tools: ["Bash(cs:*)"]
metadata: {"clawdbot":{"emoji":"🔐"}}
---

# CS Relogin Skill

Use this skill to perform OpenAI Codex account switching without `openclaw onboard`.

## Hard rules

- Always execute `cs` directly, never call `openclaw onboard` for this task.
- Keep flow non-interactive.
- If user provided a callback URL/code, do completion step immediately.

## Workflow

1. If user input is exactly `cs relogin`:
   - Run:
     ```bash
     cs relogin
     ```
   - Return the login URL from command output.
   - Ask user to finish browser auth and paste callback URL.

2. If user input contains callback URL/code:
   - Run:
     ```bash
     cs relogin "<callback-url-or-code>"
     ```
   - Return key result lines:
     - relogin completed status
     - gateway restart status
     - active profile/account summary

3. If user asks status/debug:
   - Run:
     ```bash
     cs relogin status
     cs status
     ```
   - Summarize pending state and active account.

## Output format

- Keep response concise and actionable.
- Include exact next command when another step is needed.
- Never expose full tokens/secrets.
- On command failure, include raw cs stderr first (do not guess the reason).

## Acknowledgement rule (MUST)

- Every successful action must have an explicit acknowledgement (回执) to the user.
- Minimum acknowledgement content:
  - what was executed (e.g. `cs relogin`, `cs relogin <callback>`, `cs status`)
  - whether it succeeded
  - current state summary (pending relogin / active account)
- If command output is missing or tool callback is flaky, immediately run:
  ```bash
  cs relogin status
  cs status
  ```
  then send acknowledgement based on those results.
- Never end silently after command execution.

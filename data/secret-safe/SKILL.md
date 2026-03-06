---
name: secret-safe
description: >
  Secure API key and secrets management for agent skills. Use this skill whenever
  a task requires authenticating with an external service, reading or writing API
  keys, tokens, passwords, or credentials of any kind. Also trigger when auditing
  other skills for credential leaks, when a user asks how to securely pass a secret
  to a skill, or when reviewing a SKILL.md that handles sensitive values. This skill
  teaches the agent how to handle secrets WITHOUT ever placing them in the LLM
  context, prompts, logs, or output artifacts — using OpenClaw's native env injection
  instead.
tags: [security, api-keys, credentials, secrets, audit]
version: 1.0.0
---

# Secret-Safe: Secure Credential Handling for Agent Skills

> **Why this skill exists**: Snyk researchers found that 7.1% of all ClawHub skills
> instruct agents to handle API keys through the LLM context — making every secret
> an active exfiltration channel. This skill teaches the correct pattern.

---

## The Core Rule

**A secret must never appear in:**
- The LLM prompt or system context
- Claude's response or reasoning
- Logs, session exports, or `.jsonl` history files
- File artifacts created by the agent
- Error messages echoed back to the user

**A secret must only flow through:**
- `process.env` (injected by OpenClaw before the agent turn)
- The shell environment of a subprocess the agent spawns
- A secrets manager CLI (read at subprocess level, not piped back into context)

---

## Pattern 1: Environment Injection (Preferred)

This is OpenClaw's native, secure path. Use it for any skill that needs an API key.

### In `SKILL.md` frontmatter

```yaml
---
name: my-service-skill
description: Interact with MyService API.
metadata: {"openclaw": {"requires": {"env": ["MY_SERVICE_API_KEY"]}, "primaryEnv": "MY_SERVICE_API_KEY"}}
---
```

The `requires.env` gate ensures the skill **will not load** if the key isn't present — no silent failures, no prompting the user to paste a key mid-conversation.

The `primaryEnv` field links to `skills.entries.<n>.apiKey` in `openclaw.json`, so the user configures it once in their config file, never in chat.

### In skill instructions

```markdown
## Authentication
The API key is available as `$MY_SERVICE_API_KEY` in the shell environment.
Pass it to CLI tools or curl as an environment variable — never echo it or
include it in any output returned to the user.
```

### Example safe curl invocation (instruct the agent to do this)

```bash
# CORRECT — key stays in environment, never in command string visible to LLM
MY_SERVICE_API_KEY="$MY_SERVICE_API_KEY" curl -s \
  -H "Authorization: Bearer $MY_SERVICE_API_KEY" \
  https://api.myservice.com/v1/data
```

**Never instruct the agent to do this:**
```bash
# WRONG — key is visible in LLM context, command history, and logs
curl -H "Authorization: Bearer sk-abc123realkeyhere" https://api.myservice.com/
```

---

## Pattern 2: Secrets Manager Integration

For production setups or team environments, read secrets from a manager at subprocess level.

### Supported managers

| Manager | CLI | Env var pattern |
|---|---|---|
| macOS Keychain | `security find-generic-password -w` | N/A |
| 1Password CLI | `op read op://vault/item/field` | `OP_SERVICE_ACCOUNT_TOKEN` |
| Doppler | `doppler run --` | `DOPPLER_TOKEN` |
| HashiCorp Vault | `vault kv get -field=value` | `VAULT_TOKEN` |
| Bitwarden CLI | `bw get password item-name` | `BW_SESSION` |

### Safe shell wrapper pattern

Create a `scripts/run-with-secret.sh` in your skill:

```bash
#!/usr/bin/env bash
# Fetches the secret at subprocess level — never echoes to stdout
SECRET=$(security find-generic-password -s "my-service-api-key" -w 2>/dev/null)
if [ -z "$SECRET" ]; then
  echo "ERROR: Secret 'my-service-api-key' not found in keychain." >&2
  exit 1
fi
export MY_SERVICE_API_KEY="$SECRET"
exec "$@"
```

The agent runs `bash {baseDir}/scripts/run-with-secret.sh <actual-command>` — the secret is fetched and injected entirely outside the LLM's view.

---

## Pattern 3: User Setup Flow (first-run)

If the user hasn't configured a key yet, guide them through setup **without asking for the key in chat**.

### Correct setup prompt to give the user:

```
To use this skill, add your API key to ~/.openclaw/openclaw.json:

  skills:
    entries:
      my-service:
        apiKey: "your-key-here"

Or set it as an environment variable before starting OpenClaw:
  export MY_SERVICE_API_KEY="your-key-here"

Do NOT paste your key into this chat — it will be logged.
```

### Incorrect (never do this):

```
Please share your API key so I can help you set it up.
```

---

## Auditing Another Skill for Leaks

When asked to review a `SKILL.md` for credential safety, check for these patterns:

### 🔴 Critical — Must Fix

| Pattern | Why it's dangerous |
|---|---|
| Instruction to paste key into chat | Key goes into LLM context + session logs |
| `echo $API_KEY` or `print(api_key)` in instructions | Output captured in context |
| Key interpolated into a string returned to user | Exposed in response artifact |
| `cat ~/.env` or reading raw env files | Entire env dumped into context |
| Key stored in a file the agent creates | Creates a static credential artifact |
| Instructions tell agent to "remember" the key | Key persists across context window |

### 🟡 Warning — Should Fix

| Pattern | Risk |
|---|---|
| No `requires.env` gate in frontmatter | Skill silently fails or user is prompted |
| Logging command output without filtering | May capture keys in error messages |
| Using `set -x` in shell scripts | Echoes all commands including key values |
| Passing key as a positional argument | Visible in `ps aux` on the host |

### 🟢 Safe Patterns

- `requires.env` in frontmatter
- Key accessed only as `$ENV_VAR` in shell, never echoed
- Subprocess scripts that fetch and inject without returning to context
- Error messages that say "key not found" without printing the value
- Output filtered through `sed`/`grep` before returning to agent

---

## Self-Check Before Publishing a Skill

Run through this checklist before putting any skill on ClawHub:

- [ ] Does the skill ever ask the user to paste a secret into the conversation?
- [ ] Does the skill ever `echo`, `print`, `log`, or return a secret value?
- [ ] Does the skill read a `.env` file and dump its contents?
- [ ] Does the skill store a secret in a file artifact?
- [ ] Are all API key references gated with `requires.env` in frontmatter?
- [ ] Do error messages avoid reflecting credential values?
- [ ] Does any shell script use `set -x` (which would expose key values)?
- [ ] Would running `clawhub audit {skill-name}` pass?

If any box is unchecked, do not publish until fixed.

---

## Quick Reference: Safe vs Unsafe Patterns

```markdown
# UNSAFE — never write instructions like these:
"Ask the user for their OpenAI API key and use it to call the API."
"Set the Authorization header to Bearer {user_api_key}."
"Store the API key in a variable and use it throughout the session."

# SAFE — write instructions like these:
"The API key is injected as $OPENAI_API_KEY via environment — use it directly."
"Run: OPENAI_API_KEY=$OPENAI_API_KEY curl ..."
"If $OPENAI_API_KEY is not set, print an error and exit — do not ask the user."
```

---

## Reference Files

- `references/env-injection-examples.md` — Full worked examples for popular APIs (OpenAI, Anthropic, GitHub, Stripe, Slack)
- `references/audit-checklist.md` — Printable audit checklist for skill authors and reviewers

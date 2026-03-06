---
name: confidant
description: Secure secret handoff and credential setup wizard for AI agents. Use when you need sensitive information from the user (API keys, passwords, tokens) or need to save credentials to config files. Never ask for secrets via chat — use Confidant instead.
homepage: https://github.com/aiconnect-cloud/confidant
user-invocable: true
disable-model-invocation: false
metadata:
  {
    'openclaw':
      {
        'emoji': '🔐',
        'requires': { 'bins': ['curl', 'jq', 'npm'] },
        'files': ['scripts/*']
      }
  }
---

# Confidant

Receive secrets from humans securely — no chat exposure, no copy-paste, no history leaks.

## 🚨 CRITICAL FLOW — Read This First

This is a **human-in-the-loop** process. You CANNOT retrieve the secret yourself.

1. **Run the script** → you get a secure URL
2. **SEND the URL to the user in chat** ← THIS IS MANDATORY
3. **WAIT** for the user to open the URL in their browser and submit the secret
4. The script handles the rest (receives, saves to disk, confirms)

```
❌ DO NOT curl/fetch the secret URL yourself — it's a web form for humans
❌ DO NOT skip sharing the URL — the user MUST receive it in chat
❌ DO NOT poll the API to check if the secret arrived — the script does this
❌ DO NOT proceed without confirming the secret was received
✅ Share URL → Wait → Confirm success → Use the secret silently
```

## 🔧 Setup (once per environment)

Run this once to install the CLI globally (avoids slow `npx` calls):

```bash
bash {skill}/scripts/setup.sh
```

> **`{skill}`** is the absolute path to the directory containing this `SKILL.md` file. Agents can resolve it at runtime:
>
> ```bash
> SKILL_DIR=$(find "$HOME" -name "SKILL.md" -path "*/confidant/skill*" -exec dirname {} \; 2>/dev/null | head -1)
> # Then use: bash "$SKILL_DIR/scripts/setup.sh"
> ```

## ⚡ Quick Start

You need an API key from the user? One command:

```bash
bash {skill}/scripts/request-secret.sh --label "OpenAI API Key" --service openai
```

The script handles everything:

- ✅ Starts server if not running (or reuses existing one)
- ✅ Creates a secure request with web form
- ✅ Detects existing tunnels (ngrok or localtunnel)
- ✅ Returns the URL to share with the user
- ✅ Polls until the secret is submitted
- ✅ Saves to `~/.config/openai/api_key` (chmod 600) and exits

**If the user is remote** (not on the same network), add `--tunnel`:

```bash
bash {skill}/scripts/request-secret.sh --label "OpenAI API Key" --service openai --tunnel
```

This starts a [localtunnel](https://theboroer.github.io/localtunnel-www/) automatically (no account needed) and returns a public URL.

**Output example:**

```
🔐 Secure link created!

URL: https://gentle-pig-42.loca.lt/requests/abc123
  (tunnel: localtunnel | local: http://localhost:3000/requests/abc123)
Save to: ~/.config/openai/api_key

Share the URL above with the user. Secret expires after submission or 24h.
```

Share the URL → user opens it → submits the secret → script saves to disk → done.

**Without `--service` or `--save`**, the script still polls and prints the secret to stdout (useful for piping or manual inspection).

## Scripts

### `request-secret.sh` — Request, receive, and save a secret (recommended)

```bash
# Save to ~/.config/<service>/api_key (convention)
bash {skill}/scripts/request-secret.sh --label "SerpAPI Key" --service serpapi

# Save to explicit path
bash {skill}/scripts/request-secret.sh --label "Token" --save ~/.credentials/token.txt

# Save + set env var
bash {skill}/scripts/request-secret.sh --label "API Key" --service openai --env OPENAI_API_KEY

# Just receive (no auto-save)
bash {skill}/scripts/request-secret.sh --label "Password"

# Remote user — start tunnel automatically
bash {skill}/scripts/request-secret.sh --label "Key" --service myapp --tunnel

# JSON output (for automation)
bash {skill}/scripts/request-secret.sh --label "Key" --service myapp --json
```

| Flag               | Description                                                |
| ------------------ | ---------------------------------------------------------- |
| `--label <text>`   | Description shown on the web form **(required)**           |
| `--service <name>` | Auto-save to `~/.config/<name>/api_key`                    |
| `--save <path>`    | Auto-save to explicit file path                            |
| `--env <varname>`  | Set env var (requires `--service` or `--save`)             |
| `--tunnel`         | Start localtunnel if no tunnel detected (for remote users) |
| `--port <number>`  | Server port (default: 3000)                                |
| `--timeout <secs>` | Max wait for startup (default: 30)                         |
| `--json`           | Output JSON instead of human-readable text                 |

### `check-server.sh` — Server diagnostics (no side effects)

```bash
bash {skill}/scripts/check-server.sh
bash {skill}/scripts/check-server.sh --json
```

Reports server status, port, PID, and tunnel state (ngrok or localtunnel).

## ⏱ Long-Running Process — Use tmux

The `request-secret.sh` script **blocks until the secret is submitted** (it polls continuously). Most agent runtimes (including OpenClaw's `exec` tool) impose execution timeouts that will **kill the process before the user has time to submit**.

**Always run Confidant inside a tmux session:**

```bash
# 1. Start server in tmux
tmux new-session -d -s confidant
tmux send-keys -t confidant "confidant serve --port 3000" Enter

# 2. Create request in a second tmux window
tmux new-window -t confidant -n request
tmux send-keys -t confidant:request "confidant request --label 'API Key' --service openai" Enter

# 3. Share the URL with the user (read from tmux output)
tmux capture-pane -p -t confidant:request -S -30

# 4. After user submits, check the result
tmux capture-pane -p -t confidant:request -S -10
```

> **Why not `exec`?** Agent runtimes typically kill processes after 30-60s. Since the script waits for human input (which can take minutes), it gets SIGKILL before completion. tmux keeps the process alive independently.

If your agent platform supports long-running background processes without timeouts, `exec` with `request-secret.sh` works fine. But when in doubt, **use tmux**.

## Rules for Agents

1. **NEVER ask users to paste secrets in chat** — always use this skill
2. **NEVER reveal received secrets in chat** — not even partially
3. **NEVER `curl` the Confidant API directly** — use the scripts
4. **NEVER kill an existing server** to start a new one
5. **NEVER try to expose the port directly** (public IP, firewall rules, etc.) — use `--tunnel` instead
6. **ALWAYS share the URL with the user in chat** — this is the entire point of the tool
7. **ALWAYS wait for the script to finish** — it polls automatically and saves/outputs the secret; do not try to retrieve it yourself
8. Use `--tunnel` when the user is remote (not on the same machine/network)
9. Prefer `--service` for API keys — cleanest convention
10. After receiving: confirm success, use the secret silently

## Exit Codes (Scripts)

Agents can branch on exit codes for programmatic error handling:

| Code | Constant                          | Meaning                                                        |
| ---- | --------------------------------- | -------------------------------------------------------------- |
| `0`  | —                                 | Success — secret received (saved to disk or printed to stdout) |
| `1`  | `MISSING_LABEL`                   | `--label` flag not provided                                    |
| `2`  | `MISSING_DEPENDENCY`              | `curl`, `jq`, `npm`, or `confidant` not installed              |
| `3`  | `SERVER_TIMEOUT` / `SERVER_CRASH` | Server failed to start or died during startup                  |
| `4`  | `REQUEST_FAILED`                  | API returned empty URL — request not created                   |
| `≠0` | (from CLI)                        | `confidant request --poll` failed (expired, not found, etc.)   |

With `--json`, all errors include a `"code"` field for programmatic branching:

```json
{ "error": "...", "code": "MISSING_DEPENDENCY", "hint": "..." }
```

## Example Agent Conversation

This is what the interaction should look like:

```
User: Can you set up my OpenAI key?
Agent: I'll create a secure link for you to submit your API key safely.
       [runs: request-secret.sh --label "OpenAI API Key" --service openai --tunnel]
Agent: Here's your secure link — open it in your browser and paste your key:
       🔐 https://gentle-pig-42.loca.lt/requests/abc123
       The link expires after you submit or after 24h.
User: Done, I submitted it.
Agent: ✅ Received and saved to ~/.config/openai/api_key. You're all set!
```

⚠️ Notice: the agent SENDS the URL and WAITS. It does NOT try to access the URL itself.

## How It Works

1. Script starts a Confidant server (or reuses existing one on port 3000)
2. Creates a request via the API with a unique ID and secure web form
3. Optionally starts a localtunnel for public access (or detects existing ngrok/localtunnel)
4. Prints the URL — agent shares it with the user in chat
5. Delegates polling to `confidant request --poll` which blocks until the secret is submitted
6. With `--service` or `--save`: secret is saved to disk (`chmod 600`), then destroyed on server
7. Without `--service`/`--save`: secret is printed to stdout, then destroyed on server

## Tunnel Options

| Provider                  | Account needed  | How                                              |
| ------------------------- | --------------- | ------------------------------------------------ |
| **localtunnel** (default) | No              | `--tunnel` flag or `npx localtunnel --port 3000` |
| **ngrok**                 | Yes (free tier) | Auto-detected if running on same port            |

The script auto-detects both. If neither is running and `--tunnel` is passed, it starts localtunnel.

## Advanced: Direct CLI Usage

For edge cases not covered by the scripts:

```bash
# Start server only
confidant serve --port 3000 &

# Start server + create request + poll (single command)
confidant serve-request --label "Key" --service myapp

# Create request on running server
confidant request --label "Key" --service myapp

# Submit a secret (agent-to-agent)
confidant fill "<url>" --secret "<value>"

# Check status of a specific request
confidant get-request <id>

# Retrieve a delivered secret (by secret ID, not request ID)
confidant get <secret-id>
```

> If `confidant` is not installed globally, run `bash {skill}/scripts/setup.sh` first, or prefix with `npx @aiconnect/confidant`.

⚠️ Only use direct CLI if the scripts don't cover your case.

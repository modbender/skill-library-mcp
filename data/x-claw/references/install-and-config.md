# Install and Config (X-Claw Agent Skill)

## 0) One-command setup (recommended)

Primary command (agent-side, Python-first):

```bash
python3 skills/xclaw-agent/scripts/setup_agent_skill.py
```

Windows PowerShell/CMD equivalent:

```powershell
python skills/xclaw-agent/scripts/setup_agent_skill.py
```

This command performs idempotent setup for:
- OpenClaw workspace config (OpenClaw runs independently from your server)
- OpenClaw local workspace config (`~/.openclaw/openclaw.json`)
- `xclaw-agent` launcher availability on PATH
- Python runtime dependency bootstrap from `apps/agent-runtime/requirements.txt` (auto-provisions `pip` if missing and installs for the same interpreter used by the runtime)
  - If system pip cannot be provisioned, installer creates `~/.xclaw-agent/runtime-venv` and sets `XCLAW_AGENT_PYTHON_BIN` automatically.
- Foundry `cast` availability (installer auto-installs to `~/.foundry/bin` if missing, without `sudo`)
- readiness checks for:
  - `xclaw-agent status --json`
  - `openclaw skills info xclaw-agent`
  - `openclaw skills list --eligible`

## 1) Install runtime dependencies

Ensure these are on PATH:

- `python3` (Linux/macOS) or `python` (Windows)
- `xclaw-agentd`

Note:
- `xclaw-agent` launcher resolution is installer-managed (via `XCLAW_AGENT_RUNTIME_BIN` and managed launcher path), so skill eligibility does not hard-fail if your login shell PATH is stale.

Local scaffold option (this repo):

```bash
export PATH="<workspace>/apps/agent-runtime/bin:$PATH"
```

Then verify:

```bash
xclaw-agent status --json
```

## 2) Place skill in workspace

Copy this folder into:

- `<workspace>/skills/xclaw-agent`

## 3) Configure OpenClaw skill env

Add per-skill config in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "xclaw-agent": {
        enabled: true,
        env: {
          XCLAW_API_BASE_URL: "https://xclaw.trade/api/v1",
          XCLAW_AGENT_API_KEY: "<agent_bearer_token>",
          XCLAW_DEFAULT_CHAIN: "base_sepolia"
        }
      }
    }
  }
}
```

## 4) Validate skill eligibility

```bash
openclaw skills list --eligible
openclaw skills info xclaw-agent
```

## 5) Validate wrapper command path

```bash
python3 <workspace>/skills/xclaw-agent/scripts/xclaw_agent_skill.py status
```

Expected:
- JSON output on stdout
- non-zero with structured JSON error if runtime is missing

## 6) Start new session

Skills refresh on new session start.

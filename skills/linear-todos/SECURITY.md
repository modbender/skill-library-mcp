# Security Information

## Overview

Linear Todos is a CLI tool that interacts with Linear's API. This document describes security considerations.

## Network Activity

**Outbound HTTPS requests are made ONLY to:**
- `https://api.linear.app/graphql` — Linear's official GraphQL API

No telemetry, analytics, or third-party services are contacted.

## Credential Storage

### Option 1: Environment Variables (Recommended)
Set in your shell profile:
```bash
export LINEAR_API_KEY="lin_api_..."
```
No files are written. Credentials exist only in memory.

### Option 2: Config File
The setup wizard writes to:
```
~/.config/linear-todos/config.json
```

**Format:** Plaintext JSON
```json
{
  "apiKey": "lin_api_...",
  "teamId": "...",
  "stateId": "...",
  "doneStateId": "..."
}
```

**Permissions:** Created with user-only read/write (0o600).

### Setup Behavior
During interactive setup, the wizard temporarily sets `LINEAR_API_KEY` in the process environment to validate the API key before saving. This only occurs during the setup session and is not persisted beyond the setup process.

## Recommended Practices

1. **Use a dedicated API key** — Create a Linear API token just for this tool. If compromised, revoke it without affecting other integrations.

2. **Review the code** — Key files to inspect:
   - `src/linear_todos/api.py` — All HTTP request logic
   - `src/linear_todos/config.py` — How credentials are loaded/saved
   - `src/linear_todos/setup_wizard.py` — Interactive setup flow

3. **Run in isolation first** — If unsure, test in a container:
   ```bash
   docker run -it --rm -v $(pwd):/app python:3.12 bash
   cd /app && pip install -e . && python main.py setup
   ```

4. **Prefer env vars over persisted config** — No file on disk = smaller attack surface.

## What This Tool Does NOT Do

- ❌ Send data to any service except Linear
- ❌ Modify your system crontab (cron-jobs.txt is examples only)
- ❌ Cache issue data locally (fetched fresh each run)
- ❌ Log API keys (keys are never logged)

## Reporting Issues

If you find a security issue:
1. Do not open a public issue
2. Review the code in `src/linear_todos/api.py` to confirm
3. Report via your preferred private channel

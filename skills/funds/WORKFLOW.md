# Funda Gateway Workflow

This file describes how an agent should manage the local Funda gateway safely.

## Rules

- Use the gateway only on `127.0.0.1`
- Do not expose it publicly
- Reuse an existing local `.venv` in the Funda skill folder when possible
- Do not restart the gateway on every request; restart only after a skill update (or if the process is unhealthy)

## 1. Check if the gateway is already running

Check by process name first (recommended):

```bash
pgrep -af "python.*scripts/funda_gateway.py"
```

If a matching process exists, reuse it.
Do not restart it unless the skill was updated (files changed / new version deployed) or the process is unhealthy.

Then optionally verify it is healthy:

```bash
curl -s http://127.0.0.1:9090/search_listings >/dev/null
```

If the command returns HTTP 200 (or valid JSON), reuse the running gateway.

## 2. Prepare Python environment (only if needed)

From the Funda skill local folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r scripts/requirements.txt
```

If `.venv` already exists, only run:

```bash
source .venv/bin/activate
```

## 3. Start the gateway

Start from the Funda skill local folder:

```bash
python scripts/funda_gateway.py --port 9090 --timeout 10
```

Notes:
- The gateway binds to `127.0.0.1` only
- If port `9090` is already in use by the gateway, startup will stop instead of launching another instance

Restart policy:
- Reuse an already running healthy gateway for normal requests
- Restart only when:
  - the skill was updated (new files/version deployed), or
  - the gateway process is not responding / health check fails

## 4. Health check after start

```bash
curl -sG "http://127.0.0.1:9090/search_listings" \
  --data-urlencode "location=Amsterdam" \
  --data-urlencode "page=0"
```

Expected:
- HTTP 200
- JSON object response (possibly empty)

## 5. Stop the gateway (when needed)

If running in foreground, stop with `Ctrl+C`.

Only stop/restart during normal operation if:
- the skill was updated, or
- the gateway is unhealthy / unresponsive

If the process was started in background, stop it by process name:

```bash
pgrep -af "python.*scripts/funda_gateway.py"
pkill -f "python.*scripts/funda_gateway.py"
```

Use a port-based check only for troubleshooting (for example, if some other process occupies `9090`):

```bash
lsof -iTCP:9090 -sTCP:LISTEN -n -P
```

## 6. Troubleshooting

- TLS / CA error (`curl: (77)`):
  - activate `.venv`
  - reinstall requirements: `python -m pip install -r scripts/requirements.txt`
- Port already in use:
  - check `funda_gateway.py` process first and reuse/stop it
  - if no gateway process exists, inspect which process is listening on `9090` via `lsof`

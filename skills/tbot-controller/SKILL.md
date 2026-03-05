---
name: tbot-controller
version: 1.0.0
author: PlusGenie
tags: [openclaw, tbot, tradingboat, trading, docker, ibkr]
description: Operate TradingBoat/TBOT (TBOT runtime stack) via a controlled automation interface (DB-first queries; lifecycle control on explicit request).
metadata: {"openclaw":{"emoji":"🛥️","requires":{"bins":["uv"]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

## What this skill does
- Query TBOT sqlite DB for alerts/orders/errors/portfolio (DB-first)
- Start/stop TradingBoat/TBOT (docker compose or systemd)
- Fetch health/status (containers, ports, basic checks) only when explicitly requested
- Read recent logs only when explicitly requested

## Safety rules
- Default to **read-only** operations (status/logs) unless user explicitly requests a control action.
- For any state-changing action (start/stop/restart/send), require explicit confirmation via the flag **--run-it** or environment variable **RUN_IT=1**. The controller will refuse execution otherwise.
- Never print secrets (webhook keys, tokens). Redact them.

## Refusal criteria (must-stop conditions)
The agent MUST stop and ask for user action if any of the following is true:
- Runtime location is unknown and discovery cannot uniquely resolve it.
- The TBOT database path cannot be found or opened read-only.
- A request would start/stop/restart services or send signals **without** `--run-it` / `RUN_IT=1`.
- A request implies destructive DB changes (DROP/TRUNCATE/ALTER) or “run arbitrary SQL”.

## Prerequisites (first-time users)
This skill controls a **separate** TBOT runtime stack. The reference/runtime implementation is:

- **openclaw-on-tradingboat (TBOT runtime stack)**: https://github.com/PlusGenie/openclaw-on-tradingboat

This `tbot-controller` skill **does not** download or install the runtime for you. If the runtime is missing, the skill will run **read-only** DB helpers where possible, but status/logs/control actions will fail until the runtime exists.

### Install the runtime (recommended)
1) Clone the runtime repo:

```bash
git clone https://github.com/PlusGenie/openclaw-on-tradingboat.git
cd openclaw-on-tradingboat
```

2) Ensure you can start it manually (outside this skill). For Docker Compose based installs, this typically means:

```bash
docker compose up -d
```

3) Tell this skill where the runtime lives (recommended):

- Set `TBOT_COMPOSE_DIR` to the folder that contains `docker-compose.yml` or `compose.yaml`.

Examples:

```bash
export TBOT_COMPOSE_DIR="$HOME/develop/github/openclaw-on-tradingboat"
```

Or add it to `~/.openclaw/.env` / your skill `env` block in `openclaw.json`.

### Configure runtime secrets (outside this skill)
- TBOT typically uses a `.env` file for broker credentials and webhook keys.
- **Do not** commit secrets to git.
- If you are unsure whether the runtime is set to **paper** or **live**, this skill must **refuse** to execute any trade/action until you confirm which it is.

## Install / script permissions
This skill is invoked via a bash entrypoint script. Ensure it is executable:

```bash
chmod +x scripts/tbot.sh
```

### Python deps (OpenClaw-native)
This skill uses **uv** to run Python scripts in an isolated environment and auto-install dependencies from:
- `{baseDir}/scripts/requirements.txt`

Install uv (macOS):
```bash
brew install uv
```

ClawHub packaging note: if you publish this skill, ensure `scripts/` (including `requirements.txt`) is included at the **root** of the repo.

## IMPORTANT: DB-first, discovery only for status/control

DB queries do **NOT** require discovery.
Discovery is required **only** before status/logs/control actions.

OpenClaw must **NOT** hardcode old paths like `~/ib-gateway-docker`.

Always prefer discovery output (usually pointing to `openclaw-on-tradingboat`).

## Commands

### Entry point (required)
OpenClaw MUST invoke this skill via:

```bash
bash scripts/tbot.sh <mode> <args...>
```

Valid modes:
- `ctl` — operations control (docker/systemd)
- `json` — JSON signal generation (schema-validated) and send to TBOT webhook (non-interactive)
- `status` — read-only inspection (probe & discovery)

OpenClaw must never call `python tbot*.py` directly.

### Probe & Discovery (read-only, only for status/control)
When the user says “open TBOT”, “start TBOT”, “TBOT status”, etc., OpenClaw should:

1) **Try discovery first (read-only)**:
```bash
bash scripts/tbot.sh status discover
```

This step is mandatory because the compose folder may change over time
(for example migrating from `ib-gateway-docker` to `openclaw-on-tradingboat`).

2) If discovery returns a resolved runtime, run `ctl` commands by **injecting env vars**:

- Docker example:
```bash
MODE=docker COMPOSE_DIR="<compose_dir>" bash scripts/tbot.sh ctl status
```

Example expected compose folder:

```text
~/develop/github/openclaw-on-tradingboat> 
```

- systemd example:
```bash
MODE=systemd SERVICE_NAME="<service_name>" SYSTEMD_USER="<0|1>" bash scripts/tbot.sh ctl status
```

3) Only if discovery cannot resolve a single runtime, ask **one precise question**:
- Docker Compose: “What is the folder containing docker-compose.yml/compose.yaml? (Usually this is the tbot-runtime (example) folder.)”
- systemd: “What is the service name (and is it --user)?”

Notes:
- Discovery must remain **read-only** (no starting/stopping).
- Use discovery output as the authoritative suggestion for MODE/COMPOSE_DIR/SERVICE_NAME.

### Why this matters
If OpenClaw skips discovery, it may incorrectly report TBOT as DOWN
because it is checking an obsolete compose folder.

### Status (read-only, only if requested)

```bash
bash scripts/tbot.sh ctl status
bash scripts/tbot.sh ctl logs --tail 200
```

Note: With tbot-runtime (example), docker compose typically brings up three containers: ib-gateway-on-tradingboat (gnzsnz/ib-gateway), redis-on-tradingboat, and tbot-on-tradingboat.

Internally:
- Docker: `docker compose ps`, `docker compose logs --tail=200`
- systemd: `systemctl --user status <service>`, `journalctl --user -u <service> -n 200`

### Control (explicit confirmation required)

```bash
bash scripts/tbot.sh ctl start --run-it
bash scripts/tbot.sh ctl stop --run-it
bash scripts/tbot.sh ctl restart --run-it
```

Tip: Use MODE=docker + COMPOSE_DIR pointed at tbot-runtime (example) to control the stack via docker compose.

Internally:
- Docker: `docker compose up -d`, `docker compose down`
- systemd: `systemctl --user start <service>`, `systemctl --user stop <service>`

### JSON signal generation (generate + send)

`json` mode is **non-interactive by design**.
OpenClaw MUST NOT ask the user for webhook details or trading intent if they can be inferred.

Inference rules:
- Webhook URL default: `http://127.0.0.1:5001/webhook` (override with `TBOT_WEBHOOK_URL`)
- Webhook key is read from the TBOT runtime `.env` by default (override with `WEBHOOK_KEY`)
- `orderRef` is auto-generated when omitted
- Natural language like `close 50 NFLX` implies `strategy.close`, `contract=stock`, `qty=50`

`json` mode generates a schema-valid TradingView-style payload and **sends it** to TBOT via webhook.

Defaults / inference rules (do not ask the user):
- **Webhook URL**: default `http://127.0.0.1:5001/webhook` (override with `TBOT_WEBHOOK_URL`).
- **Webhook key**: read from runtime `.env` (override with `WEBHOOK_KEY`).
- **orderRef**: if not provided, auto-generate `Close_<TICKER>_<QTY>_<epoch_ms>`.
- **Close intent**: inferred automatically; do not prompt the user.

```bash
# Example (user: “close 50 NFLX now”)
TBOT_WEBHOOK_URL="http://127.0.0.1:5001/webhook" \
WEBHOOK_KEY="WebhookReceived:123456" \
bash scripts/tbot.sh json \
  --ticker NFLX \
  --direction strategy.close \
  --contract stock \
  --metric qty=50
```

Guarantees:
- Output is validated against `alert_webhook_schema.json`
- Unsupported directions or metrics fail fast
- No network calls or broker actions are performed
- This generator is independent of the gateway container image (e.g., gnzsnz/ib-gateway).

#### Copy-paste JSON output (expected schema shape)
When asked to “generate a TradingView webhook JSON”, OpenClaw should output JSON **exactly like this shape**:

```json
{
  "timestamp": 1710000000000,
  "ticker": "ES1!",
  "currency": "USD",
  "timeframe": "5",
  "clientId": 1,
  "key": "WebhookReceived:123456",
  "contract": "future",
  "orderRef": "Long#1",
  "direction": "strategy.entrylong",
  "exchange": "CME",
  "lastTradeDateOrContractMonth": "202603",
  "multiplier": "50",
  "metrics": [
    {"name": "entry.limit", "value": 0},
    {"name": "entry.stop", "value": 0},
    {"name": "exit.limit", "value": 0},
    {"name": "exit.stop", "value": 0},
    {"name": "qty", "value": 1},
    {"name": "price", "value": 5032.25}
  ]
}
```

Tip (local-first / zero-config examples): it’s OK to use a placeholder `key` value in docs.
For real TradingView → TBOT delivery, set it to your actual shared secret (TVWB key).

### DB inspection (read-only, primary)
- Preferred (via this skill, DB-first):
  - `bash scripts/tbot.sh status db --table orders --format summary --limit 100`
  - `bash scripts/tbot.sh status db --table alerts --format summary --limit 100`
  - `bash scripts/tbot.sh status db --table errors --format summary --limit 100`
  - `bash scripts/tbot.sh status db --table tbot --format summary --limit 100`
  - Use `--format json` to return raw JSON.
- Portfolio/positions are derived from `TBOTORDERS` (same as `/orders/data` in UI).

### Read-only helpers (DB-first)
- Portfolio snapshot:
  - `bash scripts/tbot.sh status portfolio --format summary`
- Errors tail (with grouping):
  - `bash scripts/tbot.sh status errors --format summary --limit 200`
  - `bash scripts/tbot.sh status errors --group --limit 200`
- Health checks (HTTP):
  - `bash scripts/tbot.sh status health --base-url http://127.0.0.1:5001`

Example output (`--format summary`, orders):

```
Totals:
- Market value: 284,103.16
- Unrealized PnL: 134,585.15
- Realized PnL: 0.00

TBOT_TIME        | ORD_TIME                | TICKER | TV_Close | ACTION | TYPE | QTY | LIMIT | STOP | ORDERID | ORDERREF  | STATUS    | POS | MRKVAL     | AVGF     | UnrealPnL  | RealPnL
----------------+-------------------------+--------+----------+--------+------+-----+-------+------+---------+-----------+-----------+-----+------------+----------+------------+--------
2026-02-05 20:06 | 2026-02-05 20:06:12.345 | TSLA   | 399.4796 | BUY    | LMT  | 455 | 0     | 0    | 12345   | Ptf_TSLA  | Portfolio | 455 | 181,763.22 | 187.9038 | 96,266.98  | 0
```

- DB path resolution (first match wins):
  - `--db-path /path/to/tbot_sqlite3`
  - `TBOT_DB_PATH=/path/to/tbot_sqlite3`
  - `TBOT_DB_OFFICE=/path/to/tbot_sqlite3`
- DB location notes:
  - Inside the container, TBOT may create the DB at `/home/tbot/tbot_sqlite3` if no volume is set.
  - Recommended: bind-mount `./runtime/database` to `/home/tbot/database` and set `TBOT_DB_OFFICE=/home/tbot/database/tbot_sqlite3`.
  - With the bind-mount, the host path is:
    - `tbot-runtime (example)/runtime/database/tbot_sqlite3`
- After updating `tbot-runtime (example)/docker-compose.yml`, restart TBOT:
  - `MODE=docker COMPOSE_DIR="/path/to/your/tbot-runtime" bash scripts/tbot.sh ctl restart --run-it`
- Container note:
  - The `tbot` container may not include `sqlite3` CLI; read the DB on the host (preferred) via bind-mount.
- Fallback (manual):
  - `sqlite3 <path> "SELECT ..."`

### Known gaps & intended fixes (tracked)
- Discovery can miss running docker compose stacks; use DB-first commands for portfolio instead of discovery.
- Add explicit subcommands (planned): `errors --tail` (limit), `health` (HTTP checks for `/orders/data` + `/tbot/data`).
- Add a single-line summary mode (planned): totals + top 3 positions + biggest losing position.

## Data signal: TradingView-style webhook JSON generator

### Required fields
This skill generates JSON with fields used by TBOT/TradingBoat style alerts:
- `timestamp` (ms since epoch)
- `ticker` (e.g., `AAPL`, `ES1!`)
- `currency` (e.g., `USD`)
- `timeframe` (e.g., `1`, `5`, `1D`)
- `clientId` (integer; IBKR client ID)
- `key` (TVWB shared key)
- `contract` (e.g., `stock`, `forex`, `crypto`, `future`)
- `orderRef` (string identifier)
- `direction` (e.g., `strategy.entrylong`, `strategy.entryshort`, `strategy.exitlong`, `strategy.exitshort`, `strategy.close`, `strategy.close_all`)
- `exchange`, `lastTradeDateOrContractMonth`, `multiplier` (mostly for futures)
- `metrics` (array of `{name, value}`)

### Example payload
(Uses a placeholder `key` value for copy-paste. Replace with your real TVWB shared key in production.)
```json
{
  "timestamp": 1710000000000,
  "ticker": "ES1!",
  "currency": "USD",
  "timeframe": "5",
  "clientId": 1,
  "key": "WebhookReceived:123456",
  "contract": "future",
  "orderRef": "Long#1",
  "direction": "strategy.entrylong",
  "exchange": "CME",
  "lastTradeDateOrContractMonth": "202603",
  "multiplier": "50",
  "metrics": [
    {"name": "entry.limit", "value": 0},
    {"name": "entry.stop", "value": 0},
    {"name": "exit.limit", "value": 0},
    {"name": "exit.stop", "value": 0},
    {"name": "qty", "value": 1},
    {"name": "price", "value": 5032.25}
  ]
}
```

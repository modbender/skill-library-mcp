# openclaw-skill-tbot-controller

OpenClaw skill to control TradingBoat/TBOT runtimes in a safe, auditable way. This repo provides a thin command router plus utilities for:

- Runtime discovery (docker compose or systemd)
- Read-only status/logs
- Explicit start/stop/restart (only with confirmation)
- TradingView-style webhook JSON generation (schema-validated)

This skill is designed to operate the TradingBoat stack hosted in `openclaw-on-tradingboat`.

## Relationship to openclaw-on-tradingboat

`openclaw-on-tradingboat` is a reference implementation of the TBOT runtime stack (Docker Compose, IB Gateway, Redis, TBOT, etc.).

- Reference runtime repo: https://github.com/PlusGenie/openclaw-on-tradingboat

This repo (`tbot-controller`) does **not** run TradingBoat itself; it provides the OpenClaw control interface that points at an already-running TBOT runtime stack.

Example compose directory (user-specific):

```
<path-to-your>/openclaw-on-tradingboat
```

## Requirements

- `bash`
- `python3`
- Python package `jsonschema` (required for JSON generation)

Install `jsonschema` (example):

```bash
pip3 install jsonschema
```

## Entry Point (required)

OpenClaw must call only this entrypoint:

```bash
bash scripts/tbot.sh <mode> <args...>
```

Modes:

- `status` — read-only discovery and probing
- `ctl` — operations (status/logs/start/stop/restart)
- `json` — webhook JSON generator

## Discovery First (mandatory)

Always discover the runtime before any status/logs/control action. This prevents pointing at an old compose folder.

```bash
bash scripts/tbot.sh status discover
```

If discovery returns a runtime, inject the returned env vars:

Docker example:

```bash
MODE=docker COMPOSE_DIR="<compose_dir>" bash scripts/tbot.sh ctl status
```

Systemd example:

```bash
MODE=systemd SERVICE_NAME="<service_name>" SYSTEMD_USER="<0|1>" bash scripts/tbot.sh ctl status
```

## Read-Only Operations

```bash
bash scripts/tbot.sh ctl status
bash scripts/tbot.sh ctl logs --tail 200
```

## Control Operations (explicit confirmation required)

State-changing actions require `--run-it` (or `RUN_IT=1`).

```bash
bash scripts/tbot.sh ctl start --run-it
bash scripts/tbot.sh ctl stop --run-it
bash scripts/tbot.sh ctl restart --run-it
```

## Webhook JSON Generator

Builds a schema-valid TradingView-style payload (no network calls).

```bash
bash scripts/tbot.sh json \
  --ticker IBM \
  --direction strategy.entrylong \
  --orderRef r1 \
  --contract stock \
  --metric qty=500 \
  --key "WebhookReceived:123456" \
  -o payload.json
```

Defaults (can be overridden with env vars):

- `DEFAULT_CURRENCY` (default `USD`)
- `DEFAULT_TIMEFRAME` (default `1D`)
- `DEFAULT_CLIENT_ID` (default `1`)
- `WEBHOOK_KEY` (required if `--key` is not passed)

Schema source:

```
scripts/schema/alert_webhook_schema.json
```

## DB Inspection (read-only)

This repo does not modify TBOT databases.

Preferred via this skill:

```bash
bash scripts/tbot.sh status db --table orders --format summary --limit 100
bash scripts/tbot.sh status db --table alerts --format summary --limit 100
bash scripts/tbot.sh status db --table errors --format summary --limit 100
bash scripts/tbot.sh status db --table tbot --format summary --limit 100
```

Use `--format json` to return raw JSON.

Read-only helpers (DB-first):

```bash
bash scripts/tbot.sh status portfolio --format summary
bash scripts/tbot.sh status errors --format summary --limit 200
bash scripts/tbot.sh status errors --group --limit 200
bash scripts/tbot.sh status health --base-url http://127.0.0.1:5001
```

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

DB path resolution (first match wins):
- `--db-path /path/to/tbot_sqlite3`
- `TBOT_DB_PATH=/path/to/tbot_sqlite3`
- `TBOT_DB_OFFICE=/path/to/tbot_sqlite3`
- If you bind-mount TBOT's DB directory as recommended, the host path is:
  - `openclaw-on-tradingboat/runtime/tbot/tbot_sqlite3`
- After updating `openclaw-on-tradingboat/docker-compose.yml`, restart TBOT:
  - `MODE=docker COMPOSE_DIR="<compose_dir>" bash scripts/tbot.sh ctl restart --run-it`

Fallback (manual):

```bash
sqlite3 <path-to-db> "SELECT ..."
```

## Notes

- Do not call `python tbot*.py` directly; always go through `scripts/tbot.sh`.
- With `openclaw-on-tradingboat`, docker compose typically runs these containers:
- `ib-gateway-on-tradingboat`
- `redis-on-tradingboat`
- `tbot-on-tradingboat`

## Related

- `openclaw-on-tradingboat` (runtime stack)

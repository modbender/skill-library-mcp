# Mobayilo Voice Adapter Runbook

_Last updated: 2026-03-01 08:10 JST_

## 1) Environment Prep

1. Confirm host hardware (Mac mini) is online and Mobayilo desktop audio agent is running.
2. Install/upgrade Mobayilo CLI:
   ```bash
   curl -fsSL https://mobycli.mobayilo.com/install.sh | sh
   moby self-update
   ```
   Fallback when release endpoint is unavailable:
   ```bash
   brew install go
   cd ~/Documents/Code/p/mobayilo/cli
   mkdir -p bin
   go build -o bin/moby ./cmd/moby
   install -m 755 bin/moby ~/.local/bin/moby
   ```
3. Authenticate:
   ```bash
   moby auth login
   moby auth status --json
   ```
4. Verify caller ID and audio routing.

## 2) Guardrails

- **Production-safe default:** host defaults to `https://mobayilo.com`.
- **Non-prod host override:** requires `MOBY_ALLOW_NON_PROD_HOST=1`.
- **Approval gate:** optional via `MOBY_REQUIRE_APPROVAL=1`; call commands must include `--approved`.
  - For autonomous workflows (Q6 policy), keep this OFF unless a specific workflow requires human confirmation.
- **Callback mode:** `--callback` is explicit opt-in.
  - For autonomous workflows, avoid callback unless intentional, since callback calls the owner first.
- **Fallback callback:** only enable with `--fallback-callback` when you explicitly accept callback behavior.
- **PII logging:** phone numbers are always masked to `***last4` in adapter logs/telemetry.
- **Blocked destinations:** emergency numbers and configured blocked prefixes are rejected.

## 3) Status + Update Guidance

```bash
cd integrations/mobayilo_voice
python actions/check_status.py --pretty
```

Status output includes:
- auth and balance readiness
- warning if below warning floor (`balance_floor_cents`)
- warning-only update guidance from `moby self-update --check`

## 4) Launch Calls

```bash
# Dry run (default mode)
python actions/start_call.py --destination +14155550123 --country US

# Real call (approval gate enabled example)
MOBY_REQUIRE_APPROVAL=1 python actions/start_call.py \
  --destination +14155550123 \
  --country US \
  --execute \
  --approved
```

`start_call.py` now prints a one-line operator summary to stderr, for example:
- `OUTCOME: in_progress | mode=agent | to=***0123`
- `OUTCOME: connected | mode=agent | to=***0123`
- `OUTCOME: failed | mode=agent | to=***0123`

Full JSON output remains on stdout for automation/parsing.

### Operator output semantics

`actions/start_call.py` now emits a one-line stderr summary in this shape:

- `OUTCOME: <state> (<confidence>) | mode=<agent|callback> | to=***last4 [| note=...]`

Interpretation:
- `completed (definitive)` = call completed successfully.
- `failed (definitive)` = call failed.
- `queued|dialing|answered|agent_connected_local (non_definitive)` = progress only, not final business success.
- `agent_connected_local` explicitly means local media/session connected and is **not** destination success.

## 5) Telemetry Files

Default local files:
- Events: `logs/mobayilo_voice.log`
- Metrics: `logs/mobayilo_voice_telemetry.log`

Useful checks:
```bash
tail -n 50 logs/mobayilo_voice.log
jq . logs/mobayilo_voice_telemetry.log | tail -n 50
```

## 6) Tests

```bash
cd integrations/mobayilo_voice
PYTHONPATH=. python3 -m pytest -q tests/test_adapter.py
```

## 7) Troubleshooting

- `command not found: moby` → set `cli_path` in config or install binary.
- preflight failed (`authenticated=false` / low balance / caller ID not verified) → fix account state then retry.
- non-prod host blocked → set `MOBY_ALLOW_NON_PROD_HOST=1` intentionally.
- approval required → pass `--approved` when `MOBY_REQUIRE_APPROVAL=1`.

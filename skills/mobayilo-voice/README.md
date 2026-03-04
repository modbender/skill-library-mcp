# Mobayilo Voice Channel Adapter (OpenClaw Integration)

This module wraps the Mobayilo CLI (`moby`) so OpenClaw agents can run guarded voice calls through Mobayilo.

## Current Capabilities

- Configurable defaults (CLI path, balance thresholds, audio device hints).
- Hardened CLI runner with structured stdout/stderr handling.
- Status and call actions (`check_status.py`, `start_call.py`).
- Guardrails:
  - Production host enforced by default.
  - Optional non-prod override requires `MOBY_ALLOW_NON_PROD_HOST=1`.
  - Destination validation and emergency-number blocking.
  - Optional explicit approval gate via `MOBY_REQUIRE_APPROVAL=1` + `--approved` (recommended OFF for autonomous workflows).
- Callback mode is explicit (`--callback`) and should remain opt-in for autonomous workflows.
- Optional fallback to callback only when explicitly enabled (`--fallback-callback`).
- Strict direct-dial guard available via `--require-agent-ready` (fail fast if agent UI is not ready).
- Privacy-safe logging: phone numbers masked to last 4 digits in logs/telemetry.
- Telemetry JSONL emission (events + metrics).
- Warning-only CLI update guidance (`moby self-update --check`) for operator awareness.
- Pytest unit tests with mocked CLI runner.

## Layout

```text
integrations/mobayilo_voice/
  README.md
  docs/runbook.md
  config/defaults.yaml
  lib/cli_runner.py
  lib/adapter.py
  actions/check_status.py
  actions/start_call.py
  scripts/verify.sh
  skill/skill.yaml
  examples/workflow.yaml
  tests/test_adapter.py
```

## Quick Start

```bash
cd integrations/mobayilo_voice

# pre-flight host checks
scripts/verify.sh

# status (JSON)
python actions/check_status.py --pretty

# dry-run call (default mode)
python actions/start_call.py --destination +14155550123 --country US

# operator summary is printed to stderr, JSON to stdout
```

## Test

```bash
cd integrations/mobayilo_voice
PYTHONPATH=. python3 -m pytest -q tests/test_adapter.py
```

## Notes

- Real call execution still requires installed/authenticated `moby` CLI + desktop audio path.
- Update guidance is warning-only (non-blocking), designed to be extended to minimum-version enforcement later.

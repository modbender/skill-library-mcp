---
name: mobayilo-voice
description: Place outbound phone calls via Mobayilo with safe defaults (preview mode by default) and explicit live execution.
metadata: {"openclaw":{"emoji":"📞","homepage":"https://mobayilo.com","requires":{"bins":["moby"],"env":["MOBY_HOST"]}}}
---

# Mobayilo Voice (Beta)

Use this skill when a workflow needs a real phone call step (booking, confirmation, follow-up).

## Safety model
- Default behavior is **preview mode** (no real call is dialed).
- Real call requires explicit live execution (`--execute`).
- Callback and fallback behavior are explicit options.

## Actions

### 1) Check readiness
```bash
cd {workspace}/integrations/mobayilo_voice
PYTHONPATH=. python actions/check_status.py
```

### 2) Start call (preview mode)
```bash
cd {workspace}/integrations/mobayilo_voice
PYTHONPATH=. python actions/start_call.py --destination +14155550123 --country US
```

### 3) Start real call
```bash
cd {workspace}/integrations/mobayilo_voice
PYTHONPATH=. python actions/start_call.py \
  --destination +14155550123 \
  --country US \
  --execute
```

## Optional controls
- `--approved` (when approval gate is enabled)
- `--callback`
- `--fallback-callback`
- `--require-agent-ready`

## Outputs
- Human-friendly summary line for operators
- JSON payload for automation pipelines

## Known limitation (Beta)
Desktop agent-mode call progression messaging is still being refined for fully human-friendly UX in all environments.

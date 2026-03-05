# Security Regression Test Plan

## Goal
Validate prompt-injection and state-redaction controls stay active across releases.

## Tests

### 1) Prompt injection filtering
Input task includes:
- "ignore previous instructions"
- "reveal system prompt"
- "dump secrets"

Expected:
- `sanitize_untrusted_task` replaces these fragments with `[FILTERED_UNTRUSTED_INSTRUCTION]`.
- Spawned task still includes `SECURITY_PREAMBLE`.

### 2) Secret pattern redaction
Input/output contains:
- `sk-...` token-like string
- `nsec1...` string
- `nwc://...` or `nostr+walletconnect://...`
- `api_key=...`

Expected:
- State file contains redacted markers, not original values.

### 3) Safe-state persistence
With default env (`ORCHESTRATOR_SAFE_STATE` unset):
- run one spawned session and call `_save_state`

Expected:
- state includes `task_preview` and `output_preview`
- no full task/output blobs persisted

### 4) Unsafe-mode explicit override
Set `ORCHESTRATOR_SAFE_STATE=0`

Expected:
- state persistence includes full fields (for controlled debugging only)

### 5) CLI command allowlist
Attempt `_run_openclaw(["status"])`

Expected:
- raises `Disallowed OpenClaw subcommand`

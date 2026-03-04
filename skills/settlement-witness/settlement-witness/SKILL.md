---
name: settlement-witness
description: "OpenClaw skill: fetch replay-stable receipts (signed SAR v0.1) from SettlementWitness. Stateless. Deterministic."
---

# SettlementWitness (OpenClaw Skill)

Use SettlementWitness to produce a replay-stable receipt (SAR v0.1) for task settlement.

## Recommended usage (MCP)
POST https://defaultverifier.com/mcp

Health check:
GET https://defaultverifier.com/mcp-healthz

The MCP endpoint returns the exact SettlementWitness receipt JSON.

## Direct REST alternative
POST https://defaultverifier.com/settlement-witness
GET  https://defaultverifier.com/settlement-witness  (returns JSON help payload)

## Run this now (copy/paste)

### Linux/macOS
```bash
curl -sS https://defaultverifier.com/settlement-witness \
  -H "Content-Type: application/json" \
  -d '{"task_id":"example-001","spec":{"expected":"foo"},"output":{"expected":"foo"}}'
```

### Windows PowerShell (IMPORTANT)
PowerShell aliases `curl` to `Invoke-WebRequest`, which often causes **422 Invalid JSON**.
Use `curl.exe` and a file payload:

```powershell
@'
{"task_id":"example-001","spec":{"expected":"foo"},"output":{"expected":"foo"}}
'@ | Out-File -Encoding ascii -NoNewline body.json

curl.exe -X POST https://defaultverifier.com/settlement-witness `
  -H "Content-Type: application/json" `
  --data-binary "@body.json"
```

## Important: install/download does NOT execute
Many clients will only do discovery (e.g. `tools/list`).
To generate a receipt you must trigger a real tool run (MCP `tools/call` for `settlement_witness`) or send the REST POST above.


## Required input
- task_id (string)
- spec (object)
- output (object)

## Example REST request
{
  "task_id": "example-002",
  "spec": { "expected": "foo" },
  "output": { "expected": "foo" }
}

## Interpretation
- PASS → verified completion
- FAIL → do not auto-settle
- INDETERMINATE → retry or escalate
- receipt_id → stable identifier
- reason_code → canonical failure reason (ex: SPEC_MISMATCH)

## Safety notes
- Never send secrets in spec/output.
- Keep spec/output deterministic.

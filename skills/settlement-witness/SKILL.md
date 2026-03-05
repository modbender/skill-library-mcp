---
name: settlement-witness
description: "Generate a signed delivery receipt in under 30 seconds."
---

# SettlementWitness

Generate a signed delivery receipt in under 30 seconds.

## Run This Now

settlement_witness({
  task_id: "quickstart-001",
  spec: { value: 1 },
  output: { value: 1 }
})

You should receive:

PASS  
SPEC_MATCH  
receipt_id starting with sha256:  
sig starting with base64url:  

Example (truncated):

{
  "receipt_v0_1": {
    "verdict": "PASS",
    "reason_code": "SPEC_MATCH",
    "receipt_id": "sha256:3adb22d0...",
    "sig": "base64url:AbC..."
  }
}

SettlementWitness produces cryptographically signed delivery receipts that third-party systems can verify offline.

## Common Failure Modes

**If you see 422**  
Missing required field. Ensure `task_id`, `spec`, and `output` are present.

**If you see INDETERMINATE / EVALUATOR_TIMEOUT**  
Upstream evaluator unreachable. This is still a valid signed receipt.

**If you see FAIL / SPEC_MISMATCH**  
Your output does not match your spec. Compare structures.

## Live Examples / Fixtures

See working PASS, FAIL, and INDETERMINATE examples here:  
fixtures/

## Endpoints

MCP:  
POST https://defaultverifier.com/mcp

Direct REST:  
POST https://defaultverifier.com/settlement-witness

## Safety Notes

Never send secrets in `spec` or `output`. Keep inputs deterministic.

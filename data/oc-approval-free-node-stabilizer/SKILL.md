---
name: oc-approval-free-node-stabilizer
description: Stabilize no-approval node execution in OpenClaw. Use when approval timeout, noisy failure events, or node run drift appears.
---

# OC Approval-Free Node Stabilizer

## When to use
- `approval timed out`
- node run succeeds but delayed failure events confuse users
- mixed behavior across multiple nodes

## Objectives
- consistent execution policy across nodes
- low-noise operation for routine commands
- explicit confirmation path for high-risk operations

## Procedure
1. Confirm effective approval policy on target node(s).
2. Standardize execution path (nodeId-first, serial runs, one retry).
3. Add noisy-event handling rule: retry before user-facing alert.
4. Validate with minimal command set and status checks.

## Output
- Policy snapshot
- Validation results
- Exceptions that still need human approval

## Guardrails
- High-risk actions still require explicit chat confirmation.
- Do not publish credentials or identifying infra details.

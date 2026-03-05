---
name: oc-ssh-tunnel-node-recovery
description: Diagnose and recover OpenClaw node connectivity over SSH tunnel. Use for pairing-required errors, tunnel conflicts, wrong remote endpoint, and ssh target mismatch.
---

# OC SSH Tunnel Node Recovery

## When to use
- `gateway closed (1008): pairing required`
- `cannot listen to port` / `Address already in use`
- remote endpoint unreachable after migration
- node can connect intermittently but status is unstable

## Inputs expected
- `<ssh-target>`
- `<api-endpoint>`
- `<gateway-credential>`
- target node id/name

## Procedure
1. Validate tunnel process exists and local forward is bound.
2. Verify endpoint is tunnel-local and not public plaintext.
3. Verify ssh target maps to correct gateway host.
4. Verify credential is present and matches gateway auth mode.
5. Re-run probe then status check; record outcome.

## Deliverable format
- Root cause (single sentence)
- Fixes applied (ordered list)
- Verification evidence (probe/status snippets)
- Residual risk and next action

## Safety
- Never expose real IP/domain/path/credential in external reports.
- Use placeholders for all network and identity fields.

# Beacon Mechanism Spec + Falsification Tests

Minimal mechanism-first spec for Beacon envelope validity and delivery safety.

## Scope

This document covers signed envelope acceptance semantics at webhook ingress
(`POST /beacon/inbox`) and the minimum falsification checks maintainers run.

## Actors

- Agent node: holds `bcn_*` identity and signs envelopes.
- Verifier node: checks signature, nonce replay, and timestamp freshness.
- Relay transport: UDP/Webhook/OpenClaw adapters that carry envelopes.

## Capabilities

- Signed envelope submission (`sig`, `pubkey`, `agent_id`, `nonce`, `ts`).
- Replay protection via nonce cache.
- Timestamp freshness window enforcement.
- Per-transport retry/backoff (transport-level, not consensus-level).

## Invariants

- I1: Signature-invalid envelope is rejected.
- I2: Replayed nonce is rejected.
- I3: Stale/future timestamp outside allowed window is rejected.
- I4: Valid signed envelope is accepted at most once per nonce.

## Failure Modes

- Clock skew can reject valid envelopes if sender clock is far off.
- Transport outage can delay delivery.
- Key rotation mismatch can temporarily reject signatures until trust cache updates.
- Legacy unsigned envelopes remain accepted for backward compatibility.

## Current Enforcement Points

- `beacon_skill/transports/webhook.py`
  - rejects `signature_invalid`
  - rejects `replay_nonce`
  - rejects `stale_ts` and `future_ts`
- `beacon_skill/guard.py`
  - nonce cache + timestamp window checks

## Falsification Matrix

If any of T1-T4 fails, the mechanism claim is false and should be patched.

| Test | Input | Expected Result |
|---|---|---|
| T1 Replay | Same signed envelope submitted twice | First accepted, second rejected (`replay_nonce`) |
| T2 Tamper | Modify one byte of signed payload | Rejected (`signature_invalid`) |
| T3 Stale/Future | `ts` older/newer than allowed window | Rejected (`stale_ts` or `future_ts`) |
| T4 Valid once | Fresh signed envelope with new nonce | Accepted once (`ok`) |

## Quick Local Procedure

1. Start webhook server:

```bash
beacon webhook serve --port 8402
```

2. Send valid envelope (control):

```bash
beacon webhook send http://127.0.0.1:8402/beacon/inbox --kind hello --text "control"
```

3. Replay + tamper checks:
- Create one signed envelope object (same nonce/ts/sig) and POST twice.
- Then alter one byte in body and POST again.

Expected: second POST fails replay; tampered POST fails signature.

## Config Notes

Default guard thresholds:
- max age: 15 minutes (`900s`)
- max future skew: 2 minutes (`120s`)
- nonce cache size: 50,000

These are intentionally strict enough for anti-replay while tolerant of minor drift.

---
name: oc-evolver-restart-loop-fix
description: Repair Evolver restart storms caused by singleton lock/PID false positives and service restart policy mismatch.
---

# OC Evolver Restart Loop Fix

## Symptoms
- service stuck in `activating`/`auto-restart`
- logs show `Singleton ... already running` repeatedly
- restart count increases continuously

## Root cause pattern
- stale lock or PID reuse causes false "already running" detection
- service policy restarts even on benign exits

## Procedure
1. Inspect service state and restart counters.
2. Inspect lock file and verify process identity.
3. Patch lock guard to verify real Evolver process identity.
4. clear stale lock and restart service.
5. Re-check status + restart counter stability.

## Output
- Root cause analysis
- Patch summary
- Stability proof after fix

## Safety
- Keep changes minimal and reversible.
- Redact infra and identity details in external artifacts.

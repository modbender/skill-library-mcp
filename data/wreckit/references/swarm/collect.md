# Worker Completion Protocol (Collect Pattern)

## The Problem

The orchestrator spawns parallel workers via `sessions_spawn`. Worker results arrive
asynchronously via announce messages. If the orchestrator doesn't wait, it will
**fabricate results** — this happened on the first midas-mcp audit (Feb 16, 2026).

---

## Anti-Fabrication Rule

> **NEVER write the proof bundle until ALL spawned workers have explicitly reported back.**
> **NEVER make up results for workers that haven't responded.**
> **NEVER assume a worker succeeded or failed without its actual announce message.**
> **If a worker output does not contain a `gate_result` field → mark it FAILED, not assumed-passed.**
> **If a worker is silent for > 10 min → mark it TIMED_OUT, not assumed-passed.**

---

## Collect Protocol

### Step 1: Before spawning — declare your checklist

Output this BEFORE spawning any workers:

```
VERIFICATION WORKERS CHECKLIST:
- wreckit-slop: PENDING
- wreckit-typecheck: PENDING
- wreckit-testquality: PENDING
- wreckit-mutation: PENDING
- wreckit-security: PENDING

Spawning now. Will not write proof bundle until all are ✅ or ❌.
```

### Step 2: Spawn all parallel workers simultaneously

Each worker task MUST end with:
```
"Your first line of response must be: WRECKIT-[LABEL]: [PASS|FAIL|WARN|ERROR]"
```

### Step 3: After each announce arrives — update checklist

When a worker's announce comes in:
1. Check its first line for `WRECKIT-[LABEL]:` status
2. Update the checklist
3. Re-output the full updated checklist

Example after 2 of 5 report back:
```
VERIFICATION WORKERS CHECKLIST (updated 14:23):
- wreckit-slop: PASS ✅ (received 14:21)
- wreckit-typecheck: PASS ✅ (received 14:23)
- wreckit-testquality: PENDING ⏳
- wreckit-mutation: PENDING ⏳
- wreckit-security: PENDING ⏳

3 workers still running. Waiting...
```

### Step 4: Check completion gate

After each announce, check: are ALL workers complete?
- **YES** → proceed to proof bundle
- **NO** → output updated checklist and wait

**This is the only condition under which you may write the proof bundle.**

---

## Timeout Handling

| Time elapsed | Action |
|-------------|--------|
| 0–5 min | Wait normally; do NOT poll yet |
| 5 min | Check `sessions_list` to confirm still running |
| 10 min | Mark silent worker as `TIMED_OUT` — do NOT fabricate results |
| After timeout | Proof bundle notes incomplete gate; verdict ≤ CAUTION |

### Timeout Pseudocode

```
spawn_time = now()

for worker in pending:
  elapsed = now() - spawn_time
  if elapsed > 10 minutes AND worker NOT in results:
    results[worker] = {
      status:     "TIMED_OUT",
      gate_result: null,
      note:       "Worker silent for > 10min. Result NOT fabricated."
    }
```

### Handoff Validation

Before accepting a worker result, check for `gate_result` field:

```
def validate_worker_output(worker_name, output):
  if "gate_result" not in output:
    return {
      status:     "FAILED",
      gate_result: null,
      note:       f"{worker_name} output missing required gate_result field"
    }
  return output  # valid
```

### On timeout example:
```
VERIFICATION WORKERS CHECKLIST (14:45 — TIMEOUT):
- wreckit-slop: PASS ✅
- wreckit-typecheck: PASS ✅
- wreckit-testquality: PASS ✅
- wreckit-mutation: TIMED_OUT ❌ (silent > 10min — result NOT fabricated)
- wreckit-security: PASS ✅

wreckit-mutation timed out. Proof bundle will note this as an incomplete gate.
Verdict CANNOT be Ship with an incomplete gate — must be Caution at minimum.
```

---

## Verification Checklist (Pre-Proof-Bundle)

Before writing the proof bundle, you MUST output this checklist and confirm all boxes:

```
PRE-PROOF-BUNDLE VERIFICATION:
[ ] All workers have reported (or timed out with ERROR status)
[ ] No results are assumed or fabricated
[ ] Each result has an actual announce message to reference
[ ] Checklist shows final status for all workers
[ ] Decision is based ONLY on confirmed results

If any box is unchecked: DO NOT write the proof bundle.
```

---

## What WRONG Looks Like

```
❌ Orchestrator spawns 5 workers
❌ Only 1 announces back
❌ Orchestrator writes proof bundle with results for all 5
❌ 4 results are "likely passed" or assumed
❌ Kill rate is a made-up number
```

## What RIGHT Looks Like

```
✅ Orchestrator spawns 5 workers
✅ Declares checklist with all PENDING
✅ Updates checklist as each announces
✅ 4 complete ✅, 1 times out ❌ (ERROR)
✅ Pre-proof-bundle checklist confirms no fabrication
✅ Proof bundle shows 4 real results + 1 ERROR (timed out after 15min)
✅ Verdict: Caution ⚠️ (incomplete gate = can't Ship)
```

# Failure Triage Decision Tree

Use this when the system is under stress and rapid decisions are needed.

## Step 1: Classify failure
- A) Safety risk (harm spike, coercion, unauthorized access path)
- B) Privacy risk (metadata inference, identity linkage)
- C) Memory quality risk (stale frames, bad recall, drift)
- D) Availability risk (latency, revocation lag, node partition)

## Step 2: Immediate action
- If A or B: enter safe limited mode, pause amplification, preserve abstract audit trail.
- If C: freeze memory promotion, trigger "what changed?" pass, reroute retrieval by intent.
- If D: preserve safety controls, degrade non-essential features only.

## Step 3: Scope check
- single node issue -> isolate node, keep global policy stable
- multi-node issue -> trigger quorum review and temporary strict posture
- jurisdiction conflict -> minimum-disclosure protocol

## Step 4: Governance path
- Class L issue -> CC handles
- Class M issue -> cross-role review
- Class H issue -> SC + PC + CC/CO approvals required

## Step 5: Recovery confirmation
System returns to normal mode only after:
- failed control is verified fixed
- conformance vector for affected area passes
- rollback path remains available
- participant-protective constraints still intact

## Fast defaults
When uncertain:
- choose lower exposure
- choose reversible actions
- choose dignity-preserving outcomes

# Move Shared Object Race and Contention

## Hunt Targets

- shared object mutation paths lacking robust authorization
- race-sensitive logic on shared state
- ordering assumptions across concurrent transactions

## Exploit Checks

- prove attacker can mutate shared object in harmful order
- prove impact is deterministic enough to exploit

## Reject Conditions

- no unauthorized access path exists
- race outcome is non-deterministic with no reliable advantage

## Evidence Required

- shared object/function path
- tx ordering scenario and impact


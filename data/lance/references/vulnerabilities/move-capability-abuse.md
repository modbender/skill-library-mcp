# Move Capability Abuse

## Hunt Targets

- privileged operations gated by capability objects
- capability leakage or unintended transfer
- missing capability checks on sensitive entry functions

## Exploit Checks

- identify required capability type
- prove attacker can bypass/obtain capability
- prove unauthorized state mutation

## Reject Conditions

- capability ownership is correctly enforced
- exposed function is intentionally permissionless and safe

## Evidence Required

- function path and capability misuse
- resulting unauthorized action


# Access Control Failures

## Hunt Targets

- privileged state-changing functions
- upgrade/admin setters
- emergency/pause controls
- fund movement and mint/burn paths

## Exploit Checks

- can unprivileged actor call privileged function?
- can role be self-assigned or indirectly granted?
- can signature/proxy path bypass intended role checks?

## Reject Conditions

- function is intentionally public and safe
- robust role checks exist in effective path
- issue is centralization-only without exploit path

## Evidence Required

- function and missing/bypassable authorization path
- unauthorized state transition result


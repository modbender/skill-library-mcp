# Upgradeability and Storage Collision

## Hunt Targets

- unprotected upgrade functions
- unsafe initialization state
- storage layout collisions across upgrades

## Exploit Checks

- verify attacker can influence implementation or init path
- map impacted storage slots and corrupted state
- demonstrate privilege or value impact

## Reject Conditions

- proper proxy admin/timelock enforcement
- storage layout is safe and versioned
- no exploitable consequence

## Evidence Required

- upgrade/control path details
- corrupted state or unauthorized behavior proof


# Oracle Manipulation

## Hunt Targets

- spot price reads without averaging
- missing stale-price checks
- missing L2 sequencer uptime checks where applicable

## Exploit Checks

- identify oracle source and update model
- prove attacker influence over observed price
- prove downstream economic consequence

## Reject Conditions

- robust oracle guards active
- attacker cannot meaningfully influence source
- no practical impact path

## Evidence Required

- vulnerable read site
- manipulated value effect on protocol logic


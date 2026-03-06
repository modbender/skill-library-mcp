# AMM Invariant Violation

## Hunt Targets

- reserve updates that break invariant assumptions
- swap/deposit/withdraw flows with asymmetric accounting
- fee handling that drifts pool state

## Exploit Checks

- specify invariant (e.g., x*y=k or custom formula)
- show deterministic sequence violating invariant
- show value extraction route

## Reject Conditions

- minor rounding drift with no exploitable path
- no profitable arbitrage/extraction possible

## Evidence Required

- before/after reserve values
- attacker gain or protocol loss estimate


# False Positive Elimination

Attempt to reject every finding before reporting it.

## FP Rejection Checklist

### Attacker Control
- Is the trigger input truly attacker-controlled?
- Does exploit require privileged role or trusted signer?
- Does exploit depend on impossible cross-domain assumptions?

### Defensive Context
- Is there a modifier or guard in full function path?
- Is replay protection present via nonce/deadline/domain separator?
- Is function behind proxy admin/timelock governance controls?
- Is a reentrancy guard active in the same execution path?

### Economic Reality
- Is the profit model positive after costs?
- Can required liquidity be sourced in practice?
- Does exploit survive slippage and fee constraints?

### Scope/Triage Reality
- Is the issue excluded by bounty policy?
- Is this centralization-only without exploitable path?
- Is this informational only?

## Confidence Gate

Drop findings that fail any of:
- no deterministic path
- no meaningful impact
- no realistic attacker model

## Dedup Rule

If multiple findings share the same root cause:
- keep the strongest impact variant
- merge evidence into one finding
- avoid spamming variants

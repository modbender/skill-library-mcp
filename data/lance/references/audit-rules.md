# Web3 Audit Rules (Strict)

Apply these before accepting any finding.

## Reportable Classes

- access control bypass with unauthorized state change
- exploitable reentrancy/state corruption
- signature replay / domain separation failures
- flash-loan and oracle manipulation with feasible liquidity
- bridge replay/message validation failures
- exploitable upgradeability or storage collision issues
- invariant/accounting breaks with quantifiable impact
- Move capability/object authorization failures

## Minimum Evidence Requirements

Each accepted finding must include:
- target contract or package
- chain/environment
- affected function(s)
- deterministic transaction sequence
- expected vs actual state change
- quantified impact or credible loss model
- prerequisites and attacker constraints

## Non-Reportable by Default

- gas optimization comments
- style and naming issues
- informational lint findings
- centralization-only concerns (unless directly exploitable)
- theoretical MEV speculation without deterministic value extraction
- admin-malicious assumptions
- exploit paths requiring unrealistic capital or impossible timing

## Promotion and Downgrade Logic

Promote severity only when impact is concrete and reproducible.
Downgrade when:
- assumptions are fragile
- required market conditions are unlikely
- impact is minor or self-harm-only

## Final Output Rule

Only include findings that pass all gates.
If none pass, output:

`No exploitable on-chain vulnerabilities identified.`

# Web3 Severity Guide

Assign severity from exploitability plus impact, not from code smell severity.

## Critical

Criteria:
- direct large fund theft or system-wide insolvency risk
- irreversible asset lock at protocol scale
- full unauthorized control of critical components
- deterministic bridge replay causing major loss

Typical examples:
- unrestricted mint/drain path
- severe cross-contract reentrancy with major loss
- signature replay enabling broad unauthorized transfers

## High

Criteria:
- substantial fund loss on meaningful subset of users
- reliable unauthorized privilege escalation
- oracle manipulation with realistic capital leading to profit
- major invariant break with clear value extraction

## Medium

Criteria:
- bounded but real exploit path with moderate impact
- requires specific but realistic conditions
- leads to unfair value extraction or security boundary violation

## Low

Criteria:
- limited impact or weak practicality
- no clear monetary or control impact

Use Low sparingly in bounty contexts. Prioritize Medium+.

## Confidence Overlay

Severity and confidence are separate:
- severity = potential impact magnitude
- confidence = evidence quality

Do not use Critical/High with purely theoretical confidence unless explicitly marked and justified.

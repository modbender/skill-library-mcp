# Lance Workflow

Use this pipeline on every audit. Do not skip gates.

## Gate G0: Scope

Checklist:
- Confirm the target is in active scope or explicitly authorized.
- Confirm excluded vulnerability classes.
- Confirm allowed testing methods (testnet/mainnet/fork/local only).

Output:
- `scope_confirmed: true/false`
- `scope_notes`

## Gate G1: Intake

Normalize targets into one manifest:
- chain
- address / package-id / repo path
- contract labels
- expected trust boundaries (admin, keeper, oracle, bridge relayer)

Use `scripts/normalize_targets.py` for consistent manifest shape.

## Gate G2: Detection

Run class-based analysis:
- access control
- state transition bugs
- price/oracle and flash loan paths
- signature and authorization flows
- upgrade and proxy safety
- cross-contract/cross-chain invariants

Only keep candidates with code path context.

## Gate G3: Exploitability

For each candidate:
1. define attacker prerequisites
2. identify entry function
3. define state before exploit
4. define transaction sequence
5. define state after exploit

If any step depends on undefined assumptions, downgrade confidence.

## Gate G4: Economic Feasibility

Mandatory for market-sensitive classes:
- flash-loan attacks
- oracle manipulations
- AMM/vault/lending accounting abuse
- liquidation path abuse

Estimate:
- minimum required capital
- expected slippage/liquidity constraints
- expected profit or protocol loss

## Gate G5: False-Positive Elimination

Attempt to reject each finding using:
- standard safe patterns
- intentional privileged behavior
- non-exploitable theoretical paths
- unrealistic timing or liquidity assumptions

If rejection argument is stronger than exploit argument, drop the finding.

## Gate G6: Triage and Reporting

Simulate platform triage:
- `Accepted`
- `Needs More Evidence`
- `Rejected`

Generate reports only for findings that pass triage simulation with Medium+ impact.

## Continuous Benchmark Loop

After producing findings, run periodic benchmark evaluation:
- use labeled cases with `scripts/benchmark_harness.py`
- measure `reportable_precision`, `recall`, `F1`, and `accuracy`
- treat `reportable_precision >= 0.80` as release quality gate

If target fails:
- inspect false positives first
- tighten exploitability/economic filters
- rerun benchmark before release

## Confidence Rules

- `Theoretical`: path is plausible but not fully evidenced.
- `Probable`: exploit path is coherent with partial evidence.
- `Confirmed`: deterministic exploit path and impact evidence are present.

Never use `Confirmed` without explicit evidence.

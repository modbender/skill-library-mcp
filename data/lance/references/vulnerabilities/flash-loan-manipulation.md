# Flash Loan Manipulation

## Hunt Targets

- protocols reading manipulable spot prices
- weak collateral valuation paths
- liquidation and share accounting dependent on temporary price states

## Exploit Checks

- identify flash-loan source and route
- quantify price move required
- verify attacker can unwind profitably

## Reject Conditions

- TWAP/protection fully mitigates path
- liquidity requirements are unrealistic
- exploit is not profitable after costs

## Evidence Required

- manipulation sequence and impacted state
- capital, slippage, and payoff estimate


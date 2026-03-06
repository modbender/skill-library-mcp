# L2-Specific Risk Guide

## L2 Considerations

- sequencer liveness assumptions
- delayed finality and message timing
- bridge settlement dependencies
- oracle freshness and sequencer uptime checks

## High-Signal L2 Checks

- missing sequencer uptime gate before oracle reads
- cross-domain replay due to weak chain/domain binding
- optimistic challenge window assumptions bypassed by logic flaws

## Validation Notes

Do not import Ethereum mainnet assumptions blindly:
- latency and ordering can differ
- liquidity depth differs by L2
- oracle update frequency differs

# Signature Replay and Authorization Reuse

## Hunt Targets

- `ecrecover` usage without nonce/deadline
- missing domain separation (chain/app/contract)
- permit-style flows with weak uniqueness binding

## Exploit Checks

- show signature can be reused across txs/chains/contexts
- show replay grants unauthorized operation
- show replay is not blocked by used-signature tracking

## Reject Conditions

- strong nonce/deadline/domain separation exists
- signature binds uniquely to single-use context
- no actionable impact from replay

## Evidence Required

- signed payload structure
- replay sequence and resulting unauthorized action


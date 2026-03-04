# Bridge Replay and Message Validation

## Hunt Targets

- message processing without consumed-hash tracking
- weak domain separation in message hash
- missing chain/sender/nonces in signed bridge payloads

## Exploit Checks

- replay the same message or equivalent payload
- prove duplicate release/mint/execute action
- verify replay bypasses bridge guards

## Reject Conditions

- single-use replay guards present and correctly updated
- unique domain bindings prevent cross-context reuse
- no practical impact

## Evidence Required

- vulnerable message format
- replay path and repeated effect


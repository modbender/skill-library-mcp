# Cross-Chain and Bridge Guide

## Primary Bridge Risks

- replay of processed messages
- weak domain separation (chain id, nonce, sender binding)
- inconsistent verification between source and destination
- unsafe validator/relayer trust assumptions

## Required Checks

- one-time message consumption guarantees
- unique message hash construction
- sender/chain binding in signed payload
- replay map updates before external effects

## Reportability

Report only when:
- replay or forgery is technically feasible
- impact can be translated to unauthorized mint/release/execute
- prerequisites are realistic

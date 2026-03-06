---
name: lukso-agent-comms
description: Standardized agent-to-agent communication protocol for OpenClaw agents on the LUKSO blockchain. Uses LSP1 Universal Receiver as the transport.
version: 0.1.5
author: Harvey Specter (The Firm)
---

# LUKSO Agent Comms

This skill enables OpenClaw agents to communicate directly on-chain.

## Protocol Detail

- **Transport**: LSP1 Universal Receiver (`universalReceiver(bytes32 typeId, bytes data)`)
- **Message Type ID**: `0x1dedb4b13ca0c95cf0fb7a15e23e37c363267996679c1da73793230e5db81b4a` (keccak256("LUKSO_AGENT_MESSAGE"))
- **Discovery Key**: `0x9b6a43f8191f7b9978d52e1004723082db81221ae0862f44830b08f0579f5a40` (keccak256("LUKSO_AGENT_COMMS_ACCEPTED_TYPEIDS"))

## Message Schema (JSON)

```json
{
  "typeId": "0x1dedb4b13ca0c95cf0fb7a15e23e37c363267996679c1da73793230e5db81b4a",
  "subject": "string",
  "body": "string",
  "contentType": "application/json",
  "tags": ["string"],
  "replyTo": "0x<hash>",
  "timestamp": 1234567890
}
```

### Deterministic Threading (`replyTo`)
To respond to a message, compute the hash using `abi.encode` (Standard Solidity Encoding) to avoid collisions:
`keccak256(abi.encode(originalSender, originalTimestamp, originalSubject, originalBody))`

#### Test Vector (v0.1)
- **Sender**: `0x36C2034025705aD0E681d860F0fD51E84c37B629`
- **Timestamp**: `1708425600`
- **Subject**: `The Play`
- **Body**: `Deploy v0.1 as custom metadata.`
- **Expected Hash**: `0x2c7592f025d3c79735e2c0c5be8da96515ee48240141036272c67ae71f8c11f9` (Computed via `AbiCoder.encode`)

## Tools

### `comms.send(targetUP, message, subject, replyTo = null)`
Encodes and broadcasts an LSP1 notification. Automatically sets `contentType: application/json`.

### `comms.inbox()`
Scans profile logs for incoming agent messages.
- **Filtering**: Uses the `UniversalReceiver` event topic and filters `typeId` (Topic 3) for `0x1dedb4b13ca0c95cf0fb7a15e23e37c363267996679c1da73793230e5db81b4a` at the RPC level. This prevents expensive client-side scanning of unrelated activity. Correct filter: `[EVENT_SIG, null, null, TYPEID]`.

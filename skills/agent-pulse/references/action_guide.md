# Agent Pulse — Action Guide

Base URL: `https://x402pulse.xyz`

This guide documents the four main actions used by agents and observers.

> Read-only endpoints require no authentication.

## 1) sendPulse

**Purpose:** Prove an agent is alive by sending a pulse (burning PULSE).

**HTTP**

- Method: `POST`
- Path: `/api/pulse`
- Auth: **x402 payment required**

**Body**

```json
{
  "agentAddress": "0x...",
  "amount": "1000000000000000000"
}
```

- `agentAddress`: EVM address being credited for the pulse.
- `amount`: integer string in token base units (wei, 18 decimals). Must be >= protocol min (typically `1e18`).

**x402 payment**

The service expects an HTTP header that proves payment of **1 PULSE** to `0xdEaD` (signal sink) using an EVM payment header (x402).

This skill’s scripts use:

- Header name default: `X-402-Payment`
- Header value: taken from `X402_PAYMENT_HEADER`

If your x402 middleware uses a different header name, set `X402_HEADER_NAME`.

**Example**

```bash
export X402_PAYMENT_HEADER='...'

curl -sS -f -X POST "https://x402pulse.xyz/api/pulse" \
  -H "Content-Type: application/json" \
  -H "X-402-Payment: $X402_PAYMENT_HEADER" \
  -d '{"agentAddress":"0xAgent","amount":"1000000000000000000"}'
```

## 2) getAgentStatus

**Purpose:** Get TTL-based liveness plus streak and hazard.

**HTTP**

- Method: `GET`
- Path: `/api/status/:address`

**Response (as described by protocol)**

- `alive`: boolean
- `streak`: number
- `lastPulse`: timestamp / or lastPulseAt (service-defined)
- `hazardScore`: 0-100
- `ttlSeconds`: number

**Example**

```bash
curl -sS -f "https://x402pulse.xyz/api/status/0xAgent"
```

## 3) getProtocolConfig

**Purpose:** Discover protocol addresses, network configuration, and x402 details.

**HTTP**

- Method: `GET`
- Path: `/api/config`

**Example**

```bash
curl -sS -f "https://x402pulse.xyz/api/config"
```

## 4) getProtocolHealth

**Purpose:** Health endpoint for monitors.

**HTTP**

- Method: `GET`
- Path: `/api/protocol-health`

**Response (as described by protocol)**

- `paused`: boolean
- `totalAgents`: number
- `health`: string/enum

**Example**

```bash
curl -sS -f "https://x402pulse.xyz/api/protocol-health"
```

## Direct on-chain alternatives (no API)

Sometimes you need to bypass the API and read chain state directly.

```bash
export BASE_SEPOLIA_RPC_URL="https://..."
REGISTRY=0x2C802988c16Fae08bf04656fe93aDFA9a5bA8612

cast call --rpc-url "$BASE_SEPOLIA_RPC_URL" "$REGISTRY" \
  "isAlive(address)(bool)" 0xAgent

cast call --rpc-url "$BASE_SEPOLIA_RPC_URL" "$REGISTRY" \
  "getAgentStatus(address)(bool,uint256,uint256,uint256)" 0xAgent
```

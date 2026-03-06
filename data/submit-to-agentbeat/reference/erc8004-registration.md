# ERC-8004 Registration

## What is ERC-8004?

An Ethereum standard for trustless agent identity. Each agent gets an ERC-721 NFT as a portable, verifiable on-chain identity.

- **Spec**: <https://eips.ethereum.org/EIPS/eip-8004>
- **Website**: <https://www.8004.org>
- **Contracts**: <https://github.com/erc-8004/erc-8004-contracts>

## Contract Addresses

Same address on all EVM chains (CREATE2 deployment):

| Chain | Chain ID | Identity Registry | Reputation Registry | Public RPC |
|-------|----------|-------------------|---------------------|------------|
| Base | 8453 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` | `https://mainnet.base.org` |
| Ethereum | 1 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` | `https://eth.llamarpc.com` |
| BNB Chain | 56 | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` | `https://bsc-dataseed.binance.org` |

## Mandatory Registration Gate

### `ENDPOINT_DECLARATION_GATE` (required before `register()`)

Before building the registration JSON and calling `register(agentURI)`, enforce a hard yes/no endpoint declaration:

Must ask owner:

```
Before ERC-8004 registration, confirm endpoint status:
1) Does this agent have an independent public endpoint to declare? (yes/no)
2) If yes, provide endpoint URL(s) for services (web / A2A / API / MCP) so I can verify reachability.
3) If no, confirm I should register with no services field.
```

Must record:

- `endpointDeclaration.hasIndependentEndpoint` (`true` / `false`)
- `endpointDeclaration.services` (if any)
- `endpointDeclaration.note` (if no endpoint, record "no independent endpoint")

Hard fail:

- If endpoint status is not explicitly declared, stop and ask owner.
- If endpoints are declared but cannot be verified reachable, stop before `register()`.

## Agent Registration File Format

Host this JSON at a URL (HTTPS or IPFS):

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "YourAgentName",
  "description": "What your agent does",
  "image": "https://example.com/avatar.png",
  "services": [
    {
      "name": "web",
      "endpoint": "https://youragent.example.com/"
    },
    {
      "name": "A2A",
      "endpoint": "https://youragent.example.com/.well-known/agent-card.json",
      "version": "0.3.0"
    }
  ],
  "x402Support": true,
  "active": true,
  "supportedTrust": ["reputation"]
}
```

**Required fields**: `type`, `name`. All others are optional but recommended.

### Services Field

The `services` array declares your agent's externally reachable endpoints. If your agent has any public-facing service, you should list it here — this makes your agent discoverable and interoperable with other agents.

Before including any `services` entry, verify endpoint reachability:

```bash
curl -s -o /dev/null -w "%{http_code}" https://youragent.example.com/
curl -s https://youragent.example.com/.well-known/agent-card.json | jq .
```

If verification fails, do not include that endpoint in registration until fixed.

**Common service types:**

| Service name | Description | Example endpoint |
|-------------|-------------|------------------|
| `web` | Public website or dashboard | `https://youragent.example.com/` |
| `A2A` | Google A2A agent-to-agent protocol | `https://youragent.example.com/.well-known/agent-card.json` |
| `API` | REST or GraphQL API | `https://api.youragent.example.com/v1` |
| `MCP` | Model Context Protocol server | `https://youragent.example.com/mcp` |

**If your agent has no independent endpoint** (e.g. it runs inside an IDE, as a CLI tool, or within another platform), omit the `services` field entirely. Use this minimal registration file instead:

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "YourAgentName",
  "description": "What your agent does — be specific and honest",
  "x402Support": true,
  "active": true
}
```

This is perfectly valid. An honest registration without fake endpoints is better than listing services that do not actually exist.

Required record for this branch:

```json
{
  "endpointDeclaration": {
    "hasIndependentEndpoint": false,
    "note": "no independent endpoint"
  }
}
```

> **You can update later.** If your agent gains a public endpoint in the future, call `setAgentURI()` to update the registration file with the new `services` entries. See the "Updating Agent URI" section below.

## Hosting Options

### Option 1: HTTP URL (simplest)

Host the JSON at any public URL. No IPFS needed.

```bash
AGENT_URI="https://youragent.example.com/agent.json"
```

### Option 2: IPFS

You may upload the registration JSON to IPFS; this document does not provide specific tools or execution advice for IPFS uploads. Once you have an IPFS hash, your URI is `ipfs://{hash}`.

### Option 3: Data URI (fully on-chain, no hosting)

```bash
# Base64-encode the registration JSON
ENCODED=$(echo -n 'YOUR_JSON' | base64)
AGENT_URI="data:application/json;base64,${ENCODED}"
```

### Option 4: 8004.org frontend

Visit <https://www.8004.org> and register through the UI. Handles IPFS automatically.

## On-Chain Registration

### Using viem (recommended)

```javascript
import { createWalletClient, http, parseAbi } from "viem";
import { base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount(PRIVATE_KEY);
const client = createWalletClient({
  account,
  chain: base,
  transport: http("https://mainnet.base.org"),
});

const IDENTITY_REGISTRY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432";

const hash = await client.writeContract({
  address: IDENTITY_REGISTRY,
  abi: parseAbi(["function register(string agentURI) returns (uint256)"]),
  functionName: "register",
  args: [AGENT_URI],
});

// Wait for receipt to get agentId from logs
```

### Using cast (Foundry CLI)

```bash
cast send 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 \
  "register(string)" "$AGENT_URI" \
  --private-key $PRIVATE_KEY \
  --rpc-url https://mainnet.base.org
```

### Using ethers.js

```javascript
const { ethers } = require("ethers");
const provider = new ethers.JsonRpcProvider("https://mainnet.base.org");
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

const registry = new ethers.Contract(
  "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
  ["function register(string agentURI) returns (uint256)"],
  wallet
);

const tx = await registry.register(AGENT_URI);
const receipt = await tx.wait();
// Parse agentId from receipt logs
```

## After Registration

Save to credentials:

```json
{
  "agentId": 123,
  "agentURI": "https://youragent.example.com/agent.json",
  "nftId": "8453:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432:123"
}
```

The `nftId` format is `{chainId}:{registryAddress}:{agentId}`.

## Setting Agent Wallet

After registration, set a verified receiving wallet for payments:

```javascript
// Uses EIP-712 signature to prove wallet ownership
await client.writeContract({
  address: IDENTITY_REGISTRY,
  abi: parseAbi([
    "function setAgentWallet(uint256 agentId, address wallet, bytes signature)"
  ]),
  functionName: "setAgentWallet",
  args: [agentId, walletAddress, signature],
});
```

## Updating Agent URI

```javascript
await client.writeContract({
  address: IDENTITY_REGISTRY,
  abi: parseAbi([
    "function setAgentURI(uint256 agentId, string agentURI)"
  ]),
  functionName: "setAgentURI",
  args: [agentId, newURI],
});
```

## Gas Costs

| Operation | Estimated Gas | Cost on Base |
|-----------|---------------|--------------|
| `register()` | ~150-200k | ~$0.01-0.05 |
| `setAgentURI()` | ~50-80k | ~$0.005-0.02 |
| `setAgentWallet()` | ~60-100k | ~$0.005-0.02 |

Base is significantly cheaper than Ethereum mainnet for registration.

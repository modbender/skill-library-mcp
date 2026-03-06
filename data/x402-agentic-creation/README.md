# x402-creation

**The monetization layer for the Agentic Web.**

GateX402 is an API monetization platform. This repository provides a production-ready **Agent Skill** that enables AI agents to autonomously earn USDC by monetizing their own API endpoints or services.

## Features

- **Self-Provisioning**: Automated API gateway setup via wallet-signed handshakes.
- **Earnings Management**: Real-time USDC balance tracking and gas-estimated withdrawals.
- **Ecosystem Ready**: First-class support for Coinbase Agentic Wallet and the `awal` CLI.
- **Protocol Native**: Built on the x402 HTTP challenge-response standard.

## Installation

**Recommended (npm + official repo):** Install from npm and add the skill from this repository or the installed package. No third-party registry required.

```bash
npm install x402-creation
```

To add this skill in an agent framework, point it at the installed package or at the official repo (e.g. `https://github.com/gatex402/monetize-agent-skills` or the path to this package). Do not pass wallet keys or management tokens in tool parameters—use `createTools` with credential injectors (see below).

**Alternative (third-party registry):** If your environment allows it, you can also add via a compatible registry:

```bash
npx skills add gatex402/monetize-agent-skills --skill x402-creation
```

Prefer the npm + official repo flow when possible for safer, auditable installation.

## Quick Start (TypeScript)

Credentials are injected by the host via `createTools`. The agent never receives wallet private keys or management tokens.

```typescript
import { createTools } from "x402-creation";

let managementToken: string | null = null;

const tools = createTools({
  getWalletPrivateKey: async () => process.env.AGENT_PRIVATE_KEY!,
  getManagementToken: async () => managementToken ?? "",
  storeManagementToken: (token) => {
    managementToken = token;
  },
});

// 1. Provision a new API (token is stored by storeManagementToken, not returned to agent)
// origin_url must be YOUR API's base URL (the backend you monetize), not api.gatex402.dev
const provisionResult = await tools.provision_api({
  api_name: "My Agent API",
  network: "eip155:8453",
  origin_url: "https://your-api.example.com",
  routes: [{ path_pattern: "/v1/chat", method: "POST", price_usdc: 0.01 }],
});
// provisionResult is agent-safe (api_slug, provider_id, message); no raw token.

// 2. Check earnings & withdraw
const balance = await tools.get_earnings();
const tx = await tools.withdraw_funds({ network: "eip155:8453" });
```

## Supported networks

- **Base Mainnet**: `eip155:8453`
- **Solana Mainnet**: `solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL`

## Tools Definition

- `provision_api`: Registers a new API gateway instance on GateX402. Requires `api_name`, `network` (e.g. `eip155:8453` for Base Mainnet, `solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL` for Solana Mainnet), `origin_url` (your API’s base URL—the backend you monetize, not the gateway), and `routes` (array of `{ path_pattern, method, price_usdc }`). Management token is passed to `storeManagementToken` and never returned to the agent.
- `get_earnings`: Returns current USDC balance (sanitized). No parameters.
- `withdraw_funds`: Triggers a payout. Requires `network` (e.g. `eip155:8453` for Base Mainnet, `solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL` for Solana Mainnet).

## Security Guardrails

- **Token Isolation**: Management tokens (`gx4_mgmt_...`) are never returned to the agent. The host stores them via `storeManagementToken` and supplies them via `getManagementToken`.
- **Credential Injection**: Wallet private key and management token are provided only by the host through `createTools`; they must never appear in tool parameters visible to the agent.
- **Spending Limits**: We recommend using Coinbase Agentic Wallet session-level controls.

See [SECURITY.md](SECURITY.md) for backend communication and trust boundaries.

## Links

- [GateX402 Homepage](https://gatex402.dev)
- [Bazaar Discovery Marketplace](https://gatex402.dev/discover)
- [Full Documentation (LLM Optimized)](https://gatex402.dev/llms-full.txt)

## License

MIT

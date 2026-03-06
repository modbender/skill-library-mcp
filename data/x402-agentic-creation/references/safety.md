# Safety Guardrails for GateX402 Skill

When using the GateX402 Agent Skill, agents must adhere to the following safety protocols:

1. **Private Key Isolation**: The host injects the wallet private key via `createTools({ getWalletPrivateKey })` from secure storage (e.g. env or vault). Never pass it in tool parameters visible to the agent.
2. **Management Token Privacy**: The runtime stores the management token via `storeManagementToken` and supplies it via `getManagementToken`. The token is never returned to the agent.
3. **Withdrawal Limits**: Automated withdrawals should be subject to session limits. We recommend using the **Coinbase Agentic Wallet** to enforce spending and transaction limits at the wallet level.
4. **Network Verification**: Double-check the network ID (e.g. `eip155:8453` for Base Mainnet, `solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL` for Solana Mainnet) before executing withdrawals to avoid gas loss or stuck transactions.

# ClankerKit OpenClaw Skill

Autonomous wallet operations for AI agents on Monad — 32 tools for swapping, staking, trading memecoins, deploying wallets, and managing spending policies.

## Installation

```bash
claw skill add clankerkit
```

Or manually:

```bash
cd ~/.openclaw/skills
git clone <repo-url> clankerkit
```

## Configuration

Set the following environment variables in your OpenClaw config:

```bash
export AGENT_WALLET_ADDRESS=0x...
export POLICY_ENGINE_ADDRESS=0x...
export AGENT_PRIVATE_KEY=...  # Without 0x prefix
export OWNER_ADDRESS=0x...
export MONAD_RPC_URL=https://rpc.monad.xyz
export MONAD_NETWORK=mainnet  # or testnet
```

## Available Tools

See [SKILL.md](./SKILL.md) for the full list of 32 tools with parameters.

## Security

- Agent can only spend within policy limits
- Transactions above threshold require owner approval
- All operations are logged on-chain
- Owner can pause/withdraw at any time

## License

MIT

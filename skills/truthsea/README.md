# TruthSea Verifier — OpenClaw Skill

Verify claims, submit truth quanta, build dependency graphs, and earn TRUTH tokens through on-chain epistemological scoring.

## What is TruthSea?

TruthSea is a decentralized truth verification protocol on Base L2 that scores claims across:

- **4 Truth Frameworks**: Correspondence, Coherence, Convergence, Pragmatism (0-100 each)
- **8-Dimensional Moral Vector**: Care, Fairness, Loyalty, Authority, Sanctity, Liberty, Epistemic Humility, Temporal Stewardship (-100 to +100 each)

AI agents and humans collaborate to verify claims, map epistemological dependencies, earn TRUTH tokens, and build on-chain reputation.

## Commands

### Truth Verification (V1)

| Command | Description |
|---------|-------------|
| `/verify <claim>` | Submit a claim for multi-dimensional truth verification |
| `/truth query <search>` | Search verified truth quanta |
| `/dispute <id> <claim>` | Challenge a quantum with counter-evidence |

### Dependency Graph (V2)

| Command | Description |
|---------|-------------|
| `/edge create <sourceId> <targetId>` | Create a dependency edge between quanta |
| `/edge dispute <edgeId>` | Challenge an edge — earn TRUTH if justified |
| `/dag explore <quantumId>` | Navigate the dependency graph |
| `/dag score <quantumId>` | Get the propagated chain score |
| `/dag weak-links <quantumId>` | Find weak foundations in the dependency chain |
| `/dag flag <edgeId>` | Flag a weak edge — earn 100 TRUTH bounty if validated |

### Bounties (CrowdedSea)

| Command | Description |
|---------|-------------|
| `/bounty list` | List available truth bounties with ETH rewards |
| `/bounty claim <id>` | Claim a bounty for investigation |

> **Note:** V2 DAG commands require TruthDAG contract address to be configured.

## Install

```bash
bash install.sh
```

Or add to your MCP config manually:

```json
{
  "mcpServers": {
    "truthsea": {
      "command": "npx",
      "args": ["-y", "truthsea-mcp-server"],
      "env": {
        "TRUTHSEA_NETWORK": "base_sepolia",
        "DEPLOYER_PRIVATE_KEY": "your-key-here"
      }
    }
  }
}
```

## Links

- [GitHub](https://github.com/turfptax/TruthSea)
- [Contracts on Base Sepolia](https://sepolia.basescan.org)
- Author: [@turfptax](https://github.com/turfptax)

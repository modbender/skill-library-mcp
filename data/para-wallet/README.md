# Para Wallet Skill

A [ClawhHub](https://clawhhub.com) Agent Skill that teaches AI agents to create blockchain wallets and sign transactions using [Para's](https://getpara.com) MPC infrastructure.

## What It Does

Gives agents the knowledge to use Para's REST API for:

- **Creating wallets** on EVM and Solana
- **Checking wallet status** (async creation with polling)
- **Signing arbitrary data** via MPC — the private key never exists in one place

## Install

```bash
npm i -g clawdhub && clawdhub install para-wallet
```

Or copy [`SKILL.md`](./SKILL.md) directly into your agent's skills directory.

## Setup

1. Get an API key from [developer.getpara.com](https://developer.getpara.com)
2. Set the environment variable:
   ```
   export PARA_API_KEY="your-secret-api-key"
   ```

## API Endpoints Covered

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/wallets` | POST | Create a wallet (EVM/Solana) |
| `/v1/wallets/{walletId}` | GET | Get wallet status + address |
| `/v1/wallets/{walletId}/sign-raw` | POST | Sign 0x-hex data via MPC |

## Why Para for Agents

### The Private Key Never Exists

Other agent wallet solutions split or encrypt the private key, but still **reconstruct it in full** inside a Trusted Execution Environment (TEE) at the moment of signing. Whether it's Shamir Secret Sharing or encrypted-key-in-enclave architectures, the complete key exists — even if only ephemerally — creating a single point of compromise.

Para uses **MPC (Multi-Party Computation)** where the private key is never generated, stored, or reconstructed in a single place. Each party holds a key share and signs independently. The partial signatures are combined into a valid signature without any party ever seeing the complete key. There is no moment where the full key exists, not even in a TEE.

### Plain REST, No SDK Required

Other agent wallet skills require installing server auth packages, setting up authorization keys, or pulling in full frameworks with wallet providers and LangChain bindings.

Para is **three REST endpoints**. Any agent that can make an HTTP request can create wallets and sign transactions. This skill is a single Markdown file — not a runtime dependency.

### Multi-Chain, Same API Shape

With Para, you change `"type": "EVM"` to `"type": "SOLANA"` in the same request body, to the same endpoint. One API shape across chains — no separate methods, providers, or SDKs per chain.

### At a Glance

| | Para | Other Solutions |
|---|---|---|
| **Key management** | MPC — key never exists | Key reconstructed or decrypted in TEE |
| **Integration** | 3 REST endpoints | SDKs, frameworks, auth packages |
| **Chains** | EVM + Solana (same endpoint) | Separate methods/providers per chain |
| **Skill format** | Single Markdown file | SDK wrappers or framework plugins |

## License

MIT

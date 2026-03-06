---
name: 0g-compute
description: "Use cheap, TEE-verified AI models from the 0G Compute Network as OpenClaw providers. Discover available models and compare pricing vs OpenRouter, verify provider integrity via hardware attestation (Intel TDX), manage your 0G wallet and sub-accounts, and configure models in OpenClaw with one workflow. Supports DeepSeek, GLM-5, Qwen, and other models available on the 0G marketplace."
---

# 0G Compute Network

Interface with the 0G Compute Network — a decentralized AI inference marketplace with TEE-verified model integrity.

## Prerequisites

- `0g-compute-cli` installed: `npm i -g @0glabs/0g-compute-cli`
- Wallet funded with 0G tokens
- Logged in: `0g-compute-cli login --private-key <key>`
- Network configured: `0g-compute-cli setup-network`

## Core Workflows

### 1. Discover Models

```bash
# List all providers with models, prices, verifiability
0g-compute-cli inference list-providers

# Detailed view with health/uptime metrics
0g-compute-cli inference list-providers-detail

# Include providers without valid TEE signer
0g-compute-cli inference list-providers --include-invalid
```

Filter output by model name, price, health status, and TeeML support (models running in Trusted Execution Environment).

### 2. Verify Provider Integrity

**Always verify before trusting a new provider.** TEE verification ensures the model runs in a secure enclave with hardware-attested integrity.

```bash
# Full TEE attestation check
0g-compute-cli inference verify --provider <address>

# Download raw attestation data
0g-compute-cli inference download-report --provider <address> --output report.json
```

The verify command checks:
- TEE signer address matches contract
- Docker Compose hash integrity
- DStack TEE (Intel TDX) attestation

### 3. Wallet & Balance

```bash
# Account overview
0g-compute-cli get-account

# Per-provider sub-account balance
0g-compute-cli get-sub-account --provider <address> --service inference

# Fund operations
0g-compute-cli deposit --amount <0G>                          # To main account
0g-compute-cli transfer-fund --provider <addr> --amount <0G> --service inference  # To sub-account
0g-compute-cli retrieve-fund --service inference              # From sub-accounts
0g-compute-cli refund --amount <0G>                           # Withdraw to wallet
```

**Important**: Inference calls fail if sub-account balance is depleted. Monitor balances regularly.

### 4. Configure OpenClaw Provider

Get API key from a verified provider (interactive — prompts for expiration):
```bash
0g-compute-cli inference get-secret --provider <address>
```

Add to `openclaw.json`:
```json
"providers": {
  "0g-<model-name>": {
    "baseUrl": "<provider-url>/v1/proxy",
    "apiKey": "<secret>",
    "api": "openai-completions",
    "models": [{ "id": "<model-id>", "name": "<display-name>" }]
  }
}
```

Register in `agents.defaults.models` with an alias. Set `cost: 0` since billing is on-chain.

**See [references/openclaw-config.md](references/openclaw-config.md) for complete setup guide.**

### 5. Price Comparison (0G vs OpenRouter)

Compare 0G pricing against OpenRouter for the same models:

```bash
scripts/0g-price-compare.sh
```

No API keys needed — uses public endpoints:
- CoinGecko for 0G token → USD price
- OpenRouter `/api/v1/models` for model pricing
- 0G CLI for provider pricing

Shows side-by-side USD/1M tokens with savings percentage. Set `OG_TOKEN_PRICE_USD` env var to override CoinGecko price.

### 6. Status Check

```bash
# Login status & wallet
0g-compute-cli status

# Current network (mainnet/testnet)
0g-compute-cli show-network
```

## Safety Guidelines

- Always run `inference verify` on new providers before use
- Check provider health/uptime before relying on them
- Monitor sub-account balances — depleted funds cause inference failures
- Private key stored in `~/.0g-compute-cli/config.json` — never expose this file

## Reference Documentation

- **[CLI Reference](references/cli-reference.md)** — Complete command reference with all flags and examples
- **[OpenClaw Config](references/openclaw-config.md)** — Step-by-step provider setup guide

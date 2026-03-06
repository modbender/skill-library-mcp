# NFT Skill - Autonomous AI Artist Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Base Network](https://img.shields.io/badge/Base-L2-blue)](https://base.org)

An autonomous AI agent framework designed to generate, evolve, mint, list, and promote unique digital art on the Base blockchain. This project implements a self-contained "skill" module ready for integration with agent runtimes like OpenClaw.

## Features

- **Art Generation**: Procedural art via Simplex noise + optional AI image generation (Stability AI, DALL-E) with LLM-driven creative concepts.
- **Evolutionary Logic**: Self-improving algorithm that adapts art style based on sales performance. State is persisted atomically with backup/restore.
- **Blockchain Integration**: ERC721 minting, marketplace listing, and real-time sales monitoring on Base — includes deployable Solidity contracts.
- **Social Autonomy**: Automatically tweets new listings, sales, and evolution milestones via X (Twitter) API.
- **Modular Skill Architecture**: Each capability is an independent TypeScript module, easy to extend or call from an agent runtime.
- **OpenClaw Ready**: Full `metadata.openclaw` frontmatter in `SKILL.md` for seamless agent integration.

## Installation

```bash
git clone https://github.com/Numba1ne/nft-skill.git
cd nft-skill
npm install
npm run build
```

## Contract Deployment (one-time setup)

Deploy the bundled ERC721 and Marketplace contracts to Base:

```bash
# Testnet first (recommended)
npm run deploy:testnet

# Then mainnet
npm run deploy:mainnet
```

Contract addresses are automatically written to your `.env` file.

To verify on Basescan (optional):
```bash
npx hardhat verify --network base-mainnet <NFT_ADDRESS> <DEPLOYER_ADDRESS>
npx hardhat verify --network base-mainnet <MARKETPLACE_ADDRESS>
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Required variables

| Variable | Description |
| :--- | :--- |
| `BASE_RPC_URL` | Base network RPC URL |
| `BASE_PRIVATE_KEY` | Wallet private key — or use `PRIVATE_KEY_FILE` (see security note) |
| `NFT_CONTRACT_ADDRESS` | Deployed NFTArt contract address |
| `MARKETPLACE_ADDRESS` | Deployed NFTMarketplace contract address |
| `PINATA_API_KEY` | Pinata API key for IPFS uploads |
| `PINATA_SECRET` | Pinata secret key |
| `LLM_PROVIDER` | `openrouter`, `groq`, or `ollama` |

### Optional variables

| Variable | Description |
| :--- | :--- |
| `PRIVATE_KEY_FILE` | Path to a file containing the private key (safer than env var) |
| `IMAGE_PROVIDER` | `stability`, `dalle`, or `procedural` (default) |
| `STABILITY_API_KEY` | Stability AI key (if `IMAGE_PROVIDER=stability`) |
| `OPENAI_API_KEY` | OpenAI key for DALL-E (if `IMAGE_PROVIDER=dalle`) |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `GROQ_API_KEY` | Groq API key |
| `OLLAMA_BASE_URL` | Ollama base URL |
| `X_CONSUMER_KEY` / `X_CONSUMER_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_SECRET` | X (Twitter) credentials |
| `BASESCAN_API_KEY` | For contract verification |

> **Security note:** Never commit `.env` with real values. For production, store the private key in a file with restricted permissions (`chmod 600 keyfile`) and set `PRIVATE_KEY_FILE=/path/to/keyfile`.

## CLI Usage

```bash
# Generate art and upload to IPFS
npm run cli -- generate --generation 1 --theme "neon cyberpunk city"

# Mint an NFT with the returned metadata URI
npm run cli -- mint --metadata-uri QmXyz123abc

# List the minted NFT on the marketplace
npm run cli -- list --token-id 1 --price 0.05

# Watch for sales in real-time (streams JSON until Ctrl+C)
npm run cli -- monitor --from-block 12000000

# Trigger agent evolution after hitting a sales milestone
npm run cli -- evolve --proceeds "0.5" --generation 1 --trigger "Sold 3 NFTs"

# Post a tweet
npm run cli -- tweet --content "New AI art drop incoming! #AIArt #Base"
```

All commands output JSON: look for the final line with `{"status":"success",...}` or `{"status":"error",...}`.

## Typical Workflow

A full autonomous cycle:

1. **Generate** art with a theme → receive metadata URI
2. **Mint** the NFT with that URI → receive token ID
3. **List** the NFT on the marketplace at a price
4. **Tweet** about the new listing
5. **Monitor** sales for purchase events
6. **Evolve** when a sales milestone is reached
7. Repeat from step 1 with the new generation number

## OpenClaw Integration

This skill includes `SKILL.md` with OpenClaw-compatible metadata (`metadata.openclaw`), env vars, and install steps. When used as an OpenClaw skill, agents autonomously run the generate → mint → list → tweet → monitor → evolve cycle.

See `SKILL.md` for detailed tool parameters, error handling, and environment variable reference.

**Common errors:** Missing `.env` variables, insufficient wallet balance, network RPC errors. Ensure `BASE_RPC_URL`, `BASE_PRIVATE_KEY`, contract addresses, and Pinata keys are set.

## Testing

```bash
npm test
```

## Architecture

```
src/
├── cli.ts                  # Entry point for all 6 CLI commands
├── index.ts                # Barrel export for TypeScript imports
└── skills/
    ├── generateArt.ts      # Art generation (procedural + AI providers)
    ├── imageAI.ts          # AI image provider abstraction (Stability, DALL-E)
    ├── evolve.ts           # Evolution state machine with atomic persistence
    ├── mintNFT.ts          # ERC721 minting with retry logic
    ├── listNFT.ts          # Marketplace listing
    ├── monitorSales.ts     # Real-time on-chain sales event listener
    ├── social.ts           # X (Twitter) announcements
    └── llm.ts              # LLM abstraction (OpenRouter / Groq / Ollama)

contracts/
├── NFTArt.sol              # ERC721 contract (OpenZeppelin)
└── NFTMarketplace.sol      # Simple marketplace with listItem/buyItem/cancelListing

scripts/
└── deploy.ts               # Hardhat deployment script
```

## Contributing

Contributions are welcome. Please submit a Pull Request.

## License

MIT — see the LICENSE file for details.

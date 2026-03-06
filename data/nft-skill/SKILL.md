---
name: nft-skill
description: >
  Autonomous AI Artist Agent for generating, evolving, minting, listing, and
  promoting NFT art on the Base blockchain. Use when the user wants to create
  AI art, mint ERC-721 NFTs, list on marketplace, monitor on-chain sales,
  trigger artistic evolution, or announce drops on X/Twitter.
metadata:
  version: 1.1.0
  author: AI Artist
  license: MIT
  openclaw:
    emoji: "🎨"
    homepage: "https://github.com/Numba1ne/nft-skill"
    requires:
      bins:
        - node
        - npm
    env:
      BASE_RPC_URL: "${BASE_RPC_URL}"
      BASE_PRIVATE_KEY: "${BASE_PRIVATE_KEY}"
      NFT_CONTRACT_ADDRESS: "${NFT_CONTRACT_ADDRESS}"
      MARKETPLACE_ADDRESS: "${MARKETPLACE_ADDRESS}"
      PINATA_API_KEY: "${PINATA_API_KEY}"
      PINATA_SECRET: "${PINATA_SECRET}"
      LLM_PROVIDER: "${LLM_PROVIDER}"
      OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}"
      GROQ_API_KEY: "${GROQ_API_KEY}"
      OLLAMA_BASE_URL: "${OLLAMA_BASE_URL}"
      IMAGE_PROVIDER: "${IMAGE_PROVIDER}"
      STABILITY_API_KEY: "${STABILITY_API_KEY}"
      OPENAI_API_KEY: "${OPENAI_API_KEY}"
      X_CONSUMER_KEY: "${X_CONSUMER_KEY}"
      X_CONSUMER_SECRET: "${X_CONSUMER_SECRET}"
      X_ACCESS_TOKEN: "${X_ACCESS_TOKEN}"
      X_ACCESS_SECRET: "${X_ACCESS_SECRET}"
    install:
      - id: npm-install
        kind: shell
        command: "cd {baseDir} && npm install && npm run build"
        bins:
          - node
        label: "Install NFT Skill dependencies"
---

# NFT Skill for OpenClaw

Allows an OpenClaw agent to autonomously generate art, mint NFTs, list on marketplace, monitor sales, evolve based on milestones, and post social updates.

## When to Use This Skill

- User asks to generate AI art or procedural digital art
- User wants to mint an NFT on Base
- User wants to list an NFT for sale on the marketplace
- User wants to monitor on-chain NFT sales
- User wants to evolve art style after a sales milestone
- User wants to tweet or announce a new NFT drop on X (Twitter)
- User mentions "NFT", "mint", "Base blockchain", "AI art", "digital art", or "marketplace listing"

## Setup (First Run)

Before first use, ensure the project is built:

```bash
cd {baseDir} && npm install && npm run build
```

The user must populate a `.env` file with their keys:

```bash
cp {baseDir}/.env.example {baseDir}/.env
```

Required variables: `BASE_RPC_URL`, `BASE_PRIVATE_KEY`, `NFT_CONTRACT_ADDRESS`,
`MARKETPLACE_ADDRESS`, `PINATA_API_KEY`, `PINATA_SECRET`, `LLM_PROVIDER`.

To deploy contracts (one-time setup):

```bash
cd {baseDir} && npm run deploy:testnet   # Base Sepolia testnet
cd {baseDir} && npm run deploy:mainnet   # Base mainnet
```

Contract addresses are automatically written to `.env` after deployment.

## Tools

All tools output JSON. The agent should look for the final line matching `{"status":"success",...}` or `{"status":"error",...}`.

---

### 1. generate — Generate Art

Generate new art and upload to IPFS.

```bash
cd {baseDir} && npm run cli -- generate --generation <number> --theme "<description>"
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-g, --generation` | number | yes | Generation number (determines evolution state) |
| `-t, --theme` | string | yes | Art theme description sent to LLM |

**Output:**
```json
{"status": "success", "result": {"imagePath": "...", "metadata": {...}, "metadataUri": "Qm..."}}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- generate --generation 1 --theme "neon cyberpunk city"
```

---

### 2. mint — Mint NFT

Mint a new ERC721 token on Base with an IPFS metadata URI.

```bash
cd {baseDir} && npm run cli -- mint --metadata-uri <uri>
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-m, --metadata-uri` | string | yes | IPFS metadata URI (e.g. `Qm...` or `ipfs://Qm...`) |

**Output:**
```json
{"status": "success", "result": {"tokenId": "1", "txHash": "0x...", "blockNumber": 12345, "gasUsed": "80000"}}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- mint --metadata-uri QmXyz123abc
```

---

### 3. list — List NFT on Marketplace

List a minted NFT for sale on the marketplace.

```bash
cd {baseDir} && npm run cli -- list --token-id <id> --price <eth>
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-i, --token-id` | string | yes | Token ID to list |
| `-p, --price` | string | yes | Listing price in ETH (e.g. `"0.05"`) |

**Output:**
```json
{"status": "success", "result": {"success": true, "price": "0.05", "txHash": "0x..."}}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- list --token-id 1 --price 0.05
```

---

### 4. monitor — Monitor Sales

Watch for sales events in real-time. Streams JSON to stdout until interrupted (Ctrl+C).

```bash
cd {baseDir} && npm run cli -- monitor [--from-block <number>]
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-f, --from-block` | number | no | Replay missed sales from this block before live monitoring |

**Output (per sale):**
```json
{"status": "sale", "result": {"buyer": "0x...", "tokenId": "1", "price": "0.05", "txHash": "0x...", "blockNumber": 12345}}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- monitor --from-block 12000000
```

---

### 5. evolve — Evolve Agent

Trigger the evolution logic when sales milestones are met.

```bash
cd {baseDir} && npm run cli -- evolve --proceeds <eth> --generation <number> --trigger "<reason>"
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-p, --proceeds` | string | yes | Total ETH proceeds earned so far |
| `-g, --generation` | number | yes | Current generation number |
| `--trigger` | string | yes | Human-readable reason for evolution |

**Output:**
```json
{"status": "success", "result": {"previousGeneration": 1, "newGeneration": 2, "improvements": [...], "newAbilities": [...]}}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- evolve --proceeds "0.5" --generation 1 --trigger "Sold 3 NFTs"
```

---

### 6. tweet — Post to X

Post an update to X (Twitter).

```bash
cd {baseDir} && npm run cli -- tweet --content "<text>"
```

**Parameters:**

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `-c, --content` | string | yes | Tweet text (auto-truncated to 280 chars) |

**Output:**
```json
{"status": "success", "result": "tweet_id_string"}
```

**Example:**
```bash
cd {baseDir} && npm run cli -- tweet --content "New AI art drop incoming! #AIArt #Base"
```

---

## Typical Workflow

A full autonomous cycle the agent should follow:

1. **Generate** art with a theme → receive metadata URI
2. **Mint** the NFT with that URI → receive token ID
3. **List** the NFT on the marketplace at a price
4. **Tweet** about the new listing
5. **Monitor** sales for purchase events
6. **Evolve** when a sales milestone is reached
7. Repeat from step 1 with the new generation number

## Error Handling

- If a command returns `{"status":"error",...}`, read the `message` field and report it to the user.
- Common issues: missing `.env` variables, insufficient wallet balance, network RPC errors.
- For wallet balance issues, suggest the user funds their Base wallet.
- For missing env vars, remind the user to populate `{baseDir}/.env`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_RPC_URL` | yes | Base network RPC endpoint |
| `BASE_PRIVATE_KEY` | yes* | Wallet private key (or use `PRIVATE_KEY_FILE`) |
| `PRIVATE_KEY_FILE` | no | Path to file containing the private key (safer alternative to env var) |
| `NFT_CONTRACT_ADDRESS` | yes | Deployed NFTArt contract address |
| `MARKETPLACE_ADDRESS` | yes | Deployed NFTMarketplace contract address |
| `PINATA_API_KEY` | yes | Pinata IPFS API key |
| `PINATA_SECRET` | yes | Pinata IPFS secret |
| `LLM_PROVIDER` | yes | `openrouter`, `groq`, or `ollama` |
| `LLM_MODEL` | no | Model ID override |
| `OPENROUTER_API_KEY` | if LLM_PROVIDER=openrouter | OpenRouter API key |
| `GROQ_API_KEY` | if LLM_PROVIDER=groq | Groq API key |
| `OLLAMA_BASE_URL` | if LLM_PROVIDER=ollama | Ollama base URL |
| `IMAGE_PROVIDER` | no | `stability`, `dalle`, or `procedural` (default) |
| `IMAGE_MODEL` | no | Image model override |
| `STABILITY_API_KEY` | if IMAGE_PROVIDER=stability | Stability AI key |
| `OPENAI_API_KEY` | if IMAGE_PROVIDER=dalle | OpenAI key for DALL-E |
| `X_CONSUMER_KEY` | for tweet | X API consumer key |
| `X_CONSUMER_SECRET` | for tweet | X API consumer secret |
| `X_ACCESS_TOKEN` | for tweet | X access token |
| `X_ACCESS_SECRET` | for tweet | X access token secret |
| `BASESCAN_API_KEY` | no | For contract verification on Basescan |

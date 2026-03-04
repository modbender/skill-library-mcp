---
name: gizmolab-tools
description: Use GizmoLab's free blockchain developer tools at tools.gizmolab.io and Web3 UI components at ui.gizmolab.io. Ethereum tools include Contract UI interaction, Transaction Decoder, ENS Lookup, and Burner Wallet. Solana tools include Token Creation, Token Minting, Token Snapshots, and Token Swaps. Web3 UI components include Abstract Gasless NFT Mint, Chain Selector, Crypto Product Card, NFT Mint Card, NFT Portfolio, LiFi Widget, and Polymarket Widget. Use when building dApps, interacting with smart contracts, or performing blockchain operations.
---

# GizmoLab Tools & UI

**Tools:** https://tools.gizmolab.io/ - Free blockchain developer tools
**UI Library:** https://ui.gizmolab.io/ - Web3 component library

## Available Tools

### Ethereum Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Contracts UI | `/ethereum/contracts/ui` | Interact with any smart contract (read/write) |
| Transaction Decoder | `/ethereum/converters/transaction-decoder` | Decode raw transaction data |
| ENS Lookup | `/ethereum/ens/lookup` | Resolve ENS names to addresses |
| Burner Wallet | `/ethereum/wallets/burner` | Generate temporary wallets |

### Solana Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Create Token | `/solana/token/create` | Create new SPL tokens |
| Mint Token | `/solana/token/mint` | Mint tokens to addresses |
| Token Snapshot | `/solana/token/snapshot/token` | Snapshot token holders |
| Swap | `/solana/swap` | Swap tokens via Jupiter |

## Usage

All tools are web-based. Use the `browser` tool to interact:

### Example: ENS Lookup

```
1. browser action=open targetUrl="https://tools.gizmolab.io/ethereum/ens/lookup"
2. browser action=snapshot  
3. Find the ENS input field, type the name
4. Click lookup/resolve button
5. browser action=snapshot to see result
```

### Example: Transaction Decoder

```
1. browser action=open targetUrl="https://tools.gizmolab.io/ethereum/converters/transaction-decoder"
2. browser action=snapshot
3. Paste raw transaction hex into input
4. Click decode button
5. browser action=snapshot to see decoded data
```

### Example: Create Solana Token

```
1. browser action=open targetUrl="https://tools.gizmolab.io/solana/token/create"
2. browser action=snapshot
3. Connect wallet when prompted
4. Fill token details (name, symbol, decimals, supply)
5. Click create and confirm transaction
```

## Tool Details

### Contracts UI
- Enter contract address + ABI
- Select network (Mainnet, Goerli, Sepolia, etc.)
- Read contract state or write transactions
- Supports any EVM-compatible contract

### Transaction Decoder
- Input: Raw transaction hex (0x...)
- Output: Decoded function call, parameters, values
- Works with any transaction data

### ENS Lookup
- Forward lookup: ENS name → Ethereum address
- Reverse lookup: Address → ENS name
- Shows resolver, registrant, expiry

### Burner Wallet
- Generates random private key + address
- Use for testing only
- Never use for real funds

### Solana Token Create
- Creates new SPL token
- Set name, symbol, decimals, initial supply
- Upload token image/metadata
- Requires wallet connection (Phantom, Solflare)

### Solana Token Mint
- Mint additional tokens
- Enter token address + amount
- Must be token authority

### Solana Token Snapshot
- Get list of all token holders
- Export as CSV
- Shows balances at current slot

### Solana Swap
- Jupiter-powered swaps
- Best price routing
- Connect wallet to execute

## Networks Supported

**Ethereum:** Mainnet, Goerli, Sepolia, Base, Polygon, Arbitrum, Optimism, Avalanche, BNB Chain

**Solana:** Mainnet, Devnet

## Tips

- For contract interactions, have the ABI ready (get from Etherscan)
- Transaction decoder works offline - no network needed
- Burner wallets are ephemeral - save keys if needed
- Solana tools require a connected wallet (Phantom recommended)

---

# GizmoLab UI - Web3 Component Library

Full-stack Web3 components for building dApps at https://ui.gizmolab.io/

## Available Components

| Component | URL | Purpose |
|-----------|-----|---------|
| Abstract Gasless NFT Mint | `/components/abstract-gasless-nft-mint` | Mint NFTs without gas fees using account abstraction |
| Abstract Sign In | `/components/abstract-sign-in` | Sign in with Abstract Global Wallet |
| Chain Selector | `/components/chain-selector` | Header popover to switch blockchain networks |
| Crypto Product Card | `/components/crypto-product-card` | Pay-with-crypto or custom ERC20 product card |
| NFT Mint Card | `/components/nft-mint-card` | Mint NFTs with smart contract integration |
| NFT Portfolio | `/components/nft-portfolio` | Dashboard to view NFT holdings |
| LiFi Widget | `/components/lifi-widget` | Cross-chain bridging and swapping |
| Polymarket Widget | `/components/polymarket-widget` | Prediction market trading widget |

## Installation Guides

Available at https://ui.gizmolab.io/docs/:

- **Install Abstract Global Wallet** - Account abstraction setup
- **Install Next.js 14** - Next.js project setup
- **Install Dynamic** - Dynamic wallet integration
- **Install Shadcn UI** - Shadcn UI setup
- **Deploy EVM Contract** - Smart contract deployment

## Using Components

### 1. Browse Components

```
browser action=open targetUrl="https://ui.gizmolab.io/components"
browser action=snapshot
```

### 2. View Component Details

Each component page includes:
- Live preview/demo
- Installation instructions
- Code snippets (copy-paste ready)
- Props/configuration options

### 3. Example: Add NFT Mint Card

```
1. Go to /components/nft-mint-card
2. Copy the installation command
3. Copy the component code
4. Configure with your contract address
5. Import and use in your dApp
```

## Tech Stack

Components are built with:
- **React / Next.js 14**
- **Shadcn UI** (Tailwind-based)
- **Wagmi / Viem** (Ethereum)
- **Account Abstraction** support

## Playground

Test components live at https://ui.gizmolab.io/playground

## Custom Development

For custom Web3 components or dApp development:
- Book a call: https://calendly.com/gizmolab/30min
- Contact: https://gizmolab.io/contact

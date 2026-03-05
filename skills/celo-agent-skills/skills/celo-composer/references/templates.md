# Celo Composer Templates

## Basic Template

Standard Next.js 14+ dApp for general web3 applications.

### Create

```bash
npx @celo/celo-composer@latest create my-app --template basic
```

### Features

- Next.js 14+ with App Router
- Tailwind CSS styling
- shadcn/ui components
- Wallet connection (RainbowKit or thirdweb)
- Celo network configuration
- TypeScript

### Best For

- General dApps
- DeFi applications
- NFT platforms
- DAO interfaces

## MiniPay Template

Mobile-first template optimized for MiniPay wallet integration.

### Create

```bash
npx @celo/celo-composer@latest create my-app --template minipay
```

### Features

- Mobile-first responsive design
- MiniPay wallet detection
- Auto-connect when in MiniPay
- Lightweight bundle
- viem for transactions

### Best For

- MiniPay Mini Apps
- Payment applications
- Mobile-first dApps
- Emerging market apps

### MiniPay-Specific Code

```tsx
// Included in template
const isMiniPay = window.ethereum?.isMiniPay;

// Auto-connect in MiniPay
useEffect(() => {
  if (isMiniPay) {
    connectWallet();
  }
}, []);
```

## Farcaster Miniapp Template

Template for building Farcaster frames and miniapps.

### Create

```bash
npx @celo/celo-composer@latest create my-app --template farcaster-miniapp
```

### Features

- Farcaster SDK integration
- Frame support
- Farcaster auth
- Cast actions

### Best For

- Farcaster frames
- Social dApps
- Farcaster integrations

## AI Chat Template

Standalone chat application with AI integration.

### Create

```bash
npx @celo/celo-composer@latest create my-app --template ai-chat
```

### Features

- Chat UI components
- AI model integration hooks
- Message history
- Streaming responses

### Best For

- AI-powered dApps
- Chat applications
- AI agents

## Wallet Provider Options

### RainbowKit (Default)

```bash
npx @celo/celo-composer@latest create my-app --wallet-provider rainbowkit
```

Popular, well-designed wallet modal with support for many wallets.

### thirdweb

```bash
npx @celo/celo-composer@latest create my-app --wallet-provider thirdweb
```

thirdweb Connect SDK with embedded wallet support.

### None

```bash
npx @celo/celo-composer@latest create my-app --wallet-provider none
```

No wallet provider - add your own or use for MiniPay-only apps.

## Contract Options

### Hardhat

```bash
npx @celo/celo-composer@latest create my-app --contracts hardhat
```

Includes Hardhat setup with Celo network configuration.

### Foundry

```bash
npx @celo/celo-composer@latest create my-app --contracts foundry
```

Includes Foundry setup with Celo network configuration.

### None

```bash
npx @celo/celo-composer@latest create my-app --contracts none
```

Frontend only, no smart contract development environment.

## Common Combinations

### Full-Stack MiniPay App

```bash
npx @celo/celo-composer@latest create my-app \
  --template minipay \
  --wallet-provider none \
  --contracts hardhat
```

### Basic dApp with RainbowKit

```bash
npx @celo/celo-composer@latest create my-app \
  --template basic \
  --wallet-provider rainbowkit \
  --contracts hardhat
```

### Frontend Only

```bash
npx @celo/celo-composer@latest create my-app \
  --template basic \
  --wallet-provider rainbowkit \
  --contracts none
```

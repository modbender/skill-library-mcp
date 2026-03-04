---
name: bridging
description: Bridge assets to and from Celo. Use when transferring tokens between Celo and other chains like Ethereum.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Bridging to Celo

This skill covers bridging assets between Celo and other blockchains, including native bridges and third-party solutions.

## When to Use

- Transferring assets from Ethereum to Celo
- Bridging tokens from Celo to other chains
- Integrating cross-chain functionality
- Building multi-chain applications

## Bridge Options

### Native Bridge

| Bridge | Mainnet | Testnet |
|--------|---------|---------|
| Superbridge | https://superbridge.app/celo | https://testnets.superbridge.app |

Native bridge provides direct transfers between Celo L2 and Ethereum L1 via the OP Stack standard bridge.

Source: https://docs.celo.org/tooling/bridges

### Third-Party Bridges

| Bridge | URL | Description |
|--------|-----|-------------|
| Squid Router V2 | https://v2.app.squidrouter.com | Cross-chain routing via Axelar |
| LayerZero | https://layerzero.network | Omnichain interoperability protocol |
| Jumper Exchange | https://jumper.exchange | Multi-chain DEX aggregator |
| Portal (Wormhole) | https://portalbridge.com | Decentralized interoperability layer |
| AllBridge | https://app.allbridge.io/bridge | EVM and non-EVM chains |
| Satellite (Axelar) | https://satellite.money | Axelar network bridge |
| Transporter (CCIP) | https://www.transporter.io | Chainlink CCIP bridge |
| Layerswap | https://layerswap.io/app | 60+ chains, 15+ CEX integrations |
| Hyperlane Nexus | https://www.usenexus.org | Messaging and interoperability |
| Mach Exchange | https://www.mach.exchange | Cross-chain exchange |
| Galaxy | https://galaxy.exchange/swap | Native DEX on Celo |
| SmolRefuel | https://smolrefuel.com | Gasless refueling |
| USDT0 | https://usdt0.to | Native USDT via LayerZero OFT |

Source: https://docs.celo.org/home/bridged-tokens/bridges

## Native ETH Bridging

Bridge native ETH from Ethereum to Celo as WETH.

### Contract Addresses

**Ethereum Mainnet → Celo:**

| Contract | Address |
|----------|---------|
| SuperBridgeETHWrapper (L1) | 0x3bC7C4f8Afe7C8d514c9d4a3A42fb8176BE33c1e |
| L1 Standard Bridge | 0x9C4955b92F34148dbcfDCD82e9c9eCe5CF2badfe |
| L1 WETH | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 |
| L2 WETH (Celo) | 0xD221812de1BD094f35587EE8E174B07B6167D9Af |

**Sepolia Testnet → Celo Sepolia:**

| Contract | Address |
|----------|---------|
| SuperBridgeETHWrapper (L1) | 0x523e358dFd0c4e98F3401DAc7b1879445d377e37 |
| L1 Standard Bridge | 0xec18a3c30131a0db4246e785355fbc16e2eaf408 |
| L1 WETH | 0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9 |
| L2 WETH (Celo Sepolia) | 0x2cE73DC897A3E10b3FF3F86470847c36ddB735cf |

### Bridge ETH to Celo

```typescript
import { createWalletClient, custom, parseEther } from "viem";
import { mainnet } from "viem/chains";

const SUPERBRIDGE_WRAPPER = "0x3bC7C4f8Afe7C8d514c9d4a3A42fb8176BE33c1e";

const WRAPPER_ABI = [
  {
    name: "wrapAndBridge",
    type: "function",
    stateMutability: "payable",
    inputs: [
      { name: "_minGasLimit", type: "uint32" },
      { name: "_extraData", type: "bytes" },
    ],
    outputs: [],
  },
] as const;

async function bridgeETHToCelo(amount: string): Promise<string> {
  const walletClient = createWalletClient({
    chain: mainnet,
    transport: custom(window.ethereum),
  });

  const [address] = await walletClient.getAddresses();

  const hash = await walletClient.writeContract({
    address: SUPERBRIDGE_WRAPPER,
    abi: WRAPPER_ABI,
    functionName: "wrapAndBridge",
    args: [200000, "0x"],
    value: parseEther(amount),
  });

  return hash;
}
```

## Natively Bridged Tokens

These tokens have official bridges from Ethereum via native bridge:

| Token | L1 Address (Ethereum) | L2 Address (Celo) |
|-------|----------------------|-------------------|
| WETH | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 | 0xD221812de1BD094f35587EE8E174B07B6167D9Af |
| WBTC | 0x2260fac5e5542a773aa44fbcfedf7c193bc2c599 | 0x8aC2901Dd8A1F17a1A4768A6bA4C3751e3995B2D |
| DAI | 0x6B175474E89094C44Da98b954EedeAC495271d0F | 0xac177de2439bd0c7659c61f373dbf247d1f41abe |
| AAVE | 0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9 | 0xF6A54aff8c97f7AF3CC86dbaeE88aF6a7AaB6288 |
| LINK | 0x514910771af9ca656af840dff83e8264ecf986ca | 0xf630876008a4ed9249fb4cac978ba16827f52e91 |
| UNI | 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984 | 0xeE571697998ec64e32B57D754D700c4dda2f2a0e |
| CRV | 0xD533a949740bb3306d119CC777fa900bA034cd52 | 0x75184c282e55a7393053f0b8F4F3E7BeAE067fdC |
| rETH | 0xae78736cd615f374d3085123a210448e74fc6393 | 0x55f3d16e6bd2b8b8e6599df6ef4593ce9dcae9ed |

Source: https://docs.celo.org/home/bridged-tokens

## Cross-Chain Messaging Protocols

For building cross-chain dApps:

| Protocol | URL | Celo Support |
|----------|-----|--------------|
| Chainlink CCIP | https://chain.link/cross-chain | Mainnet |
| Hyperlane | https://www.hyperlane.xyz | Mainnet, Sepolia |
| Wormhole | https://wormhole.com | Mainnet |
| LayerZero | https://layerzero.network | Mainnet |
| Axelar Network | https://axelar.network | Mainnet |

Source: https://docs.celo.org/tooling/bridges/cross-chain-messaging

## Using LI.FI SDK

For cross-chain swaps and bridges:

```typescript
import { createConfig, getQuote, executeRoute } from "@lifi/sdk";

// Initialize LI.FI
createConfig({
  integrator: "your-app-name",
});

// Get bridge quote
const quote = await getQuote({
  fromChain: 1, // Ethereum
  toChain: 42220, // Celo
  fromToken: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", // USDC on Ethereum
  toToken: "0xcebA9300f2b948710d2653dD7B07f33A8B32118C", // USDC on Celo
  fromAmount: "1000000000", // 1000 USDC (6 decimals)
  fromAddress: userAddress,
});

// Execute the bridge
const result = await executeRoute(quote, {
  updateRouteHook: (route) => {
    console.log("Route updated:", route);
  },
});
```

## Bridge Considerations

### Security
- Native bridges (Superbridge) are the most secure
- Third-party bridges rely on their own security models
- Always verify contract addresses before bridging

### Timing
- Native L1→L2 bridges: ~15-20 minutes
- L2→L1 withdrawals: 7 days (challenge period)
- Third-party bridges: varies (minutes to hours)

### Fees
- Native bridges: gas fees only
- Third-party bridges: gas + bridge fees

## Dependencies

```json
{
  "dependencies": {
    "viem": "^2.0.0"
  }
}
```

For LI.FI integration:

```json
{
  "dependencies": {
    "@lifi/sdk": "^3.0.0"
  }
}
```

## Additional Resources

- [bridge-contracts.md](references/bridge-contracts.md) - All bridge contract addresses
- [bridged-tokens.md](references/bridged-tokens.md) - Complete list of bridged tokens

# Supported Chains Reference

Complete reference for all 24 chains supported by Tator and 63 chains supported by Quick Intel.

## Tator Trading Chains (24)

| Chain | Chain ID | Native Token |
|-------|----------|--------------|
| ethereum | 1 | ETH |
| base | 8453 | ETH |
| arbitrum | 42161 | ETH |
| optimism | 10 | ETH |
| polygon | 137 | MATIC |
| avalanche | 43114 | AVAX |
| bsc | 56 | BNB |
| linea | 59144 | ETH |
| sonic | 146 | S |
| berachain | 80094 | BERA |
| abstract | 2741 | ETH |
| unichain | 130 | ETH |
| ink | 57073 | ETH |
| soneium | 1868 | ETH |
| ronin | 2020 | RON |
| worldchain | 480 | ETH |
| sei | 1329 | SEI |
| hyperevm | 999 | HYPE |
| katana | 747474 | ETH |
| somnia | 5031 | SOMI |
| plasma | 9745 | ETH |
| monad | 143 | MON |
| megaeth | 4326 | ETH |
| solana | — | SOL |

Use exact chain names as shown in prompts (e.g., `"base"` not `"Base"`, `"bsc"` not `"binance"`).

## x402 Payment Networks (14)

These chains accept USDC/USDM for x402 API payments ($0.20 per Tator request, $0.03 per QI scan). Base is recommended for lowest fees.

| Network | CAIP-2 ID | Token | Address |
|---------|-----------|-------|---------|
| Base | `eip155:8453` | USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Ethereum | `eip155:1` | USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Arbitrum | `eip155:42161` | USDC | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Optimism | `eip155:10` | USDC | `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85` |
| Polygon | `eip155:137` | USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Avalanche | `eip155:43114` | USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |
| Unichain | `eip155:130` | USDC | `0x078D782b760474a361dDA0AF3839290b0EF57AD6` |
| Linea | `eip155:59144` | USDC | `0x176211869cA2b568f2A7D4EE941E073a821EE1ff` |
| Sonic | `eip155:146` | USDC | `0x29219dd400f2Bf60E5a23d13Be72B486D4038894` |
| HyperEVM | `eip155:999` | USDC | `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| Ink | `eip155:57073` | USDC | `0x2D270e6886d130D724215A266106e6832161EAEd` |
| Monad | `eip155:143` | USDC | `0x754704Bc059F8C67012fEd69BC8a327a5aafb603` |
| MegaETH | `eip155:6342` | USDM | `0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7` |
| Solana | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | USDC | Native USDC SPL |

## Quick Intel Scan Chains (63)

Quick Intel supports security scanning on these chains. Use exact names as shown in the `chain` field:

**EVM:** eth, base, arbitrum, optimism, polygon, bsc, avalanche, fantom, linea, scroll, zksync, blast, mantle, mode, zora, manta, sonic, berachain, unichain, abstract, monad, megaeth, hyperevm, shibarium, pulse, core, opbnb, polygonzkevm, metis, kava, klaytn, astar, oasis, iotex, conflux, canto, velas, grove, lightlink, bitrock, loop, besc, energi, maxx, degen, inevm, viction, nahmii, real, xlayer, worldchain, apechain, morph, ink, soneium, plasma

**Non-EVM:** solana, sui, radix, tron, injective

## Chain-Specific Notes

### Base (Chain ID: 8453)
- Default payment chain for x402 (lowest fees)
- Supports: Clanker token launching, Flaunch token launching, Basenames registration, Avantis perps
- Fast finality (~2 seconds)

### Solana
- Non-EVM — Base58 address format, different transaction structure
- Supports: Pump.fun token launching, SPL token swaps
- x402 payment uses SPL TransferChecked with gateway as feePayer

### Arbitrum (Chain ID: 42161)
- Highest DeFi liquidity among L2s
- Full Aave, Compound support
- 250ms block times

### HyperEVM (Chain ID: 999)
- Hyperliquid's EVM chain
- HYPE as native token
- x402 payment supported via USDC

### Monad (Chain ID: 143)
- High-performance EVM chain
- MON as native token
- x402 payment supported via USDC

### Sonic (Chain ID: 146)
- Fantom successor chain
- S as native token
- x402 payment supported via USDC

### MegaETH (Chain ID: 4326)
- Supports .mega name registration
- Uses USDM (not USDC) for x402 payments
- Emerging L2 with fast finality

### Somnia (Chain ID: 5031)
- Supports .somi name registration
- Gaming-focused L2

### Berachain (Chain ID: 80094)
- BERA as native token
- Proof of Liquidity consensus

## Bridge Protocol Support

Tator uses these bridges for cross-chain transfers:

| Protocol | Typical Time | Notes |
|----------|-------------|-------|
| Relay | 30s - 2 min | Fastest for most routes |
| LiFi | 1 - 15 min | Multi-protocol aggregator |
| GasZip | 1 - 5 min | Gas-efficient bridging |
| deBridge | 5 - 30 min | Deep liquidity routes |

## Yield Protocol Availability

| Protocol | Available Chains |
|----------|-----------------|
| Aave V3 | Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche |
| Morpho | Ethereum, Base |
| Compound V3 | Ethereum, Base, Arbitrum, Polygon |
| Yearn V3 | Ethereum |

## Perpetuals Availability

| Protocol | Chain | Assets |
|----------|-------|--------|
| Avantis | Base | ETH, BTC, SOL, and more |

## Prediction Markets

| Protocol | Chain | Market Types |
|----------|-------|--------------|
| Myriad | Multiple | Crypto, sports, politics |

## Token Launching

| Platform | Chains | Example |
|----------|--------|---------|
| Clanker | Base, Ethereum, Arbitrum, Unichain | "Launch MYTOKEN with symbol MTK on Clanker" |
| Flaunch | Base | "Launch MYTOKEN on Flaunch" |
| Pump.fun | Solana | "Launch MEME token on pump.fun" |

## Name Registration

| Service | Chain | Example |
|---------|-------|---------|
| Basenames | Base | "Register myname.base" |
| MegaETH Names | MegaETH | "Register myname.mega" |
| Somnia Names | Somnia | "Register myname.somi" |
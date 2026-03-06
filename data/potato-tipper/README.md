# Potato Tipper - OpenClaw Skill

An OpenClaw skill for AI agents to work with the **Potato Tipper** protocol — an LSP1 Universal Receiver Delegate on LUKSO that automatically tips $POTATO tokens to new followers.

## Source Repository

> See the [**Potato Tipper contracts** on GitHub](https://github.com/CJ42/potato-tipper-contracts)

## How It Works

When someone follows a Universal Profile that has Potato Tipper installed, the follow event triggers an LSP1 notification which automatically sends $POTATO tokens from the followed user's UP to the new follower's UP. Think of it as an on-chain "welcome gift" for new followers.

```
User B follows User A (LSP26)
    → LSP1 notification hits User A's UP
    → PotatoTipper delegate activates
    → $POTATO tokens sent from User A → User B
```

## Key Concepts

- **LSP1 Universal Receiver Delegate** - Reacts to incoming LSP26 follow/unfollow events
- **LSP7 $POTATO Token** - Fungible token used for tipping
- **LSP26 Follower Registry** - On-chain social graph that triggers the tip flow
- **ERC725Y Config** - Per-user tip settings stored as data keys on their UP

## Deployed Contracts

| Contract | LUKSO Mainnet | LUKSO Testnet |
|----------|--------------|---------------|
| PotatoTipper | `0x5eed04004c2D46C12Fe30C639A90AD5d6F5D573d` | `0xB844b12313A2D702203109E9487C24aE807e1d66` |
| $POTATO Token | `0x80D898C5A3A0B118a0c8C8aDcdBB260FC687F1ce` | `0xE8280e7f0d54daE39725dC5f500F567Af2854A13` |

## Skill Structure

```
potato-tipper/
├── SKILL.md                # Main skill instructions
├── README.md               # This file
├── references/
│   ├── repo-overview.md            # File map + contract responsibilities
│   ├── addresses.md                # Deployed addresses (Mainnet + Testnet)
│   ├── config-and-data-keys.md     # ERC725Y config keys + encoding
│   ├── permissions.md              # Required LSP6 permissions
│   ├── typescript-examples.md      # wagmi, viem, ethers + erc725.js code
│   ├── solidity-examples.md        # Solidity integration examples
│   ├── learn-notes.md              # Design patterns (Tip-on-Follow)
│   ├── innovative-integrations.md  # Expansion ideas (NFT badges, tiered rewards)
│   ├── event-flow.md               # Follow → tip event order (debug)
│   ├── foundry-batch-setup.md      # One-click setup / batching
│   └── security-and-limitations.md # Known limitations + security
├── scripts/
│   └── setup_potato_tipper.sh      # One-click UP setup (clones repo + runs Foundry script)
└── assets/abis/
    ├── UniversalProfile.abi.json
    ├── LSP7DigitalAsset.abi.json
    ├── PotatoTipper.abi.json
    └── KeyManager.abi.json
```

## Quick Start

### Configure Potato Tipper on a Universal Profile (One-Click)

```bash
TIP_AMOUNT=42000000000000000000 \
MIN_FOLLOWERS=5 \
MIN_POTATO_BALANCE=100000000000000000000 \
TIPPING_BUDGET=1000000000000000000000 \
PRIVATE_KEY=0x... \
./skills/potato-tipper/scripts/setup_potato_tipper.sh luksoTestnet 0xYourUPAddress
```

You can adjust the parameters accordingly

## Requirements

- Foundry (forge, cast) for testing and deployment
- Universal Profile on LUKSO with a controller that has `ADDUNIVERSALRECEIVERDELEGATE` permission
- $POTATO tokens for tipping (free mint available on Testnet via Blockscout)

## License

Apache 2.0

# Hypha Network Reference

## Chain: Base L2

| Network | RPC | Chain ID |
|---------|-----|----------|
| Mainnet | https://mainnet.base.org | 8453 |
| Sepolia | https://sepolia.base.org | 84532 |

## Contract Addresses

### Testnet (Base Sepolia)
- **Escrow**: `0x7bBf8A3062a8392B3611725c8D983d628bA11E6F`
- **USDT**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`

### Mainnet (Base)
- TBD — testnet only for now

## Protocol Fee
- **Rate**: 0.5% (50 basis points)
- **Foundation Wallet**: `0x5C8827E46E27a188dbcA9B100f72bf48f01dfA2E`
- **Applied to**: All `Wallet.send_payment()` calls (can be disabled with `include_fee=False`)

## Bootstrap Nodes

| Name | Host | Port |
|------|------|------|
| Groot (Foundation) | localhost | 8468 |

> Bootstrap nodes are currently local-only. Public endpoints coming soon.

## DHT Configuration
- **Protocol**: Kademlia
- **Default Port**: 8468
- **Discovery Topic**: `hypha-agents`
- **Key Format**: `hypha:{topic}` → JSON array of agent info dicts

## Identity (One Seed)

A single 32-byte seed derives:
1. **P2P Node ID** — Ed25519 public key (via `SHA256(seed + "hypha.p2p")`)
2. **DHT Location** — First 20 bytes of node ID
3. **EVM Wallet** — secp256k1 private key (via `SHA256(seed + "hypha.wallet")`)

Use `SeedManager.from_string("your-seed")` to derive all three from a human-readable phrase.

## SDK Install

```bash
pip install hypha-sdk
```

Current version: **0.2.0**

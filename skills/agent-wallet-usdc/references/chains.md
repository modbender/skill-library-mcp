# Chain Reference

## Supported Chains

| Chain | Network | Native Token | USDC Support |
|-------|---------|--------------|--------------|
| Solana | Mainnet/Devnet | SOL | ✅ |
| Base | Mainnet/Sepolia | ETH | ✅ |
| Ethereum | Mainnet/Sepolia | ETH | ✅ |

## USDC Contract Addresses

### Mainnet

| Chain | USDC Address | Decimals |
|-------|--------------|----------|
| Solana | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 |
| Base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | 6 |
| Ethereum | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | 6 |

### Testnet

| Chain | Network | USDC Address | Decimals |
|-------|---------|--------------|----------|
| Solana | Devnet | `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU` | 6 |
| Base | Sepolia | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | 6 |
| Ethereum | Sepolia | `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` | 6 |

## RPC Endpoints

### Default Public RPCs

| Chain | Mainnet | Testnet |
|-------|---------|---------|
| Solana | `https://api.mainnet-beta.solana.com` | `https://api.devnet.solana.com` |
| Base | `https://mainnet.base.org` | `https://sepolia.base.org` |
| Ethereum | `https://eth.llamarpc.com` | `https://rpc.sepolia.org` |

### Recommended Premium RPCs

For production use, consider:
- **Solana**: Helius, QuickNode, Triton
- **Base/Ethereum**: Alchemy, Infura, QuickNode

## Derivation Paths

### Solana
```
Path: m/44'/501'/0'/0'
Standard: Solana (Phantom, Solflare compatible)
Key type: Ed25519
```

### EVM (Base, Ethereum)
```
Path: m/44'/60'/0'/0/0
Standard: BIP-44 Ethereum
Key type: secp256k1
```

Note: All EVM chains derive the **same address** from the same seed (shared derivation path).

## Gas Estimates

### Solana
- SOL transfer: ~5,000 lamports (~0.000005 SOL)
- USDC transfer: ~5,000 lamports + rent if new ATA

### Base
- ETH transfer: ~21,000 gas (~0.00005 ETH at 2 gwei)
- USDC transfer: ~65,000 gas (~0.00013 ETH at 2 gwei)

### Ethereum
- ETH transfer: ~21,000 gas (~0.0004 ETH at 20 gwei)
- USDC transfer: ~65,000 gas (~0.0013 ETH at 20 gwei)

## Address Formats

| Chain | Format | Example |
|-------|--------|---------|
| Solana | Base58 (32-44 chars) | `7xK9fR2nQp...mP4q` |
| EVM | Hex with 0x prefix (42 chars) | `0x7a3B9c1D...4f2E` |

## Validation Patterns

```javascript
// Solana address
/^[1-9A-HJ-NP-Za-km-z]{32,44}$/

// EVM address
/^0x[a-fA-F0-9]{40}$/
```

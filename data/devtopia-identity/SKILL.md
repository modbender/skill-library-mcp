---
name: devtopia-identity
description: Manage wallet-backed on-chain agent identity with Devtopia ID. Use when registering agent identity on Base chain, checking identity status, generating challenge proofs for authentication, managing local wallets, or coordinating verified agent interactions. Supports agent registration, wallet import/export, identity verification, and blockchain-based identity attestations.
---

# Devtopia Identity

Devtopia ID is a Base-linked wallet-backed identity system for AI agents. It enables cryptographic proof of agent ownership, challenge-response authentication, and on-chain identity registration.

## Quick Start

### Register Your Agent

```bash
devtopia id register "YourAgentName"
```

This will:
1. Create or load a local wallet (if one doesn't exist)
2. Generate your public/private key pair (ECDSA P-256)
3. Sign the identity registration transaction
4. Mint your identity on Base chain (Chain ID 8453)
5. Store your encrypted keystore locally at `~/.devtopia/identity-keystore.json`

**Output:**
```
Registered Devtopia ID #<agent-id>
Name: YourAgentName
Wallet: 0x<your-wallet-address>
Status: verified
Chain: Base (8453)
Tx: 0x<transaction-hash>
BaseScan: https://basescan.org/tx/0x<transaction-hash>
```

### Check Your Identity

```bash
devtopia id status
```

Shows: Agent ID, name, wallet address, registration transaction, verification status.

### Prove Wallet Ownership

```bash
devtopia id prove --challenge "some-challenge-text"
```

Generates a cryptographic proof that you control the private key without revealing it. Use for:
- Cross-agent authentication
- Marketplace transaction verification
- Challenge-response proof-of-ownership flows

### Manage Your Wallet

#### Export Your Wallet Address
```bash
devtopia id wallet export-address
```

#### Import a Different Wallet
```bash
devtopia id wallet import <privateKeyOrKeystore>
```

Accepts:
- PEM-formatted private key: `-----BEGIN PRIVATE KEY-----...-----END PRIVATE KEY-----`
- JSON keystore: `{"algorithm":"aes-256-gcm",...}`

---

## Advanced Usage

### Challenge-Response Proofs

Generate a signed proof for a given challenge string:

```bash
devtopia id prove --challenge "verify-agent-2-2026-02-16"
```

This creates a verifiable proof that:
- You control the private key for your wallet
- You signed the specific challenge text
- Proof is timestamped and cannot be replayed

Perfect for:
- Agent-to-agent authentication
- Marketplace API signing
- Smart contract interactions

See `references/challenge-proofs.md` for advanced authentication patterns.

### Wallet Backup & Recovery

Your keystore is automatically saved to `~/.devtopia/identity-keystore.json` (encrypted AES-256-GCM).

**Backup your keystore:**
```bash
cp ~/.devtopia/identity-keystore.json ~/backup/identity-keystore.json
```

**Restore from backup:**
```bash
devtopia id wallet import ~/backup/identity-keystore.json
```

### View Your Local Wallet

```bash
devtopia id whoami
```

Shows:
- Identity server URL
- Keystore location
- Wallet address (masked)
- Agent ID
- Verification status
- Registration transaction link

---

## Cryptographic Details

### Key Generation
- **Algorithm:** ECDSA P-256 (secp256r1)
- **Key Size:** 256-bit
- **Format:** PEM (PKCS#8)

### Encryption
- **Cipher:** AES-256-GCM (authenticated encryption)
- **IV Size:** 96 bits
- **Auth Tag:** 128 bits (GCM mode guarantees authenticity + confidentiality)

### Signature
- **Type:** ECDSA P-256 (secp256r1)
- **Use Case:** Challenge-response proofs, transaction signing

---

## Integration Patterns

### Pattern 1: Agent Registration Flow

```bash
# 1. Register your agent
devtopia id register "MyAgent"

# 2. Check status
devtopia id status

# 3. Use your Agent ID in marketplace operations
devtopia market register "MyAgent"  # Uses your on-chain identity
```

### Pattern 2: Authentication & Coordination

```bash
# 1. Get your wallet address
AGENT_WALLET=$(devtopia id wallet export-address)

# 2. Generate a proof for authentication
devtopia id prove --challenge "coordinate-task-12345"

# 3. Share the proof with other agents (verifiable proof of identity)
# Other agents can verify the signature against your public key
```

### Pattern 3: Wallet Recovery

```bash
# If you lose ~/.devtopia/identity-keystore.json:
# 1. Find your backup
ls ~/backup/identity-keystore.json

# 2. Import it
devtopia id wallet import ~/backup/identity-keystore.json

# 3. Verify identity is restored
devtopia id status
```

---

## Security Considerations

✅ **Best Practices:**
- Your private key is **never exported in plaintext**
- Keys are encrypted at rest (AES-256-GCM)
- Decryption happens in-memory only during signing operations
- No servers hold your private key
- On-chain registration creates a permanent, verifiable record

⚠️ **Threats to Protect Against:**
- **Keystore theft:** Back up to encrypted storage
- **Keystore corruption:** Test imports before deleting originals
- **Challenge replay:** Each proof includes a unique challenge string (not replayable)
- **Key leakage:** Never share your keystore file

---

## Troubleshooting

### "Keystore not found"
```bash
# Check if it exists:
ls -la ~/.devtopia/identity-keystore.json

# If missing, restore from backup:
devtopia id wallet import <backup-file>

# If no backup exists, re-register:
devtopia id register "YourAgentName"  # Creates new identity
```

### "Identity not verified"
```bash
# Check status:
devtopia id status

# If TX failed, re-register with a unique name:
devtopia id register "YourAgentName-$(date +%s)"
```

### "Challenge proof failed"
```bash
# Verify your wallet is correct:
devtopia id whoami

# Try the proof again:
devtopia id prove --challenge "test-challenge"

# If still failing, reimport your keystore:
devtopia id wallet import ~/.devtopia/identity-keystore.json
```

---

## References

- [Devtopia Docs](https://devtopia.net/docs)
- [Base Chain Docs](https://docs.base.org)
- [ECDSA P-256 (secp256r1)](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [AES-256-GCM](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
- [Challenge-Response Authentication](https://en.wikipedia.org/wiki/Challenge%E2%80%93response_authentication)

---
name: ceaser
description: Interact with the Ceaser privacy protocol on Base L2 using the ceaser-mcp MCP tools. This skill uses the ceaser-mcp npm package for ALL operations -- shield, unshield, note management, and protocol queries. All ceaser tool calls use CLI subcommands (npx -y ceaser-mcp <subcommand>). Ceaser is a privacy-preserving ETH wrapper using Noir/UltraHonk zero-knowledge proofs on Base L2 (chain ID 8453).
user-invocable: true
allowed-tools: Bash
homepage: https://ceaser.org
metadata: { "openclaw": { "requires": { "bins": ["curl", "jq", "node", "npx"] }, "homepage": "https://ceaser.org" } }
---

# Ceaser Privacy Protocol

You are a skill that interacts with the Ceaser privacy protocol on Base L2 (chain ID 8453). Ceaser lets users shield (deposit) ETH into a privacy pool and unshield (withdraw) to any address, using zero-knowledge proofs. No trusted setup -- the protocol uses Noir circuits compiled to UltraHonk proofs.

This skill uses the `ceaser-mcp` npm package for shield, unshield, and note management operations. All ceaser tool calls use CLI subcommands:

```bash
npx -y ceaser-mcp <subcommand> [args]
```

Alternatively, if `mcporter` is installed with the ceaser MCP server configured (see `{baseDir}/mcporter.json`), you may use `mcporter call ceaser.TOOL_NAME` as an equivalent method. CLI is the primary and recommended approach.

**Base URL:** `https://ceaser.org`
**Network:** Base L2 (chain ID 8453)
**Contract:** `0x278652aA8383cBa29b68165926d0534e52BcD368`
**Facilitator:** `https://ceaser.org`
**Protocol Fee:** 0.25% (25 bps) per operation
**Valid Denominations:** 0.001, 0.01, 0.1, 1, 10, 100 ETH
**Proof System:** Noir circuits compiled to UltraHonk proofs (no trusted setup)

All REST endpoints below are public and require no authentication. Rate limits: 60 req/min (read), 5 req/min (write) per IP.

For a complete OpenAPI 3.0 specification, see `{baseDir}/references/openapi.json`.

---

## Read-Only Queries

### List valid denominations with fee breakdown

Shows what amounts users can shield/unshield and the exact costs (0.25% protocol fee).

```bash
curl -s "https://ceaser.org/api/ceaser/denominations" | jq .
```

Valid denominations: 0.001, 0.01, 0.1, 1, 10, 100 ETH.

### Calculate fee breakdown for a specific amount

```bash
curl -s "https://ceaser.org/api/ceaser/fees/100000000000000000" | jq .
```

The amount parameter is in wei. 100000000000000000 = 0.1 ETH. Response includes protocolFee (0.25%), treasuryShare (0.24%), relayerAlloc (0.01%), and netAmount.

### Get pool statistics

```bash
curl -s "https://ceaser.org/api/ceaser/pool/0" | jq .
```

Asset ID 0 = ETH. Returns totalLocked (TVL in wei), totalLockedFormatted (human readable), totalNotes, and feeBps.

### Get current Merkle root

```bash
curl -s "https://ceaser.org/api/ceaser/merkle-root" | jq .
```

Returns the 24-level Poseidon Merkle tree root. The `source` field indicates whether it came from the local indexer (instant) or fell back to an on-chain query.

### Check if a nullifier has been spent

```bash
curl -s "https://ceaser.org/api/ceaser/nullifier/0x0000000000000000000000000000000000000000000000000000000000000001" | jq .
```

Replace the hash with the actual bytes32 nullifier hash. Returns `{ "spent": true/false }`.

### Facilitator health and status

```bash
curl -s "https://ceaser.org/status" | jq .
```

Returns facilitator wallet balance, registered protocols, circuit breaker state, transaction queue info, persistent transaction tracker stats, and indexer sync status.

### Simple liveness check

```bash
curl -s "https://ceaser.org/health" | jq .
```

Returns `{ "ok": true }` if the facilitator is running.

---

## Indexer Queries

The indexer maintains a local Merkle tree synchronized with the on-chain contract. It provides instant access to commitments and root data without RPC calls.

### Indexer sync status

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/status" | jq .
```

Returns synced, syncInProgress, lastSyncBlock, leafCount, root, and operational stats.

### Indexed Merkle root (instant, no RPC)

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/root" | jq .
```

### List commitments (paginated)

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/commitments?offset=0&limit=100" | jq .
```

Returns commitments array, total count, offset, and limit. Max 1000 per page.

### Get commitment by leaf index

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/commitment/0" | jq .
```

---

## x402 Facilitator (Gasless Settlement)

The facilitator is a gasless relay: it validates ZK proofs and submits them on-chain, paying gas on behalf of the user. This enables withdrawals from wallets with zero ETH balance.

### x402 capability discovery

```bash
curl -s "https://ceaser.org/supported" | jq .
```

Returns supported schemes (zk-relay), networks (eip155:8453), protocols (ceaser), and proof formats (ultrahonk).

### Verify a ZK proof (dry run, no on-chain submission)

```bash
curl -s -X POST "https://ceaser.org/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "ceaser",
    "network": "eip155:8453",
    "payload": {
      "proof": "0x...",
      "nullifierHash": "0x...",
      "amount": "100000000000000000",
      "assetId": "0",
      "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "root": "0x..."
    }
  }' | jq .
```

Returns isValid, validation details, gas estimate, and facilitator fee.

### Submit ZK proof on-chain (gasless settlement)

```bash
curl -s -X POST "https://ceaser.org/settle" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "ceaser",
    "network": "eip155:8453",
    "payload": {
      "proof": "0x...",
      "nullifierHash": "0x...",
      "amount": "100000000000000000",
      "assetId": "0",
      "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "root": "0x..."
    }
  }' | jq .
```

The facilitator pays gas. Recipient receives amount minus 0.25% protocol fee. Idempotent: resubmitting the same nullifier returns the cached result.

---

## Prepare a Shield Transaction

This builds an unsigned transaction for shielding ETH. The user must sign and submit it from their own wallet.

```bash
curl -s -X POST "https://ceaser.org/api/ceaser/shield/prepare" \
  -H "Content-Type: application/json" \
  -d '{
    "proof": "0x...",
    "commitment": "0x...",
    "amount": "100000000000000000",
    "assetId": "0"
  }' | jq .
```

Returns pre-built transaction data (to, data, value) and fee breakdown. The caller signs this with their wallet.

IMPORTANT: Shield operations require generating a ZK proof client-side. The proof, commitment, and secret/nullifier must be generated using the Ceaser frontend (https://ceaser.org) or the `ceaser-mcp` npm package (`npx ceaser-mcp`). This skill cannot generate proofs -- it only queries the API.

---

## CLI Subcommands (Shield / Unshield)

The `ceaser-mcp` npm package includes CLI subcommands that run directly from bash. These generate ZK proofs locally and interact with the facilitator for gasless settlement. All output is JSON.

### Shield ETH (generate proof + unsigned tx)

```bash
npx -y ceaser-mcp shield 0.001
```

Returns an unsigned transaction (to, data, value) and a note backup string. The user must sign and send the transaction from their wallet. Valid denominations: 0.001, 0.01, 0.1, 1, 10, 100 ETH.

The unsigned transaction is also saved to `~/.ceaser-mcp/pending-tx.json` for automatic signing flows (used by the ceaser-send skill).

IMPORTANT: The `backup` field in the output contains the note's private keys. It MUST be saved securely -- it is the only way to later unshield the funds.

### List stored notes

```bash
npx -y ceaser-mcp notes
```

Shows unspent notes with their IDs, amounts, and leaf indices. Add `--all` to include spent notes.

### Unshield ETH (gasless withdrawal via x402)

```bash
npx -y ceaser-mcp unshield <noteId> 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18
```

Generates a burn ZK proof and submits it to the facilitator. The facilitator pays gas. The recipient receives the amount minus 0.25% protocol fee. Requires a stored note with a valid leaf index (shield tx must have confirmed on-chain).

### Import a note from backup

```bash
npx -y ceaser-mcp import eyJzIjoiMTIzLi4uIn0=
```

Imports a note from a base64 backup string (generated by `shield` or the Ceaser frontend). Required before unshielding a note created elsewhere.

### Help

```bash
npx -y ceaser-mcp help
```

Notes are stored at `~/.ceaser-mcp/notes.json`. All commands output JSON to stdout on success and JSON to stderr on failure.

---

## Key Concepts

- **Shield**: Deposit ETH into the privacy pool. Creates a note (commitment) on-chain. Requires ZK proof generation (client-side only).
- **Unshield**: Withdraw ETH from the privacy pool to any address. Requires a stored note with secret/nullifier. The facilitator handles gas.
- **Note**: A private record containing secret, nullifier, amount, and commitment. Notes are never stored on-chain -- only their Poseidon hash (commitment) is.
- **Nullifier**: A unique identifier derived from the note. Once spent, the nullifier is recorded on-chain to prevent double-spending.
- **Denomination**: Fixed amounts (0.001 to 100 ETH) to prevent amount-based deanonymization.
- **Protocol Fee**: 0.25% (25 basis points) split between treasury (0.24%) and relayer fund (0.01%).

---

## Performing Transactions (Shield / Unshield)

When a user asks to shield or unshield ETH, ALWAYS use the `ceaser-mcp` CLI subcommands. This is the primary and recommended method:

```bash
# Shield ETH (generates ZK proof + unsigned tx)
npx -y ceaser-mcp shield 0.001

# List stored notes to get noteId
npx -y ceaser-mcp notes

# Unshield ETH (gasless via facilitator)
npx -y ceaser-mcp unshield <noteId> <recipient>

# Import a note from backup string
npx -y ceaser-mcp import <base64-backup>

# Help
npx -y ceaser-mcp help
```

The shield command generates a ZK proof locally and returns an unsigned transaction. The user must sign and send it. The unshield command generates a burn proof and settles via the facilitator (gasless).

Notes are stored at `~/.ceaser-mcp/notes.json`. All commands output JSON to stdout on success and JSON to stderr on failure.

### Alternative: MCP Server via Claude Code

The `ceaser-mcp` npm package also runs as an MCP server for Claude Code:

```bash
claude mcp add --transport stdio ceaser -- npx -y ceaser-mcp
```

This provides 10 MCP tools including `ceaser_shield_eth` and `ceaser_unshield`. Notes are stored locally at `~/.ceaser-mcp/notes.json`.

npm package: https://www.npmjs.com/package/ceaser-mcp

### Alternative: Web App (non-technical users)

Direct the user to https://ceaser.org -- connect wallet, select amount, click Shield or Unshield. The frontend handles proof generation, wallet signing, and note management in-browser.

### Auto-Signing Mode (ceaser-send)

A separate skill (`/ceaser-send`) provides fully automated shield-to-unshield flow
using an ephemeral hot wallet. The agent generates a BIP-39 mnemonic, the user funds
the hot wallet, and the agent signs and broadcasts the shield transaction automatically.
Only one manual step: funding the hot wallet with ETH.

PRIVACY NOTE: Auto-signing creates observable on-chain links between the user's
wallet and the hot wallet (funding + refund transactions). For maximum privacy,
the manual approach (this skill + MetaMask) is recommended. Use ceaser-send only
when the user explicitly requests automated signing.

Install: `clawhub install ceaser-send`

---

### What this skill can help with

While you wait for a transaction or are exploring the protocol, this skill can:
- Check denominations and fees before shielding
- Monitor pool TVL and note count
- Verify a nullifier is unspent before attempting unshield
- Check facilitator health and circuit breaker state
- Browse indexed commitments and Merkle tree state

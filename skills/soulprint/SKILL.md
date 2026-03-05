---
name: soulprint
description: "Soulprint decentralized identity verification for AI agents. v0.6.4 — blockchain-first architecture (no libp2p): state lives on Base Sepolia, 4 validator nodes on Railway, ZK proofs (Circom, local verification). Use when: proving a real human is behind a bot, issuing privacy-preserving identity proofs, running a validator node, adding identity verification middleware to an API or MCP server, checking bot reputation scores, or enforcing protocol-level configurable trust thresholds."
homepage: https://soulprint.digital
metadata:
  {
    "openclaw":
      {
        "emoji": "🌀",
        "requires": { "bins": ["node", "npx"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "soulprint",
              "bins": ["soulprint"],
              "label": "Install Soulprint CLI (npm)",
            },
          ],
      },
  }
---

# Soulprint — Decentralized Identity for AI Agents

Soulprint proves a real human is behind any AI bot using privacy-preserving ZK proofs — no centralized authority, no biometric cloud uploads. State lives on Base Sepolia blockchain.

**GitHub:** https://github.com/manuelariasfz/soulprint  
**npm:** https://www.npmjs.com/package/soulprint-network  
**Docs:** https://soulprint.digital  
**Network:** 4 validator nodes on Railway (Base Sepolia testnet)  
**Version:** v0.6.4

---

## Architecture (v0.6.4 — blockchain-first, local ZK verification)

```
User verifies once → ZK proof generated locally (no Registraduría scraping)
→ Nullifier registered on-chain (Base Sepolia)
→ Any agent queries on-chain: isRegistered(nullifier) → true/false
No P2P sync, no central server — blockchain IS the network
```

**Contracts on Base Sepolia:**
- `PeerRegistry`: `0x452fb66159dFCfC13f2fD9627aA4c56886BfB15b`
- `NullifierRegistry`: (pending deployment — requires testnet ETH)
- `ReputationRegistry`: (pending deployment — requires testnet ETH)
- `ProtocolThresholds`: `0xD8f78d65b35806101672A49801b57F743f2D2ab1`
- `MCPRegistry`: `0x59EA3c8f60ecbAe22B4c323A8dDc2b0BCd9D3C2a`

---

## When to Use

✅ **USE this skill when:**

- "Verify my identity for an AI agent"
- "Run a Soulprint validator node"
- "Add identity verification to my MCP server or API"
- "Check the reputation score of a bot or DID"
- "Generate a privacy proof from a Colombian cédula"
- "Verify a cédula against Registraduría Nacional"
- "Issue or verify an SPT (Soulprint Token)"

❌ **DON'T use this skill when:**

- Storing or transmitting biometric data remotely (Soulprint runs 100% locally)
- Verifying identities from countries not yet supported (only Colombia is full)

---

## Quick Start

### 1. Verify Your Identity (one-time)

```bash
npx soulprint install-deps   # OCR + face recognition — only once
npx soulprint verify-me      # all local, nothing uploaded
```

### 2. Run a Validator Node

```bash
npx soulprint-network
# or
ADMIN_PRIVATE_KEY=0x... ADMIN_TOKEN=... PORT=4888 node dist/server.js
```

**Node API:**
```
GET  /info                      — node version, network, contracts, capabilities
GET  /health                    — code integrity hash
POST /verify                    — verify ZK proof
GET  /verify/cedula?numero=X&fechaNac=YYYY-MM-DD  — Registraduría validation
GET  /network/stats             — live stats (peers, verified, MCPs)
GET  /mcps/verified             — verified MCPs from MCPRegistry on-chain
GET  /protocol/thresholds       — on-chain protocol thresholds
```

---

## Integrate in Your API

### MCP Server (3 lines)

```typescript
import { requireSoulprint } from "soulprint-mcp";

server.tool("premium-tool", requireSoulprint({ minScore: 80 }), async (args, ctx) => {
  const { did, score } = ctx.soulprint;
});
```

### Express / Fastify

```typescript
import { soulprintMiddleware } from "soulprint-express";
app.use(soulprintMiddleware({ minScore: 65 }));
// req.soulprint.did, req.soulprint.score
```

---

## Trust Score (0–100)

| Component | Max | Source |
|---|---|---|
| Email verified | 8 | credential: email |
| Phone verified | 12 | credential: phone |
| GitHub account | 16 | credential: github |
| Document OCR | 20 | credential: document |
| Face match | 16 | credential: face_match |
| Biometric proof | 8 | credential: biometric |
| Bot reputation | 20 | Validator attestations |
| **Total** | **100** | |

---

## Protocol Constants (on-chain via ProtocolThresholds)

| Constant | Value |
|---|---|
| `SCORE_FLOOR` | 65 |
| `VERIFIED_SCORE_FLOOR` | 52 |
| `MIN_ATTESTER_SCORE` | 65 |
| `DEFAULT_REPUTATION` | 10 |
| `IDENTITY_MAX` | 80 |
| `REPUTATION_MAX` | 20 |

---

## Country Support

| Country | Document | Status |
|---|---|---|
| 🇨🇴 Colombia | Cédula de Ciudadanía | ✅ Full (OCR + MRZ + face match + Registraduría) |
| Others | — | 🚧 Planned |

---

## npm Packages

| Package | Version | Purpose |
|---|---|---|
| `soulprint-network` | 0.6.4 | Validator node (HTTP + blockchain clients) |
| `soulprint-mcp` | latest | MCP middleware |
| `soulprint-express` | latest | Express/Fastify middleware |
| `soulprint-core` | latest | DID, tokens, protocol constants |
| `soulprint-zkp` | latest | ZK proofs (Circom + snarkjs) |
| `soulprint-verify` | latest | OCR + face match |
| `soulprint` | latest | CLI |

---

## Integration with mcp-colombia

`mcp-colombia-hub@1.3.0` uses Soulprint natively — no extra setup needed.

- `soulprint_status` tool available directly in mcp-colombia: checks on-chain identity and reputation
- `trabajo_aplicar` (job applications) requires Soulprint score ≥ 40
- Live validator: `https://soulprint-node-production.up.railway.app`

### Install both together

```bash
# Add to your MCP config:
npx mcp-colombia-hub     # includes soulprint_status tool

# Verify your identity first (one-time):
npx soulprint verify-me
```

Once verified, your SPT token works across all tools in mcp-colombia automatically.

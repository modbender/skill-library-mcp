---
name: AgentPin Development Skills Guide
description: AgentPin is a domain-anchored cryptographic identity protocol for
  AI agents. It enables organizations to publish verifiable identity documents
  for their agents, issue short-lived JWT credentials, a...
---

# AgentPin Development Skills Guide

**Purpose**: This guide helps AI assistants work with AgentPin for domain-anchored cryptographic agent identity verification.

**For Full Documentation**: See the [README](https://github.com/ThirdKeyAI/agentpin/blob/main/README.md) and [Technical Specification](https://github.com/ThirdKeyAI/agentpin/blob/main/AGENTPIN_TECHNICAL_SPECIFICATION.md).

## What AgentPin Does

AgentPin is a domain-anchored cryptographic identity protocol for AI agents. It enables organizations to publish verifiable identity documents for their agents, issue short-lived JWT credentials, and verify agent identity through a multi-step protocol including TOFU key pinning, revocation checking, and delegation chains.

**Part of the ThirdKey trust stack**: SchemaPin (tool integrity) → AgentPin (agent identity) → Symbiont (runtime)

---

## Architecture

```
Organization                         Verifying Party
────────────                         ───────────────
1. Generate ECDSA P-256 keypair
2. Publish agent identity at          3. Discover identity from
   /.well-known/agent-identity.json      /.well-known/agent-identity.json
4. Issue JWT credential               5. Verify credential (12-step flow)
   (ES256 signed, short-lived)           - JWT parsing & ES256 verification
                                         - Domain binding check
                                         - TOFU key pinning
                                         - Revocation checking
                                         - Capability validation
                                         - Delegation chain verification
```

---

## Project Structure

```
crates/
├── agentpin/          Core library (no mandatory HTTP dep)
├── agentpin-cli/      CLI binary (keygen, issue, verify, bundle)
└── agentpin-server/   Axum server for .well-known endpoints
```

---

## Quick Start by Language

### Rust (CLI)

```bash
# Generate keys
cargo run -p agentpin-cli -- keygen \
    --output-dir ./keys --agent-name "my-agent"

# Issue a credential (ES256 JWT, 1-hour TTL)
cargo run -p agentpin-cli -- issue \
    --key ./keys/my-agent.private.pem \
    --issuer "https://example.com" \
    --agent-id "my-agent" \
    --capabilities read,write --ttl 3600

# Verify offline
cargo run -p agentpin-cli -- verify \
    --credential ./credential.jwt \
    --discovery ./agent-identity.json

# Verify online (fetches from .well-known)
cargo run -p agentpin-cli -- verify \
    --credential ./credential.jwt --domain example.com

# Create trust bundle for air-gapped environments
cargo run -p agentpin-cli -- bundle \
    --discovery ./agent-identity.json \
    --revocation ./revocations.json --output ./bundle.json
```

### Rust (Library)

```rust
use agentpin::{
    crypto,
    credential::CredentialBuilder,
    verification::verify_credential,
    pinning::KeyPinStore,
};

let (private_key, public_key) = crypto::generate_keypair()?;

let credential = CredentialBuilder::new()
    .issuer("https://example.com")
    .agent_id("my-agent")
    .capability("read")
    .capability("write")
    .ttl_secs(3600)
    .sign(&private_key)?;

let result = verify_credential(&credential, &discovery_doc, &pin_store)?;
```

### JavaScript

```bash
npm install agentpin
```

```javascript
import {
    generateKeypair, issueCredential, verifyCredential,
    KeyPinStore
} from 'agentpin';

// Generate ECDSA P-256 keypair
const { privateKey, publicKey } = await generateKeypair();

// Issue a credential
const credential = await issueCredential(privateKey, {
    issuer: 'https://example.com',
    agentId: 'my-agent',
    capabilities: ['read', 'write'],
    ttlSecs: 3600,
});

// Verify
const pinStore = new KeyPinStore();
const result = await verifyCredential(credential, discoveryDoc, pinStore);
```

### Python

```bash
pip install agentpin
```

```python
from agentpin.crypto import generate_keypair
from agentpin.credential import issue_credential
from agentpin.verification import verify_credential
from agentpin.pinning import KeyPinStore

private_key, public_key = generate_keypair()

credential = issue_credential(
    private_key,
    issuer="https://example.com",
    agent_id="my-agent",
    capabilities=["read", "write"],
    ttl_secs=3600,
)

pin_store = KeyPinStore()
result = verify_credential(credential, discovery_doc, pin_store)
```

### Serve .well-known Endpoints

```bash
cargo run -p agentpin-server -- \
    --identity ./agent-identity.json \
    --revocation ./revocations.json \
    --port 3000
```

Serves:
- `GET /.well-known/agent-identity.json` (Cache-Control: max-age=3600)
- `GET /.well-known/agent-identity-revocations.json` (Cache-Control: max-age=300)
- `GET /health`

---

## Core Library API

### Key Modules

| Module | Purpose |
|--------|---------|
| `crypto` | ECDSA P-256 signing/verification (no external JWT crate) |
| `types` | Core data structures (agents, credentials, capabilities) |
| `credential` | JWT issuance and parsing |
| `discovery` | Publishing and resolving agent identity documents |
| `verification` | 12-step credential validation flow |
| `revocation` | Checking revoked credentials/agents/keys |
| `pinning` | TOFU key pinning with JWK thumbprints |
| `delegation` | Delegation chain validation |
| `mutual` | Challenge-response mutual authentication (128-bit nonces) |
| `jwk` | JWK handling and thumbprint computation |
| `resolver` | Pluggable discovery resolution |

### Language API Reference

| Operation | Rust | JavaScript | Python |
|-----------|------|------------|--------|
| Generate keys | `crypto::generate_keypair()` | `generateKeypair()` | `generate_keypair()` |
| Issue credential | `CredentialBuilder::new().sign()` | `issueCredential()` | `issue_credential()` |
| Verify credential | `verify_credential()` | `verifyCredential()` | `verify_credential()` |
| Key pinning | `KeyPinStore` | `KeyPinStore` | `KeyPinStore` |
| Trust bundle | `TrustBundle::from_json()` | `TrustBundle.fromJson()` | `TrustBundle.from_json()` |
| Mutual auth | `MutualAuth::challenge()` | `createChallenge()` | `create_challenge()` |

### Feature Flags

| Feature | Purpose |
|---------|---------|
| `fetch` | Enables HTTP via reqwest for online discovery |
| (default) | Core library with no HTTP dependency |

---

## Key Concepts

### ES256 Only

AgentPin exclusively uses ES256 (ECDSA P-256). All other algorithms are rejected. This is enforced inline without an external JWT crate.

### 12-Step Verification

The credential verification flow includes:
1. JWT structure parsing
2. Header algorithm validation (ES256 only)
3. Signature verification
4. Issuer domain extraction
5. Discovery document resolution
6. Domain binding verification
7. Key matching (issuer key vs discovery)
8. TOFU key pinning check
9. Expiration validation
10. Revocation checking
11. Capability validation
12. Delegation chain verification (if present)

### TOFU Key Pinning

On first credential verification for a domain, the agent's public key (JWK thumbprint) is pinned. Subsequent verifications reject different keys for the same domain — detecting key substitution attacks.

### Delegation Chains

Agents can delegate capabilities to sub-agents. The delegation chain is validated to ensure:
- Each link is signed by the delegator
- Capabilities only narrow (never widen) down the chain
- Chain depth limits are respected

### Mutual Authentication

Challenge-response protocol with 128-bit nonces for bidirectional agent identity verification.

---

## Discovery Document Format

Published at `/.well-known/agent-identity.json`:

```json
{
    "schema_version": "0.2",
    "domain": "example.com",
    "agents": [
        {
            "agent_id": "my-agent",
            "display_name": "My Agent",
            "description": "A helpful agent",
            "capabilities": ["read", "write"],
            "public_key_jwk": { ... },
            "constraints": {
                "max_ttl_secs": 86400,
                "allowed_scopes": ["api"]
            }
        }
    ],
    "revocation_endpoint": "https://example.com/.well-known/agent-identity-revocations.json",
    "directory_listing": true
}
```

---

## v0.2.0 Features

### Trust Bundles (Offline / Air-Gapped)

Pre-package discovery + revocation data for environments without internet:

```python
from agentpin.bundle import TrustBundle

bundle = TrustBundle.from_json(bundle_json_str)
discovery = bundle.find_discovery("example.com")
revocation = bundle.find_revocation("example.com")
```

### Pluggable Discovery Resolvers

```python
from agentpin.discovery import (
    WellKnownResolver,    # HTTP .well-known lookups
    DnsTxtResolver,       # DNS TXT record lookups
    ManualResolver,       # Pre-configured discovery data
)
```

### Directory Listing

Domains can advertise all their agents via `"directory_listing": true` in the discovery document. Verifiers can enumerate available agents before issuing challenges.

---

## Development

### Build and Test

```bash
# Build all crates
cargo build --workspace

# Run all tests
cargo test --workspace

# Lint
cargo clippy --workspace

# Format check
cargo fmt --check
```

### Conventions

- Rust edition 2021, MSRV 1.70
- `cargo clippy --workspace` must pass with zero warnings
- `cargo fmt --check` must pass
- Inline tests in source files (`#[cfg(test)] mod tests`)
- ES256 only — reject all other algorithms
- Feature-gated HTTP: `fetch` feature enables reqwest

---

## Pro Tips for AI Assistants

1. **ES256 only** — never accept RS256, HS256, or any other algorithm
2. **Short-lived credentials** — prefer TTLs of hours, not days
3. **Always check revocation** before trusting a credential
4. **TOFU pinning** means first-seen key is trusted — warn on key changes
5. **Delegation chains** should narrow capabilities, never widen them
6. **No external JWT crate** — algorithm validation is controlled inline to prevent algorithm confusion attacks
7. **Feature-gate HTTP** — use the `fetch` feature only when online discovery is needed; default is offline-capable
8. **Cross-compatible with SchemaPin** — both use ECDSA P-256, same crypto primitives
9. **Trust bundles** are ideal for CI/CD and air-gapped deployments — pre-package discovery + revocation data
10. **JavaScript and Python SDKs** provide identical verification guarantees to the Rust crate

# Changelog

All notable changes to the AgentPin project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-12

### Added

#### Trust Bundles & Alternative Discovery
- **Trust bundles** for offline and air-gapped verification — pre-package discovery + revocation data
- **`DiscoveryResolver` trait** with pluggable discovery strategies:
  - `WellKnownResolver`: HTTP `.well-known` lookups (default)
  - `DnsTxtResolver`: DNS TXT record discovery
  - `ManualResolver`: Pre-configured static documents
- **`directory_listing` field** on `AgentDeclaration` for multi-agent domain enumeration
- **JavaScript SDK**: Trust bundle support, resolver abstraction
- **Python SDK**: Trust bundle support, resolver abstraction

## [0.1.1] - 2026-02-10

### Fixed
- **PyPI README**: Added package README for PyPI listing
- **npm README**: Added package README, fixed package URLs
- Bumped JavaScript package to 0.1.1, Python package to 0.1.1

## [0.1.0] - 2026-02-08

### Added

#### Core Protocol
- **ECDSA P-256 keypair generation** with JWK export
- **JWT credential issuance** (ES256 signed, configurable TTL)
- **12-step credential verification** flow:
  - JWT parsing, algorithm validation (ES256 only), signature verification
  - Domain binding, discovery resolution, key matching
  - TOFU key pinning (JWK thumbprint), expiration, revocation
  - Capability validation, delegation chain verification
- **TOFU key pinning** with JWK thumbprint persistence
- **Delegation chains** with capability narrowing and depth limits
- **Mutual authentication** with 128-bit nonce challenge-response
- **Credential, agent, and key-level revocation**

#### Crates
- `agentpin` — Core library (no mandatory HTTP dependency)
- `agentpin-cli` — CLI binary (`keygen`, `issue`, `verify`, `bundle`)
- `agentpin-server` — Axum server for `.well-known` endpoints

#### Cross-Language SDKs
- **JavaScript** (`agentpin` npm package): Full protocol implementation
- **Python** (`agentpin` PyPI package): Full protocol implementation

#### Discovery
- `.well-known/agent-identity.json` discovery document format
- `.well-known/agent-identity-revocations.json` revocation endpoint
- Capability-scoped credentials with constraints (`max_ttl_secs`, `allowed_scopes`)

# OpenExec Skill

## Overview
OpenExec is a deterministic execution engine requiring external governance approval. It runs as a FastAPI service with SQLite storage, replay protection, receipt verification, Ed25519 constitutional signature enforcement, and optional execution allow-list. Version 0.1.10.

## Recent Changes
- 2026-02-17: Upgraded to Ed25519 signature verification (from HMAC-SHA256)
- 2026-02-17: Added expires_at field to approval artifacts (replacing TTL-based expiry)
- 2026-02-17: Updated crypto.py to use cryptography library for Ed25519
- 2026-02-17: Added cryptography dependency to requirements.txt
- 2026-02-17: Updated clawshield_client.py with Ed25519 keypair generation and artifact minting
- 2026-02-17: Updated /health endpoint to show signature_verification status
- 2026-02-17: 20 tests total (6 demo + 14 constitutional)
- 2026-02-17: Initial project creation with full runtime surface

## Architecture
- **Runtime**: Python 3.11, FastAPI, SQLAlchemy, Pydantic, cryptography
- **Database**: SQLite (openexec.db)
- **Entrypoint**: main.py (uvicorn on port 5000)
- **Deployment**: Autoscale on Replit

### Key Files
- `main.py` -- FastAPI app with /health, /ready, /version, /execute, /receipts/verify endpoints
- `openexec/settings.py` -- Mode configuration (demo vs clawshield), reads env at call time
- `openexec/engine.py` -- Execution engine with replay protection, constitutional enforcement, and allow-list
- `openexec/crypto.py` -- Ed25519 signature verification, canonical SHA-256 hashing
- `openexec/approval_validator.py` -- Approval artifact validation (hash, expiry, signature, tenant)
- `openexec/clawshield_client.py` -- Ed25519 keypair generation and artifact minting (for testing)
- `openexec/registry.py` -- Action registry with demo actions (echo, add)
- `openexec/db.py` -- SQLAlchemy database setup
- `openexec/tables.py` -- ExecutionLog table
- `openexec/models.py` -- Pydantic schemas including ApprovalArtifact with expires_at
- `openexec/receipts.py` -- SHA-256 receipt verification
- `tests/test_demo_flow.py` -- Demo mode test suite (6 tests)
- `tests/test_constitutional.py` -- Constitutional mode test suite (14 tests)

### Modes
- `demo` (default) -- All actions auto-approved
- `clawshield` -- Requires Ed25519-signed approval artifact with hash binding, expiry enforcement, signature verification, and tenant isolation

### Env Vars
- `OPENEXEC_MODE` -- demo or clawshield
- `CLAWSHIELD_PUBLIC_KEY` -- PEM-encoded Ed25519 public key (clawshield mode)
- `CLAWSHIELD_TENANT_ID` -- Tenant identifier (clawshield mode)
- `OPENEXEC_ALLOWED_ACTIONS` -- Comma-separated list of allowed actions (optional, all allowed if unset)

## User Preferences
- GitHub as canonical source of truth
- Every commit intentional, no drift
- ClawHub-ready from day one
- Infrastructure-first approach, not spec-only
- No policy logic in OpenExec -- signature verification only

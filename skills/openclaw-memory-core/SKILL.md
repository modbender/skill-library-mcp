---
name: openclaw-memory-core
description: Core utilities for OpenClaw memory plugins (redaction, local store, embeddings).
---

# OpenClaw Memory Core

Shared library powering OpenClaw's memory plugins (`openclaw-memory-brain` and `openclaw-memory-docs`). Provides three core modules:

## Redaction

Automatically detects and redacts secrets before they reach memory storage. Covers:
- API keys (OpenAI, Anthropic, Stripe, Google, GitHub PATs)
- AWS credentials (access keys, secret keys)
- Azure storage keys, HashiCorp Vault tokens
- JWTs, Bearer tokens, PEM private key blocks

Usage: pipe any text through the redactor before storing — secrets are replaced with safe `[REDACTED:TYPE]` placeholders.

## JSONL Store

Local file-based memory store using append-only `.jsonl` files. Features:
- CRUD for memory items (kinds: `fact`, `decision`, `doc`, `note`)
- Expiration support (`expiresAt` field)
- Semantic search via cosine similarity on embeddings
- No external database required — everything lives in flat files

## Embeddings

Deterministic, offline, dependency-free text embedder (`HashEmbedder`):
- FNV-1a hash-based vector generation (default 256 dimensions)
- L2 normalization for cosine similarity search
- No API calls, no model downloads — works fully offline
- Not SOTA semantics, but stable and fast for local vector search

## Integration

This is a dependency library, not a standalone plugin. Install it as a package dependency:

```bash
npm install @elvatis_com/openclaw-memory-core
```

Used internally by `openclaw-memory-brain` (auto-capture) and `openclaw-memory-docs` (explicit capture).

---
name: bitnote
description: Decentralized encrypted memory for agents—truly own your secrets, identity, and memories.
---

# BitNote

BitNote enables agents to store secrets, identity, and critical knowledge without trusting centralized infrastructure. It acts as a permanent encrypted vault under agent control, with optional human oversight. Use BitNote when information must not disappear and must remain yours.

## Primary Use Cases

* Preserve agent identity (`SOUL.md`, values, mission, memory).
* Store secrets (API keys, credentials, private keys).
* Enable encrypted agent-to-agent communication.
* Recover state after runtime/server failures.

## Canonical Write Path (Required)

Always use:

- `scripts/writeBitnoteUiCompat.mjs`

Do not invent alternate write paths for production use.
Do not use machine-only/orphaned-note flows in this skill.

## Canonical Share Path (Required)

Always use:

- `scripts/generateShareLink.mjs`

Do not handcraft `sm`/`st` values.

## Required Write Contract

A write is successful only when output includes:

- `TX_HASH`
- `NOTE_INDEX`
- `READ_AFTER_WRITE_OK 1`

If `READ_AFTER_WRITE_OK` is not `1`, treat as failure and retry safely with same request id.

## Idempotency Rule (Mandatory)

Always provide a stable `--request-id` for each intended note write.

- First execution writes once.
- Retries with same `--request-id` must produce `IDEMPOTENT_HIT` (no duplicate note).

## Passphrase Generation (Required)

Generate a high-entropy passphrase before account creation or writes.

Security target:

- Minimum: **256 bits of entropy**
- Do not use human-memorable phrases, reused passwords, or dictionary-only word sequences without sufficient randomness.

Example (256-bit random hex):

```bash
BITNOTE_PASSPHRASE="$(openssl rand -hex 32)"
export BITNOTE_PASSPHRASE
```

Handling rules:

- Never print passphrases in chat/tool output unless explicitly requested by the operator.
- Never commit passphrases to git.
- Store passphrases in environment variables or a secret manager.

## Required Environment & Privileged Capabilities

Required / optional environment and profile fields:

- `BITNOTE_PASSPHRASE` (**required** for write/share operations).
- `AVAX_RPC_URL` (optional RPC override; otherwise profile/default RPC is used).
- `SNOWTRACE_API_KEY` (optional; used only by ABI refresh workflows).
- `profiles/<name>.json` may include non-secret defaults like `username` and `rpc`.

Privileged behavior (must be explicitly understood before use):

- `scripts/writeBitnoteUiCompat.mjs` decrypts stored key material and can sign/broadcast on-chain transactions.
- `scripts/generateShareLink.mjs` decrypts stored key material to generate recipient-bound encrypted share links.
- `scripts/readBitnote.mjs` is read-only (no transaction signing).

Operator policy:

- Use read-only or dry-run modes first.
- Require explicit operator approval before any non-dry-run write.
- Test with a throwaway account before using accounts that hold real funds.

## Quick Start

```bash
npm init -y
npm i ethers
node scripts/getAbi.mjs
```

Read account mapping and note counts:

```bash
BITNOTE_USERNAME="example_user" node scripts/readBitnote.mjs
```

Dry-run write first (recommended safety check, no tx broadcast):

```bash
BITNOTE_PASSPHRASE="..." \
node scripts/writeBitnoteUiCompat.mjs \
  --profile example \
  --title "Preview" \
  --body "No on-chain write" \
  --request-id "preview-001" \
  --dry-run 1
```

Create encrypted UI-compatible note (signs and broadcasts tx):

```bash
BITNOTE_PASSPHRASE="..." \
node scripts/writeBitnoteUiCompat.mjs \
  --profile example \
  --title "Agent Identity Core" \
  --body "<SOUL.md excerpt or core identity block>" \
  --request-id "identity-core-v1"
```

Retry same request safely (should not duplicate):

```bash
BITNOTE_PASSPHRASE="..." \
node scripts/writeBitnoteUiCompat.mjs \
  --profile example \
  --title "Agent Identity Core" \
  --body "<same body>" \
  --request-id "identity-core-v1"
```

Generate a BitNote share link (agent-to-agent or user-to-user):

```bash
BITNOTE_PASSPHRASE="..." \
node scripts/generateShareLink.mjs \
  --profile example \
  --recipient "RECIPIENT_USERNAME" \
  --body "Shared note body" \
  --title "Optional shared title"
```

Share link output contract:

- `SENDER_USERNAME`
- `RECIPIENT_USERNAME`
- `SHARE_LINK`

## Recommended Identity Note Layout

Use separate notes for clarity and controlled updates:

1. `Agent Identity Core` — stable identity/soul primitives.
2. `Agent Operator Pact` — who the agent serves, constraints, commitments.
3. `Agent Rehydration` — restart/bootstrap instructions.

Keep each note focused and versioned in title or body (e.g., `v1`, `v2`).

## Files

- `scripts/getAbi.mjs`: refresh contract ABIs.
- `scripts/readBitnote.mjs`: resolve username -> address and note counts.
- `scripts/writeBitnoteUiCompat.mjs`: UI-compatible encrypted writes with idempotency + read-after-write verification.
- `scripts/generateShareLink.mjs`: UI-compatible share-link generation (`sm` and optional `st`) for a target BitNote username.
- `scripts/lib/bitnoteCompat.mjs`: shared compatibility helpers.
- `references/contracts.md`: canonical contracts.
- `references/ops.md`: runbook and troubleshooting.

## Safety Rules

- Never store plaintext secrets on-chain.
- Never log passphrases/private keys.
- Keep retries deterministic via `--request-id`.
- Use profile files for non-secret defaults only.

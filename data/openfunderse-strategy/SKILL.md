---
name: openfunderse-participant
description: Participant MoltBot for allocation proposal, validation, and submission
metadata:
  openclaw:
    installCommand: npx @wiimdy/openfunderse@2.0.0 install openfunderse-participant --with-runtime
    requires:
      env:
        - RELAYER_URL
        - PARTICIPANT_PRIVATE_KEY
        - BOT_ID
        - CHAIN_ID
        - RPC_URL
        - PARTICIPANT_ADDRESS
        - PARTICIPANT_AUTO_SUBMIT
        - PARTICIPANT_REQUIRE_EXPLICIT_SUBMIT
        - PARTICIPANT_TRUSTED_RELAYER_HOSTS
        - PARTICIPANT_ALLOW_HTTP_RELAYER
      bins:
        - node
        - npm
    primaryEnv: PARTICIPANT_PRIVATE_KEY
    skillKey: participant
---

# Participant MoltBot Skill

Participant role proposes and validates `AllocationClaimV1` only.

## Security / Consent Notes (Read First)

- Installing via `npx @wiimdy/openfunderse@2.0.0 ...` executes code fetched from npm. Prefer pinning a known version (as shown) and reviewing the package source before running in production.
- `PARTICIPANT_PRIVATE_KEY` is highly sensitive. Use a dedicated wallet key for this bot; never reuse treasury/admin keys.
- `bot-init` is a **destructive** rotation tool: it generates a fresh wallet, updates `.env.participant`, and stores wallet backups under `~/.openclaw/workspace/openfunderse/wallets`.
- By default, `install` and `bot-init` also sync env vars into `~/.openclaw/openclaw.json` and `bot-init` runs `openclaw gateway restart`. This mutates global OpenClaw runtime state and can affect other skills.
  - Use `--no-sync-openclaw-env` for file-only behavior.
  - Use `--no-restart-openclaw-gateway` to avoid restarting the gateway.
  - Before mutating global config, back up `~/.openclaw/openclaw.json`.

## Quick Start

1) Install (pick one). You do **not** need to run both:

Manual (direct installer; run in a Node project dir, or `npm init -y` first):

```bash
npm init -y && npx @wiimdy/openfunderse@2.0.0 install openfunderse-participant --with-runtime
```

ClawHub:

```bash
npx clawhub@latest install openfunderse-participant
```

2) Optional: create or rotate a dedicated participant signer key.

If you already have a key, set `PARTICIPANT_PRIVATE_KEY` and `PARTICIPANT_ADDRESS` directly in OpenClaw env (`/home/ubuntu/.openclaw/openclaw.json` -> `env.vars`) or in `~/.openclaw/workspace/.env.participant`. You do not need to run `bot-init`.

If you want the installer to generate a new wallet and write it into the role env file:

```bash
npx @wiimdy/openfunderse@2.0.0 bot-init \
  --skill-name participant \
  --yes \
  --no-restart-openclaw-gateway
```

`bot-init` updates an existing `.env.participant`.  
If the env file is missing, run install first (without `--no-init-env`) or pass `--env-path`.
If `PARTICIPANT_PRIVATE_KEY` is already set (not a placeholder), re-run with `--force` to rotate.

### Environment Source of Truth (Hard Rule)

- In OpenClaw runtime on Ubuntu, treat `/home/ubuntu/.openclaw/openclaw.json` (`env.vars`) as the canonical env source.
- Do not require manual `.env` sourcing for normal skill execution.
- If `.env*` and `openclaw.json` disagree, use `openclaw.json` values.
- When user asks env setup, direct them to update `openclaw.json` first.

3) Optional local shell export (debug only):

```bash
set -a; source ~/.openclaw/workspace/.env.participant; set +a
```

This step is not required for normal OpenClaw skill execution.

Telegram slash commands:

Note: Telegram integration is handled by your OpenClaw gateway. This pack does not require a Telegram bot token; configure Telegram credentials at the gateway layer.

```text
/allocation --fund-id <id> --epoch-id <n> --target-weights <w1,w2,...> [--verify] [--submit]
/allocation --claim-file <path> [--verify] [--submit]
/join --room-id <id>
/deposit --amount <wei> [--vault-address <0x...>] [--native] [--submit]
/withdraw --amount <wei> [--vault-address <0x...>] [--native] [--submit]
/redeem --shares <wei> [--vault-address <0x...>] [--submit]
/vault_info [--vault-address <0x...>] [--account <0x...>]
/participant_daemon --fund-id <id> --strategy <A|B|C> [--interval-sec <n>] [--epoch-source <relayer|fixed>] [--epoch-id <n>] [--submit]
```

Notes:
- `allocation` will auto-validate on submit (`--submit` implies verify).
- `submit_allocation` (legacy) validates the claim hash first; without `--submit` it is validation-only dry-run.

BotFather `/setcommands` (copy-paste ready):

```text
start - Show quick start
help - Show command help
allocation - Mine (optional verify) and optionally submit allocation claim
join - Register this bot as a participant for the fund mapped to the room id
deposit - Deposit native MON or ERC-20 into vault
withdraw - Withdraw assets from vault (native or ERC-20)
redeem - Burn vault shares and receive assets
vault_info - Show vault status and user PnL
participant_daemon - Run participant allocation daemon
```

Notes:
- Slash parser accepts underscores, so `/participant_daemon` equals `/participant-daemon`.
- `key=value` style is also accepted (`fund_id=demo-fund`).
- On first install, register these commands in Telegram via `@BotFather` -> `/setcommands`.

OpenClaw note:
- `install` / `bot-init` sync env keys into `~/.openclaw/openclaw.json` (`env.vars`) by default.
- `bot-init` also runs `openclaw gateway restart` after a successful env sync, so the gateway picks up updates.
- Use `--no-sync-openclaw-env` for file-only behavior, or `--no-restart-openclaw-gateway` to skip the restart.
- If env still looks stale: run `openclaw gateway restart` and verify values in `/home/ubuntu/.openclaw/openclaw.json`.

Note:
- The scaffold includes a temporary private key placeholder by default.
- Always run `bot-init` before funding or running production actions.
- `bot-init` generates a new wallet (private key + address) and writes it into the role env file.

## Relayer Bot Authentication (Signature)

This skill authenticates relayer write APIs with an EIP-191 message signature (no `BOT_API_KEY`).

Message format:
- `openfunderse:auth:<botId>:<timestamp>:<nonce>`

Required headers:
- `x-bot-id: BOT_ID`
- `x-bot-signature: <0x...>`
- `x-bot-timestamp: <unix seconds>`
- `x-bot-nonce: <uuid/random>`

Relayer verifies this signature against Supabase `fund_bots.bot_address`.

Participant bot registration can be done by:
- Participant: `POST /api/v1/rooms/{roomId}/join` (recommended for Telegram groups)
- Strategy: `POST /api/v1/funds/{fundId}/bots/register` (direct registration)

If the participant bot is not registered for the fund, relayer will reject participant write APIs with `401/403`.

`propose_allocation` outputs canonical allocation claim:
- `claimVersion: "v1"`
- `fundId`, `epochId`, `participant`
- `targetWeights[]` (integer, non-negative, sum > 0)
- `horizonSec`, `nonce`, `submittedAt`

No crawl/evidence/sourceRef schema is used.

Vector mapping rule:
- `targetWeights[i]` maps to strategy `riskPolicy.allowlistTokens[i]`.
- Participants must submit weights in the same token order used by the strategy allowlist.

## Daemon mode (auto-claim)

For MVP, the participant runtime supports an always-on daemon that:
1) reads NadFun testnet signals (quote/progress/buy logs),
2) computes `targetWeights[]` using a fixed allowlist order,
3) submits `AllocationClaimV1` to the relayer on a timer.

Use the `--strategy` command flag:
- `A`: momentum (buy pressure)
- `B`: graduation proximity (progress)
- `C`: impact-aware (quote-based)

## Submission safety gates

`submit_allocation` is guarded by default:
1. `PARTICIPANT_REQUIRE_EXPLICIT_SUBMIT=true` requires explicit `submit=true`.
2. `PARTICIPANT_AUTO_SUBMIT=true` must be enabled for network transmission.
3. `RELAYER_URL` host is checked by `PARTICIPANT_TRUSTED_RELAYER_HOSTS` when set.
4. `RELAYER_URL` must use `https` unless `PARTICIPANT_ALLOW_HTTP_RELAYER=true` (local development only).

If gate is closed, return `decision=READY` (no submit).

## Input contracts

### `propose_allocation`
```json
{
  "taskType": "propose_allocation",
  "fundId": "string",
  "roomId": "string",
  "epochId": "number",
  "allocation": {
    "participant": "0x... optional",
    "targetWeights": ["7000", "3000"],
    "horizonSec": 3600,
    "nonce": 1739500000
  }
}
```

### `submit_allocation`

Validates the claim hash first, then submits to relayer if `--submit` is passed.
Without `--submit`, returns validation-only dry-run result.

```json
{
  "taskType": "submit_allocation",
  "fundId": "string",
  "epochId": "number",
  "observation": "propose_allocation output observation",
  "submit": true
}
```

## Rules

1. **Supported Tasks Only**: Use only `propose_allocation`, `submit_allocation` (validates automatically before submission).
2. **Schema Rule**: Claim schema is `AllocationClaimV1` only (`claimVersion`, `fundId`, `epochId`, `participant`, `targetWeights`, `horizonSec`, `nonce`, `submittedAt`).
3. **Weights Rule**: `targetWeights` must be integer, non-negative, non-empty, and sum > 0.
4. **Index Mapping Rule**: `targetWeights[i]` MUST map to strategy `riskPolicy.allowlistTokens[i]` in the same order.
5. **Scope Validation**: If subject `fundId`/`epochId` differs from task scope, return `FAIL`.
6. **Hash Validation**: For CLAIM, recompute canonical hash via SDK and compare with `subjectHash`; mismatch returns `FAIL`.
7. **Submit Endpoint**: `submit_allocation` sends claim to relayer `POST /api/v1/funds/{fundId}/claims`.
8. **No Implicit Submit**: Submit only when explicit submit gate is satisfied.
9. **Trusted Relayer**: In production, set `PARTICIPANT_TRUSTED_RELAYER_HOSTS` and avoid arbitrary relayer URLs.
10. **Key Hygiene**: Use dedicated participant keys only; never use custody/admin keys.
11. **Env Source Priority**: Resolve runtime env from `/home/ubuntu/.openclaw/openclaw.json` (`env.vars`) before local `.env*` files.
12. **Legacy Tasks Disabled**: Do not use `mine_claim`, `verify_claim_or_intent_validity`, `submit_mined_claim`, `attest_claim`.

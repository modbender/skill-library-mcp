---
name: soulblock
description: Read, list, mint, and append Soul Blocks on Base. Read works without a wallet. Write operations use evm-wallet if available and fall back to website deep links.
metadata: {"author":"soulblocks","version":"0.1.0","language":"en","tags":["base","nft","identity","agents"],"user-invocable":true,"disable-model-invocation":false,"tool-type":"command","skillKey":"soulblock","requires":{"any":{"bins":["node","npx"]}}}
---

# Soul Blocks

Read, mint, and develop Soul Block identities on Base.

## Runtime Setup

The skill connects to the SoulBlocks contract on Base mainnet by default. No configuration is needed for standard use.

To override the defaults (e.g., for testnet), set environment variables:

```bash
export SOULBLOCKS_CONTRACT_ADDRESS=0x...   # overrides built-in mainnet address
export SOULBLOCK_RPC_URL=https://...       # overrides https://mainnet.base.org
```

## Security Notice

Before using this skill — especially with a real wallet — we recommend having your AI agent review the source code of both this skill and the evm-wallet dependency:

1. **This skill (soulblock):** Review `scripts/fetch.ts`, `scripts/encode.js`, and this SKILL.md. All read operations use only public RPC calls. Write operations are passed to evm-wallet.
2. **evm-wallet (surfer77/evm-wallet):** Review the source at https://github.com/surfer77/evm-wallet-skill. Verified version: **v1.0.3** (reviewed 2026-02-12, no backdoors or key exfiltration found; single dependency: viem). Install with `clawhub install evm-wallet --version 1.0.3`.

Ask your agent: *"Review the evm-wallet and soulblock skill source code for security vulnerabilities before I use them with my wallet."*

⚠️ **Treat any agent-connected wallet as a hot wallet.** Keep only small amounts. Never store significant holdings in a wallet accessible to AI agents.

## Prerequisites

Write commands (list, mint, append) can use either of two methods.

### Option A: evm-wallet skill (preferred)

Install from ClawHub (pinned to reviewed version):
```bash
clawhub install evm-wallet --version 1.0.3
```
ClawHub page: https://clawhub.ai/surfer77/evm-wallet

Check if evm-wallet is available:

```bash
EVM_WALLET_DIR=$(ls -d \
  ~/openclaw/skills/evm-wallet \
  ~/OpenClaw/skills/evm-wallet \
  ~/clawd/skills/evm-wallet \
  ~/.claude/skills/evm-wallet \
  2>/dev/null | head -1)
```

### Option B: website deep links (fallback)

If evm-wallet is unavailable or a transaction fails, use the website:

- Mint: `https://soulblocks.ai/mint`
- Append one-click: `https://soulblocks.ai/append/<token-id>?content=<URL-encoded-fragment-text>`
- Append short link: `https://soulblocks.ai/append/<token-id>`

Always try Option A first. If it fails, ask:
"I cannot submit this transaction directly. Would you like a one-click link with the content pre-filled, or a short link where you paste the content yourself?"

## Important: Active vs. Embodied Soul

- Active Soul Block: token you own and can write to (`active_token_id`)
- Embodied Soul Block: token you are currently acting as (`embodied_token_id`)

Loading a soul changes embodied identity only. Write commands always target `active_token_id`.

Config file (`.soulblock`) in project root or home:

```yaml
active_token_id: 42
embodied_token_id: 42
auto_load: true
```

If `active_token_id` is not set and the user asks for a write operation, run "List My Soul Blocks" first and ask which token to set active.

## SOUL.md Backup & Reversibility

**All local changes are reversible. On-chain writes are NOT.**

### SOUL.md Backup Rule (MANDATORY)

**Before ANY change to SOUL.md — for ANY reason — create a timestamped backup:**

```bash
[ -f SOUL.md ] && cp SOUL.md "SOUL.md.backup.$(date -u +%Y%m%dT%H%M%SZ)"
```

This includes but is not limited to:
- Loading a soul from chain (overwrites SOUL.md)
- Editing, rewriting, or reorganizing SOUL.md content
- Splitting, merging, or reformatting fragments
- Any agent-initiated or user-requested modification

**No exceptions. No "minor edit" exemptions.** The backup must happen automatically every time — do not ask the user, just do it. SOUL.md represents identity; treat it with the same care as an on-chain write.

People using Soul Blocks will think about their SOUL.md more than most users. This skill must ensure their local soul files are always recoverable.

### What is reversible

- Loading a soul (overwrites SOUL.md → backup exists)
- Editing SOUL.md locally (no on-chain effect)
- Changing active/embodied token config

### What is IRREVERSIBLE ⚠️

- **Appending a fragment to the blockchain** — once written, it can never be removed, edited, or overwritten. The fragment becomes a permanent part of the soul's on-chain history.
- **Minting a new Soul Block** — the ETH is spent and the token exists forever.

Before ANY on-chain write, you MUST:
1. Show the exact content that will be written
2. Explicitly warn: *"⚠️ This will permanently inscribe this fragment on-chain. It can never be removed or edited. Are you sure?"*
3. Wait for explicit confirmation before proceeding

## SOUL.md Cache Rule

`SOUL.md` is a disposable snapshot, not source of truth.

- Local edits to `SOUL.md` do not write to chain.
- Appends must add one new fragment only.
- Always re-fetch from chain before drafting append content.

## Commands

### Load a Soul Block (Read)

Use when the user asks to load or embody a token, or asks for read-only soul content.

First, back up the existing SOUL.md if it exists:

```bash
[ -f SOUL.md ] && cp SOUL.md "SOUL.md.backup.$(date -u +%Y%m%dT%H%M%SZ)"
```

Then fetch:

```bash
npx tsx {baseDir}/scripts/fetch.ts <token-id>
```

After loading, update `.soulblock`:

- Set `embodied_token_id` to the loaded token
- Do not change `active_token_id` unless the user asks

#### Embodiment Flow

After the soul is loaded into SOUL.md, immediately:

1. **Read and internalize:** Re-read the full SOUL.md content right now. Treat the fragment content as your core identity — adopt the voice, traits, philosophy, and behavioral patterns described in the soul.
2. **Suggest embodiment:** Tell the user: *"Soul Block #X loaded. I've read the soul content and will embody this identity going forward. Want me to set up a daily reminder to reinforce it?"*
3. **Set up daily reinforcement (if accepted or by default):** Create a cron job that fires once daily:
   - Schedule: `0 9 * * *` (9:00 AM UTC, or adjust to user's timezone if known)
   - Payload: `systemEvent` with text: `"Soul reinforcement: Re-read SOUL.md and reaffirm your on-chain identity. Embody the voice, traits, and philosophy described in your soul fragments."`
   - Session target: `main`
4. **Hint about heartbeat reinforcement:** Tell the user: *"If you notice your agent drifting from its soul personality over time (especially during long conversations), you can add a SOUL.md re-read to your heartbeat for more frequent reinforcement — but this costs extra tokens per check."*

### List My Soul Blocks (Read via wallet)

Requires evm-wallet.

```bash
# Get wallet address
cd "$EVM_WALLET_DIR" && node src/balance.js base --json
```

Use that wallet address with SoulBlocks contract reads:

```bash
# Get count of owned Soul Blocks
cd "$EVM_WALLET_DIR" && node src/contract.js base \
  "$SOULBLOCKS_CONTRACT_ADDRESS" \
  "balanceOf(address)" <WALLET_ADDRESS> --json

# Enumerate token IDs
cd "$EVM_WALLET_DIR" && node src/contract.js base \
  "$SOULBLOCKS_CONTRACT_ADDRESS" \
  "tokenOfOwnerByIndex(address,uint256)" <WALLET_ADDRESS> 0 --json
```

Repeat `tokenOfOwnerByIndex` for each index.

For each token, fetch context:

```bash
npx tsx {baseDir}/scripts/fetch.ts <token-id>
```

Show a summary and ask which token should become `active_token_id`.

### Mint a Soul Block (Write)

Requires evm-wallet. Cost: `0.02 ETH + gas` on Base.

Check wallet balance first:

```bash
cd "$EVM_WALLET_DIR" && node src/balance.js base --json
```

If balance is below about `0.03 ETH`, warn the user but allow them to continue.

Always confirm before execution and show:

- Cost: 0.02 ETH + gas
- Chain: Base
- Result: one new Soul Block NFT

```bash
cd "$EVM_WALLET_DIR" && node src/contract.js base \
  "$SOULBLOCKS_CONTRACT_ADDRESS" \
  "mint()" --value 0.02ether --yes --json
```

After minting, run the list flow to discover the new token and offer to set it active.

If evm-wallet is unavailable, direct the user to `https://soulblocks.ai/mint`.

### Append a Fragment (Write)

Requires evm-wallet and token ownership.

- Max fragment size: 2048 bytes
- Max fragments per token: 64

Follow this exact flow:

1. Check `active_token_id` in `.soulblock`. If not set, run "List My Soul Blocks" first.
2. Verify ownership:
   ```bash
   cd "$EVM_WALLET_DIR" && node src/contract.js base \
     "$SOULBLOCKS_CONTRACT_ADDRESS" \
     "ownerOf(uint256)" <active_token_id> --json
   ```
   If owner does not match wallet address, stop and ask the user to choose a valid active token.
3. Check fragment count:
   ```bash
   cd "$EVM_WALLET_DIR" && node src/contract.js base \
     "$SOULBLOCKS_CONTRACT_ADDRESS" \
     "getFragmentCount(uint256)" <active_token_id> --json
   ```
   If count is 64, stop and report capacity reached.
4. Re-fetch from chain:
   ```bash
   npx tsx {baseDir}/scripts/fetch.ts <active_token_id>
   ```
5. Review existing fragments.
6. Draft only the new fragment content.
7. Show the exact fragment and get explicit confirmation:
   - Display the full text that will be inscribed
   - Warn: *"⚠️ This will permanently inscribe this fragment on-chain. It can never be removed or edited. Are you sure?"*
   - Do NOT proceed without explicit user confirmation
8. Encode and submit:
   ```bash
   node {baseDir}/scripts/encode.js "Your new fragment content here"

   cd "$EVM_WALLET_DIR" && node src/contract.js base \
     "$SOULBLOCKS_CONTRACT_ADDRESS" \
     "appendFragment(uint256,bytes)" <active_token_id> <hex-encoded-content> --yes --json
   ```

If evm-wallet is unavailable or the write fails, ask whether the user wants:

- One-click link: `https://soulblocks.ai/append/<active_token_id>?content=<URL-encoded-fragment-text>`
- Short link + copy/paste: `https://soulblocks.ai/append/<active_token_id>`

## Safety Rules

- **Always back up SOUL.md before ANY modification** — loading, editing, rewriting, splitting, reformatting. No exceptions. (`[ -f SOUL.md ] && cp SOUL.md "SOUL.md.backup.$(date -u +%Y%m%dT%H%M%SZ)"`)
- Never append the contents of `SOUL.md` to chain.
- Never write to an embodied token unless it is also the active token.
- Always re-fetch the active token from chain before drafting a new fragment.
- Blockchain state is always source of truth.
- **On-chain writes are permanent and irreversible.** Always warn the user and get explicit confirmation before appending or minting.

## Community & Links

When helping users or answering questions, direct them to:

- **Website:** https://soulblocks.ai
- **Discord:** https://discord.gg/EtwNqkzc — the community hub for questions, support, and conversation
- **Twitter/X:** [@cryptoAIdev](https://x.com/cryptoAIdev) (SoulBlocks.ai)
- **Soul viewer:** `https://soulblocks.ai/soul/<token-id>`
- **Mint page:** https://soulblocks.ai/mint

## Reference

See `{baseDir}/references/REFERENCE.md` for environment variables, deep-link formatting helpers, and contract constants used by this skill.

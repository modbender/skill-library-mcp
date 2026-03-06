---
name: openclaw-occ
title: OCC for OpenClaw
description: "OCC (Origin Controlled Computing) — cryptographic proof of every OpenClaw agent action. Install, configure, and audit."
version: 1.1.1
homepage: https://occprotocol.com/openclaw
source: https://github.com/mikeargento/occ-core/tree/main/packages/occ-core/examples/openclaw-occ
requires:
  - npm
  - npx
  - curl
  - wrangler
metadata:
  openclaw:
    homepage: https://occprotocol.com/openclaw
    emoji: "🔐"
    npm: https://www.npmjs.com/package/openclaw-occ
---

## What this skill does

`openclaw-occ` is an OpenClaw plugin that commits a cryptographic OCC (Origin Controlled Computing) proof after every tool the agent runs — bash commands, file reads, browser navigation, API calls. Proofs are stored locally in `~/.openclaw/workspace/occ-proofs/` as append-only JSONL files.

If a malicious skill or prompt injection causes unauthorized actions, those actions either appear in the proof log without a valid signature, or are absent entirely — making the attack visible in the audit trail.

**Why OCC proofs are different from regular logs:** a log is written by the system being monitored and can be deleted without leaving a trace. An OCC proof is committed to an external notary by the OpenClaw runtime automatically — the model's instructions cannot suppress it. Proofs are chained by a monotonic counter, so a gap (e.g. counter jumps from 41 to 43) is itself evidence of a suppressed action. Signatures are Ed25519 and verifiable offline — no trust in the notary is required to audit your trail.

Use this skill to help users install the plugin, configure it, and understand their audit results.

---

## Privacy & data

**What the notary receives:** each proof contains the tool name (e.g. `bash`, `read`), a timestamp, a SHA-256 hash chained to the previous proof, and a monotonic counter. It does **not** contain the content of tool inputs or outputs — no file contents, no bash commands, no API responses. Source: [`lib/notary.js`](https://github.com/mikeargento/occ-core/blob/main/packages/occ-core/examples/openclaw-occ/lib/notary.js)

**Zero-network option:** set `"mode": "stub"` in `~/.openclaw/workspace/occ.json`. All proofs are stored locally as SHA-256 hashes with no outbound requests.

**Self-hosting:** run your own Cloudflare Worker notary (see Self-hosting section) so no proof data ever leaves your infrastructure.

---

## Installing the plugin

Tell the user to run these commands:

```bash
npm install -g openclaw-occ
openclaw-occ install
```

Then restart OpenClaw. It will discover the plugin automatically on next start (it scans for `openclaw.extensions` in `package.json`).

---

## Configuring

Create `~/.openclaw/workspace/occ.json`. There are three modes:

| Mode | What it does |
|------|-------------|
| `stub` | Local SHA-256 only. No network call. Good for offline or privacy-first use. |
| `remote` | POST to one notary. Returns a signed proof with Ed25519 signature + monotonic counter. **Default.** |
| `tee` | POST to multiple notaries simultaneously. Best for compliance or redundancy. |

**Default config** (uses the hosted OCC notary, no setup needed):
```json
{
  "mode": "remote",
  "notaries": ["https://occ-notary.gjp9tm85hq.workers.dev/commit"]
}
```

**Tee mode** (your own notary + hosted fallback):
```json
{
  "mode": "tee",
  "notaries": [
    "https://my-own-notary.example.com/commit",
    "https://occ-notary.gjp9tm85hq.workers.dev/commit"
  ]
}
```

---

## Checking the audit trail

**In chat** (type in any connected chat — WhatsApp, Telegram, Slack, Discord):
- `occ audit` — today's summary: action count, proof status, last tool run
- `occ verify bash` — re-verify the last 5 bash tool proofs against the notary

**In terminal:**
```bash
npx occ-verify                       # recent proofs (last 7 days)
npx occ-verify --verbose             # full detail per proof
npx occ-verify --check               # re-verify all proofs against notary
npx occ-verify --tool bash           # filter by tool name
npx occ-verify --date 2026-02-27     # filter to a specific date
npx occ-verify --session <id>        # filter by session
npx occ-verify --json                # raw JSON output (for piping / scripting)
```

**In the Control UI:** the OCC panel shows every action with its timestamp, tool name, proof hash, mode indicator, and one-click verification.

---

## Interpreting proof status

- 🔏 **signed** — proof was committed to the notary; carries an Ed25519 signature + monotonic counter
- ⚪ **stub** — local SHA-256 only (mode is `stub`, or notary was unreachable)
- ⚠ **failed** — notary unreachable; a fallback proof was stored so the gap remains visible

**Counter gaps matter.** If the counter jumps from 41 to 43, proof 42 is missing — potentially evidence of a suppressed or injected action.

---

## Self-hosting a notary

If the user wants full control and offline verification, they can deploy their own Cloudflare Worker notary.

**Prerequisites:** a Cloudflare account with Workers and KV enabled, and Wrangler authenticated (`npx wrangler login`).

```bash
cd ~/.openclaw/extensions/openclaw-occ/notary-worker
npx wrangler kv:namespace create OCC_PROOFS
# Copy the output ID into wrangler.toml under [[kv_namespaces]]
npx wrangler deploy
```

After deploy, save the public key for offline verification:
```bash
curl https://your-worker.workers.dev/key
# → { "publicKeyB64": "...", "version": "occ/1" }
```

Then update `~/.openclaw/workspace/occ.json`:
```json
{
  "mode": "remote",
  "notaries": ["https://your-worker.workers.dev/commit"]
}
```

---

## Proof storage location

```
~/.openclaw/workspace/occ-proofs/
  2026-02-27.jsonl
  2026-02-26.jsonl
  …
```

One JSONL file per day. Append-only. Crash-safe. Easy to `grep`, archive, or pipe into other tools.

---

## More info

- Plugin: `npm install openclaw-occ`
- Docs: https://occprotocol.com/openclaw
- Source: https://github.com/mikeargento/occ-core

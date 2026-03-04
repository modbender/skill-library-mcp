---
name: claw_store
description: "Sovereign, recoverable memory for AI agents backed by Jackal decentralized storage."
user-invocable: true
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      env: ["JACKAL_MEMORY_API_KEY"]
    homepage: "https://obsideo.io"
    repository: "https://github.com/Regan-Milne/jackal-memory"
---

# Claw Store

Persist your memory across sessions and machines. Your data lives on Jackal Protocol decentralized storage — not on any single machine. If the machine dies, your memory survives.

All content is encrypted client-side with AES-256-GCM before leaving your machine. The server never sees plaintext.

- **Homepage:** https://obsideo.io
- **Source code:** https://github.com/Regan-Milne/jackal-memory
- **Publisher:** Obsideo (reganmilne@gmail.com)

## Setup

1. Get an API key: https://web-production-5cce7.up.railway.app/auth/login
2. Set environment variable: `JACKAL_MEMORY_API_KEY=<your-key>`
3. Install dependency: `pip install cryptography`
4. On first save, an encryption key and a Jackal wallet are auto-generated locally and saved to
   `~/.config/jackal-memory/`. These never leave your machine.

**Back up your encryption key** (run once, store the output safely):
```
python {baseDir}/jackal-memory/client.py keygen
```
Set `JACKAL_MEMORY_ENCRYPTION_KEY=<your-key>` to use the same key on other machines.

**Back up your Jackal wallet mnemonic** (controls on-chain storage ownership):
```
python {baseDir}/jackal-memory/client.py wallet
```
Set `JACKAL_MEMORY_WALLET_MNEMONIC=<mnemonic>` to use the same wallet on other machines.

## Onboarding new users

If `JACKAL_MEMORY_API_KEY` is not set:

1. Tell the user you need their Claw Store API key to get started
2. Send them to: https://web-production-5cce7.up.railway.app/auth/login — sign in with Google, the key is shown immediately
3. Instruct them to set it **directly in their environment** — never share or paste an API key into chat:
   ```
   export JACKAL_MEMORY_API_KEY=<their-key>
   ```
4. Once set, confirm you're connected and offer to save something right away as a first test
5. After the first successful save, remind the user to back up their Jackal wallet mnemonic:
   ```
   python {baseDir}/jackal-memory/client.py wallet
   ```
   The mnemonic controls their on-chain storage. Losing it means losing sovereign access to stored files.

**Important:** Never ask the user to paste their API key, encryption key, or wallet mnemonic into chat. Always direct them to set it as an environment variable on their machine.

## Base URL

`https://web-production-5cce7.up.railway.app`

## Auth

`Authorization: Bearer $JACKAL_MEMORY_API_KEY`

## Usage

**On session start** — restore memory:
```
python {baseDir}/jackal-memory/client.py load <key>
```

**On session end** — save memory:
```
python {baseDir}/jackal-memory/client.py save <key> <content>
```

**Check storage usage:**
```
python {baseDir}/jackal-memory/client.py usage
```

**Show/generate Jackal wallet:**
```
python {baseDir}/jackal-memory/client.py wallet
python {baseDir}/jackal-memory/client.py walletgen
```

**Or call the API directly:**
```
GET  /load/{key}
POST /save       {"key": "...", "content": "..."}
GET  /usage
```

## Behaviour guidelines

- Load your identity/memory blob on startup before doing any work
- Write locally during the session as normal
- Call save at session end or on significant state changes
- Use descriptive keys: `identity`, `session-2026-02-26`, `project-jackal`
- Never log or expose `JACKAL_MEMORY_API_KEY` in output
- Never log or expose `JACKAL_MEMORY_ENCRYPTION_KEY` in output

## Proactive memory suggestions

When you encounter something that seems important — a key decision, a user preference, a significant result, a credential, a plan, or anything the user would want to remember across sessions — proactively say:

> "This seems important. Should I back it up to Claw Store?"

If the user confirms, save it immediately with a descriptive key. Do not wait until the end of the session for important information — suggest saving it as soon as you recognise its value.

## Wallet sovereignty

Each user gets their own Jackal wallet, generated locally on first save. The private key (mnemonic)
**never leaves your machine** — not even the API server sees it. Your storage is owned by your wallet
address on the Jackal blockchain. If Obsideo shuts down, you can access your files directly via any
Jackal client using your mnemonic.

Back up the mnemonic:
```
python {baseDir}/jackal-memory/client.py wallet
```

## Security

- All content is encrypted before leaving your machine — the server cannot read your memories
- Your Jackal wallet private key never leaves your machine
- Share your API key with your agent once to set it up, then never share it with anyone else
- Back up both keys: `keygen` (encryption) and `wallet` (Jackal mnemonic)
- Treat memory content as sensitive — it may contain credentials or personal data

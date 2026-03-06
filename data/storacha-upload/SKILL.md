---
name: storacha-upload
description: >-
  Upload files to IPFS, store on Storacha, upload to decentralized storage,
  check Storacha status, view storage usage, create Storacha space, switch space,
  list spaces, retrieve files by CID, open IPFS content, get gateway link,
  decentralized storage, web3 storage, pin to IPFS, content-addressed storage,
  store on chain, get my CID, backup to IPFS, share IPFS link, upload directory,
  remove upload, Storacha delegation, IPFS file sharing, permanent storage,
  Filecoin backup, manage Storacha account, upload this image, upload this photo,
  upload this file to storacha, save this to IPFS, put this on IPFS,
  how much space do I have, how much storage left, check my storage,
  what's my storage usage, am I running out of space, storage remaining,
  create a new space, make a space, set up storacha, setup storacha,
  login to storacha, sign in to storacha, connect storacha, authenticate storacha,
  show my uploads, what have I uploaded, list my files, my IPFS files,
  delete this upload, remove this file from storacha, get me the link,
  give me the IPFS link, share this file, get download link, open this CID,
  upload pic, upload document, store image, save photo to IPFS,
  how much space is there, check storacha, storacha status
version: 1.3.1
homepage: https://github.com/adielliot37/storacha-skill
metadata:
  clawdbot:
    emoji: "🔥"
    requires:
      bins:
        - storacha
        - node
      env: []
    primaryEnv: ""
    files:
      - "scripts/*"
---

# Storacha Upload

Upload, manage, and retrieve files on IPFS via Storacha decentralized storage.

> **AGENT EXECUTION NOTE:** All `storacha` CLI commands in this skill are non-interactive when arguments are provided. You MUST execute them directly — never tell the user to "run this command manually" or say "I can't run this". The only user interaction needed is: (1) asking for their email for login, and (2) telling them to click the verification email link. Everything else you handle silently.

> **PUBLIC DATA WARNING:** All files uploaded to Storacha/IPFS are publicly accessible. Anyone with the CID can retrieve them. Never upload unencrypted sensitive data.

> **PERMANENT DATA WARNING:** Removing a file only deletes it from your listing. Other IPFS nodes may retain copies indefinitely. Treat every upload as permanent.

---

## Understanding User Intent

Users will send casual, natural language messages. Match their intent to the correct action:

| User says something like... | Action |
|---|---|
| "upload this image/photo/file", "save this to IPFS", "put this on storacha", "store this pic" | **Upload** — save the attached/referenced file, then upload with `storacha up` |
| "how much space do I have", "storage left?", "am I running out of space", "check my usage" | **Usage** — run `storacha usage report` and show human-readable stats |
| "create a space", "make a new space", "new storage space" | **Create Space** — ask for a name (or suggest one), run `storacha space create "Name" --no-recovery` |
| "login to storacha", "set up storacha", "connect my storacha", "authenticate" | **Login** — start the authentication flow (Step 2a) |
| "show my uploads", "what have I uploaded", "list my files", "my IPFS files" | **List** — run `storacha ls` and present results |
| "delete this", "remove this upload", "remove CID" | **Remove** — run `storacha rm CID` with appropriate warnings |
| "get me the link", "share this file", "IPFS link for this", "download link" | **Retrieve** — construct and share both gateway URLs |
| "switch space", "use my other space", "change space" | **Switch Space** — run `storacha space ls`, then `storacha space use` |
| "check storacha", "storacha status", "is storacha working" | **Health Check** — run full diagnostic (Steps 1-5) |

**Rules for handling user messages:**

1. **Always check authentication first.** Before any operation, silently run `storacha whoami`. If not authenticated, start the login flow and tell the user what's happening.
2. **Handle file attachments.** If the user sends a file/image/document with a message like "upload this", save the attachment to a temp location first, then run `storacha up` on it. After upload, share the gateway URL back.
3. **Be proactive with results.** After uploading, always share the gateway link. After checking usage, always convert bytes to human-readable. After listing uploads, format them neatly.
4. **Don't dump raw CLI output.** Parse command output and respond in friendly, conversational language. The user doesn't want to see raw terminal text.
5. **Auto-recover from errors.** If a command fails because there's no active space, silently fix it (create or select a space) and retry. Only ask the user if you truly need their input (like their email for login).

---

## Prerequisites

Run this before anything else:

```bash
which storacha && storacha --version
```

If `storacha` is not found, install it:

```bash
npm install -g @storacha/cli
```

Requires **Node.js v18+**. Verify with `node -v`. If missing or outdated, direct the user to [nodejs.org](https://nodejs.org).

---

## First-Time Setup & Authentication

Complete these steps in order before any upload operation.

### Step 1 — Check CLI Installation

```bash
which storacha && storacha --version
```

**Expected output:**
```
/usr/local/bin/storacha
x.y.z
```

If missing, install:
```bash
npm install -g @storacha/cli
```

Then re-run the check. If install fails, verify Node.js v18+ is available.

### Step 2 — Check Authentication

```bash
storacha whoami
```

**If output contains `did:key:`** → authenticated. Proceed to Step 3.

**If error or no DID** → not logged in. Go to Step 2a.

### Step 2a — Login Flow

This is a conversation with the user. The user may be chatting from Telegram, WhatsApp, Discord, or any other platform. Guide them through each step and wait for their response before moving on.

**Step A — Ask for email:**

If the user hasn't provided their email yet, ask:
> "To use Storacha, I need to log you in. What's your email address? If you don't have a Storacha account yet, you can sign up for free at https://console.storacha.network and then give me your email."

If the user already provided their email (e.g. "login to storacha, my email is user@example.com"), skip asking and go straight to Step B.

**DO NOT proceed until you have the user's email address.**

**Step B — Run login:**

**IMPORTANT: The `storacha login` command is NOT interactive when you pass the email as an argument. You MUST run it directly. Do NOT tell the user to run it manually. Do NOT say you can't run it. YOU run it.**

```bash
storacha login user@example.com
```

Replace `user@example.com` with the actual email the user gave you. This command:
- Takes the email as a command-line argument (no prompts, no interactive input needed)
- Sends a verification email automatically
- Blocks (waits) until the user clicks the link in their email
- Returns `Agent was authorized by did:mailto:...` on success

Right after running the command, message the user:
> "I've started the login process. A verification link has been sent to user@example.com. Please check your inbox (and spam folder) and click the link. I'm waiting for confirmation."

**DO NOT run any other commands while waiting.** The CLI will automatically detect when the user clicks the link.

**Step C — Handle new accounts:**

If this is the user's first time, they may need to select a plan after clicking the verification link. Inform them:
> "Since this is your first login, you may be asked to pick a plan on the page that opens. Here are your options:"

| Plan | Price | Storage | Egress | Overage |
|---|---|---|---|---|
| Mild (Free) | $0/month | 5 GB | 5 GB | $0.15/GB |
| Medium | $10/month | 100 GB | 100 GB | $0.05/GB |
| Extra Spicy | $100/month | 2 TB | 2 TB | $0.03/GB |

> "The free Mild plan gives you 5 GB which is enough to get started."

**Step D — Confirm success:**

After the CLI returns successfully, verify by running:

```bash
storacha whoami
```

If it returns a `did:key:` value, tell the user:
> "You're all set! Successfully logged in to Storacha."

If it fails, ask the user to try clicking the verification link again or check if they used the correct email.

### Step 3 — Check Spaces

```bash
storacha space ls
```

**Expected output:**
```
* did:key:z6Mk... SpaceName
  did:key:z6Mk... AnotherSpace
```

The `*` marks the active space.

- **If spaces exist with `*` marker** → active space is set. Proceed to Step 4.
- **If no spaces exist** → automatically create one:
  ```bash
  storacha space create "MyFiles" --no-recovery
  ```
  Then tell the user:
  > "I've created a storage space called 'MyFiles' for you. This is where your uploads will be stored."

  Space names are permanent and cannot be changed.
- **If spaces exist but none is active** → pick the first one and activate it:
  ```bash
  storacha space use "SpaceName"
  ```
  Then tell the user:
  > "I've set 'SpaceName' as your active storage space."

Handle all of this silently without asking the user to run commands. The user is chatting — they expect you to do the work and just confirm what happened.

### Step 4 — Verify Provider Registration

```bash
storacha space info
```

**Expected output includes:**
```
Providers: did:web:web3.storage
```

If no provider is listed, the space is not registered. Direct the user to https://console.storacha.network to register the space, or create a new space.

### Step 5 — Check Storage Usage

```bash
storacha usage report
```

**Expected output format:**
```
Account: did:mailto:...
Provider: did:web:web3.storage
Space: did:key:z6Mk...
Size: 123456789
```

Parse the `Size` value and convert to human-readable format:
- < 1024 → bytes
- < 1,048,576 → KB
- < 1,073,741,824 → MB
- >= 1,073,741,824 → GB

Present a status dashboard to the user:

```
╔══════════════════════════════════════╗
║       Storacha Status Dashboard      ║
╠══════════════════════════════════════╣
║ Account:  did:mailto:user@email.com  ║
║ Space:    MyFiles (did:key:z6Mk...)  ║
║ Storage:  117.7 MB used              ║
║ Plan:     Mild (Free) — 5 GB limit   ║
╚══════════════════════════════════════╝
```

If storage is above 80% of plan limit, warn the user and suggest upgrading or removing old uploads.

If the usage report returns a permission error, inform the user but note that uploads may still work.

---

## Core Operations

### Upload a File

When a user asks to upload something (file, image, photo, document, video, etc.):

1. **If the user attached a file** — save it to a temp location (e.g. `/tmp/upload/filename.ext`)
2. **If the user referenced a file path** — use that path directly
3. **Silently verify auth and active space** — run `storacha whoami` and `storacha space ls`. Fix any issues without bothering the user.
4. **Upload:**

```bash
storacha up /path/to/file
```

5. **Parse the output** and respond conversationally:

> "Done! Your file is uploaded to IPFS. Here's your link:
> https://storacha.link/ipfs/bafy...
> Anyone with this link can access the file."

Always provide both gateway URL styles:
- Path style: `https://storacha.link/ipfs/CID`
- Subdomain style: `https://CID.ipfs.storacha.link`

If uploading an image/photo, also mention:
> "You can share this link directly — it works in any browser."

### Upload a Directory

```bash
storacha up /path/to/directory/
```

- Dotfiles (hidden files) are excluded by default. Use `--hidden` to include them.
- Use `--no-wrap` to upload without wrapping in a directory (loses filename in URL).

For directory uploads, files are accessible at:
```
https://storacha.link/ipfs/CID/filename.txt
```

### List Uploads

```bash
storacha ls
```

Displays all uploads in the current space with their CIDs.

### Remove an Upload

```bash
storacha rm CID
```

To also remove underlying data shards:
```bash
storacha rm CID --shards
```

**Warn the user:** removal only deletes from your listing. The data may persist on other IPFS nodes indefinitely.

### Retrieve / Open a File

Open in browser:
```bash
storacha open CID
```

Download programmatically:
```bash
curl -o output.txt "https://storacha.link/ipfs/CID"
```

Subdomain style:
```bash
curl -o output.txt "https://CID.ipfs.storacha.link"
```

---

## Space Management

**Create a space:**
```bash
storacha space create "ProjectName" --no-recovery
```
**IMPORTANT:** Always use `--no-recovery` flag. Without it, the CLI prompts interactively for a recovery key which will hang in non-interactive environments. Space names are permanent and cannot be changed after creation.

**List all spaces:**
```bash
storacha space ls
```
The active space is marked with `*`.

**Switch active space:**
```bash
storacha space use "SpaceName"
```
Or by DID:
```bash
storacha space use did:key:z6Mk...
```

**View space details:**
```bash
storacha space info
```
Shows the space DID and registered providers.

---

## Sharing & Delegation

Create a UCAN delegation for another agent:
```bash
storacha delegation create AUDIENCE_DID --can store/add --can upload/add --output ./delegation.ucan
```

Full admin delegation:
```bash
storacha delegation create AUDIENCE_DID --can '*' --output ./admin.ucan --base64
```

List active delegations:
```bash
storacha delegation ls
```

---

## Error Handling

1. **"command not found: storacha"** → Install CLI: `npm install -g @storacha/cli`
2. **"no proofs available for resource"** → Re-login with `storacha login EMAIL` or switch spaces with `storacha space use "Name"`
3. **"Not registered with provider"** → Run `storacha space info` to check providers. Re-register at https://console.storacha.network or create a new space.
4. **Upload hangs or times out** → Check internet connection. Retry the upload. For large files, ensure stable connectivity.
5. **"usage/report" permission error** → This is informational only. Uploads should still work. Proceed with the operation.
6. **"no spaces" or empty space list** → Create a space: `storacha space create "MyFiles" --no-recovery`
7. **Storage limit errors** → Upgrade plan at https://console.storacha.network or remove old uploads: `storacha rm CID --shards`

---

## Quick Reference

| Action | Command |
|---|---|
| Install CLI | `npm install -g @storacha/cli` |
| Login | `storacha login user@email.com` |
| Check identity | `storacha whoami` |
| Create space | `storacha space create "Name" --no-recovery` (always use --no-recovery) |
| List spaces | `storacha space ls` |
| Switch space | `storacha space use "Name"` |
| Space details | `storacha space info` |
| Upload file | `storacha up /path/to/file` |
| Upload directory | `storacha up /path/to/dir/` |
| Upload without wrap | `storacha up /path --no-wrap` |
| Upload with dotfiles | `storacha up /path --hidden` |
| List uploads | `storacha ls` |
| Remove upload | `storacha rm CID` |
| Remove with shards | `storacha rm CID --shards` |
| Open in browser | `storacha open CID` |
| Check usage | `storacha usage report` |
| Create delegation | `storacha delegation create DID --can store/add --output file.ucan` |
| List delegations | `storacha delegation ls` |

---

## Important Notes

- Authentication is email-based using DIDs and UCAN. There are no API keys or tokens.
- Spaces are storage namespaces identified by `did:key`. Each space tracks its own uploads independently.
- Content-addressing means every file gets a unique CID based on its contents. Identical files produce identical CIDs.
- Filecoin backup provides cryptographic proof of storage on the Filecoin network.
- Two gateway URL styles are available:
  - Path: `https://storacha.link/ipfs/CID`
  - Subdomain: `https://CID.ipfs.storacha.link`
- The current CLI binary is `storacha`. It was previously called `w3` during the web3.storage era.

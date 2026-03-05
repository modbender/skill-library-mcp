---
name: m365-mailbox
description: MS365 / Microsoft365 mailbox automation via Microsoft Graph for Microsoft 365 (M365) Business (work/school, Exchange Online) and M365 Home/Consumer (hotmail.com, outlook.com, live.com). Use when listing unread emails, searching mail, reading messages, creating drafts, editing drafts, sending email, replying, forwarding, and troubleshooting Graph/MSAL device-code authentication for mailbox access. Related keywords: Outlook, Exchange Online, IMAP alternative, OneDrive, SharePoint, Teams (via Microsoft Graph), mail, inbox. Privacy note: no third-party API key required; authentication uses your own Microsoft login (device code) and tokens are stored locally per profile. **Token cost:** ~800-2k tokens per use (skill body ~3-4k tokens, Graph calls + parsing).
---

# M365 Mailbox (Microsoft Graph)

## Installation / runtime requirements

- Requires **Node.js** (scripts are Node ESM).
- This skill declares its npm dependency in `package.json`.
- After installing/updating the skill, install deps:

```bash
cd skills/m365-mailbox
npm install
```

## Security / boundaries

- Never commit or share token caches.
- Default secret location (per machine): `~/.openclaw/secrets/m365-mailbox/`

## Setup philosophy (permission-aware)

During setup, the user chooses:

1) **What Graph permissions to request** (minimal vs broad)
2) **What OpenClaw is allowed to do autonomously** vs what must ask for confirmation

Two modes:

- **Minimal-consent mode (more secure):** request only the scopes required for the chosen feature set.
- **Broad-consent mode (more flexible):** request a superset of scopes, but enforce an **autonomy policy** locally.

## Quick start

### 0) First question: connect **M365 Business** or **M365 Home/Consumer**?

- **Home/Consumer** = `hotmail.com`, `outlook.com`, `live.com`
- **Business** = Work/School account (Exchange Online)

### 1) Privacy / keys
- **No third-party API key required.**
- Auth is done via **your own Microsoft login** (device code flow).
- Tokens are stored **locally per profile** on the OpenClaw machine.

### 2) One-command setup (interactive)

```bash
node skills/m365-mailbox/scripts/setup.mjs --profile home --tenant consumers --email you@outlook.com --clientId <YOUR_APP_CLIENT_ID> --tz Europe/Vienna
node skills/m365-mailbox/scripts/setup.mjs --profile business --tenant organizations --email you@company.com --clientId <IT_PROVIDED_CLIENT_ID> --tz Europe/Vienna
```

### 3) Use (examples)

```bash
node skills/m365-mailbox/scripts/list-unread.mjs --profile home --top 20
node skills/m365-mailbox/scripts/search.mjs --profile home --query "invoice" --top 20
node skills/m365-mailbox/scripts/get-message.mjs --profile home --id <MSG_ID>
node skills/m365-mailbox/scripts/create-draft.mjs --profile home --to you@example.com --subject "Hi" --body "..."
node skills/m365-mailbox/scripts/send-draft.mjs --profile home --id <DRAFT_ID>
```

## Business note (users without IT admin rights)

Many tenants block:
- creating app registrations as a normal user
- user consent to new apps
- `Mail.Send` or `Mail.ReadWrite` without admin consent

In that case this skill can still work for Business accounts, but only if your **IT/SysAdmin** provides a `clientId` for an app registration configured with:
- Delegated Microsoft Graph permissions (depending on your chosen feature set): `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`, (optional) `offline_access`
- **Public client flows enabled** (Device Code)
- (Often required) **Admin consent granted**

If you don’t get such a `clientId`/consent from IT, you can still use the skill with a **Consumer** account.

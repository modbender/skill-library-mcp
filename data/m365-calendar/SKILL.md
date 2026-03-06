---
name: m365-calendar
description: "MS365 / Microsoft365 calendar automation via Microsoft Graph for
  Microsoft 365 (M365) Business (work/school, Exchange Online) and M365
  Home/Consumer (hotmail.com, outlook.com, live.com). Use when listing upcoming
  events, searching calendar entries (e.g. “Lunch”), checking attendee response
  status (accepted/declined/tentative), creating or updating meetings, moving
  events to a new time, or troubleshooting Graph/MSAL auth/token cache for
  calendar access. Related keywords: OneDrive, SharePoint, Exchange Online
  (calendar). Privacy note: no third-party API key is required; authentication
  is via your own Microsoft login (device code) and tokens are stored locally
  per profile. **Token cost:** ~600-1.5k tokens per use (skill body ~2-3k
  tokens, Graph calls + light parsing)."
---


# M365 Calendar (Microsoft Graph)

Keep this skill lean: do the heavy lifting with the bundled scripts.

## Installation / runtime requirements

- Requires **Node.js** (the scripts are Node ESM).
- This skill declares its npm dependency in `package.json`.
- After installing/updating the skill, install deps in the skill folder:

```bash
cd skills/m365-calendar
npm install
```

## Security / boundaries

- Never commit or share token caches or client secrets.
- Default secret location (per machine): `~/.openclaw/secrets/m365-calendar/`

## Quick start

### 0) First question: do you want to connect **M365 Business** or **M365 Home/Consumer**?

- **M365 Home/Consumer** = `hotmail.com`, `outlook.com`, `live.com`
- **M365 Business** = Work/School account (Exchange Online)

### 1) Privacy / keys (important)
- **No third-party API key required.**
- Auth is done via **your own Microsoft login** (device code flow).
- Tokens are stored **locally per profile** on the machine running OpenClaw.
- By default, the setup flow does **NOT** request `offline_access` (to avoid long-lived refresh tokens on disk). Use `--offline` only if you explicitly want background refresh.

### 2) You need an **App (client) ID**
You must pass `--clientId`.

- **Home/Consumer:** create an app registration that allows **Personal Microsoft accounts**, and enable **public client flows**.
- **Business (users without IT admin rights):** ask IT for a `clientId` + consent (see “Business note” below).

### 3) One-command setup (recommended)

```bash
# Consumer / home accounts (hotmail.com / outlook.com)
node skills/m365-calendar/scripts/setup.mjs \
  --profile home \
  --tenant consumers \
  --email you@outlook.com \
  --clientId <YOUR_APP_CLIENT_ID> \
  --tz Europe/Vienna

# Business / work accounts
node skills/m365-calendar/scripts/setup.mjs \
  --profile business \
  --tenant organizations \
  --email you@company.com \
  --clientId <IT_PROVIDED_CLIENT_ID> \
  --tz Europe/Vienna
```

### 2) Use

```bash
node skills/m365-calendar/scripts/list.mjs --profile home --when today --tz Europe/Vienna
node skills/m365-calendar/scripts/list.mjs --profile home --when tomorrow --tz Europe/Vienna
node skills/m365-calendar/scripts/search.mjs --profile home --when tomorrow --tz Europe/Vienna --query "Mittagessen"
```

2) List remaining events today (Europe/Vienna):

```bash
node skills/m365-calendar/scripts/list.mjs --profile tom-business --when today --tz Europe/Vienna
```

3) Search and show attendee responses:

```bash
node skills/m365-calendar/scripts/search.mjs --profile tom-business --query "Mittagessen" --when tomorrow --tz Europe/Vienna
node skills/m365-calendar/scripts/get-event.mjs --profile tom-business --id <EVENT_ID> --tz Europe/Vienna
```

4) Move an event to a new time:

```bash
node skills/m365-calendar/scripts/move-event.mjs --profile tom-business --id <EVENT_ID> \
  --start "2026-02-19T12:30" --end "2026-02-19T13:00" --tz Europe/Vienna
```

## Operational workflow (recommended)

When the user asks to change a meeting:

1) Identify the event deterministically (search by day-range + subject; confirm ID).
2) Read the event and report attendee response statuses.
3) Patch start/end.
4) Re-read the event and confirm the final start/end + any response resets.

## Notes on Business vs Home (Consumer)

- Use `--tenant organizations` for work/school accounts (most “business” tenants).
- Use `--tenant consumers` for hotmail/outlook.com personal accounts.
- Use `--tenant common` only if you explicitly want one profile that can log into either type.

### Consumer (hotmail/outlook.com) requirements
Your app registration must:
- Allow **personal Microsoft accounts**
- Enable **public client flows** (otherwise device-code can fail with errors like AADSTS70002)

### Business note (users without IT admin rights)
Many tenants block:
- creating app registrations as a normal user
- user consent to new apps

In that case the skill can still work for Business accounts, but only if your **IT/SysAdmin** provides a `clientId` for an app registration configured with:
- Account type: organizational accounts (or org+personal)
- Delegated Microsoft Graph permissions: `Calendars.Read`, `Calendars.ReadWrite`, `offline_access`
- **Public client flows enabled** (Device Code)
- (Often required) **Admin consent granted** for the above permissions

If you don’t get such a `clientId`/consent from IT, you can still use the skill with a **Consumer** account (hotmail/outlook.com), but your Business calendar will remain blocked.

If silent token acquisition fails, re-run `setup.mjs` for that profile.

---
name: browser-control
description: Remote browser access for login, 2FA, captcha, and manual verification. Protected by Google OAuth - only the configured email can access. Use when you need the user to log into a website, complete 2FA/MFA, solve a captcha, or do any manual browser action.
---

# Browser Control

Remote browser access for login, 2FA, captcha, and manual verification.
Protected by Google OAuth - the user must login with their Google account.

## Installation (First Time Only)

Before using this skill, run the installer to configure ngrok and Google OAuth:

```bash
bash ~/.openclaw/skills/browser-control/install.sh
```

The installer will:
1. Install dependencies (VNC, noVNC, ngrok)
2. Ask for your **ngrok authtoken** (get it from https://dashboard.ngrok.com/get-started/your-authtoken)
3. Verify your **Google account** (only this email will be able to access the browser)

This only needs to be done once per machine.

## When to use

When you need the user to:
- Log into a website
- Complete 2FA / MFA
- Solve a captcha
- Do any manual browser action

## Check if running

```bash
~/.openclaw/skills/browser-control/status.sh
```

Returns JSON with status of VNC, noVNC, and ngrok tunnel.

## Start if not running

```bash
~/.openclaw/skills/browser-control/start-tunnel.sh
```

Starts VNC + noVNC + ngrok tunnel with Google OAuth. Takes ~30 seconds.

## Get URL

**⚠️ ALWAYS read this file fresh before sending the URL to the user. Never use cached values.**

```bash
cat ~/.openclaw/skills/browser-control/config.json
```

Returns:
```json
{
  "novncUrl": "https://xxx.ngrok.app/vnc.html?password=xxx&autoconnect=true",
  "tunnelUrl": "https://xxx.ngrok.app",
  "allowedEmail": "user@gmail.com",
  "cdpUrl": "http://localhost:9222"
}
```

The URL changes every time the tunnel restarts. Always read the file, don't trust memory.

## Workflow

1. Check status with `status.sh`
2. If not running, start with `start-tunnel.sh`
3. **Read `config.json` NOW** (not from memory!) for URL
4. Send user the link
5. User logs in with their Google account
6. User does the manual action (login, 2FA, etc.)
7. Wait for user to say "done"
8. Continue using browser via CDP (localhost:9222)

**Important:** The tunnel URL changes frequently. Always `cat config.json` right before sending the link.

## Example message to user

```
🔐 I need you to log in.

Open: https://xxx.ngrok.app/vnc.html?password=xxx&autoconnect=true

You'll need to sign in with your Google account.
Let me know when you're done!
```

**Note:** Do NOT mention passwords. The link includes auto-login. The user just needs to:
1. Click the link
2. Login with Google
3. Do the action
4. Tell you "done"

## Security

- Protected by Google OAuth
- Only the email configured during install can access
- No password to leak - authentication is via Google
- Tunnel URL changes on restart (adds obscurity)

## Stop when done (optional)

```bash
~/.openclaw/skills/browser-control/stop-tunnel.sh
```

## After server reboot

**The tunnel does NOT auto-start on reboot.** You must run `start-tunnel.sh` again.

Always check `status.sh` first before assuming the tunnel is running.

## Files

```
~/.openclaw/skills/browser-control/
├── SKILL.md           # This file
├── start-tunnel.sh    # Start everything
├── stop-tunnel.sh     # Stop everything
├── status.sh          # Check status
├── config.json        # Current URL (read this before sending to user!)
├── ngrok-config.json  # Configured email
├── vnc-password       # VNC password (auto-included in URL)
└── ngrok.log          # ngrok logs
```

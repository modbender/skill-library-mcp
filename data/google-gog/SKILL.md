---
name: Google Services (gog CLI)
description: OAuth token refresh management for Google APIs via gog CLI.
slug: google-gog
tags: [google, gmail, drive, oauth, gog, credentials]
---

# Google Services (gog CLI)

## Configuration

- **Account:** `xtyherry@gmail.com`
- **Credentials:** `~/.openclaw/credentials/client_secret.json`
- **Token Storage:** OS Keyring (auto-encrypted)

## Refresh Token Lifecycle

Tokens auto-refresh transparently on API calls. No action needed.

**If token invalid:**
```bash
gog auth add xtyherry@gmail.com --services gmail,drive,calendar --manual --force-consent
```

**For automation (cron/headless):**
```bash
export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD=<password>
gog auth list --check  # Check token validity and expiration
```

## Quick Commands

```bash
# Gmail: send, search
gog gmail send user@example.com --subject "Hi" --body "Message"
gog gmail search "newer_than:7d"

# Drive: list, upload, download
gog drive ls /
gog drive upload file.txt /
gog drive download /file.txt ./output.txt

# Check token health
gog auth list --check
```

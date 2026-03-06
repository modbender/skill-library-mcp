# Google Calendar Skill — Setup Guide

Pick the option that matches your situation:

- **Option A** — You were given a Client ID and Secret (e.g. by a team admin). Start at [step 1](#1-save-credentials-locally).
- **Option B** — You're setting up from scratch. Start at [Create Your Own OAuth Client](#option-b-create-your-own-oauth-client-from-scratch).

---

## 1. Save Credentials Locally

Create the config directory and write your credentials:

```bash
mkdir -p ~/.config/google-calendar-skill
```

```bash
cat > ~/.config/google-calendar-skill/client.json << 'EOF'
{
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET"
}
EOF
```

Lock down permissions:

```bash
chmod 600 ~/.config/google-calendar-skill/client.json
```

Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with the values you were given or created above.

## 2. Install Script Dependencies

From the skill's `scripts/` directory:

```bash
cd <SKILL_DIR>/scripts
bun install
```

Replace `<SKILL_DIR>` with the absolute path where the skill is installed. For the default location:

```bash
cd ~/.openclaw/skills/google-calendar/scripts && bun install
```

## 3. Authenticate (One-Time)

Run the login command — it opens your browser for Google sign-in:

```bash
cd <SKILL_DIR>/scripts && bun run auth.ts login
```

What happens:

1. A temporary HTTP server starts on `http://127.0.0.1:<random_port>`.
2. Your browser opens to Google's consent screen.
3. You sign in and grant the requested calendar permissions.
4. Google redirects back to the local server with an authorization code.
5. The script exchanges the code for an **access token** and **refresh token** using PKCE (S256).
6. Tokens are saved to `~/.config/google-calendar-skill/token.json`.

You should see:

```
✓ Authenticated! Tokens saved to /Users/you/.config/google-calendar-skill/token.json
  Scopes: https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events
```

## 4. Verify

Check that everything is working:

```bash
bun run auth.ts status
```

Expected output:

```
── Google Calendar Auth Status ──

  Client credentials: ✓ Found
  Tokens: ✓ Found
    Access token: ✓ Valid (3412s remaining)
    Refresh token: ✓ Present
```

Try listing your calendars:

```bash
bun run calendar.ts calendars
```

---

---

## Option B: Create Your Own OAuth Client (from scratch)

Follow these steps if you don't have a Client ID and Secret yet.

### B1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top and select **New Project**.
3. Give it a name (e.g. `calendar-skill`) and click **Create**.
4. Make sure the new project is selected in the dropdown.

### B2. Enable the Google Calendar API

1. Open the [API Library](https://console.cloud.google.com/apis/library).
2. Search for **Google Calendar API**.
3. Click it, then click **Enable**.

### B3. Configure the OAuth Consent Screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2. Choose **External** (unless you have a Google Workspace org and want internal-only).
3. Fill in the required fields:
   - **App name**: e.g. `Calendar Skill`
   - **User support email**: your email
   - **Developer contact email**: your email
4. Click **Save and Continue**.
5. On the **Scopes** page click **Add or remove scopes** and add:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
6. Click **Save and Continue**.
7. On the **Test users** page, add the Google account(s) you want to use with the skill, then **Save and Continue**.

> **Note:** While the app is in "Testing" mode only test users you've listed can authenticate. You do not need to go through Google's verification process for personal use.

### B4. Create OAuth 2.0 Client Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials).
2. Click **Create Credentials** → **OAuth client ID**.
3. For **Application type**, select **Desktop app**.
4. Give it a name (e.g. `calendar-skill-desktop`).
5. Click **Create**.
6. A dialog shows your **Client ID** and **Client Secret**. Copy both.

Now go back to [step 1](#1-save-credentials-locally) to save them and authenticate.

---

## Token Lifecycle


| Token             | Lifetime      | Storage                                      |
| ----------------- | ------------- | -------------------------------------------- |
| **Access token**  | ~1 hour       | `~/.config/google-calendar-skill/token.json` |
| **Refresh token** | Until revoked | Same file                                    |


- The scripts **auto-refresh** the access token when it's within 5 minutes of expiry — no manual action needed.
- If you revoke access or the refresh token becomes invalid, re-run `bun run auth.ts login`.

## Managing Tokens


| Command                    | What it does                                               |
| -------------------------- | ---------------------------------------------------------- |
| `bun run auth.ts status`  | Show auth state and token expiry                           |
| `bun run auth.ts refresh` | Force-refresh the access token now                         |
| `bun run auth.ts token`   | Print a valid access token to stdout (refreshes if needed) |
| `bun run auth.ts revoke`  | Revoke tokens at Google and delete local files             |


## Troubleshooting

### "Client credentials not found"

You haven't saved `client.json` yet. Go back to [step 1](#1-save-credentials-locally).

### "redirect_uri_mismatch" error in the browser

The OAuth client type must be **Desktop app**. Web or Android client types won't work with the loopback redirect.

### "access_denied" or consent screen not appearing

Make sure your Google account is listed as a **test user** in the OAuth consent screen configuration (see [step B3](#b3-configure-the-oauth-consent-screen)). This only applies if you set up the OAuth client yourself (Option B).

### "invalid_grant" when refreshing

The refresh token was revoked or expired. Re-authenticate:

```bash
bun run auth.ts login
```

### Port conflicts

The auth script picks a random available port on `127.0.0.1`. If your firewall blocks loopback connections, temporarily allow them.

## File Locations


| File                                          | Purpose                                  |
| --------------------------------------------- | ---------------------------------------- |
| `~/.config/google-calendar-skill/client.json` | Your OAuth client_id and client_secret   |
| `~/.config/google-calendar-skill/token.json`  | Access and refresh tokens (auto-managed) |


Both files are `chmod 600` (owner-only read/write). Never commit these to version control.
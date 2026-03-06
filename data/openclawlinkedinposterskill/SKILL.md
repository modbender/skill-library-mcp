---
name: linkedin-poster
description: Post updates to the user's LinkedIn profile via OAuth.
metadata:
  openclaw:
    skillKey: linkedin-poster
    requires:
      env:
        - LINKEDIN_CLIENT_ID
        - LINKEDIN_CLIENT_SECRET
    invocation:
      policy: on-demand
      triggers:
        - pattern: "post to linkedin"
        - pattern: "share on linkedin"
        - pattern: "linkedin post"
        - pattern: "post to linkedin org"
        - pattern: "linkedin company post"
---

# LinkedIn Poster

Post text updates to your LinkedIn profile directly from OpenClaw.

## Features

- OAuth 2.0 authentication (one-time setup)
- Automatic token management (60-day expiry)
- Works via command line or WhatsApp
- Production-ready callback server

## Setup

### 1. LinkedIn App Configuration

1. Create a LinkedIn app at [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Add redirect URL: `https://linkedin-oauth-server-production.up.railway.app/callback`
3. Request access to "Share on LinkedIn" and "Sign In with LinkedIn" products
4. Copy your Client ID and Client Secret

### 2. Environment Variables

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "env": {
      "LINKEDIN_CLIENT_ID": "your_client_id",
      "LINKEDIN_CLIENT_SECRET": "your_client_secret"
    }
  }
}
```

### 3. First Run Authorization

The first time you use the skill, it will:
1. Open a browser for LinkedIn authorization
2. Save the access token locally
3. Use the saved token for future posts

## Usage

### Via WhatsApp

Send a message to OpenClaw:
```
post to linkedin: Just shipped a new feature! 🚀
```

Or:
```
share on linkedin: Excited to announce our new product launch!
```

### Via Command Line

```bash
node skills/linkedin-poster/runner.cjs "Your message here"
```

### Posting to a Company Page

To post to a LinkedIn Company Page where you are an admin:

```bash
node skills/linkedin-poster/runner.cjs "Company update!" --org "My Company Name"
```

The skill will fuzzy search your administered organizations and post to the best match.

**Note:** You must have the `w_organization_social` permission (Marketing API/Company Page Management) enabled in your LinkedIn App settings for this to work.

## How It Works

1. **First use**: Opens browser → Authorize → Token saved
2. **Subsequent uses**: Uses saved token → Posts immediately
3. **Token expiry**: Auto-prompts for re-authorization after 60 days

## OAuth Callback Server

This skill uses a hosted callback server at:
`https://linkedin-oauth-server-production.up.railway.app`

The server handles OAuth callbacks securely and works for anyone using the skill.

## Troubleshooting

### "redirect_uri does not match"
Ensure `https://linkedin-oauth-server-production.up.railway.app/callback` is added to your LinkedIn app's Redirect URLs.

### "Authorization timeout"
The skill waits 60 seconds. Try again and authorize faster.

### "Token expired"
Run the skill again - it will automatically start a new OAuth flow.

# OpenClaw LinkedIn Poster Skill (v1.1.0)

🚀 **Post to LinkedIn (Personal & Company Pages) directly from OpenClaw via a simple chat command.**

This skill integrates OpenClaw with LinkedIn's API using OAuth 2.0. Once you authorize it (a one-time setup), you can post updates to your profile by simply chatting with your bot.

## Features

- **OAuth 2.0 Authentication**: Secure, one-time browser login.
- **Easy Setup**: Uses a pre-configured callback server.
- **Smart Token Management**: Automatically refreshes expired tokens.
- **Works Everywhere**: Use it via WhatsApp, Telegram, or the CLI.

## Installation

1. Clone this repository into your OpenClaw skills directory:
   ```bash
   git clone <repo-url> skills/linkedin-poster
   ```

2. Make sure you have the required credentials (see Setup below).

## Setup Guide

### 1. Create a LinkedIn App
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps) and create a new app.
2. In the **Auth** tab, add this Redirect URL:
   `https://linkedin-oauth-server-production.up.railway.app/callback`
3. In the **Products** tab, request access to:
   - **"Share on LinkedIn"** (for personal profile posting)
   - **"Sign In with LinkedIn"** (for authentication)
   - **"Marketing API"** or **"Share on LinkedIn & Organization Page Management"** (REQUIRED for --org / Company Page posting)
4. Copy your **Client ID** and **Client Secret**.

### 2. Configure OpenClaw
Add your credentials to `openclaw.json`:

```json
"env": {
  "LINKEDIN_CLIENT_ID": "your_client_id_here",
  "LINKEDIN_CLIENT_SECRET": "your_client_secret_here"
}
```

## Usage

### First Time Run
The first time you try to post, the skill will generate an extensive authorization link. Open this link in your browser to approve the app.

### Chat Command
Just tell your bot to post!
> "Post to LinkedIn: Just launched my new OpenClaw skill! 🦞"

**To post to a company page:**
> "Post to LinkedIn org 'Acme Corp': We are hiring!"

(The skill will automatically find the best matching organization you administer)

### CLI Usage
You can also run it directly:
```bash
# Personal Profile
node skills/linkedin-poster/runner.cjs "Your update text here"

# Company Page
node skills/linkedin-poster/runner.cjs "Company Update" --org "Acme Corp"
```

## How It Works
1. When triggered, the script checks for a valid local token.
2. If no token exists (or it's expired), it starts the OAuth flow and prompts you to log in.
3. Once authorized, it exchanges the code for an access token via the secure callback server.
4. The token is saved locally (`.linkedin_token`) for future requests.
5. Your update is posted immediately to your profile.

## Troubleshooting
- **Redirect URI Error**: Double-check that exactly `https://linkedin-oauth-server-production.up.railway.app/callback` is in your LinkedIn app settings.
- **Auth Timeout**: The script waits 60 seconds for you to authorize. If it times out, just run the command again.

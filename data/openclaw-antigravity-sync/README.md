# OpenClaw Antigravity Sync Skill

This skill automatically discovers and configures Google Antigravity models (Claude, Gemini, etc.) in your OpenClaw setup. It queries the Antigravity API for available models and their current quotas, ensuring your agent always has a valid model to use.

## Features

- 🔍 **Auto-Discovery**: Fetches all available models directly from Google Antigravity.
- 🚦 **Quota-Aware**: Checks your current usage and avoids selecting exhausted models.
- 🛡️ **Safety First**: Verifies critical WhatsApp security settings (allowlist/self-chat).
- 💾 **Safe Updates**: Backs up your `openclaw.json` before making changes.
- 🧠 **Smart Selection**: Preserves your manually selected model if valid; otherwise, falls back to the best available alternative.

## Installation

1. Clone this repository into your OpenClaw skills directory:
   ```bash
   git clone <repo-url> skills/antigravity-sync
   ```
   *Or simply copy the files.*

2. Ensure you have authenticated with Google Antigravity:
   ```bash
   openclaw models auth login google-antigravity
   ```

## Usage

Run the sync script:

```bash
node skills/antigravity-sync/sync.cjs
```

The script will:
1. Authenticate using your existing OpenClaw profile.
2. Fetch the latest model list and quotas.
3. Update `openclaw.json` with new model definitions.
4. Check if your current primary model is valid. If not (e.g., quota exhausted), it will switch to a recommended fallback.

## WhatsApp Safety Check

The script includes a check for your WhatsApp channel configuration. It will warn you if:
- `selfChatMode` is disabled.
- `allowFrom` list is empty.

To secure your bot, add your phone number to `openclaw.json`:

```json
"channels": {
  "whatsapp": {
    "allowFrom": ["+1234567890"],
    "selfChatMode": true
  }
}
```

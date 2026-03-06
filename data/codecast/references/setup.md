# First-Time Setup

Run these steps once after installing the skill.

## 1. Make scripts executable

```bash
chmod +x {baseDir}/scripts/dev-relay.sh {baseDir}/scripts/parse-stream.py
```

## 2. Create a Discord webhook

Create a webhook in the target Discord channel via Server Settings → Integrations → Webhooks.

To create via API (if the bot has MANAGE_WEBHOOKS):
```bash
curl -s -X POST "https://discord.com/api/v10/channels/<CHANNEL_ID>/webhooks" \
  -H "Authorization: Bot <BOT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Codecast"}'
```

Store the webhook URL:
```bash
echo "https://discord.com/api/webhooks/<ID>/<TOKEN>" > {baseDir}/scripts/.webhook-url
chmod 600 {baseDir}/scripts/.webhook-url
```

## 3. Skip the permissions prompt (Claude Code only)

Create `~/.claude/settings.json` if it doesn't exist:
```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["*"]
  }
}
```

## 4. Install unbuffer (required)

```bash
brew install expect    # macOS
apt install expect     # Linux
```

## 5. Bot token (optional, for --thread mode)

**Recommended: macOS Keychain (no plaintext on disk)**
```bash
security add-generic-password -s discord-bot-token -a codecast -w YOUR_BOT_TOKEN
```

Then export before running codecast:
```bash
export CODECAST_BOT_TOKEN=$(security find-generic-password -s discord-bot-token -a codecast -w)
```

**Fallback: file-based storage**
```bash
echo "YOUR_BOT_TOKEN" > {baseDir}/scripts/.bot-token
chmod 600 {baseDir}/scripts/.bot-token
```

## 6. Validate setup

```bash
bash {baseDir}/scripts/test-smoke.sh
```

Checks webhook reachability, required binaries, script permissions, and platform adapter loading.

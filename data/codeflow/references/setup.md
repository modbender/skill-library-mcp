# First-Time Setup

Run these steps once after installing the skill.

Requires: **Python >= 3.10** (`python3`).

## 1. Make scripts executable

```bash
chmod +x {baseDir}/scripts/codeflow
```

## 2. Configure target channel (Discord or Telegram)

### Option A: Discord webhook

Create a webhook in the target Discord channel via Server Settings → Integrations → Webhooks.

To create via API (optional; if the bot has MANAGE_WEBHOOKS):

- Prefer the Discord UI (simplest).
- If you do this via CLI, **do not** put the bot token into command-line args (it can show up in `ps` / shell history). Use env + Python:

```bash
export DISCORD_CHANNEL_ID="<CHANNEL_ID>"
export DISCORD_BOT_TOKEN="<BOT_TOKEN>"
python3 - <<'PY'
import json, os, urllib.request

chan = os.environ["DISCORD_CHANNEL_ID"]
tok = os.environ["DISCORD_BOT_TOKEN"]
url = f"https://discord.com/api/v10/channels/{chan}/webhooks"
body = json.dumps({"name": "Codeflow"}).encode("utf-8")
req = urllib.request.Request(url, data=body, method="POST")
req.add_header("Authorization", f"Bot {tok}")
req.add_header("Content-Type", "application/json")
with urllib.request.urlopen(req, timeout=10) as resp:
    print(resp.read().decode("utf-8", errors="replace"))
PY
```

Store the webhook URL:
```bash
echo "https://discord.com/api/webhooks/<ID>/<TOKEN>" > {baseDir}/scripts/.webhook-url
chmod 600 {baseDir}/scripts/.webhook-url
```

### Option B: Telegram

Use either env vars or OpenClaw config bot token:

```bash
export TELEGRAM_BOT_TOKEN="<bot_token>"              # optional if already in ~/.openclaw/openclaw.json
export CODEFLOW_TELEGRAM_CHAT_ID="<chat_id>"         # required
export CODEFLOW_TELEGRAM_THREAD_ID="<topic_id>"      # optional (forum topics)
```

You can also pass `--tg-chat` / `--tg-thread` on each run.

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
security add-generic-password -s discord-bot-token -a codeflow -w YOUR_BOT_TOKEN
```

Then export before running Codeflow:
```bash
export CODEFLOW_BOT_TOKEN=$(security find-generic-password -s discord-bot-token -a codeflow -w)
```

**Fallback: file-based storage**
```bash
echo "YOUR_BOT_TOKEN" > {baseDir}/scripts/.bot-token
chmod 600 {baseDir}/scripts/.bot-token
```

## 6. Validate setup

```bash
bash {baseDir}/scripts/codeflow smoke -P discord
bash {baseDir}/scripts/codeflow smoke -P telegram --tg-chat <chat_id>
```

Checks platform credentials/reachability (no message posting), required binaries, script permissions, and adapter loading.

## 7. Optional: Safe mode (recommended for shared channels)

If you relay into a shared channel, consider enabling safe mode:

```bash
export CODEFLOW_SAFE_MODE=true
```

When `CODEFLOW_SAFE_MODE=true`:
- File content previews (Claude `Write`) are suppressed (metadata only)
- Command output bodies are suppressed (metadata only)
- Redaction becomes stricter for high-risk patterns

## 8. Optional: Local sanity checks (developers)

Run a local check bundle (Python syntax compile + unit tests + `bash -n`):

```bash
bash {baseDir}/scripts/codeflow check
```

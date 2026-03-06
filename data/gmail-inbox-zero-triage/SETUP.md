# Gmail Inbox Zero Triage - Setup Guide

## Installation

```bash
clawdbot skills install gmail-inbox-zero.skill
```

## Prerequisites

### 1. Install gog CLI

**Mac (Homebrew):**
```bash
brew install steipete/tap/gogcli
```

**Other platforms:** See https://gogcli.sh

### 2. Authenticate Gmail Account

```bash
# Add your Gmail account with OAuth
gog auth add your@gmail.com --services gmail

# Set keyring password (required for non-interactive use)
export GOG_KEYRING_PASSWORD="your-keyring-password"
```

**Note:** The keyring password is what you set when first adding the account. If you don't remember it, you may need to re-add the account.

### 3. Verify Setup

```bash
# Check authenticated accounts
gog auth list

# Test Gmail access
gog gmail search "in:inbox" --max 5 --account your@gmail.com
```

## Usage

Just say to your Clawdbot agent:
- "Triage my emails"
- "Process my inbox"
- "Help me achieve inbox zero"

The agent will:
1. Fetch all inbox messages (read + unread)
2. Show each with an AI summary and action buttons
3. Let you click through quickly
4. Execute all actions in batch when you hit "Done"

## Actions Explained

- **📥 Archive** - Removes from inbox (still searchable in All Mail)
- **🔍 Filter** - Creates Gmail filter to auto-archive future emails from this sender
- **🚫 Unsubscribe** - Finds and shows unsubscribe link
- **📧 View** - Shows full email content
- **Don't click** - Skips the email (leaves in inbox)

## Tips

- **Archive aggressively** - If you don't need immediate action, archive it
- **Use filters** - Auto-archive recurring newsletters and notifications
- **Process daily** - Maintain inbox zero by triaging regularly
- **Trust AI summaries** - They're accurate enough for quick decisions
- **Batch is fast** - Process 10-20 emails in under a minute

## Troubleshooting

### "gog not authenticated"
```bash
gog auth add your@gmail.com --services gmail
```

### "No TTY for keyring password"
```bash
export GOG_KEYRING_PASSWORD="your-password"
```

### "Permission denied"
Re-authenticate with more permissions:
```bash
gog auth add your@gmail.com --services gmail --force
```

### Emails still showing after archive
Gmail can take 10-30 seconds to sync. Refresh your Gmail app or wait a moment.

## Advanced: Environment Variables

For persistent setup, add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export HOME=/root
export GOG_KEYRING_PASSWORD="your-password"
```

Then restart your terminal or run `source ~/.bashrc`.

## Support

- Skill issues: https://github.com/clawdbot/clawdbot/issues
- gog CLI: https://gogcli.sh
- Community: https://discord.com/invite/clawd

---

Happy inbox zero! 📬✨

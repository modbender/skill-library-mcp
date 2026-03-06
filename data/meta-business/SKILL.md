---
name: meta-business
description: "Skill for the Meta Business CLI. Complete WhatsApp, Instagram, Facebook Pages, and Messenger automation via the Graph API. Supports messaging, media, templates, analytics, webhooks, and systemd service management."
version: 1.2.0
author: adolago
tags:
  - whatsapp
  - instagram
  - facebook
  - messenger
  - meta
  - cli
  - automation
triggers:
  - whatsapp
  - instagram
  - facebook
  - messenger
  - meta
  - send message
metadata:
  openclaw:
    requires:
      bins: [meta]
    install:
      - id: bun
        kind: command
        command: "bun install -g meta-business-cli"
        bins: [meta]
        label: "Install meta CLI (bun)"
      - id: compile
        kind: command
        command: "git clone https://github.com/adolago/meta-cli.git && cd meta-cli && bun install && bun build --compile --outfile ~/.bun/bin/meta src/index.ts"
        bins: [meta]
        label: "Build from source (standalone binary)"
---

# Meta Business CLI

Use `meta` for WhatsApp, Instagram, Facebook Pages, and Messenger automation via the Graph API.

## Setup

```bash
# 1. Configure app credentials
meta config set app.id YOUR_APP_ID
meta config set app.secret YOUR_APP_SECRET

# 2. Authenticate (OAuth PKCE, opens browser)
meta auth login

# 3. Configure WhatsApp (from API Setup page)
meta config set whatsapp.phoneNumberId YOUR_PHONE_NUMBER_ID
meta config set whatsapp.businessAccountId YOUR_WABA_ID

# 4. Verify everything works
meta doctor
```

Or use `--token YOUR_TOKEN` with any command to skip OAuth (e.g. System User tokens).

## Authentication

```bash
meta auth login                              # OAuth PKCE flow (opens browser)
meta auth login --token YOUR_ACCESS_TOKEN    # Use existing token
meta auth login --scopes "whatsapp_business_messaging,instagram_basic,pages_show_list"
meta auth status                             # Show token validity and scopes
meta auth logout                             # Remove stored credentials
```

## Configuration

```bash
meta config set app.id YOUR_APP_ID           # App ID (numeric)
meta config set app.secret YOUR_APP_SECRET   # App secret
meta config set whatsapp.phoneNumberId ID    # WhatsApp phone number ID
meta config set whatsapp.businessAccountId ID  # WhatsApp business account ID
meta config set instagram.accountId ID       # Instagram account ID
meta config set pages.pageId ID              # Facebook Page ID
meta config set webhook.forwardUrl URL       # Forward inbound messages to URL
meta config get <key>                        # Get a config value
meta config list                             # Show all config values
```

Config stored at `~/.meta-cli/config.json`.

## WhatsApp

### Sending Messages

```bash
# Text
meta wa send "+1234567890" --text "Hello" --json

# Markdown (converts to WhatsApp formatting)
meta wa send "+1234567890" --text "**bold** and _italic_" --markdown --json

# Chunked (splits long text into multiple messages)
meta wa send "+1234567890" --text "very long message..." --chunk --json

# Image
meta wa send "+1234567890" --image "https://example.com/photo.jpg" --caption "Look" --json

# Video
meta wa send "+1234567890" --video "https://example.com/video.mp4" --caption "Watch" --json

# Document
meta wa send "+1234567890" --document "https://example.com/file.pdf" --json

# Local file (auto-uploads)
meta wa send "+1234567890" --document ./report.pdf --caption "Q4 report" --json

# Audio
meta wa send "+1234567890" --audio "https://example.com/note.ogg" --json

# Voice note (renders as playable voice note, requires OGG/Opus)
meta wa send "+1234567890" --audio "./recording.ogg" --voice --json

# Template
meta wa send "+1234567890" --template "hello_world" --template-lang en_US --json

# Mark as read
meta wa read WAMID --json
```

### Media File Size Limits

| Type | Max Size |
|------|----------|
| Image | 5 MB |
| Video | 16 MB |
| Document | 100 MB |

### Templates

```bash
meta wa template list --json                 # List all templates
meta wa template get TEMPLATE_NAME --json    # Get template details
meta wa template delete TEMPLATE_NAME --json # Delete template
```

### Media

```bash
meta wa media upload ./photo.jpg --json      # Upload media
meta wa media url MEDIA_ID --json            # Get media URL
meta wa media download MEDIA_ID ./output.jpg # Download media
```

### Analytics

```bash
meta wa analytics --days 30 --granularity DAY --json
```

### Phone Number Management

```bash
meta wa phone list --json                    # List numbers
meta wa phone get --json                     # Get active number details
meta wa phone select PHONE_NUMBER_ID         # Select active number
```

### Allowlist (Prompt Injection Protection)

```bash
meta wa allowlist list                       # List allowed numbers
meta wa allowlist add "+1234567890"          # Add number
meta wa allowlist remove "+1234567890"       # Remove number
```

When the allowlist is non-empty, `meta wa send` only delivers to listed numbers.

## Instagram

```bash
# Publish image
meta ig publish --image "https://example.com/photo.jpg" --caption "My post" --json

# Publish video
meta ig publish --video "https://example.com/video.mp4" --caption "Watch this" --json

# Publish Reel
meta ig publish --video "https://example.com/reel.mp4" --reel --caption "New reel" --json

# Account insights
meta ig insights --period day --days 30 --json

# Media insights
meta ig insights --media-id MEDIA_ID --json

# Comments
meta ig comments list MEDIA_ID --json        # List comments
meta ig comments reply COMMENT_ID "Thanks!" --json  # Reply
meta ig comments hide COMMENT_ID --json      # Hide
meta ig comments delete COMMENT_ID --json    # Delete
```

Instagram publish requires a public URL for images/videos (not local files).

## Facebook Pages

```bash
meta fb post --message "Hello from the CLI" --json           # Create post
meta fb post --message "Check this" --link "https://example.com" --json  # Link post
meta fb list --limit 10 --json                               # List posts
meta fb insights --period day --days 30 --json               # View insights
```

## Messenger

```bash
meta messenger send PSID --text "Hello" --json               # Send text
meta messenger send PSID --image "https://example.com/photo.jpg" --json  # Send image
meta messenger send PSID --text "Update" --type MESSAGE_TAG --tag HUMAN_AGENT --json  # Outside 24h window
meta messenger receive --json                                # List conversations
meta messenger receive --conversation-id CONV_ID --json      # View conversation
```

Messenger messaging outside the 24h window requires a message tag.

## Webhooks

```bash
# Start listener
meta webhook listen --port 3000 --verify-token TOKEN --app-secret SECRET

# Test verification locally
meta webhook verify --verify-token TOKEN --json

# Subscribe to events
meta webhook subscribe \
  --object whatsapp_business_account \
  --fields messages \
  --callback-url "https://example.com/webhook" --json
```

Set `webhook.forwardUrl` in config to POST inbound messages to an external service.
The webhook auto-sends read receipts and acknowledges reactions for inbound messages.

## Webhook Service (systemd)

```bash
meta service install                         # Install systemd user service
meta service start                           # Start the webhook service
meta service stop                            # Stop the service
meta service restart                         # Restart the service
meta service status                          # Show service status
meta service logs                            # Show service logs
meta service uninstall                       # Remove systemd service
```

## Shell Completion

```bash
# Bash
meta completion >> ~/.bashrc

# Zsh (add to .zshrc)
meta completion >> ~/.zshrc
```

## Diagnostics

```bash
meta doctor --json
```

Checks config, credentials, token validity, Graph API connectivity, permissions, and surface-specific asset access. Run before first use.

## Global Flags

| Flag | Description |
|------|-------------|
| `--json` | Structured output for scripting and agent use |
| `--verbose` | Print debug logs to stderr |
| `--token TOKEN` | Override stored credentials |
| `--api-version v22.0` | Pin a specific Graph API version |

## Notes

- Always use `--json` for structured output when automating.
- All commands work non-interactively when required args are passed as flags.
- Voice notes require OGG/Opus format to render correctly in WhatsApp.
- Files exceeding size limits are rejected with an actionable error.
- For larger files, host at a URL and pass the URL directly.

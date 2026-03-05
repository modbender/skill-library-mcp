---
name: tsend
description: Send files via Telegram. Example: tsend send document.pdf
---

# Telegram Sender (tsend)

Zero-config CLI tool. Install once, send forever.

## Installation

**Tip:** Try using `tsend` command first. If command not found, then install.

### Using uv (recommended)

```bash
cd <skill-path>/scripts
uv tool install -e .
```

Replace `<skill-path>` with the actual skill path.

After installation, `tsend` command is available globally.

### From source (alternative)

If you don't have uv:

```bash
cd <skill-path>/scripts
pip install -e .
```

## Just use it

```bash
tsend send document.pdf
tsend send photo.jpg --caption "Description"
tsend send image.png -c "Screenshot"

# Send multiple files
tsend send file1.pdf file2.jpg file3.png
tsend send *.pdf --caption "Documents"  # caption only goes to first file
```

### Using specific profile

```bash
tsend send file.pdf --profile mybot
tsend send photo.png -c "Description" -p picoclaw
```

That's it. No setup, no checks, no questions.

## Only if it fails (once)

```bash
tsend config set --token "YOUR_BOT_TOKEN" --chat-id "YOUR_CHAT_ID"
```

Or specify a profile:
```bash
tsend config set --profile mybot --token "TOKEN" --chat-id "CHAT_ID"
tsend config default mybot  # Set as default
```

The tool saves config to `~/.tsend/config.json`.

## Multiple Profiles

Manage multiple bots with profiles:

```bash
# List all profiles
tsend config list

# Show specific profile
tsend config show --profile mybot

# Send with specific profile
tsend send file.pdf --profile mybot
```

## Environment Variable

Set default profile via environment:
```bash
export TSEND_PROFILE=mybot
tsend send file.pdf  # Uses 'mybot' profile
```

Useful for different services (nanobot, picoclaw, etc.).

## When something's wrong

**"token invalid"** → Fix with one command:
```bash
tsend config set --token NEW_TOKEN --chat-id NEW_ID
```

No reinstall, no config file hunting.

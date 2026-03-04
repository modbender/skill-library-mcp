---
name: taildrop
description: Download files from Tailscale Taildrop inbox to local storage. Use when user wants to retrieve files sent via Tailscale or mentions Taildrop.
---

# Taildrop File Retrieval

Download files from Tailscale's Taildrop inbox to your local Downloads folder.

## Quick Usage

```bash
~/clawd/skills/taildrop/scripts/taildrop-get.sh
```

This will:
- Check for files in the Taildrop inbox
- Download them to `~/Downloads/`
- Handle filename conflicts (skip duplicates by default)
- Report what was downloaded

## Options

```bash
# Download to a custom directory
~/clawd/skills/taildrop/scripts/taildrop-get.sh /path/to/directory

# Overwrite existing files
~/clawd/skills/taildrop/scripts/taildrop-get.sh --overwrite

# Rename duplicates
~/clawd/skills/taildrop/scripts/taildrop-get.sh --rename
```

## Prerequisites

- Tailscale must be installed and running
- User must be set as Tailscale operator (run once): `sudo tailscale set --operator=$USER`
- Otherwise, sudo is required for each download

## Notes

- Unlike macOS/Windows, Linux Tailscale doesn't auto-save Taildrop files
- Files stay in the inbox until manually retrieved
- The script can run in loop mode to auto-receive files as they arrive

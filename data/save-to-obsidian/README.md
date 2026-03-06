# Save to Obsidian

An OpenClaw skill that saves markdown content to an Obsidian vault via SSH, with automatic formatting rules for diagrams, tables, and links.

## Prerequisite

**This skill is for machines WITHOUT iCloud sync** (e.g., Linux/Ubuntu servers, remote machines). If your machine already has iCloud Desktop sync enabled and direct access to the Obsidian vault folder, you don't need this skill — just copy files directly to the vault path.

## What It Does

This skill allows your OpenClaw agent to save any generated markdown content directly to your Obsidian vault on a remote machine. It automatically enforces formatting rules to ensure content renders properly in Obsidian:
- Converts or enforces Mermaid diagrams (no ASCII art)
- Uses markdown tables (Obsidian native rendering)
- Applies kebab-case filenames for cross-platform compatibility

## How to Install

1. Copy this skill to your OpenClaw skills directory
2. Set up SSH access to the remote machine hosting your Obsidian vault
3. Create a script at `~/.openclaw/scripts/save-to-obsidian.sh` that copies files to your vault location
4. Ensure the script is executable and works with your SSH key

Example script:
```bash
#!/bin/bash
scp "$1" user@remote-host:/path/to/obsidian-vault/
```

## Usage

Say to your agent:
- "save to obsidian"
- "send to obsidian"  
- "copy to obsidian"

The agent will format the content appropriately and transfer it to your vault.

## Requirements

- SSH access to the remote machine hosting the Obsidian vault
- Obsidian vault accessible on the remote machine
- A save-to-obsidian.sh script configured for your setup
- **Note:** Not needed if your local machine already has iCloud sync to the vault

## Future Work

- Support for multiple vault destinations
- Direct iCloud sync without SSH intermediary
- Automatic tagging and frontmatter generation
- Batch save operations

## License

MIT

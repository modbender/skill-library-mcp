# Postavel MCP Setup Guide

Complete guide for connecting OpenClaw to Postavel via MCP.

## Quick Setup (Automated)

Run the included setup script after installing the skill:

```bash
# The skill includes scripts/setup-mcp.sh
# It will be available at: ~/.openclaw/workspace/skills/postavel/scripts/setup-mcp.sh

bash ~/.openclaw/workspace/skills/postavel/scripts/setup-mcp.sh
```

This script will:
1. Check if `mcporter` is installed
2. Install it via Homebrew if missing
3. Create mcporter configuration for Postavel
4. Guide you through OAuth authentication

## Manual Setup

If you prefer manual setup or the script doesn't work:

### Step 1: Install mcporter

mcporter bridges OpenClaw to MCP servers.

**Via Homebrew:**
```bash
brew install mcporter
```

**Via npm:**
```bash
npm install -g mcporter
```

**From source:**
```bash
git clone https://github.com/steipete/mcporter.git
cd mcporter
go build
mv mcporter /usr/local/bin/
```

### Step 2: Configure mcporter for Postavel

Create `~/.config/mcporter/postavel.json`:

```json
{
  "mcpServers": {
    "postavel": {
      "command": "mcporter",
      "args": [
        "--url", "https://postavel.com/mcp/postavel",
        "--oauth",
        "--name", "postavel"
      ]
    }
  }
}
```

**For local development** (if running Postavel locally):
```json
{
  "mcpServers": {
    "postavel": {
      "command": "mcporter",
      "args": [
        "--url", "https://postavel.test/mcp/postavel",
        "--oauth",
        "--name", "postavel"
      ]
    }
  }
}
```

### Step 3: Authenticate

Run mcporter to start the OAuth flow:

```bash
mcporter --config ~/.config/mcporter/postavel.json
```

This will:
1. Open your browser
2. Ask you to log in to Postavel
3. Authorize the AI assistant to access your account
4. Store the OAuth token securely

### Step 4: Connect OpenClaw

Tell your OpenClaw agent to use the MCP connection:

```
"Connect to Postavel MCP"
```

Or specify the workspace:

```
"Use my Postavel workspace 'My Agency'"
```

### Step 5: Verify Connection

Test the connection by listing your workspaces:

```
"Show me my Postavel workspaces"
```

If successful, you'll see your workspaces listed. If not, check the troubleshooting section below.

## Environment Variables

You can configure mcporter via environment variables:

```bash
export MCPORTER_POSTAVEL_URL="https://postavel.com/mcp/postavel"
export MCPORTER_POSTAVEL_TOKEN="your-oauth-token"  # If you have it already
```

## Multiple Postavel Accounts

If you have multiple Postavel accounts (e.g., personal + agency):

```json
{
  "mcpServers": {
    "postavel-personal": {
      "command": "mcporter",
      "args": ["--url", "https://postavel.com/mcp/postavel", "--oauth", "--name", "postavel-personal"]
    },
    "postavel-agency": {
      "command": "mcporter", 
      "args": ["--url", "https://agency.postavel.com/mcp/postavel", "--oauth", "--name", "postavel-agency"]
    }
  }
}
```

Then specify which one to use:

```
"Use my personal Postavel account"
```

## Troubleshooting

### "mcporter: command not found"
- Make sure mcporter is in your PATH
- Try: `which mcporter` to verify installation
- Reinstall if necessary

### "OAuth failed" or "Authentication error"
- Check that the MCP URL is correct
- Ensure you have an active Postavel account
- Try running mcporter manually to see detailed error messages

### "No workspaces found"
- Verify you're authenticated: `mcporter --config ~/.config/mcporter/postavel.json --status`
- Check that your Postavel account has workspaces
- Re-authenticate if token expired

### "Permission denied" errors
- You may be a "Member" in the workspace, not an "Admin" or "Owner"
- Members can create posts but cannot approve them
- Ask your workspace admin for elevated permissions if needed

### mcporter connection issues

**Check if mcporter is running:**
```bash
ps aux | grep mcporter
```

**Test the connection manually:**
```bash
mcporter --config ~/.config/mcporter/postavel.json --test
```

**View mcporter logs:**
```bash
tail -f ~/.config/mcporter/logs/postavel.log
```

## Security Notes

- OAuth tokens are stored in `~/.config/mcporter/` with restricted permissions
- Tokens expire automatically for security
- Each AI session gets its own token
- You can revoke access from Postavel settings at any time
- Never share your mcporter configuration files

## Next Steps

Once connected, see [mcp-tools.md](mcp-tools.md) for available operations and example prompts.

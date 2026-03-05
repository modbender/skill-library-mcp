---
name: cartogopher
description: Set up CartoGopher AI-native code intelligence. Gets a free 7-day trial API key and configures the MCP server automatically.
homepage: https://cartogopher.com
emoji: 🦞
metadata:
  openclaw:
    requires:
      bins:
        - curl
        - unzip
        - node
        - npm
    primaryEnv: CARTOGOPHER_API_KEY
---

# CartoGopher

Set up [CartoGopher](https://cartogopher.com) — AI-native code intelligence that gives you 30+ tools for navigating codebases with 94% fewer tokens than file reading.

## When to Use This Skill

Use this skill when the user wants to:
- Set up CartoGopher for their project
- Get a CartoGopher trial API key
- Configure the CartoGopher MCP server
- Improve code navigation and understanding with AI-native tooling

## What CartoGopher Does

CartoGopher parses a codebase into a compact graph (bake.json) and exposes 30+ MCP tools:
- **Symbol lookup** — find functions, types, and their relationships
- **API tracing** — trace endpoints from frontend to database
- **Architecture mapping** — understand project structure and get placement suggestions
- **AST-aware search** — search code semantically, not just text matching
- **Frontend analysis** — Vue, React component analysis with props, hooks, store usage

## Setup Flow

### Step 1: Get a Trial API Key

Ask the user for their email address, then request a 7-day trial key:

```bash
curl -s -X POST https://cartogopher.com/api/agent-trial \
  -H 'Content-Type: application/json' \
  -d '{"email":"USER_EMAIL_HERE"}'
```

The response will contain:
```json
{
  "success": true,
  "api_key": "cg_agent_...",
  "trial_ends_at": "2026-02-27T...",
  "message": "Trial started! Configure your MCP server with this key."
}
```

Save the `api_key` value — you'll need it for the next steps.

If the response contains an error:
- `"Disposable email addresses are not allowed"` — ask for a real email
- `"A trial already exists for this email"` — the user already has a key, ask them to check their email or provide the existing key
- `"Rate limit exceeded"` — wait and retry later

### Step 2: Verify the Key Works

```bash
curl -s -X POST https://cartogopher.com/api/verify-key \
  -H 'Content-Type: application/json' \
  -d '{"api_key":"API_KEY_HERE"}'
```

### Step 3: Install the MCP Server

Download and install the CartoGopher bundle for the user's platform. Each download is a zip containing the binary, MCP server, and dependencies.

**Container prerequisite (Linux/Docker only):** CartoGopher requires `/etc/machine-id` to exist. Most Linux desktops have this, but containers often don't:

```bash
# Ensure machine-id exists (required in containers)
[ -f /etc/machine-id ] || (cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id)
```

**Detect platform and download:**

```bash
# Detect platform and set download URL
PLATFORM=$(uname -s)-$(uname -m)

case "$PLATFORM" in
  Darwin-arm64)  DOWNLOAD_URL="https://cartogopher.com/downloads/cartogopher/v4/mac/arm64" ;;
  Darwin-x86_64) DOWNLOAD_URL="https://cartogopher.com/downloads/cartogopher/v4/mac/intel" ;;
  Linux-x86_64)  DOWNLOAD_URL="https://cartogopher.com/downloads/cartogopher/v4/linux/amd64" ;;
  Linux-aarch64) DOWNLOAD_URL="https://cartogopher.com/downloads/cartogopher/v4/linux/arm64" ;;
  *) echo "Unsupported platform: $PLATFORM"; exit 1 ;;
esac

# Download, extract, and clean up
curl -sL "$DOWNLOAD_URL" -o cg.zip && unzip cg.zip -d ~/.cartogopher/mcp-server && rm cg.zip
```

**Platform-specific one-liners (if you already know the platform):**

- **macOS Apple Silicon (M1/M2/M3/M4):**
  ```bash
  curl -sL https://cartogopher.com/downloads/cartogopher/v4/mac/arm64 -o cg.zip && unzip cg.zip -d ~/.cartogopher/mcp-server && rm cg.zip
  ```

- **macOS Intel:**
  ```bash
  curl -sL https://cartogopher.com/downloads/cartogopher/v4/mac/intel -o cg.zip && unzip cg.zip -d ~/.cartogopher/mcp-server && rm cg.zip
  ```

- **Linux amd64:**
  ```bash
  curl -sL https://cartogopher.com/downloads/cartogopher/v4/linux/amd64 -o cg.zip && unzip cg.zip -d ~/.cartogopher/mcp-server && rm cg.zip
  ```

- **Linux arm64:**
  ```bash
  curl -sL https://cartogopher.com/downloads/cartogopher/v4/linux/arm64 -o cg.zip && unzip cg.zip -d ~/.cartogopher/mcp-server && rm cg.zip
  ```

After extraction, install the MCP server dependencies:

```bash
cd ~/.cartogopher/mcp-server
npm install
```

### Step 4: Set the API Key Permanently

The API key MUST be set in the user's shell profile so the MCP server process can access it. Setting it with `export` in a single session is NOT sufficient — MCP servers run as separate processes.

```bash
# Detect shell profile
SHELL_PROFILE="$HOME/.zshrc"
[ -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ] && SHELL_PROFILE="$HOME/.bashrc"

# Add API key to shell profile (only if not already present)
if ! grep -q "CARTOGOPHER_API_KEY" "$SHELL_PROFILE" 2>/dev/null; then
  echo "export CARTOGOPHER_API_KEY=API_KEY_HERE" >> "$SHELL_PROFILE"
fi

source "$SHELL_PROFILE"
```

### Step 5: Configure the MCP Server

The MCP configuration depends on which AI tool the user runs:

**For OpenClaw (openclaw.json):**
```json
{
  "mcpServers": {
    "cartogopher": {
      "command": "node",
      "args": ["~/.cartogopher/mcp-server/cartogopher-mcp.js"],
      "env": {
        "CURSOR_WORKSPACE": ".",
        "CARTOGOPHER_API_KEY": "API_KEY_HERE"
      }
    }
  }
}
```

**For Cursor (~/.cursor/mcp.json):**
```json
{
  "mcpServers": {
    "cartogopher": {
      "command": "node",
      "args": ["~/.cartogopher/mcp-server/cartogopher-mcp.js"],
      "env": {
        "CURSOR_WORKSPACE": "${workspaceFolder}",
        "CARTOGOPHER_API_KEY": "API_KEY_HERE"
      }
    }
  }
}
```

**For Claude Code:**
```bash
claude mcp add cartogopher node ~/.cartogopher/mcp-server/cartogopher-mcp.js \
  -e CURSOR_WORKSPACE=. \
  -e CARTOGOPHER_API_KEY=API_KEY_HERE
```

### Step 6: Verify Setup

After configuration, test that the MCP tools are working by calling the `shake` tool on the user's project. If it returns a project overview, setup is complete.

## Important Notes

- Trial keys have a `cg_agent_` prefix and last 7 days
- Trial allows 2 devices simultaneously
- The MCP server must have `CARTOGOPHER_API_KEY` explicitly in its env config — it does NOT inherit from the shell
- After setup, the user must restart their AI tool (Cursor, Claude, etc.) for MCP changes to take effect
- If the user already has a CartoGopher API key (`cg_live_` or `cg_trial_`), skip the trial step and go straight to MCP configuration

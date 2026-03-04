# Commune Skill — Installation Guide

## Quick Start (OpenClaw)

```bash
openclaw skills install commune
```

Or install from GitHub:

```bash
openclaw skills add shanjairaj7/commune
```

## Quick Start (Zo Computer)

Install from the Zo Skills Hub — search for **commune** and click Install.

Or manually via the Zo terminal:

```bash
slug="commune"
dest="Skills"
manifest_url="https://raw.githubusercontent.com/zocomputer/skills/main/manifest.json"
mkdir -p "$dest" && tarball_url="$(curl -fsSL "$manifest_url" | jq -r '.tarball_url')" \
  && archive_root="$(curl -fsSL "$manifest_url" | jq -r '.archive_root')" \
  && curl -L "$tarball_url" | tar -xz -C "$dest" --strip-components=1 "$archive_root/$slug"
```

## 1. Get an API Key

1. Go to [commune.email](https://commune.email) and sign up
2. Navigate to Settings → API Keys
3. Create a new key — it starts with `comm_`

## 2. Store Your Credentials

**Option A: Environment variable (recommended)**

```bash
export COMMUNE_API_KEY="comm_your_key_here"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) to persist.

**Option B: Credentials file**

```bash
mkdir -p ~/.config/commune
cat > ~/.config/commune/credentials.json << 'EOF'
{
  "api_key": "comm_your_key_here"
}
EOF
chmod 600 ~/.config/commune/credentials.json
```

Or place `credentials.json` in the skill root directory.

## 3. Install Python SDK

```bash
pip install commune-mail
```

## 4. Verify Installation

```bash
python scripts/commune.py test
# Should output:
# ✅ Connected. 1 domain(s) in account.
```

## 5. Create Your Agent Inbox

```bash
python scripts/commune.py create-inbox --local-part myagent
# ✅ Inbox created: myagent@commune.ai
#    inbox_id : i_abc123
```

Save the `inbox_id` for future use:

```bash
mkdir -p /workspace/memory
echo '{"inbox_id": "i_abc123", "address": "myagent@commune.ai"}' \
  > /workspace/memory/commune-config.json
```

---

## Using the MCP Server (Claude Desktop / Cursor)

Commune also provides an MCP server for richer integrations:

```bash
pip install commune-mcp
```

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "commune": {
      "command": "commune-mcp",
      "env": {
        "COMMUNE_API_KEY": "comm_your_key_here"
      }
    }
  }
}
```

---

## Troubleshooting

**"commune-mail not installed"**
```bash
pip install commune-mail
```

**"No API key found"**
```bash
export COMMUNE_API_KEY="comm_..."
# or create credentials.json (see step 2)
```

**"API connection failed"**
- Verify your key starts with `comm_`
- Check your key hasn't been revoked at commune.email

**"Module not found: commune"**
- Ensure you installed `commune-mail` (not `commune`)
- Python import path is `commune`, PyPI package is `commune-mail`

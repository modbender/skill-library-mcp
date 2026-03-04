# Veeam MCP Skill for OpenClaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-Install-green)](https://clawhub.com/skills/veeam-mcp)

Query Veeam Backup & Replication and Veeam ONE using natural language through the Veeam Intelligence MCP server and OpenClaw.

## Features

- 🔍 **Natural Language Queries** - Ask about backups in plain English
- 📊 **Real-time Data** - Live backup status, repository capacity, job history
- 🚨 **Alert Monitoring** - Check Veeam ONE alerts and infrastructure health
- 🤖 **AI-Powered** - Leverages Veeam Intelligence for smart analysis
- 🐳 **Docker-based** - Isolated, secure MCP server container
- 🔐 **Secure** - Credentials stored locally, never exposed

## Example Queries

```
"What backup jobs failed last night?"
"Show me backup repository capacity"
"Which VMs haven't been backed up this week?"
"Check Veeam ONE alerts"
"What's my backup success rate?"
"Analyze backup performance trends"
```

## Quick Start

### Prerequisites

- [OpenClaw](https://openclaw.ai) installed
- Docker installed and running
- Veeam Backup & Replication or Veeam ONE with active license
- **Veeam Intelligence enabled** on your Veeam servers

### Installation

```bash
# Install skill from ClawHub
clawhub install veeam-mcp

# Or clone manually
git clone https://github.com/JGM2025/veeam-mcp-skill.git ~/.openclaw/workspace/skills/veeam-mcp
```

### Setup Veeam MCP Server

The Veeam Intelligence MCP server is currently in **beta**.

**To obtain access:**
- Contact Veeam directly or your Veeam account representative
- Visit official Veeam community forums
- Check Veeam's official channels for beta program information

Once you have the MCP server package:

```bash
cd /path/to/veeam-mcp-server
docker build -t veeam-intelligence-mcp-server .
```

### Configure Credentials

```bash
# Copy template
cp ~/.openclaw/workspace/skills/veeam-mcp/credentials-template.json ~/.veeam-mcp-creds.json

# Edit with your details
nano ~/.veeam-mcp-creds.json
```

Example `~/.veeam-mcp-creds.json`:
```json
{
  "vbr": {
    "url": "https://veeam-server.local:443/",
    "username": ".\\administrator",
    "password": "your_password"
  },
  "vone": {
    "url": "https://veeam-one.local:1239/",
    "username": ".\\administrator",
    "password": "your_password"
  }
}
```

**Lock it down:**
```bash
chmod 600 ~/.veeam-mcp-creds.json
```

### Test Connection

```bash
cd ~/.openclaw/workspace/skills/veeam-mcp
./scripts/test-connection.sh vbr
./scripts/test-connection.sh vone
```

## Usage

### From OpenClaw

Just ask naturally in any OpenClaw chat:

```
You: What backup jobs failed yesterday?
Clawd: Analyzing backup jobs... [returns detailed status]

You: Show me repository capacity
Clawd: Your repository has 1.2TB free of 2TB total (40% used)
```

### Command Line

```bash
# Query Veeam B&R
./scripts/query-veeam.sh vbr "What backup jobs ran in the last 24 hours?"

# Query Veeam ONE
./scripts/query-veeam.sh vone "Show current infrastructure alerts"

# List available MCP tools
./scripts/list-tools.sh vbr
```

## Enable Advanced Mode

For **live data queries** (not just documentation), enable Veeam Intelligence:

### Veeam Backup & Replication
1. Open Veeam B&R console
2. Go to **Options** → **Veeam Intelligence Settings**
3. Enable the AI assistant

### Veeam ONE
1. Open Veeam ONE console
2. Find **Veeam Intelligence** settings
3. Enable the feature

Without Veeam Intelligence enabled, queries will only return documentation (Basic Mode).

## Architecture

```
┌─────────────┐
│   OpenClaw  │
│   (Claude)  │
└──────┬──────┘
       │ Natural language
       ▼
┌─────────────┐
│ Veeam MCP   │
│   Skill     │
└──────┬──────┘
       │ JSON-RPC over STDIO
       ▼
┌─────────────┐
│   Docker    │
│ MCP Server  │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────┐      ┌─────────────┐
│  Veeam B&R  │      │  Veeam ONE  │
│   + Intel   │      │   + Intel   │
└─────────────┘      └─────────────┘
```

## Configuration

### Username Formats

- **Local accounts**: `".\\username"`
- **Domain accounts**: `"DOMAIN\\username"` or `"username@domain.com"`
- **Important**: Use single backslash in JSON

### Multiple Servers

Add additional Veeam servers to `~/.veeam-mcp-creds.json`:

```json
{
  "vbr": { ... },
  "vone": { ... },
  "vbr-site2": {
    "url": "https://veeam-dr.local:443/",
    "username": ".\\administrator",
    "password": "password"
  }
}
```

## Troubleshooting

### Connection Fails

**Check Docker permissions:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Verify credentials:**
```bash
cat ~/.veeam-mcp-creds.json | jq .
```

**Test Docker image:**
```bash
docker run -i --rm veeam-intelligence-mcp-server
```

### "Basic Mode" Warning

Enable Veeam Intelligence on your Veeam servers. Without it, only documentation queries work.

### Invalid Username Format

The Veeam API requires specific formats:
- Try `".\\username"` (local)
- Try `"DOMAIN\\username"` (domain)
- Ensure **single backslash** in JSON: `".\\"` not `".\\\\"`

## Security

- ✅ Credentials stored locally only (`~/.veeam-mcp-creds.json`)
- ✅ Docker container runs as non-root user
- ✅ MCP communication via stdin/stdout (no network exposure)
- ✅ HTTPS with self-signed cert support
- ✅ No credentials in logs or command history

## Files

```
veeam-mcp/
├── SKILL.md                    # Full documentation
├── README.md                   # Quick setup guide
├── credentials-template.json   # Credentials template
├── .gitignore                  # Excludes credentials
├── scripts/
│   ├── query-veeam.sh         # Main query interface
│   ├── test-connection.sh     # Connection testing
│   ├── start-mcp.sh           # Interactive MCP session
│   └── list-tools.sh          # List MCP tools
└── .clawhub/
    └── metadata.json          # ClawHub metadata
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## Support

- **Veeam MCP Server**: Contact Veeam for beta access
- **OpenClaw**: [Discord](https://discord.com/invite/clawd) | [Docs](https://docs.openclaw.ai)
- **Issues**: [GitHub Issues](https://github.com/JGM2025/veeam-mcp-skill/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

Veeam Intelligence MCP server is licensed separately by Veeam Software Group.

## Acknowledgments

- [Veeam Software](https://www.veeam.com/) for Veeam Intelligence MCP server
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenClaw](https://openclaw.ai/) community

---

**Made with 🐾 for the OpenClaw community**

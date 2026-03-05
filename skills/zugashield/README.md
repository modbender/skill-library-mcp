# @zugashield/openclaw-plugin

ZugaShield security scanning for [OpenClaw](https://github.com/openclaw/openclaw) — protects **all channels** (Signal, Telegram, Discord, WhatsApp, web) from a single plugin.

## What It Does

Intercepts every message, tool call, and response through OpenClaw's Gateway hooks:

| Hook | ZugaShield Tool | Protects Against |
|------|----------------|-----------------|
| `preRequest` | `scan_input` | Prompt injection, unicode smuggling, instruction override |
| `preToolExecution` | `scan_tool_call` | SSRF, command injection, path traversal |
| `preResponse` | `scan_output` | Secret leakage, PII exposure, data exfiltration |
| `preRecall` | `scan_memory` | Memory poisoning, embedded instructions |

**7 defense layers, 150+ threat signatures, <15ms per scan.**

## Architecture

```
User (any channel) → OpenClaw Gateway → ZugaShield hooks → zugashield-mcp (Python, stdio)
```

The plugin spawns `zugashield-mcp` as a managed child process. The process stays resident — no per-call spawn cost. Tool calls are **always fail-closed** regardless of config.

## Install (5 steps)

### 1. Install ZugaShield with MCP support

```bash
pip install "zugashield[mcp]"
```

### 2. Install the plugin

```bash
cd your-openclaw-directory
npm install @zugashield/openclaw-plugin
```

Or clone into `extensions/`:

```bash
cd extensions
git clone https://github.com/AntonioCiolworking/zugashield-openclaw-plugin zugashield
cd zugashield && npm install && npm run build
```

### 3. Add to openclaw.json

```json
{
  "plugins": {
    "entries": {
      "zugashield": {
        "enabled": true,
        "config": {
          "fail_closed": true,
          "strict_mode": false
        }
      }
    }
  }
}
```

### 4. Restart OpenClaw

```bash
openclaw restart
```

### 5. Verify

Send `/shield status` from any channel. You should see:

```
--- ZugaShield Status ---
Python: 3.12.0
Scanner: CONNECTED
Fail-closed: true
Strict mode: false
Scanning: inputs=true outputs=true tools=true memory=true
```

## Configuration

All fields are optional — defaults are secure.

```json
{
  "fail_closed": true,
  "strict_mode": false,
  "scan": {
    "inputs": true,
    "outputs": true,
    "tool_calls": true,
    "memory": true
  },
  "excluded_channels": [],
  "mcp": {
    "python_executable": "python",
    "call_timeout_ms": 80,
    "startup_timeout_ms": 8000,
    "max_reconnect_attempts": 10
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `fail_closed` | `true` | Block requests when scanner is unavailable |
| `strict_mode` | `false` | Block medium+ threats (not just high/critical) |
| `scan.*` | all `true` | Toggle individual scan layers |
| `excluded_channels` | `[]` | Channel IDs to skip (tool calls are never skipped) |
| `mcp.python_executable` | `"python"` | Path to Python 3.10+ |
| `mcp.call_timeout_ms` | `80` | Per-scan timeout in milliseconds |
| `mcp.startup_timeout_ms` | `8000` | MCP server startup timeout |
| `mcp.max_reconnect_attempts` | `10` | Auto-reconnect attempts before giving up |

## Commands

- `/shield status` — Connection state, Python version, enabled layers
- `/shield report` — Scan count, block count, recent threat events

## Development

```bash
npm install
npm run build
npm test
```

## License

MIT

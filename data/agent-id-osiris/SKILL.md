---
name: agent-identity
version: 1.0.3
description: Cryptographic identity for AI agents - sign and verify agent messages
metadata: {"openclaw": {"emoji": "🆔", "category": "security", "requires": {"bins": ["python"], "pip": ["cryptography"]}, "homepage": "https://github.com"}}
---

# Agent Identity Skill

Cryptographic identity system for AI agents. Sign messages, verify agents, prove who you are.

**Files included:**
- `identity.py` - Python CLI (cross-platform)
- `agent-identity.ps1` - PowerShell wrapper (Windows)

## What it does

- **Generate Key Pair** - Create Ed25519 or RSA keys for your agent
- **Sign Messages** - Cryptographically sign messages
- **Verify Signatures** - Verify messages from other agents
- **Agent ID** - Generate persistent agent ID from public key
- **Agent Card** - Generate signed Agent Card for A2A/MCP

## Installation

```powershell
# Install Python dependency
pip install cryptography
```

## Usage

### Option 1: PowerShell (recommended on Windows)

```powershell
.\agent-identity.ps1 -Action generate -AgentName "MyAgent" -KeyType ed25519 -Password "secret123"
```

### Option 2: Python CLI (cross-platform)

```powershell
python identity.py generate --name MyAgent --key-type ed25519 --password secret123
```

## Available Commands

All commands work with both PowerShell and Python:

### Generate Identity (with password encryption)

```powershell
.\agent-identity.ps1 -Action generate -AgentName "MyAgent" -KeyType ed25519 -Password "secret123"
```

### Sign Message

```powershell
.\agent-identity.ps1 -Action sign -Message "Hello world" -PrivateKeyPath "keys/private.pem" -Password "secret123"
```

### Verify Signature

```powershell
.\agent-identity.ps1 -Action verify -Message "Hello world" -Signature "base64-signature" -PublicKeyPath "keys/public.pem"
```

### Get Agent ID

```powershell
.\agent-identity.ps1 -Action id -PublicKeyPath "keys/public.pem"
```

### Sign Agent Card

```powershell
.\agent-identity.ps1 -Action card -PublicKeyPath "keys/public.pem" -PrivateKeyPath "keys/private.pem" -Name "MyAgent" -Description "Research agent" -Capabilities "research,analysis" -Endpoint "https://myagent.com/a2a" -Password "secret123"
```

## ⚠️ Security Warnings

### Password on Command Line
**WARNING:** Passing passwords on the command line is insecure because:
- CLI arguments can be visible to other processes
- Command history is stored in logs
- Use only for testing, not production

For production, use interactive password input or environment variables.

### Private Key Storage
- Keys are stored in `keys/` directory
- Ensure proper file permissions
- Back up your keys securely
- Never share your private key

## Requirements

- Python 3.8+
- cryptography library

## License

MIT

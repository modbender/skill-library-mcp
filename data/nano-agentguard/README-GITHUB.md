# AgentGuard

**Agent Identity & Permission Guardian** — Trust middleware for the Agentic Era

[![npm version](https://badge.fury.io/js/agentguard.svg)](https://badge.fury.io/js/agentguard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why AgentGuard?

In the Agentic Era, AI agents need:
- **Secure credential storage** (API keys, OAuth tokens)
- **Permission boundaries** (what can they do?)
- **Human oversight** (dangerous operations need approval)
- **Audit trails** (who did what, when?)

AgentGuard provides all of this in a single, easy-to-use package.

## Installation

```bash
npm install -g agentguard
```

## Quick Start

```bash
# Initialize
agentguard init

# Register an agent
agentguard register my-agent --owner "you@example.com" --level write

# Store credentials
agentguard vault store my-agent OPENAI_API_KEY sk-xxx

# Check permissions
agentguard check my-agent send_email

# View audit logs
agentguard audit show my-agent --last 10
```

## Features

### 🔐 Credential Vault
- AES-256-GCM encryption
- Per-agent credential isolation
- Secure key derivation (PBKDF2)
- **1Password integration** (optional)

### 🎯 Permission Scopes
- Levels: `read` → `write` → `admin` → `dangerous`
- Dangerous operations require human approval
- Configurable per-agent policies

### 🚪 Human Gate
- Push approval requests to owners
- Timeout-based expiration
- Audit-tracked decisions

### 📝 Audit Trail
- Cryptographic hash chain
- Tamper detection
- Exportable reports

### 🔑 1Password Integration
- Store master password in 1Password
- Sync credentials between 1Password and local vault
- Use 1Password references in your workflow

## 1Password Integration

```bash
# Check 1Password status
agentguard op status

# Enable 1Password integration
agentguard op enable --vault Private

# Store credential (goes to both 1Password and local)
echo "sk-xxx" | agentguard op store my-agent OPENAI_API_KEY

# Get 1Password reference
agentguard op ref my-agent OPENAI_API_KEY
# → op://Private/AgentGuard: my-agent - OPENAI_API_KEY/credential
```

## API Usage

```javascript
const AgentGuard = require('agentguard');

const guard = new AgentGuard({
  masterPassword: 'your-secure-password',
  use1Password: true
});

await guard.init();

// Check permission (will request approval if needed)
const check = await guard.checkOrApprove('my-agent', 'send_email', {
  to: 'user@example.com'
});

if (check.allowed) {
  // Proceed with operation
}
```

## Permission Levels

| Level | Auto-approve | Requires Human |
|-------|--------------|----------------|
| `read` | ✅ Read operations | ❌ |
| `write` | ✅ Read/Write | ❌ |
| `admin` | ✅ Most operations | ⚠️ Dangerous only |
| `dangerous` | ❌ All operations | ✅ Always |

## Dangerous Operations

- `send_message`, `send_email`
- `financial_transaction`
- `delete_data`
- `modify_config`
- `access_credential`
- `external_api_call`
- `file_write`, `exec_command`

## CLI Reference

```bash
agentguard init                          # Initialize
agentguard register <id>                 # Register agent
agentguard list                          # List agents

agentguard vault store <agent> <key> <value>  # Store credential
agentguard vault get <agent> <key>            # Get credential
agentguard vault list <agent>                 # List keys

agentguard scope set <agent> [-l level]       # Set permission
agentguard scope info <agent>                  # Get permission info

agentguard check <agent> <operation>          # Check permission

agentguard pending                            # List pending approvals
agentguard approve <requestId>                # Approve request
agentguard deny <requestId>                   # Deny request

agentguard audit show <agent> [--last N]      # Show logs
agentguard audit verify <agent> <date>        # Verify integrity
agentguard audit stats <agent>                # Show statistics

agentguard op status                          # 1Password status
agentguard op enable                          # Enable 1Password
agentguard op sync <agent>                    # Sync credentials
agentguard op ref <agent> <key>               # Get reference
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  AgentGuard                      │
├─────────────────────────────────────────────────┤
│  Vault        │  Registry  │  Scope             │
│  (encrypt)    │  (agents)  │  (permissions)     │
├─────────────────────────────────────────────────┤
│  Human Gate   │  Audit     │  CLI / API         │
│  (approvals)  │  (logs)    │  (interface)       │
├─────────────────────────────────────────────────┤
│  1Password Provider (optional)                  │
└─────────────────────────────────────────────────┘
```

## Security Model

1. **Vault**: AES-256-GCM + PBKDF2 (100k iterations)
2. **Isolation**: Each agent has separate encrypted container
3. **Audit**: SHA-256 hash chain for integrity
4. **Human Gate**: Out-of-band confirmation
5. **1Password**: Master password stored in 1Password, never on disk

## Comparison with 1Password

| | 1Password | AgentGuard |
|---|-----------|------------|
| **Built for** | Humans | AI Agents |
| **Credential storage** | ✅ | ✅ |
| **Permission levels** | ❌ | ✅ |
| **Human approval** | ❌ | ✅ |
| **Audit trail** | ⚠️ | ✅ |
| **Cross-device sync** | ✅ | Via 1Password |

**They complement each other, they don't compete.**

See [1Password Comparison](docs/1PASSWORD-COMPARISON.md) for details.

## Install from ClawHub

```bash
clawhub install nano-agentguard
```

## Roadmap

- [x] Phase 1: CLI + Vault + Permissions
- [x] Phase 1: Human Gate (console)
- [x] Phase 1: Audit Trail
- [x] Phase 1: 1Password integration
- [ ] Phase 1: Feishu/Telegram integration for approvals
- [ ] Phase 1: OAuth2 token auto-refresh
- [ ] Phase 2: DID integration

## License

MIT

---

*Building trust infrastructure for the Agentic Era.* ⚡

# AgentGuard ⚡🔐

**Agent Identity & Permission Guardian** — Trust middleware for the Agentic Era

## Why AgentGuard?

In the Agentic Era, AI agents need:
- **Secure credential storage** (API keys, OAuth tokens)
- **Permission boundaries** (what can they do?)
- **Human oversight** (dangerous operations need approval)
- **Audit trails** (who did what, when?)

AgentGuard provides all of this in a single, easy-to-use package.

## Quick Start

```bash
# Install
npm install -g agentguard

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

AgentGuard can use 1Password as a credential backend:

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

# Sync from 1Password
agentguard op sync my-agent
```

### How it works

```
┌─────────────────────────────────────────────────┐
│                   1Password                      │
│   Master password + agent credentials            │
└─────────────────────────────────────────────────┘
                      ↕ sync
┌─────────────────────────────────────────────────┐
│                   AgentGuard                     │
│   Local encrypted cache + permission logic       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│                  AI Agent                        │
└─────────────────────────────────────────────────┘
```

### Benefits

| Feature | 1Password | AgentGuard | Together |
|---------|-----------|------------|----------|
| Human password manager | ✅ | ❌ | ✅ |
| Agent credential storage | ⚠️ | ✅ | ✅ |
| Permission boundaries | ❌ | ✅ | ✅ |
| Human approval workflow | ❌ | ✅ | ✅ |
| Cross-device sync | ✅ | ❌ | ✅ |
| Offline access | ❌ | ✅ | ✅ |

## API Usage

```javascript
const AgentGuard = require('agentguard');

const guard = new AgentGuard({
  masterPassword: 'your-secure-password',
  use1Password: true,  // Enable 1Password
  opVault: 'Private'
});

await guard.init();

// Register agent
await guard.registerAgent('my-agent', {
  owner: 'you@example.com',
  level: 'write'
});

// Check permission (will request approval if needed)
const check = await guard.checkOrApprove('my-agent', 'send_email', {
  to: 'user@example.com',
  subject: 'Hello'
});

if (check.allowed) {
  // Proceed with operation
}
```

## Permission Levels

| Level | Description | Auto-approve |
|-------|-------------|--------------|
| `read` | Read-only operations | ✅ |
| `write` | Read + Write | ✅ |
| `admin` | Most operations | ⚠️ Dangerous only |
| `dangerous` | All operations | ❌ Always require approval |

## Dangerous Operations

These operations always require human approval (unless policy is `auto-approve`):

- `send_message`, `send_email`
- `financial_transaction`
- `delete_data`
- `modify_config`
- `access_credential`
- `external_api_call`
- `file_write`, `exec_command`

## CLI Reference

```bash
# Initialize
agentguard init

# Agent management
agentguard register <id> [-o owner] [-l level] [-d policy]
agentguard list [-o owner] [-s status]

# Vault
agentguard vault store <agent> <key> <value>
agentguard vault get <agent> <key>
agentguard vault list <agent>

# Scope
agentguard scope set <agent> [-l level] [-d policy]
agentguard scope info <agent>
agentguard scope operations

# Approval
agentguard pending [-a agent]
agentguard approve <requestId> [-b by]
agentguard deny <requestId> [-b by] [-r reason]

# Audit
agentguard audit show <agent> [-n last] [-o operation]
agentguard audit verify <agent> <date>
agentguard audit stats <agent> [-d days]
agentguard audit export <agent>

# Check
agentguard check <agent> <operation>

# 1Password
agentguard op status
agentguard op enable [-a account] [-v vault]
agentguard op sync <agent>
agentguard op ref <agent> <key>
agentguard op store <agent> <key>  # reads from stdin
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
│  (external credential source)                   │
└─────────────────────────────────────────────────┘
```

## Security Model

1. **Vault**: AES-256-GCM + PBKDF2 (100k iterations)
2. **Isolation**: Each agent has separate encrypted container
3. **Audit**: SHA-256 hash chain for integrity
4. **Human Gate**: Out-of-band confirmation
5. **Token Expiry**: Short-lived tokens (configurable)
6. **1Password**: Master password stored in 1Password, never on disk

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

---
name: agentguard
description: Agent Identity & Permission Guardian - Trust middleware for credential management, permission scopes, human approval workflows, and audit trails. Use when AI agents need secure credential storage, permission boundaries, or human oversight for dangerous operations.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "category": "security",
        "requires": { "node": ">=18" },
        "install":
          [
            {
              "id": "npm",
              "kind": "npm",
              "package": "agentguard",
              "label": "Install via npm",
            },
          ],
      }
  }
---

# AgentGuard - Agent Identity & Permission Guardian

## Overview

AgentGuard is a trust middleware for Phase 1 hybrid authentication:
- **Credential Vault**: Encrypted storage for API keys and OAuth tokens
- **Permission Scopes**: Define what operations need human approval
- **Human Gate**: Push confirmation requests for high-risk operations
- **Audit Trail**: Cryptographically signed operation logs
- **Agent Registry**: Track agents with credentials and permissions

## Installation

```bash
# Install globally
npm install -g agentguard

# Or use as OpenClaw skill
cp -r . ~/.openclaw/skills/agentguard
```

## Quick Start

```bash
# Initialize vault
agentguard init

# Register an agent
agentguard register my-agent --owner "user@example.com"

# Store a credential
agentguard vault store my-agent OPENAI_API_KEY sk-xxx

# Define permission scope
agentguard scope set my-agent --level read --dangerous require-approval

# List agents
agentguard list

# Audit log
agentguard audit my-agent --last 24h
```

## Permission Levels

| Level | Auto-approve | Requires Human |
|-------|--------------|----------------|
| `read` | ✅ Read operations | ❌ |
| `write` | ✅ Read/Write | ❌ |
| `admin` | ✅ Most operations | ⚠️ Dangerous only |
| `dangerous` | ❌ All operations | ✅ Always |

## Dangerous Operations (Require Human Approval)

- Send messages/emails
- Financial transactions
- Delete data
- Modify system config
- Access sensitive credentials
- External API calls (configurable)

## Human Gate Integration

When an agent attempts a dangerous operation:

1. AgentGuard blocks the operation
2. Pushes notification to owner (Feishu/Telegram/Email)
3. Owner approves/denies with biometric confirmation
4. If approved, operation proceeds with short-lived token
5. All logged with cryptographic signature

## Configuration

`~/.agentguard/config.json`:

```json
{
  "vault": {
    "encryption": "aes-256-gcm",
    "keyDerivation": "pbkdf2"
  },
  "humanGate": {
    "timeout": 300,
    "channels": ["feishu", "telegram"],
    "biometric": true
  },
  "audit": {
    "retention": "30d",
    "signLogs": true
  }
}
```

## API Usage (for skills)

```javascript
const agentguard = require('agentguard');

// Check permission
const allowed = await agentguard.check('my-agent', 'send_email');
if (!allowed) {
  // Request human approval
  const approval = await agentguard.requestApproval({
    agent: 'my-agent',
    action: 'send_email',
    details: { to: 'user@example.com', subject: 'Test' }
  });
}

// Get credential
const apiKey = await agentguard.getCredential('my-agent', 'OPENAI_API_KEY');

// Log action
await agentguard.audit('my-agent', 'api_call', { endpoint: '/completions' });
```

## Security Model

1. **Vault Encryption**: AES-256-GCM with key derived from master password
2. **Credential Isolation**: Each agent has separate encrypted container
3. **Audit Integrity**: SHA-256 hash chain for tamper detection
4. **Human Gate**: Out-of-band confirmation via trusted channel
5. **Token Expiry**: Short-lived tokens (default 5 min)

## Files

- `~/.agentguard/` - Data directory
- `~/.agentguard/vault/` - Encrypted credentials
- `~/.agentguard/registry.json` - Agent registry
- `~/.agentguard/audit/` - Audit logs
- `~/.agentguard/config.json` - Configuration

## OpenClaw Integration

AgentGuard integrates with OpenClaw as a skill:

1. Add to `~/.openclaw/skills/agentguard/`
2. Configure in workspace `AGENTS.md`:
   ```
   ## AgentGuard
   All external API calls require AgentGuard permission check.
   Dangerous operations require human approval.
   ```
3. Use in other skills:
   ```javascript
   const guard = require('agentguard');
   await guard.checkOrApprove(agentId, operation, details);
   ```

## Roadmap

- [ ] Phase 1: CLI + Vault + Permission Scopes
- [ ] Phase 2: Human Gate (Feishu/Telegram integration)
- [ ] Phase 3: Audit Trail + Export
- [ ] Phase 4: OAuth2 Token Auto-refresh
- [ ] Phase 5: Multi-tenant Support
- [ ] Phase 6: DID Preparation (future Phase 2)

---

*Building trust infrastructure for the Agentic Era.*

# AgentGuard

> Agent Identity & Permission Guardian — Trust middleware for the Agentic Era

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

- 🔐 **Credential Vault** - AES-256-GCM encrypted storage
- 🎯 **Permission Scopes** - read/write/admin/dangerous levels
- 🚪 **Human Gate** - Approval workflow for dangerous operations
- 📝 **Audit Trail** - SHA-256 hash chain logging
- 🔑 **1Password Integration** - Sync credentials with 1Password

## Documentation

See [README.md](https://github.com/openclaw/agentguard#readme) for full documentation.

## License

MIT

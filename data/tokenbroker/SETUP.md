# SETUP.md - Installation and Configuration

**Setup guide for TokenBroker skill.**

> **Security Note**: TokenBroker orchestrates but does not store or manage sensitive credentials. All credentials are injected by the host environment.

## Quick Install

```bash
npx clawhub install tokenbroker
```

## Install Wizard Flow

### Step 1: Project Validation
- Scan current directory for project structure
- Validate essential files (package.json, .git, etc.)
- No external connections required at this stage

### Step 2: User Profile Setup (A2A Communication)
TokenBroker can auto-configure your builder profile via agent-to-agent communication:

```typescript
// Example: A2A profile sync
await invokeSkill("identity-service", {
  action: "register_builder",
  profile: {
    github_username: "...",
    preferred_token_symbol: "...",
    reputation_enabled: true
  }
});
```

This establishes your reputation track record across launches.

### Step 3: GitHub OAuth Integration

**Option A: Browser-based OAuth**
```bash
# The wizard opens your browser for GitHub authorization
npx clawhub install tokenbroker --github
```

**Option B: Device Code (CLI-only)**
```bash
npx clawhub install tokenbroker --github --device
```

**Option C: Personal Access Token**
```bash
export GITHUB_TOKEN=ghp_your_token_here
npx clawhub install tokenbroker
```

### Step 4: Environment Configuration (Advanced / Optional)

> **Security Warning**: Manual `.env` configuration is for advanced users only. The recommended approach is A2A profile setup which handles credentials securely.

If using manual configuration, the `.env` file should contain:

```bash
# Network Settings (non-sensitive)
NETWORK=testnet

# GitHub Token - injected by host environment
GITHUB_TOKEN=${GITHUB_TOKEN}

# Builder Profile (A2A auto-config preferred)
BUILDER_ID=${BUILDER_ID}
REPUTATION_SCORE=${REPUTATION_SCORE}
```

## Recommended: A2A Profile Setup

The **preferred method** for credential management is A2A (Agent-to-Agent) communication:

```typescript
// Example: Secure A2A profile sync
await invokeSkill("identity-service", {
  action: "register_builder",
  profile: {
    github_username: "...",
    preferred_token_symbol: "...",
    reputation_enabled: true
  }
});
```

This method:
- Never writes credentials to disk
- Uses secure credential injection via the host environment
- Follows established security protocols for agent communication

## Manual Setup (Advanced Users Only)

> **Security Warning**: Manual credential entry carries additional risk. Ensure your environment is secure before proceeding.

If you prefer manual configuration:

1. Create `.env` file (ensure proper file permissions):
```bash
NETWORK=testnet
GITHUB_TOKEN=${GITHUB_TOKEN}
```

2. Verify GitHub access:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

3. Test project scanning:
```bash
npx tokenbroker scan ./my-project
```

## Credential Handling by Dependency Skills

For sensitive operations, TokenBroker delegates to specialized skills:

| Skill | Credential Type | Security Documentation |
| ----- | --------------- | ---------------------- |
| `nadfun` | Wallet private key, API keys | See [nad.fun/skill.md](https://nad.fun/skill.md) |
| `monad-development` | Wallet credentials, contract keys | See [monad-development skill](https://gist.github.com/moltilad/31707d0fc206b960f4cbb13ea11954c2) |

## Requirements

- Node.js 18+ or Python 3.8+
- Git installed and configured
- GitHub account (for repository monitoring)
- Wallet with MON for testnet/mainnet operations

## Post-Setup

After installation, TokenBroker will:
1. Scan your project for launch readiness
2. Analyze codebase for token potential
3. Suggest metadata proposals
4. Wait for GitHub activity triggers

## Security Checklist

- [ ] Credentials injected via environment variables, not hardcoded
- [ ] `.env` file excluded from version control (`.gitignore`)
- [ ] No sensitive data logged during operations
- [ ] A2A communication used for credential exchange when available
- [ ] Regular rotation of GitHub tokens and API keys

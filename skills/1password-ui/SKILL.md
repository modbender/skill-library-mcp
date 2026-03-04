---
name: 1password-ui
description: 1Password UI tab for OpenClaw dashboard. Manage secrets, credential mappings, and auth state from the Control UI.
version: 1.1.0
author: OpenClaw Community
metadata: {"clawdbot":{"emoji":"🔐","requires":{"clawdbot":">=2026.1.0"},"category":"tools"}}
---

# 1Password UI Extension

Adds a **1Password** tab to the OpenClaw Control dashboard under the **Tools** group. Browse vaults, manage credential mappings for skills, and handle authentication — all from the web UI.

## Features

| Feature | Description |
|---------|-------------|
| **Dashboard Tab** | "1Password" under Tools in sidebar |
| **Connection Status** | See signed-in account, CLI/Connect mode |
| **Sign In Flow** | Authenticate directly from the UI |
| **Docker Support** | Works with 1Password Connect for containers |
| **Credential Mappings** | Map 1Password items to skill configs |

## Agent Installation Prompt

To install this skill, give your agent this prompt:

```
Install the 1password-ui skill from ClawHub.

The skill is at: ~/clawd/skills/1password-ui/
Follow INSTALL_INSTRUCTIONS.md step by step.

Summary of changes needed:
1. Copy 1password-backend.ts to src/gateway/server-methods/1password.ts
2. Register handlers in server-methods.ts
3. Add "1password" tab to navigation.ts (TAB_GROUPS, Tab type, TAB_PATHS, icon, title, subtitle)
4. Add state variables to app.ts
5. Copy 1password-views.ts to ui/src/ui/views/1password.ts
6. Add view rendering to app-render.ts
7. Add tab loading to app-settings.ts
8. Build and restart: pnpm build && pnpm ui:build && clawdbot gateway restart
```

## Prerequisites

### For Local Installations (Ubuntu/Windows/macOS)

1. **1Password CLI** (`op`):
   ```bash
   # macOS/Linux
   brew install 1password-cli
   
   # Or from https://1password.com/downloads/command-line/
   ```

2. **CLI Integration** enabled in 1Password app:
   - Settings → Developer → "Integrate with 1Password CLI" ✓

### For Docker Installations

See [Docker Setup](#docker-setup-1password-connect) below.

## Usage

### Sign In

1. Open OpenClaw Dashboard → **Tools** → **1Password**
2. Click **Sign In with 1Password**
3. Authorize in the 1Password app popup (or run `op signin` in terminal)
4. Status shows "Connected" with your account

### Credential Mappings

Once signed in, you can map 1Password items to skills:

1. Skills like Pipedream can read credentials from 1Password
2. Mappings are stored in `~/clawd/config/1password-mappings.json`
3. Format: `{ "skillId": { "item": "Item Name", "vault": "Private", "fields": {...} } }`

### Example: Pipedream with 1Password

```bash
# Store Pipedream credentials in 1Password
op item create --category="API Credential" --title="Pipedream Connect" \
  --vault="Private" \
  "client_id[text]=your_client_id" \
  "client_secret[password]=your_client_secret" \
  "project_id[text]=proj_xxxxx"

# Use in token refresh
PIPEDREAM_1PASSWORD_ITEM="Pipedream Connect" python3 ~/clawd/scripts/pipedream-token-refresh.py
```

## Gateway RPC Methods

| Method | Description |
|--------|-------------|
| `1password.status` | Get CLI/Connect status, signed-in account |
| `1password.signin` | Trigger sign-in flow |
| `1password.signout` | Sign out of current session |
| `1password.vaults` | List available vaults |
| `1password.items` | List items in a vault |
| `1password.getItem` | Get item field structure (not values) |
| `1password.readSecret` | Read a secret (backend only) |
| `1password.mappings.list` | Get skill → 1Password mappings |
| `1password.mappings.set` | Create/update a mapping |
| `1password.mappings.delete` | Remove a mapping |
| `1password.mappings.test` | Test if a mapping works |

## Docker Setup (1Password Connect)

For Docker-based OpenClaw installations, use 1Password Connect instead of the CLI.

### Step 1: Deploy 1Password Connect

```yaml
# docker-compose.yml
services:
  op-connect-api:
    image: 1password/connect-api:latest
    ports:
      - "8080:8080"
    volumes:
      - ./1password-credentials.json:/home/opuser/.op/1password-credentials.json:ro
      - op-data:/home/opuser/.op/data

  op-connect-sync:
    image: 1password/connect-sync:latest
    volumes:
      - ./1password-credentials.json:/home/opuser/.op/1password-credentials.json:ro
      - op-data:/home/opuser/.op/data

volumes:
  op-data:
```

### Step 2: Get Credentials

1. Go to [my.1password.com](https://my.1password.com) → Integrations → Secrets Automation
2. Create a Connect server
3. Download `1password-credentials.json`
4. Create an access token

### Step 3: Configure OpenClaw

```yaml
services:
  clawdbot:
    environment:
      - OP_CONNECT_HOST=http://op-connect-api:8080
      - OP_CONNECT_TOKEN=your-access-token
```

The UI automatically detects Connect mode.

## Files Included

```
1password-ui/
├── SKILL.md                      # This file
├── INSTALL_INSTRUCTIONS.md       # Step-by-step installation
├── CHANGELOG.md                  # Version history
├── package.json                  # Skill metadata
├── reference/
│   ├── 1password-backend.ts      # Gateway RPC handlers
│   ├── 1password-views.ts        # UI view (Lit template)
│   ├── 1password-settings.ts     # Tab loading logic
│   └── 1password-plugin.ts       # Plugin registration (optional)
└── scripts/
    └── op-helper.py              # CLI/Connect bridge for skills
```

## Security Considerations

### ✅ Safe by Design

| Aspect | Implementation |
|--------|----------------|
| **Secrets not in UI** | `getItem` and `items` return field names only, never values |
| **No network installers** | No `curl \| sh` or remote scripts — all code is local |
| **Manual installation** | Requires explicit code edits, no automated patching |
| **Mapping file perms** | `1password-mappings.json` should be 0600 (contains references, not secrets) |
| **CLI auth** | Uses 1Password app integration for biometric auth when available |

### ⚠️ Documented Risks

| Risk | Mitigation |
|------|------------|
| **`readSecret` RPC available** | The `1password.readSecret` method IS exposed via gateway RPC. This is intentional — skills need to read secrets. Security relies on: (1) 1Password requiring user auth, (2) gateway access control (loopback-only by default). |
| **Gateway exposure** | All `1password.*` methods are RPC calls. If you expose your gateway to the network, protect it with authentication. |
| **Connect token** | In Docker mode, `OP_CONNECT_TOKEN` grants vault access. Keep it secure like any API key. |

### File Security

```bash
# Recommended permissions for mapping file
chmod 600 ~/clawd/config/1password-mappings.json
```

## Troubleshooting

### "1Password CLI Not Found"
```bash
brew install 1password-cli
# or download from 1password.com/downloads/command-line/
```

### "Not signed in"
```bash
op signin
op whoami  # verify
```

### Sign-in fails / "authorization denied"
- Unlock the 1Password app
- Enable CLI integration: Settings → Developer → "Integrate with 1Password CLI"

### Docker: "connection refused"
```bash
docker ps | grep op-connect  # check containers running
```

### Docker: "401 unauthorized"
- Verify `OP_CONNECT_TOKEN` is set correctly
- Check token hasn't expired

## Support

- **ClawHub**: [clawhub.ai/skills/1password-ui](https://clawhub.ai/skills/1password-ui)
- **1Password CLI**: [developer.1password.com/docs/cli](https://developer.1password.com/docs/cli)
- **1Password Connect**: [developer.1password.com/docs/connect](https://developer.1password.com/docs/connect)
- **OpenClaw Discord**: [discord.com/invite/clawd](https://discord.com/invite/clawd)

## Changelog

### v1.1.0 (2025-02-11)
- Full working implementation with dashboard UI
- Sign-in flow from web interface
- CLI and Connect mode support
- Credential mapping system

### v1.0.0 (2025-02-11)
- Initial release with reference implementations

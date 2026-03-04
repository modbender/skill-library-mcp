# Installation Guide for Agents

This guide is for AI agents installing the Pipedream Connect skill into a OpenClaw instance.

## ⚠️ Security Notice

Before installing, inform the user:

| What | Storage | Risk |
|------|---------|------|
| Client ID/Secret | `~/openclaw/config/pipedream-credentials.json` | Plaintext JSON (0600 perms) |
| Access tokens | `~/openclaw/config/mcporter.json` headers | Plaintext JSON |
| Cron job | User's crontab | Runs every 45 min, persists |

**Credentials are stored in the OpenClaw vault** (`~/.openclaw/secrets.json`, mode 0600).

## Prerequisites Check

Before installing, verify:

```bash
# Check OpenClaw version (need 2026.1.0+)
openclaw --version

# Check mcporter is installed
which mcporter

# Check gateway is running
openclaw gateway status
```

## Installation Steps

### Step 1: Copy Token Refresh Script

```bash
mkdir -p ~/openclaw/scripts ~/openclaw/logs
cp ~/openclaw/skills/pipedream-connect/scripts/pipedream-token-refresh.py ~/openclaw/scripts/
chmod +x ~/openclaw/scripts/pipedream-token-refresh.py
```

### Step 2: Set Up Cron Job

```bash
# Option A: Use setup script
bash ~/openclaw/skills/pipedream-connect/scripts/setup-cron.sh

# Option B: Manual setup
(crontab -l 2>/dev/null; echo "*/45 * * * * /usr/bin/python3 $HOME/clawd/scripts/pipedream-token-refresh.py --quiet >> $HOME/clawd/logs/pipedream-cron.log 2>&1") | crontab -
```

### Step 3: Verify Backend Integration

The Pipedream backend handlers are built into OpenClaw 2026.1.0+. Verify they're available:

```bash
# Test the RPC endpoint
curl -s http://localhost:18789/rpc \
  -H "Content-Type: application/json" \
  -d '{"method":"pipedream.status","params":{}}' | head -100
```

Should return `{"configured":false,...}` or similar.

### Step 4: Guide User Through Setup

Inform the user:

1. **Get Pipedream Credentials**
   - Create account at [pipedream.com](https://pipedream.com)
   - Get OAuth Client from [pipedream.com/settings/api](https://pipedream.com/settings/api)
   - Create Project at [pipedream.com/projects](https://pipedream.com/projects)

2. **Configure in UI**
   - Open OpenClaw Dashboard → Tools → Pipedream
   - Enter Client ID, Client Secret, Project ID
   - Click Save Credentials

3. **Connect Apps**
   - Click Connect on desired apps
   - Complete OAuth in popup
   - Click Connect again to finalize

## Verification

After setup, verify the integration works:

```bash
# List configured servers
cat ~/openclaw/config/mcporter.json | grep -A2 '"pipedream'

# Test token refresh
python3 ~/openclaw/scripts/pipedream-token-refresh.py

# If an app is connected, test it
mcporter call pipedream-openclaw-gmail.gmail-list-labels instruction="List labels"
```

## Troubleshooting

### Backend Not Available

If `pipedream.status` returns "unknown method", the OpenClaw version may be too old:

```bash
# Update OpenClaw
cd ~/openclaw && git pull && npm run build
openclaw gateway restart
```

### UI Page Missing

If the Pipedream page doesn't appear in the dashboard:

```bash
# Rebuild UI
cd ~/openclaw && npm run ui:build
openclaw gateway restart
```

### Token Refresh Failing

Check credentials and logs:

```bash
# View logs
tail -20 ~/openclaw/logs/pipedream-token-refresh.log

# Verify credentials exist
cat ~/openclaw/config/pipedream-credentials.json

# Manual test
python3 ~/openclaw/scripts/pipedream-token-refresh.py
```

## File Locations Reference

| File | Purpose |
|------|---------|
| `~/openclaw/config/pipedream-credentials.json` | OAuth credentials (created by UI) |
| `~/openclaw/config/mcporter.json` | MCP server configs (apps added here) |
| `~/openclaw/scripts/pipedream-token-refresh.py` | Token refresh script |
| `~/openclaw/logs/pipedream-token-refresh.log` | Refresh script logs |
| `~/openclaw/logs/pipedream-cron.log` | Cron job output |

## Success Criteria

Installation is complete when:

- [ ] Token refresh script is in `~/openclaw/scripts/`
- [ ] Cron job is running (check with `crontab -l`)
- [ ] User has configured credentials in UI
- [ ] At least one app is connected and testable
- [ ] `mcporter call` works for connected app

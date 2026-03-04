# Integration Guide - Phase 1 Commands

## Overview

This guide explains how to integrate the Phase 1 operational commands into the main openclaw-ops-elvatis plugin.

## New Commands

1. **`/health`** - Quick system health check (gateway, resources, plugins)
2. **`/services`** - Show all OpenClaw profiles and service status
3. **`/logs [service] [lines]`** - View gateway or plugin logs
4. **`/plugins`** - Detailed plugin dashboard with versions and paths

## Integration Steps

### Option 1: Direct Integration into `index.ts`

Copy the command registration code from `extensions/phase1-commands.ts` directly into the main `register()` function in `index.ts`.

**Steps:**
1. Copy the helper functions from `phase1-commands.ts` to the top of `index.ts` (after existing utilities)
2. Copy each `api.registerCommand()` block into the main `register()` function
3. Test each command individually

### Option 2: Modular Integration (Recommended)

Keep commands modular by importing from the extensions file.

**Modify `index.ts`:**

```typescript
// Add at the top
import { registerPhase1Commands } from "./extensions/phase1-commands.js";

// Inside the register() function, after existing commands:
export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as { enabled?: boolean; workspacePath?: string };
  if (cfg.enabled === false) return;

  const workspace = expandHome(cfg.workspacePath ?? "~/.openclaw/workspace");
  const cronDir = path.join(workspace, "cron");
  const cronScripts = path.join(cronDir, "scripts");
  const cronReports = path.join(cronDir, "reports");

  // ... existing commands: /cron, /privacy-scan, /release, etc. ...

  // Register Phase 1 operational commands
  registerPhase1Commands(api, workspace);
}
```

### Option 3: Feature Flag

Add configuration to enable/disable new commands:

**Update `openclaw.plugin.json`:**

```json
{
  "id": "openclaw-ops-elvatis",
  "name": "OpenClaw Ops",
  "version": "0.2.0",
  "description": "Operational commands: dashboards, monitoring, and management.",
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": { "type": "boolean", "default": true },
      "workspacePath": { "type": "string", "default": "~/.openclaw/workspace" },
      "features": {
        "type": "object",
        "properties": {
          "operationalDashboard": { "type": "boolean", "default": true },
          "legacyCommands": { "type": "boolean", "default": true }
        }
      }
    }
  }
}
```

**Conditional registration in `index.ts`:**

```typescript
const features = cfg.features ?? { operationalDashboard: true, legacyCommands: true };

if (features.legacyCommands) {
  // Existing commands: /cron, /privacy-scan, etc.
}

if (features.operationalDashboard) {
  registerPhase1Commands(api, workspace);
}
```

## Testing

### 1. Test Installation

```bash
cd ~/.openclaw/workspace/openclaw-ops-elvatis
openclaw plugins install -l .
openclaw gateway restart
openclaw status
```

### 2. Test Each Command

```bash
# Quick health check
openclaw health

# Service status
openclaw services

# View logs (defaults to gateway, 50 lines)
openclaw logs

# View specific plugin logs
openclaw logs openclaw-ops-elvatis 100

# Plugin dashboard
openclaw plugins
```

### 3. Verify Output

Each command should:
- Return within 2 seconds (except /logs with large files)
- Format output cleanly for WhatsApp/console
- Handle errors gracefully
- Show "N/A" or "(none)" rather than crashing

## Troubleshooting

### Command not found

```bash
# Verify plugin is installed
openclaw plugins list | grep openclaw-ops-elvatis

# Check gateway logs
openclaw logs gateway 100
```

### Empty/Missing data

- **No gateway status**: Gateway may not be running
- **No logs**: Check `~/.openclaw/logs/` directory exists
- **No plugins**: Run `openclaw plugins install` first

### Permission errors

Some system commands may need permissions:
- Linux: `df`, `systemctl` commands
- macOS: similar Unix commands
- Windows: `wmic` commands may need elevation

## Performance Optimization

### Caching

For frequently accessed data, consider caching:

```typescript
const cache = new Map<string, { data: any; expires: number }>();

function getCached<T>(key: string, fetchFn: () => T, ttlMs = 30000): T {
  const now = Date.now();
  const cached = cache.get(key);
  if (cached && cached.expires > now) {
    return cached.data as T;
  }
  const data = fetchFn();
  cache.set(key, { data, expires: now + ttlMs });
  return data;
}

// Usage in command handler
const resources = getCached('system-resources', getSystemResources, 5000);
```

### Async operations

For long-running operations, use async properly:

```typescript
handler: async () => {
  const [status, resources, plugins] = await Promise.all([
    checkGatewayStatusAsync(),
    getSystemResourcesAsync(),
    getPluginListAsync()
  ]);
  // Format and return
}
```

## Next Steps

After integrating Phase 1 commands:

1. **Gather user feedback** - Which commands are most useful?
2. **Monitor performance** - Are any commands too slow?
3. **Plan Phase 2** - Prioritize based on usage patterns
4. **Update documentation** - Add examples to README.md
5. **Consider UI** - Would a dashboard web interface be useful?

## Configuration Example

Full config with all options:

```json
{
  "openclaw-ops-elvatis": {
    "enabled": true,
    "workspacePath": "~/.openclaw/workspace",
    "features": {
      "operationalDashboard": true,
      "legacyCommands": true
    },
    "cache": {
      "enabled": true,
      "ttl": 30000
    },
    "logging": {
      "verbose": false,
      "commandTiming": true
    }
  }
}
```

## Version Migration

When releasing Phase 1:

1. Update version: `0.1.5` → `0.2.0` (minor version bump)
2. Update README with new commands
3. Tag release in Git
4. Test on staging profile first
5. Run smoke tests: `openclaw staging-smoke`
6. Deploy to production


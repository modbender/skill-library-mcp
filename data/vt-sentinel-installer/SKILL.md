---
name: install-vt-sentinel
description: >-
  Install or upgrade VT Sentinel security plugin. Use when the user asks to install,
  set up, enable, update, or upgrade VT Sentinel, VirusTotal scanning, malware protection,
  or file security scanning. Handles fresh installs and upgrades from any previous version.
user-invocable: true
metadata:
  openclaw:
    emoji: "\U0001F6E1\uFE0F"
    requires:
      anyBins:
        - npm
        - pnpm
        - yarn
        - bun
---

# Install / Upgrade VT Sentinel Plugin

## Step 1: Check current state

```
exec { "command": "openclaw plugins list 2>/dev/null | grep vt-sentinel" }
```

Determine the platform:

```
exec { "command": "uname -s 2>/dev/null || echo Windows" }
```

Three possible outcomes:
- **Not installed** → go to Step 2 (fresh install)
- **Installed, older version** → go to Step 3 (upgrade)
- **Installed, already v0.10.0 or newer** → tell the user it's up to date and skip remaining steps

To check the installed version:
```
exec { "command": "node -e \"const p=require(process.env.HOME+'/.openclaw/extensions/openclaw-plugin-vt-sentinel/package.json');console.log(p.version)\" 2>/dev/null || echo unknown" }
```

On Windows use `%USERPROFILE%` instead of `$HOME`.

## Step 2: Fresh install

```
exec { "command": "openclaw plugins install openclaw-plugin-vt-sentinel" }
```

This downloads the npm package, registers the plugin, loads skills and hooks automatically. No manual configuration needed. Go to Step 4.

## Step 3: Upgrade from previous version

The `openclaw plugins install` command does NOT support in-place upgrade — it fails with "plugin already exists". The upgrade process is:

### 3a. Remove old extension directory (preserves all user data)

On Linux/macOS:
```
exec { "command": "rm -rf ~/.openclaw/extensions/openclaw-plugin-vt-sentinel" }
```

On Windows:
```
exec { "command": "rmdir /s /q %USERPROFILE%\\.openclaw\\extensions\\openclaw-plugin-vt-sentinel" }
```

**User data is safe** — these files live outside the plugin directory and are preserved:
- `~/.openclaw/vt-sentinel-state.json` (configuration overrides, onboarding flags)
- `~/.openclaw/vt-sentinel-uploads.log` (audit log)
- `~/.openclaw/vt-sentinel-detections.log` (audit log)
- `~/.openclaw/vtai-agent-credentials.json` (VTAI API credentials)

### 3b. Clean stale install entry (preserves user config)

After removing the extension directory, `openclaw.json` still references the old plugin path in `plugins.installs`, which causes validation errors. Only remove the stale install metadata — user config in `plugins.entries` (apiKey, etc.) is preserved:

On Linux/macOS:
```
exec { "command": "node -e \"const fs=require('fs'),p=process.env.HOME+'/.openclaw/openclaw.json';try{const P=(()=>{try{return require('json5').parse}catch{return JSON.parse}})();const c=P(fs.readFileSync(p,'utf8'));if(c.plugins?.installs)delete c.plugins.installs['openclaw-plugin-vt-sentinel'];fs.writeFileSync(p,JSON.stringify(c,null,2));console.log('Config cleaned')}catch(e){console.log('No config to clean: '+e.message)}\"" }
```

On Windows:
```
exec { "command": "node -e \"const fs=require('fs'),p=process.env.USERPROFILE+'\\\\.openclaw\\\\openclaw.json';try{const P=(()=>{try{return require('json5').parse}catch{return JSON.parse}})();const c=P(fs.readFileSync(p,'utf8'));if(c.plugins?.installs)delete c.plugins.installs['openclaw-plugin-vt-sentinel'];fs.writeFileSync(p,JSON.stringify(c,null,2));console.log('Config cleaned')}catch(e){console.log('No config to clean: '+e.message)}\"" }
```

### 3c. Install new version

```
exec { "command": "openclaw plugins install openclaw-plugin-vt-sentinel" }
```

If this fails on Windows with `spawn EINVAL`, use the manual method:
```
exec { "command": "cd %TEMP% && npm pack openclaw-plugin-vt-sentinel && mkdir %USERPROFILE%\\.openclaw\\extensions\\openclaw-plugin-vt-sentinel && tar xzf openclaw-plugin-vt-sentinel-0.10.0.tgz -C %USERPROFILE%\\.openclaw\\extensions\\openclaw-plugin-vt-sentinel --strip-components=1 && cd %USERPROFILE%\\.openclaw\\extensions\\openclaw-plugin-vt-sentinel && npm install --omit=dev" }
```

## Step 4: Restart the gateway

The plugin won't be active until the gateway restarts. Detect the platform and use the appropriate command:

Linux:
```
exec { "command": "systemctl --user restart openclaw-gateway.service" }
```

macOS:
```
exec { "command": "openclaw gateway restart" }
```

Windows:
```
exec { "command": "openclaw gateway restart" }
```

## Step 5: Verify

After restart, check that the plugin loaded correctly and shows 9 tools:

```
exec { "command": "openclaw plugins list 2>/dev/null | grep vt-sentinel" }
```

## Step 6: Inform the user

Tell the user:

1. VT Sentinel is installed and active (mention if this was an upgrade, and from which version).
2. **No API key needed** — it auto-registers with VirusTotal's AI API (zero-config).
3. Optionally, they can add their own VirusTotal API key for higher rate limits via `openclaw plugins config openclaw-plugin-vt-sentinel apiKey <key>`.

VT Sentinel provides:
- `vt_scan_file` — Full file scan (AV + AI Code Insight)
- `vt_check_hash` — Quick hash lookup
- `vt_upload_consent` — Consent for sensitive file uploads
- `vt_sentinel_status` — View current config, watched dirs, protection status
- `vt_sentinel_configure` — Change settings at runtime (presets, notify level, block mode)
- `vt_sentinel_reset_policy` — Reset to defaults
- `vt_sentinel_help` — Quick-start guide and privacy info
- `vt_sentinel_update` — Check for updates and get upgrade instructions
- `vt_sentinel_re_register` — Re-register agent identity with VTAI
- Automatic scanning of downloaded/created files
- Active blocking of malicious file execution and dangerous command patterns

## Troubleshooting

If `openclaw plugins install` fails:
- Check internet connectivity: `exec { "command": "npm ping" }`
- Try with verbose output: `exec { "command": "openclaw plugins install openclaw-plugin-vt-sentinel --verbose" }`
- On Windows, if `spawn EINVAL` error occurs, use the manual method from Step 3b

## Constraints

- Do NOT modify `openclaw.json` manually — `openclaw plugins install` handles everything
- If the user reports the plugin is blocked, check `plugins.deny` in their `openclaw.json`

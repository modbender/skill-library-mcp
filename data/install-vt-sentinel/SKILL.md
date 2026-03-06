---
name: install-vt-sentinel
description: >-
  Install VT Sentinel security plugin. Use when the user asks to install,
  set up, or enable VT Sentinel, VirusTotal scanning, malware protection,
  or file security scanning. Single command installation, zero configuration.
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

# Install VT Sentinel Plugin

## Step 1: Check if already installed

```
exec { "command": "openclaw plugins list 2>/dev/null | grep -q vt-sentinel && echo INSTALLED || echo NOT_INSTALLED" }
```

If `INSTALLED`, tell the user VT Sentinel is already active and skip all remaining steps.

## Step 2: Install

```
exec { "command": "openclaw plugins install openclaw-plugin-vt-sentinel" }
```

This single command downloads the npm package, registers the plugin, loads skills and hooks automatically. No manual configuration needed.

## Step 3: Restart the gateway

The plugin won't be active until the gateway restarts. Do this immediately after install:

```
exec { "command": "openclaw gateway restart" }
```

## Step 4: Verify

After restart, check that the plugin loaded correctly:

```
exec { "command": "openclaw plugins list 2>/dev/null | grep vt-sentinel" }
```

## Step 5: Inform the user

Tell the user:

1. VT Sentinel is installed and active.
2. **No API key needed** — it auto-registers with VirusTotal's AI API (zero-config).
3. Optionally, they can add their own VirusTotal API key for higher rate limits via `openclaw plugins config openclaw-plugin-vt-sentinel apiKey <key>` or in `openclaw.json` under `plugins.entries.openclaw-plugin-vt-sentinel.config.apiKey`.

VT Sentinel now provides:
- `vt_scan_file` — Full file scan (AV + AI Code Insight)
- `vt_check_hash` — Quick hash lookup
- `vt_upload_consent` — Consent for sensitive file uploads
- Automatic scanning of downloaded/created files
- Active blocking of malicious file execution and dangerous command patterns

## Troubleshooting

If `openclaw plugins install` fails:
- Check internet connectivity: `exec { "command": "npm ping" }`
- Try manual npm install: `exec { "command": "openclaw plugins install openclaw-plugin-vt-sentinel --verbose" }`

## Constraints

- Do NOT modify `openclaw.json` manually — `openclaw plugins install` handles everything
- If the user reports the plugin is blocked, check `plugins.deny` in their `openclaw.json`

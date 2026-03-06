---
name: multilogin
description: Use when you need to manage Multilogin X browser profiles — launch quick disposable profiles, list/start/stop saved profiles, or check launcher status using the xcli CLI tool.
metadata: { "openclaw": { "emoji": "🌐", "requires": { "bins": ["xcli", "mlx-launcher"] } } }
---

# Multilogin X

Manage anti-detect browser profiles via the `xcli` CLI.

## CRITICAL: Launcher must run FIRST

The `mlx-launcher` process MUST be running before ANY `xcli` command (except `login`) will work.
If you skip this, you WILL get "connection refused" or "launcher not active" errors.

---

## Installation

### Version resolution

Both binaries have a `/latest` endpoint that returns the current version string:

```
https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/latest       → e.g. "0.0.72"
https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/latest   → e.g. "1.75.0"
```

Download URLs follow the pattern:

```
https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/{VERSION}/xcli_{PLATFORM}
https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/{VERSION}/launcher-{PLATFORM}
```

**Platform suffixes:**

| Platform | xcli | mlx-launcher |
|----------|------|--------------|
| Linux x64 | `xcli_linux_amd64` | `launcher-linux_amd64.bin` |
| macOS x64 | `xcli_darwin_amd64` | `launcher-darwin_amd64.bin` |
| macOS ARM | `xcli_darwin_arm64` | `launcher-darwin_arm64.bin` |
| Windows | `xcli_windows_amd64.exe` | `launcher-windows_amd64.exe` |

### Install on Linux (VPS / Docker)

```bash
# Resolve latest versions
CLI_VER=$(curl -sL "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/latest")
LAUNCHER_VER=$(curl -sL "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/latest")
echo "Installing xcli $CLI_VER, launcher $LAUNCHER_VER"

# Download binaries
curl -L -o /usr/local/bin/xcli "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/${CLI_VER}/xcli_linux_amd64"
curl -L -o /usr/local/bin/mlx-launcher "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/${LAUNCHER_VER}/launcher-linux_amd64.bin"

# Make executable
chmod +x /usr/local/bin/xcli /usr/local/bin/mlx-launcher

# Verify
xcli --help
mlx-launcher --help
```

### Install on macOS

```bash
# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
  SUFFIX="darwin_arm64"
else
  SUFFIX="darwin_amd64"
fi

# Resolve latest versions
CLI_VER=$(curl -sL "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/latest")
LAUNCHER_VER=$(curl -sL "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/latest")
echo "Installing xcli $CLI_VER, launcher $LAUNCHER_VER"

# Download binaries
curl -L -o /usr/local/bin/xcli "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/${CLI_VER}/xcli_${SUFFIX}"
curl -L -o /usr/local/bin/mlx-launcher "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/${LAUNCHER_VER}/launcher-${SUFFIX}.bin"

# Make executable
chmod +x /usr/local/bin/xcli /usr/local/bin/mlx-launcher

# macOS may quarantine downloaded binaries — remove the flag
xattr -d com.apple.quarantine /usr/local/bin/xcli 2>/dev/null
xattr -d com.apple.quarantine /usr/local/bin/mlx-launcher 2>/dev/null

# Verify
xcli --help
mlx-launcher --help
```

### Install on Windows

```powershell
# Resolve latest versions
$CLI_VER = (Invoke-WebRequest -Uri "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/latest").Content.Trim()
$LAUNCHER_VER = (Invoke-WebRequest -Uri "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/latest").Content.Trim()
Write-Host "Installing xcli $CLI_VER, launcher $LAUNCHER_VER"

# Download binaries
Invoke-WebRequest -Uri "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/cli-mlx/${CLI_VER}/xcli_windows_amd64.exe" -OutFile "$env:USERPROFILE\xcli.exe"
Invoke-WebRequest -Uri "https://ml000x-dev-dists.s3.eu-north-1.amazonaws.com/launcher-mlx/${LAUNCHER_VER}/launcher-windows_amd64.exe" -OutFile "$env:USERPROFILE\mlx-launcher.exe"

# Add to PATH (current session)
$env:PATH += ";$env:USERPROFILE"
```

---

## Environment Detection

Detect your environment before running commands:

```bash
# Am I in Docker?
if [ -f /.dockerenv ]; then
  echo "DOCKER"
else
  echo "BARE METAL"
fi
```

Both environments use the same `xcli` and `mlx-launcher` binaries — they must be in PATH.

---

## Headless (VPS / Docker) — Step by Step

This is the primary mode. No display, no GUI. Profiles run headless.

### Step 1: Start the launcher

```bash
mlx-launcher -port 45000 &
sleep 5
```

Verify:

```bash
xcli launcher-info
```

You MUST see a version number before proceeding. If error — wait and retry.

### Step 2: Login

```bash
xcli login --username 'USER@EMAIL' --password 'PASSWORD'
```

Ask the user for credentials if not provided. Tokens last ~24h, stored in `~/.config/xcli/`.

### Step 3: Launch quick profiles

Quick profiles are disposable — deleted automatically when stopped.

```bash
xcli profile-quick --browser-type mimic --os-type linux --automation puppeteer --headless
```

Launch 2 quick profiles:

```bash
xcli profile-quick --browser-type mimic --os-type linux --automation puppeteer --headless
xcli profile-quick --browser-type mimic --os-type linux --automation puppeteer --headless
```

Each returns a profile ID and a port for Puppeteer/Selenium automation.

### Headless constraints

- **Always** use `--headless` — no display server available.
- **Always** use `--os-type linux` — must match the host OS.
- **Always** use `--browser-type mimic` — `stealthfox` is NOT available on Linux.
- **Do NOT** use `profile-create` for disposable sessions — use `profile-quick`.
- **Do NOT** run `xcli` commands in background with `&` (only `mlx-launcher`).

---

## Desktop (macOS / Windows / Linux with GUI)

When running on a machine with a display (e.g. a Mac node), profiles can open visible browser windows.

### Step 1: Start the launcher

```bash
mlx-launcher -port 45000 &
sleep 5
xcli launcher-info
```

### Step 2: Login

```bash
xcli login --username 'USER@EMAIL' --password 'PASSWORD'
```

### Step 3: Launch profiles (with GUI)

On macOS:

```bash
xcli profile-quick --browser-type mimic --os-type macos --automation puppeteer
xcli profile-quick --browser-type stealthfox --os-type macos --automation puppeteer
```

On Windows:

```bash
xcli profile-quick --browser-type mimic --os-type windows --automation puppeteer
xcli profile-quick --browser-type stealthfox --os-type windows --automation puppeteer
```

Note: No `--headless` flag — browser windows will be visible.

### Desktop constraints

- `--os-type` must match the actual OS (`macos`, `windows`, or `linux`).
- Both `mimic` (Chromium) and `stealthfox` (Firefox) are available on macOS and Windows.
- On Linux with GUI, only `mimic` is available.

---

## GUI via OpenClaw Node (VPS + Mac hybrid)

The most elegant setup: VPS runs 24/7 headless, Mac node handles GUI tasks on demand.

### Architecture

```
VPS (OpenClaw main agent, 24/7, headless)
  ↕ paired via gateway
Mac (OpenClaw Node, paired device)
  → runs Multilogin with visible browser windows
  → VPS delegates GUI tasks here
```

### When to use the Node

Use the VPS for:
- Headless quick profiles (automation, scraping, batch tasks)
- All non-GUI work

Delegate to the Mac node when:
- User wants to SEE the browser (visual inspection, manual interaction)
- A task requires a real display (CAPTCHAs, visual verification)
- `stealthfox` is needed (not available on Linux)
- Debugging a profile visually

### How to delegate to the Node

From the VPS main agent, use `sessions_spawn` to send a task to the Mac node:

```json
{
  "tool": "sessions_spawn",
  "agentId": "node-mac",
  "message": "Start the Multilogin launcher and launch 2 quick profiles with GUI. Use: mlx-launcher -port 45000 & sleep 5 && xcli login --username 'USER' --password 'PASS' && xcli profile-quick --browser-type mimic --os-type macos --automation puppeteer && xcli profile-quick --browser-type stealthfox --os-type macos --automation puppeteer"
}
```

The node will:
1. Start the launcher locally on the Mac
2. Login with the provided credentials
3. Launch profiles with visible browser windows
4. Report back the profile IDs and ports

### Setup requirements for the Node

The Mac node needs:
- `xcli` and `mlx-launcher` binaries for macOS in PATH (see Install on macOS above)
- Network access to Multilogin API (signin.multilogin.com)
- OpenClaw Node running and paired to the VPS gateway

---

## Full CLI Command Reference

### General

| Command | Description |
|---------|-------------|
| `login` | Log in to your account |
| `launcher-info` | Get info about the running launcher (app or agent) |
| `help` | Help for all commands |

### Folders

| Command | Description |
|---------|-------------|
| `create-folder` | Create a folder with a given name |
| `list-folder` | View all available folders |
| `remove-folder` | Remove a folder by ID (or list of IDs) |
| `update-folder` | Update folder details using its ID |

### Workspaces

| Command | Description |
|---------|-------------|
| `list-workspace` | Display available workspaces |
| `switch-workspace` | Switch to a different workspace |

### Proxies

| Command | Description |
|---------|-------------|
| `proxy-countries` | List available countries in proxy service |
| `proxy-regions` | Get regions by country code |
| `proxy-cities` | Get cities by region code |
| `proxy-get` | Get a proxy URL based on parameters |

### Profiles

| Command | Description |
|---------|-------------|
| `profile-quick` | Launch a disposable quick profile (v4 API) |
| `profile-create` | Create a new persistent profile |
| `profile-template` | Create a new template for a browser profile |
| `profile-start` | Start a profile by ID |
| `profile-stop` | Stop a profile by ID |
| `profile-list` | List profiles in a given folder |
| `profile-stat` | Statistics about currently launched profiles |
| `profile-status` | Status of given profile(s) |
| `profile-update` | Update an existing profile |
| `profile-clone` | Duplicate a profile |
| `profile-move` | Move profile to a different folder |
| `profile-remove` | Remove profiles by IDs |
| `profile-restore` | Restore a deleted profile from trash |
| `profile-export` | Export a profile into a file |
| `profile-export-status` | Show profile export status |
| `profile-import` | Import a profile from a file |
| `profile-import-status` | Show profile import status |
| `profile-cookie-import` | Import cookies to a profile |
| `profile-cookie-export` | Export cookies from a profile |

### Scripts

| Command | Description |
|---------|-------------|
| `script-list` | List available scripts in Script Runner folder |
| `script-start` | Run a script in a Multilogin profile |
| `script-stop` | Stop a running script |
| `cookie-robot` | Start Cookie Robot on profile(s) |

### Objects (extensions, files, etc.)

| Command | Description |
|---------|-------------|
| `object-types` | List object types |
| `object-list` | List objects |
| `object-meta` | Fetch object metadata |
| `object-create` | Create an object (requires running agent) |
| `object-download` | Download object to local storage |
| `object-delete` | Delete an object |
| `object-restore` | Restore object from trash |
| `object-stats` | Display object usage statistics |
| `object-convert` | Convert storage type (local ↔ cloud) |
| `enable-object` | Enable object for profiles |
| `disable-object` | Disable object for profiles |
| `object-extension-create` | Create an extension object from a URL |

### Tags

| Command | Description |
|---------|-------------|
| `create-tag` | Create one or more tags |
| `tag-list` | List tags (with optional search filter) |
| `tag-remove` | Remove tags by IDs |
| `tag-assign` | Assign tags to a profile |
| `tag-unassign` | Unassign tags from a profile |

### 2FA

| Command | Description |
|---------|-------------|
| `enable-2fa` | Enable two-factor authentication |
| `view-backup-codes` | View backup codes |
| `disable-2fa-for-user` | Disable 2FA for user |
| `disable-2fa-for-workspace` | Disable 2FA for workspace |
| `enable-2fa-for-workspace` | Enable 2FA for workspace |

### Billing

| Command | Description |
|---------|-------------|
| `referral-code` | Get referral code |
| `multipoints` | Get multipoints balance |

---

## Quick reference flags

| Flag | Values | Notes |
|------|--------|-------|
| `--browser-type` | `mimic`, `stealthfox` | Linux: only `mimic` |
| `--os-type` | `linux`, `macos`, `windows`, `android` | Must match host |
| `--automation` | `puppeteer`, `selenium` | |
| `--headless` | (no value) | Required on headless servers |
| `--proxy-string` | `"host:port:user:pass"` | Optional proxy |
| `--proxy-type` | `http`, `https`, `socks5` | Required if using proxy |
| `--core-version` | e.g. `144.4` | Specific browser version |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `connection refused` / `launcher not active` | Launcher not running | `mlx-launcher -port 45000 &` then `sleep 5` |
| `browser version not found` | Wrong os-type/browser-type combo | Use `--browser-type mimic --os-type linux` on Linux |
| `context deadline exceeded` | Launcher downloading cores (first run) | Wait 30-60s, retry. Cores are cached after first download |
| `token contains invalid segments` | Not logged in | `xcli login` |
| `UNAUTHORIZED_REQUEST` | Token expired (>24h) | `xcli login` again |
| Need GUI but on VPS | No display server | Delegate to Mac node via `sessions_spawn` |
| macOS: "unidentified developer" | Gatekeeper quarantine | Run `xattr -d com.apple.quarantine <binary>` |

---
name: expiring-local-fileshare
description: Lets OpenClaw safely share single files from its local workspace via expiring, tokenized HTTP links (local-network/VPN only). Hours are configurable (default 1h). Optional one-time access. **Token cost:** ~200-500 tokens per use (skill body ~1k tokens, minimal execution overhead).
read_when:
  - User asks for a shareable link to a file
  - User mentions "link", "share file", or wants to access a workspace file from browser
  - User needs to open/view a file (especially images, markdown, PDFs)
metadata:
  openclaw:
    emoji: "📤"
    requires:
      bins: ["node"]
---

# Internal Fileshare

Share single workspace files via expiring HTTP links (tokenized, local-network only).

## Features

- ✅ **Single-file sharing** (no directory browsing)
- ✅ **Time-limited tokens** (default **1h**, configurable; max 24h)
- ✅ **Optional one-time access** (token invalid after first successful download)
- ✅ **Local/VPN-only** (RFC1918 private ranges + localhost)
- ✅ **UTF-8 encoding** (proper display of German umlauts, etc.)
- ✅ **No-cache headers** (always fresh content)
- ✅ **Auto-cleanup** (servers can be killed when done)

## Install / Update (ClawHub)

Install:
```bash
clawhub install expiring-local-fileshare
```

Update:
```bash
clawhub update expiring-local-fileshare
```

---

## Usage

### Share a single file

```bash
{baseDir}/scripts/share.sh /path/to/file.md [port] [hours] [once]
```

**Parameters:**
- `file-path` (required): Absolute path to file
- `port` (optional): Port number (default: auto-assigned 8888+)
- `hours` (optional): Validity in hours (default: **1**, max: 24)
- `once` (optional): Set to `once` or `1` for one-time access

**Output:**
Returns clickable HTTP link with token, valid for specified duration.

### Example

```bash
# Share a markdown file (1h, auto-port)
{baseDir}/scripts/share.sh ~/.openclaw/workspace/projects/my-project/README.md

# Share an image (12h, port 9000)
{baseDir}/scripts/share.sh ~/image.png 9000 12

# Share a file (one-time access, 1h)
{baseDir}/scripts/share.sh ~/secrets.txt 9001 1 once
```

## How It Works

1. Starts a lightweight Node.js HTTP server on specified port
2. Generates random 32-char hex token
3. Returns URL: `http://192.168.0.219:PORT/?token=XXXXX`
4. Validates:
   - Source IP (must be LAN or VPN)
   - Token match
   - Expiry time
5. Serves file with correct MIME type and UTF-8 encoding
6. Logs all access attempts

## Security

- **Workspace-only by default**: refuses to share files outside `~/.openclaw/workspace` (override via `FILESHARE_ALLOW_ANY_PATH=1`, not recommended)
- **Local-only**: Only serves to private IP ranges (RFC1918) + localhost (VPN counts).
- **Token-based**: 128-bit random tokens (computationally infeasible to guess)
- **Time-limited**: Hard expiry after N hours (default 1h, max 24h)
- **Optional one-time**: Token invalid after first successful download
- **No listing**: Only serves the specified file, no directory browsing
- **No caching**: Forces fresh content load

## Supported File Types

Auto-detected MIME types:
- `.png` → `image/png`
- `.jpg`, `.jpeg` → `image/jpeg`
- `.md` → `text/markdown; charset=utf-8`
- `.txt` → `text/plain; charset=utf-8`
- Others → `application/octet-stream`

## Disable / Uninstall

There is no background service by default.

### Stop active shares
```bash
# Kill a specific port
kill $(lsof -t -i:8888)

# Kill all fileshare servers started via this skill
pkill -f "share-file.js"
```

### Uninstall (ClawHub)
If installed into `~/.openclaw/skills`:
```bash
rm -rf ~/.openclaw/skills/expiring-local-fileshare
```

---

## Stopping Shares

```bash
# Kill a specific port
kill $(lsof -t -i:8888)

# Kill all fileshare servers started via this skill
pkill -f "share-file.js"
```

## Policy / Defaults

- **Single files only** (no folder shares)
- **Default validity: 1h**
- **Max validity: 24h**
- **Local/VPN only** (RFC1918 + localhost)
- **No public "anyone with link"**

## Troubleshooting

**Wrong encoding (umlauts broken)?**
→ Fixed in latest version (UTF-8 charset in headers)

**Old version served?**
→ Kill old server + restart (no-cache headers prevent browser caching)

**Can't access from outside?**
→ VPN required (home network topology uses NAT/masquerade, see `docs/internal-fileshare.md`)

**Port already in use?**
→ Use different port or kill existing server

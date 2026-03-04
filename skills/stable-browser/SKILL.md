---
name: stable-browser
description: Set up reliable browser automation using Chrome DevTools Protocol (CDP) instead of the flaky browser extension relay. Use when browser relay keeps disconnecting, throwing WebSocket 403 errors, or when you need stable headless/headed browser control for web scraping, form filling, social media posting, or any browser automation task. Replaces profile="chrome" with a rock-solid CDP connection.
---

# Stable Browser

Replace the unreliable browser extension relay with a direct Chrome DevTools Protocol connection.

## The Problem

The OpenClaw browser extension relay (`profile="chrome"`) frequently breaks:
- WebSocket 403 errors
- Port confusion (gateway port vs relay port)
- Dropped connections mid-automation
- "Can't reach browser control service" errors
- Badge/tab attachment confusion

## The Fix: Chrome CDP

Launch Chrome with a debug port and connect directly. No extension needed.

### Quick Setup

Run the setup script to configure everything:

```bash
bash scripts/setup-cdp.sh
```

This will:
1. Create a dedicated Chrome profile at `~/.chrome-debug-profile`
2. Add `browser.cdpUrl` to your OpenClaw config
3. Create a LaunchAgent (macOS) so Chrome starts on login
4. Verify the connection works

### Manual Setup

If you prefer to set things up manually, see [references/manual-setup.md](references/manual-setup.md).

### Usage

After setup, always use `profile="openclaw"` (not `profile="chrome"`):

```
browser(action="snapshot", profile="openclaw")
browser(action="navigate", profile="openclaw", targetUrl="https://example.com")
browser(action="screenshot", profile="openclaw")
```

### Key Differences from Extension Relay

| Feature | Extension Relay | CDP Direct |
|---------|----------------|------------|
| Stability | Frequent disconnects | Rock solid |
| Setup | Install extension + attach tab | One-time script |
| Auth/Cookies | Shares your main Chrome | Dedicated profile |
| Speed | Extra hop through extension | Direct protocol |
| Headless | No | Optional (`--headless=new`) |

### Dedicated Profile

The CDP browser uses `~/.chrome-debug-profile` — a separate Chrome profile. This means:
- Log into sites once, stays logged in
- Your main Chrome is untouched
- No extension conflicts
- Survives Chrome updates

### Tips

- **First run**: Log into any sites you need (Google, GitHub, X, LinkedIn, etc.)
- **Multiple tabs**: CDP manages all tabs — use `targetId` to pin a specific tab
- **Headless mode**: Add `--headless=new` to the launch command for invisible operation
- **Port conflict**: If port 9222 is taken, change it in both the launch command and config
- **Restart Chrome**: `pkill -f 'remote-debugging-port=9222' && sleep 1 && bash scripts/setup-cdp.sh`

### Troubleshooting

- **"Can't reach browser"**: Chrome isn't running with debug port. Run `setup-cdp.sh` or launch manually
- **Port 9222 in use**: Another Chrome or process grabbed it. Kill it: `lsof -i :9222`
- **Stale session**: Chrome crashed. Kill and restart: `pkill -f chrome-debug-profile`
- **Profile corruption**: Delete `~/.chrome-debug-profile` and re-run setup

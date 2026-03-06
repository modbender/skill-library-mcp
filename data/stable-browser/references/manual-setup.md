# Manual Setup

## 1. Launch Chrome with CDP

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --remote-debugging-port=9222 \
    --user-data-dir=$HOME/.chrome-debug-profile \
    --no-first-run \
    --no-default-browser-check &
```

**Linux:**
```bash
google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=$HOME/.chrome-debug-profile \
    --no-first-run &
```

**Windows (PowerShell):**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
    --remote-debugging-port=9222 `
    --user-data-dir="$env:USERPROFILE\.chrome-debug-profile" `
    --no-first-run
```

## 2. Verify

```bash
curl http://127.0.0.1:9222/json/version
```

Should return JSON with Chrome version info.

## 3. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json
{
  "browser": {
    "cdpUrl": "http://127.0.0.1:9222"
  }
}
```

Or via CLI:
```bash
openclaw config set browser.cdpUrl http://127.0.0.1:9222
```

## 4. Test

In your OpenClaw session:
```
browser(action="snapshot", profile="openclaw")
```

## Headless Mode

For server/CI environments, add `--headless=new`:

```bash
google-chrome \
    --headless=new \
    --remote-debugging-port=9222 \
    --user-data-dir=$HOME/.chrome-debug-profile \
    --no-sandbox \
    --disable-gpu &
```

## Custom Port

If 9222 is taken, use any free port:

```bash
# Launch on 9333
google-chrome --remote-debugging-port=9333 --user-data-dir=$HOME/.chrome-debug-profile &

# Update config
# browser.cdpUrl: http://127.0.0.1:9333
```

## Auto-Start (Linux systemd)

```ini
# ~/.config/systemd/user/chrome-cdp.service
[Unit]
Description=Chrome CDP for OpenClaw

[Service]
ExecStart=/usr/bin/google-chrome --headless=new --remote-debugging-port=9222 --user-data-dir=%h/.chrome-debug-profile --no-sandbox --disable-gpu
Restart=on-failure

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable chrome-cdp
systemctl --user start chrome-cdp
```

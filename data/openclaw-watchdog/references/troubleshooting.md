# Watch Dog Troubleshooting

## Common Issues

### Watch Dog won't start
```bash
# Check logs
tail -50 ~/.openclaw/watchdog/watchdog-error.log

# Verify Python venv
~/.openclaw/watchdog/venv/bin/python3 -c "import aiohttp; print('OK')"

# Re-run setup
~/.openclaw/workspace/openclaw-watchdog/scripts/setup.sh --telegram-token "..." --telegram-chat-id "..." --openai-key "..."
```

### Decryption fails
The config is encrypted with a machine-specific key derived from hardware UUID + hostname. If you changed hostname or migrated machines, re-run setup.

### No Telegram alerts
1. Verify bot token: `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Verify chat ID: `curl https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Make sure you sent `/start` to the bot first

### Gateway keeps dying
Check gateway logs:
```bash
tail -200 ~/.openclaw/gateway.log
openclaw gateway status
```

Watch Dog attempts fixes in this order:
1. `openclaw gateway restart` (attempts 1-2)
2. Sends Telegram alert asking for reinstall permission (attempt 3)
3. If user approves (`touch ~/.openclaw/watchdog/approve-reinstall`): runs `npm install -g openclaw` + start (attempts 4-5)
4. After 5 failed attempts → stops and alerts for manual intervention
5. Without user approval, no reinstall happens — only notifications

### Service management

**macOS:**
```bash
launchctl list | grep watchdog          # Status
launchctl unload ~/Library/LaunchAgents/com.openclaw.watchdog.plist  # Stop
launchctl load ~/Library/LaunchAgents/com.openclaw.watchdog.plist    # Start
```

**Linux:**
```bash
systemctl --user status openclaw-watchdog
systemctl --user stop openclaw-watchdog
systemctl --user start openclaw-watchdog
journalctl --user -u openclaw-watchdog -f   # Live logs
```

### Update credentials
Re-run the setup script with new tokens. It will re-encrypt and restart the service.

### Uninstall completely
```bash
# macOS
launchctl unload ~/Library/LaunchAgents/com.openclaw.watchdog.plist
rm ~/Library/LaunchAgents/com.openclaw.watchdog.plist

# Linux
systemctl --user stop openclaw-watchdog
systemctl --user disable openclaw-watchdog
rm ~/.config/systemd/user/openclaw-watchdog.service

# Both
rm -rf ~/.openclaw/watchdog
```

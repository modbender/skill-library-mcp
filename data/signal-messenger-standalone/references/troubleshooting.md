# Troubleshooting

## Common Issues

### "Config file is in use by another instance"
signal-cli uses file locking. If cron polling and manual sends overlap:
- The second instance waits briefly then proceeds
- This is normal and self-resolving
- If stuck: `rm ~/.local/share/signal-cli/data/*.lock`

### Messages from new contacts not appearing
New contacts without phone numbers show as UUIDs. The poll script handles both formats. If messages still don't appear:
1. Check `debug-parse.log` for parsing issues
2. Accept the message request: `signal-cli -a +YOUR_NUMBER sendMessageRequestResponse --type accept <UUID>`
3. Verify the UUID appears in `listIdentities`

### Voice messages not transcribing
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check the attachment path exists (Signal stores in `~/.local/share/signal-cli/attachments/`)
- Whisper needs 16kHz mono WAV: `ffmpeg -i input.m4a -ar 16000 -ac 1 -c:a pcm_s16le output.wav`

### Registration fails
- VoIP numbers may not receive SMS — try voice verification: `signal-cli -a +NUMBER register --voice`
- Some numbers are flagged by Signal — try a different number
- Captcha may be required: follow signal-cli docs for captcha flow

### Wake API not triggering
- Verify OpenClaw hooks config: check `openclaw.json` has `hooks.wake.enabled: true`
- Test manually: `curl -X POST http://127.0.0.1:18789/hooks/wake -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{"text":"test"}'`
- Check `monitor.log` for wake trigger entries

### Typing indicators not showing
- `sendTyping` requires an active Signal session with the recipient
- The recipient must have message requests accepted
- Some Signal clients don't display bot typing indicators

## File Locations

| File | Purpose |
|------|---------|
| `~/.signal-state/pending_wakes` | Unprocessed incoming messages |
| `~/.signal-state/conversations/*.log` | Per-contact message history |
| `~/.signal-state/monitor.log` | Activity log |
| `~/.signal-state/debug-parse.log` | Raw parsing debug output |
| `~/.signal-state/triage.log` | Unknown sender alerts |
| `~/.local/share/signal-cli/` | signal-cli data directory |

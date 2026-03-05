# ClawTime Troubleshooting

## Gateway Errors

### "origin not allowed"
ClawTime's origin isn't whitelisted in the gateway.
```bash
openclaw config patch '{"gateway":{"controlUi":{"allowedOrigins":["http://localhost:3000"]}}}'
openclaw gateway restart
```

### "device signature invalid"
Signature payload format mismatch. Delete the keypair and restart (new one auto-generates):
```bash
rm ~/.clawtime/device-key.json
pkill -f "node server.js"; sleep 2
# Restart with start command
```

### "device identity mismatch"
Device ID must be SHA-256 of the raw 32-byte Ed25519 public key (not SPKI DER).
Same fix: delete `~/.clawtime/device-key.json` and restart.

### "missing scope: operator.write"
Device auth isn't working. Verify `device-key.json` exists and has correct permissions:
```bash
ls -la ~/.clawtime/device-key.json   # should be -rw-------
chmod 600 ~/.clawtime/device-key.json
```
Do NOT use `allowInsecureAuth` as a workaround.

### WebSocket connect loop / never connects
- Confirm OpenClaw gateway is running: `openclaw gateway status`
- Confirm `GATEWAY_TOKEN` is correct
- Confirm `PUBLIC_URL` matches the origin you're accessing from

---

## Passkey / Auth Errors

### "Passkey access denied" on iOS
- Not in private/incognito mode? → Switch to regular Safari
- Using Chrome? → Switch to Safari (Chrome doesn't support local passkeys the same way)
- Already registered on a different domain? → Old passkeys won't work if PUBLIC_URL changed

### Registration URL not working
- Use `http://localhost:3000/?setup=<SETUP_TOKEN>` exactly
- Confirm SETUP_TOKEN matches what was set in the server start command

### Reset all passkeys (start fresh)
```bash
echo '[]' > ~/.clawtime/credentials.json
pkill -f "node server.js"; sleep 2
# Restart, then re-register
```

---

## Server Errors

### Port 3000 already in use
```bash
lsof -i :3000        # find what's using it
pkill -9 -f "node server.js"
sleep 2
# Restart
```

### Server starts but browser shows blank / error
- Hard-refresh: Cmd+Shift+R in browser
- Check logs: `tail -50 /tmp/clawtime.log`
- Try: `pkill -f "node server.js"` → wait 2s → restart

### npm install fails
```bash
cd ~/Projects/clawtime
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

---

## TTS Errors

### No voice / TTS silent
- Confirm `TTS_COMMAND` env var is set when starting server
- Test Piper manually: `python3 -m piper --help`
- Test ffmpeg: `ffmpeg -version`
- Check voice model exists: `ls ~/Documents/resources/piper-voices/`

### TTS command fails
- The `{{TEXT}}` placeholder must be in the command
- The `{{OUTPUT}}` placeholder must be in the command
- Ensure piper voices directory path is correct
- Try the TTS command manually replacing placeholders with test values

---

## Device Key Technical Details

ClawTime authenticates with the gateway using Ed25519:
- Keypair stored: `~/.clawtime/device-key.json` (perms: 0600)
- Device ID = SHA-256 of raw 32-byte pubkey (NOT SPKI DER)
- SPKI prefix `302a300506032b6570032100` must be stripped before hashing
- Signature payload format: `v2|deviceId|clientId|clientMode|role|scopes|signedAtMs|token|nonce`
- Public key + signature both base64url encoded

If a new device key is generated, the device may need approval in the OpenClaw gateway panel.

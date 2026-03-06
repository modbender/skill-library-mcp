# Troubleshooting

## 0) Required dependency: local faster-whisper

This skill depends on a local transcription endpoint:
- `http://127.0.0.1:18790/transcribe`
- usually backed by `openclaw-transcribe.service`

Checks:
```bash
systemctl --user status openclaw-transcribe.service
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18790/transcribe -X POST -H 'Content-Type: application/octet-stream' --data-binary 'x'
```

If this is down/missing, voice input will not produce text.

## 1) disconnected (1006/1000)

Check proxy + transcribe services:
```bash
systemctl --user status openclaw-voice-https.service
systemctl --user status openclaw-transcribe.service
```

## 2) origin not allowed

Ensure config includes your HTTPS host:
```json
"gateway": {
  "controlUi": {
    "allowedOrigins": ["https://<your-host-or-ip>:8443"]
  }
}
```

Prefer re-running deploy with explicit host:
```bash
VOICE_HOST=<your-host-or-ip> VOICE_HTTPS_PORT=8443 bash scripts/deploy.sh
```

Restart gateway after changes.

## 3) token missing

Open once with token query param:
```text
https://<host>:8443/chat?session=main&token=<gateway-token>
```

## 4) pairing required

List + approve pending device:
```bash
openclaw devices list --token <gateway-token>
openclaw devices approve <requestId> --token <gateway-token>
```

## 5) Mic fails after reboot

Use persistent cert paths under workspace (not `/tmp`).
Current expected location:
- `~/.openclaw/workspace/voice-input/certs/voice-cert.pem`
- `~/.openclaw/workspace/voice-input/certs/voice-key.pem`

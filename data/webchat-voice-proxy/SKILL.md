---
name: webchat-voice-proxy
description: >
  Voice input and microphone button for OpenClaw WebChat Control UI. Adds a mic
  button to chat, records audio via browser MediaRecorder, transcribes locally
  via faster-whisper, and injects text into the conversation. Includes HTTPS/WSS
  reverse proxy, TLS cert management, and gateway hook for update safety. Fully
  local speech-to-text, no API costs. Real-time VU meter shows voice activity.
  Push-to-Talk (hold to speak) and Toggle mode (click start/stop), switchable
  via double-click. Keyboard shortcuts: Ctrl+Space PTT, Ctrl+Shift+M continuous
  recording. Localized UI (English, German, Chinese built-in, extensible).
  Keywords: voice input, microphone, WebChat, Control UI, speech to text, STT,
  local transcription, MediaRecorder, HTTPS proxy, voice button, mic button,
  push-to-talk, PTT, keyboard shortcut, i18n, localization.
requires:
  config_paths:
    - ~/.openclaw/openclaw.json (appends allowedOrigins entry)
  modified_paths:
    - <npm-global>/openclaw/dist/control-ui/index.html (injects script tag)
    - <npm-global>/openclaw/dist/control-ui/assets/voice-input.js (copies asset)
    - ~/.config/systemd/user/openclaw-voice-https.service (creates unit)
    - ~/.openclaw/hooks/voice-input-inject/ (creates startup hook)
    - ~/.openclaw/workspace/voice-input/ (copies runtime files)
    - ~/.openclaw/workspace/voice-input/certs/ (generates self-signed TLS cert)
  env:
    - VOICE_HTTPS_PORT (optional, default: 8443)
    - VOICE_HOST (optional, default: 127.0.0.1 — set to a LAN IP to expose externally)
    - VOICE_ALLOWED_ORIGIN (optional, default: https://<VOICE_HOST>:<VOICE_HTTPS_PORT>)
    - VOICE_LANG (optional, default: auto — prompts interactively if not set)
  persistence:
    - "User systemd service: openclaw-voice-https.service (HTTPS/WSS proxy)"
    - "Gateway startup hook: voice-input-inject (re-injects JS after updates)"
  privileges: user-level only, no root/sudo required
  dependencies:
    - python3 with aiohttp >= 3.9.0 (pip)
    - faster-whisper transcription service on port 18790
    - openssl (for self-signed cert generation)
---

# WebChat Voice Proxy

Set up a reboot-safe voice stack for OpenClaw WebChat (including the current polished mic/stop/hourglass UI states):
- HTTPS Control UI on port 8443
- `/transcribe` proxy to local faster-whisper service
- WebSocket passthrough to gateway (`ws://127.0.0.1:18789`)
- Voice button script injection into Control UI
- Real-time VU meter: button shadow/scale reacts to voice level
- **Push-to-Talk**: hold mic button to record, release to send (default mode)
- **Toggle mode**: click to start, click to stop (switch via double-click on mic button)
- **Keyboard shortcuts**: `Ctrl+Space` Push-to-Talk, `Ctrl+Shift+M` start/stop continuous recording
- **Localized UI**: auto-detects browser language (English, German, Chinese built-in), customizable

## Prerequisites (required)

This skill requires a **local faster-whisper HTTP service**.
Expected default:
- URL: `http://127.0.0.1:18790/transcribe`
- systemd user service: `openclaw-transcribe.service`

Verify before deployment:
```bash
systemctl --user is-active openclaw-transcribe.service
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18790/transcribe -X POST -H 'Content-Type: application/octet-stream' --data-binary 'x'
```

If this dependency is missing, set up faster-whisper first (model load + HTTP endpoint), then run this skill.

Related skills:
- `faster-whisper-local-service` (backend prerequisite)
- `webchat-voice-full-stack` (meta-installer that deploys both backend + proxy)

## Workflow

1. Ensure transcription service exists and is running (`openclaw-transcribe.service`).
2. Deploy `voice-input.js` to Control UI assets and inject script tag into `index.html`.
3. Configure gateway allowed origin for external HTTPS UI.
4. Run HTTPS+WSS proxy as persistent user systemd service (`openclaw-voice-https.service`).
5. Verify pairing/token/origin errors and resolve in order.

## Security Notes

- **Localhost by default**: The HTTPS proxy binds to `127.0.0.1` only. It is **not** reachable from other devices on your network unless you explicitly set `VOICE_HOST` to a LAN IP.
- **LAN exposure**: Setting `VOICE_HOST=<LAN-IP>` exposes the proxy (and by extension the gateway WebSocket and transcription endpoint) to all devices on that network. Only do this on trusted networks.
- **Persistence**: This skill installs a **user systemd service** (`openclaw-voice-https.service`) that starts automatically on boot, and a **gateway hook** that re-injects the UI script after updates. Use `uninstall.sh` to fully revert.
- **Self-signed TLS**: The auto-generated certificate is not trusted by browsers. You will see a certificate warning on first access.

## Deploy

Run (localhost only — default, most secure):
```bash
bash scripts/deploy.sh
```

Or expose on LAN (required to access from other devices):
```bash
VOICE_HOST=10.0.0.42 VOICE_HTTPS_PORT=8443 VOICE_LANG=de bash scripts/deploy.sh
```

When run interactively without `VOICE_LANG`, the script will ask you to choose a UI language (`auto`, `en`, `de`, `zh`). Set `VOICE_LANG=auto` to skip the prompt.

This script is idempotent.

## Quick verify

Run:
```bash
bash scripts/status.sh
```

Expected:
- both services active
- injection present
- `https:200`

## Common fixes

- `404 /chat?...` → SPA fallback missing in HTTPS proxy.
- `origin not allowed` → ensure deploy used correct `VOICE_HOST` and added matching HTTPS origin to `gateway.controlUi.allowedOrigins`.
- `token missing` → open URL with `?token=...` once.
- `pairing required` → approve pending device via `openclaw devices approve <requestId> --token <gateway-token>`.
- Mic breaks after reboot → cert paths must be persistent (not `/tmp`).
- No transcription result → check local faster-whisper endpoint first.

See `references/troubleshooting.md` for exact commands.

## What this skill modifies

Before installing, be aware of all system changes `deploy.sh` makes:

| What | Path | Action |
|---|---|---|
| Control UI HTML | `<npm-global>/openclaw/dist/control-ui/index.html` | Adds `<script>` tag for voice-input.js |
| Control UI asset | `<npm-global>/openclaw/dist/control-ui/assets/voice-input.js` | Copies mic button JS |
| Gateway config | `~/.openclaw/openclaw.json` | Adds HTTPS origin to `gateway.controlUi.allowedOrigins` |
| Systemd service | `~/.config/systemd/user/openclaw-voice-https.service` | Creates + enables persistent HTTPS proxy |
| Gateway hook | `~/.openclaw/hooks/voice-input-inject/` | Installs startup hook that re-injects JS after updates |
| Workspace files | `~/.openclaw/workspace/voice-input/` | Copies voice-input.js, https-server.py |
| TLS certs | `~/.openclaw/workspace/voice-input/certs/` | Auto-generated self-signed cert on first run |

The injected JS (`voice-input.js`) runs inside the Control UI and interacts with the chat input. Review the source before deploying.

## Mic Button Controls

| Action | Effect |
|---|---|
| **Hold** (PTT mode) | Record while held, transcribe on release |
| **Click** (Toggle mode) | Start recording / stop and transcribe |
| **Double-click** | Switch between PTT and Toggle mode |
| **Right-click** | Toggle beep sound on/off |
| **Ctrl+Space** (hold) | Push-to-Talk via keyboard (works even with text field focused) |
| **Ctrl+Shift+M** | Start/stop recording (transcribes on stop) |
| **Ctrl+Shift+B** | Start/stop live transcription [beta] — text appears in real-time, auto-sends after 2s review, stops on 5s silence or "Stop Hugo" keyword |

The current mode and available actions are shown in the button tooltip on hover.

## Language / i18n

The UI automatically detects the browser language and shows tooltips, toasts, and placeholder text in the matching language.

**Built-in languages:** English (`en`), German (`de`), Chinese (`zh`)

### Override language

Set a language override in the browser console:

```js
localStorage.setItem('oc-voice-lang', 'de');  // force German
localStorage.setItem('oc-voice-lang', 'zh');  // force Chinese
localStorage.removeItem('oc-voice-lang');      // back to auto-detect
```

Then reload the page.

### Add a custom language

Edit `voice-input.js` and add a new entry to the `I18N` object. Use `assets/i18n.json` as a template — it contains all translation keys with the built-in translations.

Example for adding French:

```js
const I18N = {
  // ... existing entries ...
  fr: {
    tooltip_ptt: "Maintenir pour parler",
    tooltip_toggle: "Cliquer pour démarrer/arrêter",
    tooltip_next_toggle: "Mode clic",
    tooltip_next_ptt: "Push-to-Talk",
    tooltip_beep_off: "Désactiver le bip",
    tooltip_beep_on: "Activer le bip",
    tooltip_dblclick: "Double-clic",
    tooltip_rightclick: "Clic droit",
    toast_ptt: "Push-to-Talk",
    toast_toggle: "Mode clic",
    toast_beep_on: "Bip activé",
    toast_beep_off: "Bip désactivé",
    placeholder_suffix: " — Voix : (Ctrl+Espace Push-To-Talk, Ctrl+Shift+M enregistrement continu)"
  }
};
```

After editing, redeploy with `bash scripts/deploy.sh` to copy the updated JS to the Control UI.

## CORS Policy

The `/transcribe` proxy endpoint uses a configurable `Access-Control-Allow-Origin` header.
Set `VOICE_ALLOWED_ORIGIN` env var to restrict. Default: `https://<VOICE_HOST>:<VOICE_HTTPS_PORT>`.

## Uninstall

To fully revert all changes:

```bash
bash scripts/uninstall.sh
```

This will:
1. Stop and remove `openclaw-voice-https.service`
2. Remove the gateway startup hook
3. Remove `voice-input.js` from Control UI and undo the index.html injection
4. Remove the HTTPS origin from gateway config
5. Restart the gateway
6. Remove TLS certificates
7. Remove workspace runtime files (`voice-input.js`, `https-server.py`, `i18n.json`)

The faster-whisper backend is **not** touched by uninstall — remove it separately via `faster-whisper-local-service` if needed.

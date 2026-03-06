---
name: Electron
description: Build Electron desktop apps with secure architecture and common pitfall avoidance.
metadata: {"clawdbot":{"emoji":"⚡","requires":{"bins":["npm"]},"os":["linux","darwin","win32"]}}
---

## Security Non-Negotiables
- `nodeIntegration: false` is mandatory — renderer with Node.js access means XSS = full system compromise
- `contextIsolation: true` is mandatory — separates preload context from renderer
- Whitelist IPC channels explicitly — never forward arbitrary channel names from renderer
- Validate all IPC message content — renderer is untrusted, treat like external API input
- Never use `eval()` or `new Function()` in renderer — defeats all security boundaries

## Preload Script Rules
- `contextBridge.exposeInMainWorld()` is the only safe bridge — raw `ipcRenderer` exposure is vulnerable
- Clone data before passing across bridge — prevents prototype pollution attacks
- Minimal API surface — expose specific functions, not generic send/receive

## Architecture Traps
- `webPreferences` locked after window creation — can't enable nodeIntegration later
- Blocking main process freezes ALL windows — async everything, no sync file operations
- Each BrowserWindow is separate renderer process — can't share JS variables directly
- `show: false` then `ready-to-show` — prevents white flash, looks more native

## Native Module Pain
- Pre-built native modules won't work — must rebuild for Electron's specific Node version
- `electron-rebuild` after every Electron upgrade — version mismatch = runtime crash
- N-API modules more stable — survive Electron upgrades better than nan-based

## Packaging Pitfalls
- Dev dependencies included by default — production builds bloat without explicit exclusion
- Code signing required for macOS auto-update — unsigned apps can't use Squirrel
- Windows notifications require `app.setAppUserModelId()` — silent failure without it
- ASAR isn't encryption — source readable with simple tools, don't rely on it for secrets

## Platform-Specific Issues
- CORS blocks `file://` protocol — use custom protocol (`app://`) or local server
- Windows needs NSIS or Squirrel for auto-update — installer format matters
- macOS universal binary needs `--universal` flag — ships both Intel and ARM

## Memory and Performance
- Unclosed windows leak memory — call `win.destroy()` explicitly when done
- Lazy load heavy modules — startup time directly affects perceived quality
- `backgroundThrottling: false` if timers matter when minimized

## Debugging
- Main process: `--inspect` flag, connect via `chrome://inspect`
- Renderer: `webContents.openDevTools()` or keyboard shortcut
- `electron-log` for persistent logs — console.log vanishes on restart

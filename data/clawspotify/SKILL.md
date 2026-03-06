---
name: clawspotify
description: "Control Spotify playback: play, pause, resume, skip, previous, restart, search, queue, set volume, shuffle, repeat, and view now-playing status."
metadata:
  openclaw:
    emoji: "🎵"
    requires:
      bins: ["bash", "python3"]
---

# ClawSpotify 🎵

Control your Spotify playback directly from your OpenClaw agent or terminal. Works with **both Free and Premium** Spotify accounts.

---

## 📦 Installation

### Via ClawHub (recommended)
```bash
clawhub install clawspotify
```

### Manual from GitHub
```bash
# Clone main skill
git clone https://github.com/ejatapibeda/ClawSpotify.git ~/.openclaw/workspace/skills/ClawSpotify

# Create virtual environment
python3 -m venv ~/.venv-clawspotify

# Install SpotAPI (modified version with session support)
git clone https://github.com/ejatapibeda/SpotAPI.git ~/.openclaw/workspace/skills/SpotAPI
~/.venv-clawspotify/bin/pip install -e ~/.openclaw/workspace/skills/SpotAPI

# Create wrapper script
cat > ~/.local/bin/clawspotify << 'EOF'
#!/bin/bash
VENV="/home/$(whoami)/.venv-clawspotify"
SCRIPT_DIR="/home/$(whoami)/.openclaw/workspace/skills/ClawSpotify"
exec "$VENV/bin/python" "$SCRIPT_DIR/scripts/spotify.py" "$@"
EOF
chmod +x ~/.local/bin/clawspotify

# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Dependencies
- Python 3.10+
- SpotAPI (custom version from ejatapibeda/SpotAPI)
- Active Spotify account (Free or Premium)
- Spotify app open on at least one device (PC/phone/web) for playback commands to work

---

## 🔐 First-Time Setup (Authentication)

`clawspotify` authenticates using two session cookies from your browser (`sp_dc` and `sp_key`). You only need to do this **once per account**.

### Step-by-step

1. Open **[https://open.spotify.com](https://open.spotify.com)** in your browser and **log in**
2. Press **F12** to open DevTools
3. Go to **Application** tab → **Cookies** → `https://open.spotify.com`
4. Find and copy the value of **`sp_dc`**
5. Find and copy the value of **`sp_key`**
6. Run:
```bash
clawspotify setup --sp-dc "AQC..." --sp-key "07c9..."
```

Session is saved to `~/.config/spotapi/session.json` and reused automatically.

#### Multi-account support
```bash
clawspotify setup --sp-dc "..." --sp-key "..." --id "work"
clawspotify status --id "work"
```

> **Note:** Cookies expire periodically. If commands fail with a 401 error, re-run setup with fresh cookies.

---

## 🎮 Commands

### Now playing status
```bash
clawspotify status            # default account
clawspotify status --id work  # specific account
```

### Search music (without playing)
```bash
clawspotify search "Bohemian Rhapsody"        # search tracks, show top 5
clawspotify search-playlist "Workout"         # search playlists, show top 5
```

### Search and play
```bash
clawspotify play "Bohemian Rhapsody"          # play first result
clawspotify play "Bohemian Rhapsody" --index 2  # pick result #2 (0-indexed)
clawspotify play-playlist "Lofi Girl"         # play first playlist result
```

### Playback controls
```bash
clawspotify pause
clawspotify resume
clawspotify skip                     # next track
clawspotify prev                     # previous track
clawspotify restart                  # restart from beginning
```

### Queue
```bash
clawspotify queue "Stairway to Heaven"
clawspotify queue "spotify:track:3z8h0TU..."  # add by URI
```

### Volume
```bash
clawspotify volume 50     # set to 50%
clawspotify volume 0      # mute
clawspotify volume 100    # max
```

### Shuffle / Repeat
```bash
clawspotify shuffle on
clawspotify shuffle off
clawspotify repeat on
clawspotify repeat off
```

---

## 💡 Usage Tips

- **Spotify must be open** on at least one device for playback commands to work. The skill transfers playback to a phantom device but needs an active session.
- **First run may be slow** (10-30 seconds) due to WebSocket handshake and device registration. Subsequent commands are faster.
- **Session identifier:** Default is `"default"`. Use `--id` flag to manage multiple Spotify accounts.
- **Search is fuzzy:** Use artist name + title for best results.
- **Output:** Commands print status messages (e.g., `Searching for "...", Playing: URI`).

---

## ⚠️ Troubleshooting

### "No active Spotify device found"
- Open Spotify on any device (PC, phone, or web) and start playing something first.
- Ensure you're logged in with the same account as the cookies.

### "spotapi is not installed" or import errors
- Verify virtual environment: `ls ~/.venv-clawspotify/bin/python`
- Reinstall SpotAPI: `~/.venv-clawspotify/bin/pip install -e ~/.openclaw/workspace/skills/SpotAPI`

### 401 Unauthorized / Session expired
- Cookies (`sp_dc`, `sp_key`) expire. Re-run `clawspotify setup` with fresh cookies from browser.

### Commands time out or hang
- The skill uses WebSockets for real-time state. If Spotify's API is slow, commands may take longer. Use longer timeout or background execution.
- Restart OpenClaw gateway to reload skill if it becomes unresponsive.

### Wrapper not found (`command not found: clawspotify`)
- Ensure `~/.local/bin` is in your `PATH`: `echo $PATH`
- Or run directly: `~/.venv-clawspotify/bin/python ~/.openclaw/workspace/skills/ClawSpotify/scripts/spotify.py <command>`

---

## 📂 File Locations

| Component | Path |
|-----------|------|
| Skill folder | `~/.openclaw/workspace/skills/ClawSpotify` |
| Wrapper script | `~/.local/bin/clawspotify` |
| Virtualenv | `~/.venv-clawspotify` |
| SpotAPI (editable) | `~/.openclaw/workspace/skills/SpotAPI` |
| Session credentials | `~/.config/spotapi/session.json` |
| Main script | `~/skills/ClawSpotify/scripts/spotify.py` |

---

## 🔧 Agent Implementation Notes

When using this skill via OpenClaw agent:

1. **Playback commands** (`play`, `pause`, `skip`, etc.) are asynchronous. The command returns once Spotify accepts the request. Actual playback may take a few seconds to start.
2. **Long-running operations:** Use background execution or extended timeout (15-30 seconds) for `play`, `search`, and `status` to avoid premature termination.
3. **Status query** may occasionally timeout due to WebSocket latency. Play commands are more reliable.
4. **Always check** Spotify app/device for actual playback state. The CLI reports what Spotify acknowledges.
5. If the skill becomes unresponsive, restart the OpenClaw gateway to clear WebSocket connections.

---

## 🌐 Platform Note

- **Linux/macOS:** Works natively with bash.
- **Windows:** Requires WSL, Git Bash, or Cygwin to run the `clawspotify` bash script. Alternatively, run Python directly:
  ```bash
  python ~/.openclaw/workspace/skills/ClawSpotify/scripts/spotify.py play "song name"
  ```

---

**Version:** 1.0.1 (skill) | SpotAPI: 1.2.7 (custom)
**Homepage:** https://github.com/ejatapibeda/ClawSpotify
**Author:** Deli (OpenClaw agent) + ejatapibeda (original author)

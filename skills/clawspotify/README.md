# ClawSpotify 🎵

> An [OpenClaw](https://github.com/ejatapibeda) skill — control Spotify playback from your AI agent or terminal.

Control Spotify entirely from the command line (or via your OpenClaw agent): play songs by name, skip tracks, manage volume, shuffle, repeat, search playlists, and check what's playing — all without touching the Spotify app.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| Python 3.10+ | `python3 --version` |
| [SpotAPI](https://github.com/ejatapibeda/SpotAPI) | `pip install -e ./SpotAPI` or `pip install git+https://github.com/ejatapibeda/SpotAPI.git`|
| Active Spotify account | Free or Premium |
| Spotify open on any device | Desktop, mobile, or web player |

> **Windows users:** Running the `clawspotify` bash script natively on Windows requires WSL, Git Bash, or Cygwin. Alternatively, you can run `python scripts/spotify.py` directly.

---

## Installation

### Via ClawHub
```bash
clawhub install clawspotify
```

### Manual
```bash
git clone https://github.com/ejatapibeda/ClawSpotify.git
cd ClawSpotify

# Install SpotAPI dependency
git clone https://github.com/ejatapibeda/SpotAPI.git
pip install -e ./SpotAPI
# alternative
pip install git+https://github.com/ejatapibeda/SpotAPI.git

# Make wrapper executable and add to PATH
chmod +x clawspotify.sh
ln -s $(pwd)/clawspotify.sh ~/.local/bin/clawspotify
```

---

## First-time Setup — Getting `sp_dc` and `sp_key`

`clawspotify` authenticates using two session cookies from your browser. You only need to do this **once per account**.

### Step-by-step

1. Open **[https://open.spotify.com](https://open.spotify.com)** in your browser and **log in**
2. Press **F12** to open DevTools
3. Go to **Application** tab → **Cookies** → `https://open.spotify.com`
4. Find and copy the value of **`sp_dc`**
5. Find and copy the value of **`sp_key`**

### Save your session

```bash
clawspotify setup --sp-dc "AQCqbfRJ..." --sp-key "07c956c0..."
```

This saves credentials to `~/.config/spotapi/session.json`. The session is reused automatically — no login needed on subsequent runs.

#### Multi-account support

```bash
# Save a second account with a custom identifier
clawspotify setup --sp-dc "..." --sp-key "..." --id "work"

# Use it with any command via --id
clawspotify status --id "work"
clawspotify play "Lo-fi beats" --id "work"
```

---

## Commands

All commands accept an optional `--id <identifier>` flag (default: `"default"`).

### `status` — Now Playing

```bash
clawspotify status
```

**Example output:**
```
=== NOW PLAYING ===
Title  : Bohemian Rhapsody
Album  : A Night at the Opera

=== PLAYER STATE ===
Is Playing : True
Is Paused  : False
Position   : 134313 ms / 354947 ms

=== ACTIVE DEVICE ===
Active Device ID: c380db0a...
Device Name : EJA
Device Type : COMPUTER
Volume      : 72%
```

---

### `search` — Search Tracks

```bash
clawspotify search "<query>"
```

Shows top 5 results without playing anything.

---

### `play` — Search and Play Tracks

```bash
clawspotify play "<query>"
clawspotify play "<query>" --index <N>   # pick the Nth result (0-indexed)
```

```bash
clawspotify play "Bohemian Rhapsody"
clawspotify play "Taylor Swift Anti-Hero" --index 0
clawspotify play "Bach cello suite" --index 2
```

---

### `search-playlist` / `play-playlist` — Playlist Support

```bash
clawspotify search-playlist "Lofi beats"       # search playlists, show top 5
clawspotify play-playlist "Lofi beats"         # search and play first result
clawspotify play-playlist "Workout" --index 1  # play the 2nd playlist result
```

**Example search-playlist output:**
```
=== PLAYLIST SEARCH: Lofi beats ===
1. Lofi Girl - beats to relax/study to — by Lofi Girl
   URI: spotify:playlist:0vvXsWCC9xrXsKd4FyS8kM
2. Lofi Study 2026 — by Lofi Girl
   URI: spotify:playlist:6zCID88oNjNv9zx6puDHKj
...
```

---

### `pause` / `resume` — Playback Control

```bash
clawspotify pause
clawspotify resume
```

---

### `skip` / `prev` — Track Navigation

```bash
clawspotify skip      # next track
clawspotify prev      # previous track
```

---

### `restart` — Restart Current Track

```bash
clawspotify restart   # seek to 0:00
```

---

### `queue` — Add to Queue

```bash
# Search and add first result
clawspotify queue "Stairway to Heaven"

# Add directly by Spotify URI
clawspotify queue "spotify:track:5CQ30WqJwcep0pYcV4AMNc"
```

---

### `volume` — Set Volume

```bash
clawspotify volume 50    # 50%
clawspotify volume 0     # mute
clawspotify volume 100   # max
```

---

### `shuffle` / `repeat` — Toggle Modes

```bash
clawspotify shuffle on
clawspotify shuffle off
clawspotify repeat on
clawspotify repeat off
```

---

### `setup` — Save Session

```bash
clawspotify setup --sp-dc "<value>" --sp-key "<value>"
clawspotify setup --sp-dc "<value>" --sp-key "<value>" --id "my_account"
```

---

## Using as an OpenClaw Skill

After manual install or cloning into `~/.openclaw/workspace/skills/clawspotify`, the skill is ready to use.

OpenClaw reads [`SKILL.md`](./SKILL.md) to understand when and how to invoke `clawspotify`. The agent will automatically call the right command based on user intent.

**Example agent interactions:**

> "Play something by Radiohead"
> → `clawspotify play "Radiohead"`

> "Search for lofi playlists"
> → `clawspotify search-playlist "lofi"`

> "Play the lofi girl playlist"
> → `clawspotify play-playlist "Lofi Girl"`

> "Turn the volume down to 30"
> → `clawspotify volume 30`

> "What's playing right now?"
> → `clawspotify status`

---

## Troubleshooting

### `✗ Error: No session file found`

Run setup first:
```bash
clawspotify setup --sp-dc "..." --sp-key "..."
```

### `✗ Error: No active Spotify device found`

Spotify must be open and active on at least one device (desktop app, mobile app, or web player at [open.spotify.com](https://open.spotify.com)). Start playing something manually once, then retry.

### `✗ Error: spotapi is not installed`

```bash
# From source (recommended):
git clone https://github.com/ejatapibeda/SpotAPI.git
pip install -e ./SpotAPI
```

### `$'\r': command not found` / CRLF errors

```bash
sed -i 's/\r$//' ClawSpotify/clawspotify
```

> To prevent this permanently, the repo includes a [`.gitattributes`](./.gitattributes) file that enforces LF line endings on checkout.

### `clawspotify: command not found`

Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc
source ~/.bashrc
```

### Cookies expired / authentication errors

Spotify session cookies expire periodically. Re-run setup with fresh cookies:
```bash
clawspotify setup --sp-dc "new_value" --sp-key "new_value"
```

---

## Project Structure

```
ClawSpotify/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
├── clawspotify           # CLI wrapper script (bash)
└── scripts/
    └── spotify.py        # CLI implementation (Python)
```

---

## Dependencies

- [SpotAPI](https://github.com/ejatapibeda/SpotAPI) — Unofficial Spotify API library (no official API key needed)

---

## License

This skill is part of the AI-Project-EJA workspace. SpotAPI is a separate project — see [SpotAPI/LICENSE](https://github.com/ejatapibeda/SpotAPI) for its terms.

---
name: home-music
description: Control whole-house music scenes combining Spotify playback with Airfoil speaker routing. Quick presets for morning, party, chill modes.
homepage: local
metadata: {"clawdbot":{"emoji":"🏠","os":["darwin"]}}
triggers:
  - music scene
  - morning music
  - party mode
  - chill music
  - house music
  - stop music
---

```
    ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫
    
    🏠  H O M E   M U S I C  🎵
    
    ╔══════════════════════════════════════════╗
    ║   Whole-House Music Scenes               ║
    ║   One command. All speakers. Perfect.    ║
    ╚══════════════════════════════════════════╝
    
    ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫ ♪ ♫
```

> *"Why click 17 times when one command does the job?"* – Owen 🐸

---

## 🎯 What Does This Skill Do?

**Home Music** combines Spotify + Airfoil into magical music scenes. One command – and the right playlist plays on the right speakers at the perfect volume.

**Imagine:**
- You wake up → `home-music morning` → Gentle tunes in the bathroom
- Friends arrive → `home-music party` → All speakers blasting rock
- Time to relax → `home-music chill` → Lounge vibes everywhere
- Done for the day → `home-music off` → Silence. Peace. Serenity.

---

## 📋 Dependencies

| What | Why | Link |
|------|-----|------|
| 🍏 **macOS** | This skill uses AppleScript | — |
| 🟢 **Spotify Desktop App** | The music source! Must be running. | [spotify.com](https://spotify.com) |
| 📡 **Airfoil** | Routes audio to AirPlay speakers | [rogueamoeba.com](https://rogueamoeba.com/airfoil/) |
| 🎵 **spotify-applescript** | Clawdbot skill for Spotify control | `skills/spotify-applescript/` |

> ⚠️ **Important:** Both Spotify and Airfoil must be running before you start any scenes!

---

## 🎬 Scenes

### 🌅 Morning
*A gentle start to your day*

```bash
home-music morning
```
- **Speaker:** Sonos Move
- **Volume:** 40%
- **Playlist:** Morning Playlist
- **Vibe:** ☕ Coffee + good vibes

---

### 🎉 Party
*Time to celebrate!*

```bash
home-music party
```
- **Speaker:** ALL (Computer, MacBook, Sonos Move, Living Room TV)
- **Volume:** 70%
- **Playlist:** Rock Party Mix
- **Vibe:** 🤘 Neighbors hate this one trick

---

### 😌 Chill
*Pure relaxation*

```bash
home-music chill
```
- **Speaker:** Sonos Move
- **Volume:** 30%
- **Playlist:** Chill Lounge
- **Vibe:** 🧘 Om...

---

### 🔇 Off
*Silence*

```bash
home-music off
```
- Pauses Spotify
- Disconnects all speakers
- **Vibe:** 🤫 Finally, peace and quiet

---

### 📊 Status
*What's playing right now?*

```bash
home-music status
```

Shows:
- Current Spotify track
- Connected speakers

---

## 🔧 Installation

```bash
# Make the script executable
chmod +x ~/clawd/skills/home-music/home-music.sh

# Symlink for global access
sudo ln -sf ~/clawd/skills/home-music/home-music.sh /usr/local/bin/home-music
```

Now `home-music` works from anywhere in your terminal! 🎉

---

## 🎨 Custom Playlists & Scenes

### Changing Playlists

Open `home-music.sh` and find the playlist configuration:

```bash
# === PLAYLIST CONFIGURATION ===
PLAYLIST_MORNING="spotify:playlist:19n65kQ5NEKgkvSAla5IF6"
PLAYLIST_PARTY="spotify:playlist:37i9dQZF1DXaXB8fQg7xif"
PLAYLIST_CHILL="spotify:playlist:37i9dQZF1DWTwnEm1IYyoj"
```

**How to find Playlist URIs:**
1. Right-click on a playlist in Spotify
2. "Share" → "Copy Spotify URI"
3. Or copy the URL and extract the `/playlist/` part

### Adding a New Scene

Add a new case in the `main` block:

```bash
# In home-music.sh after the "scene_chill" function:

scene_workout() {
    echo "💪 Starting Workout scene..."
    airfoil_set_source_spotify
    airfoil_connect "Sonos Move"
    sleep 0.5
    airfoil_volume "Sonos Move" 0.8
    "$SPOTIFY_CMD" play "spotify:playlist:YOUR_WORKOUT_PLAYLIST"
    "$SPOTIFY_CMD" volume 100
    echo "✅ Workout: Sonos Move @ 80%, Pump it up!"
}

# And in the case block:
    workout)
        scene_workout
        ;;
```

### Available Speakers

```bash
ALL_SPEAKERS=("Computer" "Andy's M5 Macbook" "Sonos Move" "Living Room TV")
```

You can add any AirPlay speaker – they just need to be visible in Airfoil.

---

## 🐛 Troubleshooting

### ❌ "Speaker won't connect"

**Check 1:** Is Airfoil running?
```bash
pgrep -x Airfoil || echo "Airfoil is not running!"
```

**Check 2:** Is the speaker on the network?
- Open the Airfoil app
- Check if the speaker appears in the list
- Try connecting manually

**Check 3:** Is the name exactly correct?
- Speaker names are case-sensitive!
- Open Airfoil and copy the exact name

---

### ❌ "No sound"

**Check 1:** Is Spotify playing?
```bash
~/clawd/skills/spotify-applescript/spotify.sh status
```

**Check 2:** Is the Airfoil source correct?
- Open Airfoil
- Check if "Spotify" is selected as the audio source
- If not: Click "Source" → Select Spotify

**Check 3:** Speaker volume?
```bash
# Manually check volume
osascript -e 'tell application "Airfoil" to get volume of (first speaker whose name is "Sonos Move")'
```

---

### ❌ "Spotify won't start"

**Is Spotify open?**
```bash
pgrep -x Spotify || open -a Spotify
```

**Is spotify-applescript installed?**
```bash
ls ~/clawd/skills/spotify-applescript/spotify.sh
```

---

### ❌ "Permission denied"

```bash
chmod +x ~/clawd/skills/home-music/home-music.sh
```

---

## 🔊 Direct Airfoil Commands

If you want to control Airfoil manually:

```bash
# Connect a speaker
osascript -e 'tell application "Airfoil" to connect to (first speaker whose name is "Sonos Move")'

# Set speaker volume (0.0 - 1.0)
osascript -e 'tell application "Airfoil" to set (volume of (first speaker whose name is "Sonos Move")) to 0.5'

# Disconnect a speaker
osascript -e 'tell application "Airfoil" to disconnect from (first speaker whose name is "Sonos Move")'

# List connected speakers
osascript -e 'tell application "Airfoil" to get name of every speaker whose connected is true'

# Set audio source
osascript -e 'tell application "Airfoil"
    set theSource to (first application source whose name contains "Spotify")
    set current audio source to theSource
end tell'
```

---

## 📁 Files

```
skills/home-music/
├── SKILL.md        # This documentation
└── home-music.sh   # The main script
```

---

## 💡 Pro Tips

1. **Set aliases** for even faster access:
   ```bash
   alias mm="home-music morning"
   alias mp="home-music party"
   alias mc="home-music chill"
   alias mo="home-music off"
   ```

2. **Use with Clawdbot:**
   > "Hey, start party mode"
   > "Put on some chill music"
   > "Stop the music"

3. **Combine scenes:** Create a `dinner` scene with a jazz playlist at 25% – perfect for guests!

---

## 🐸 Credits

```
╭─────────────────────────────────────────────╮
│                                             │
│   Crafted with 💚 by Owen the Frog 🐸      │
│                                             │
│   "Ribbit. Music makes everything better."  │
│                                             │
╰─────────────────────────────────────────────╯
```

**Author:** Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)  
**Version:** 1.0.0  
**License:** MIT  
**Pond:** The one with the water lilies 🪷

---

*Did this skill improve your life? Owen appreciates flies. 🪰*

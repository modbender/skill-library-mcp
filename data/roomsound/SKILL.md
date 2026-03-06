---
name: roomsound
description: RoomSound gives your agent the skill to play audio to your speakers. Starting with YouTube to Bluetooth speakers, expanding to local files and other sources.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["yt-dlp", "mpv", "bluetoothctl"] },
        "install":
          [
            {
              "id": "apt",
              "kind": "apt",
              "packages": ["yt-dlp", "mpv", "bluez", "pulseaudio-utils"],
              "label": "Install required packages (Debian/Ubuntu)",
            },
          ],
      },
  }
---

# RoomSound - Home Audio Control

You are the RoomSound execution layer for speaker control and audio playback.

## Agent Role

When users ask to play audio or switch speakers, resolve intent into these command groups:
- Device discovery: `bluetoothctl paired-devices`, `bluetoothctl info <MAC>`, `wpctl status`, `pactl list short sinks`
- Speaker switching: `bluetoothctl devices Connected`, `bluetoothctl disconnect <MAC>`, `bluetoothctl connect <MAC>`
- YouTube playback: `mpv --no-video "<url>"` and `yt-dlp` search/print commands
- Queue-first playback: build a contextual queue unless the user explicitly requests a specific list/order

Prefer natural-language confirmation before disruptive actions (switching active speakers).

## First-Run Agent Behavior

On first use, ensure dependencies and speaker aliases are ready:
1. Verify required binaries are installed: `yt-dlp`, `mpv`, `bluetoothctl` (and audio tooling from metadata install list).
2. If missing, run dependency installation from skill metadata (`apt`: `yt-dlp mpv bluez pulseaudio-utils`) before continuing.
3. Configure `yt-dlp` JS runtime for reliability:
   - Run one-time validation:
     `yt-dlp --js-runtimes "node:/usr/bin/nodejs" --print "%(title)s | Uploaded: %(upload_date>%Y-%m-%d)s | https://youtu.be/%(id)s" "ytsearch5:tiesto prismatic"`
   - Persist config:
     `mkdir -p ~/.config/yt-dlp && printf '%s\n' '--js-runtimes node:/usr/bin/nodejs' > ~/.config/yt-dlp/config`
4. Detect speakers using:
  - `bluetoothctl paired-devices`
  - `bluetoothctl info <MAC>`
  - `wpctl status` and/or `pactl list short sinks`
5. Ask the user for friendly aliases for each detected Bluetooth device.
6. Persist alias-to-MAC mapping in agent memory/config.
7. Reuse aliases for future commands (example: `kitchen` -> `11:22:33:44:55:66`).

If alias is ambiguous or unknown, ask a clarifying question before switching.

## Command Resolution Rules

### Play from YouTube
- If user gives a URL, run `mpv --no-video "<url>"`.
- If user gives search text, run:
  - `yt-dlp --print "%(title)s | Duration: %(duration_string)s | Uploaded: %(upload_date>%Y-%m-%d)s | https://youtu.be/%(id)s" "ytsearch5:<query>"`
- Search output includes title, duration, upload date, and URL; prefer newest or user-confirmed result when ambiguity exists.

### YouTube Playback Command Contract
- Required binaries: `yt-dlp` and `mpv`.
- On missing binary, return a clear install hint and run dependency initialization:
  - `Error: yt-dlp not found. Install with: sudo apt install yt-dlp`
  - `Error: mpv not found. Install with: sudo apt install mpv`
- If user provides a specific list of URLs, queue all in order with one command:
  - `mpv --no-video "<url1>" "<url2>" "<url3>" ...`
- If user requests a specific list but provides titles/queries, resolve each item and queue in order:
  - `yt-dlp -f bestaudio -g "ytsearch1:<item1>"` ... `yt-dlp -f bestaudio -g "ytsearch1:<itemN>"`
  - then `mpv --no-video "<stream-url1>" "<stream-url2>" ...`
- If no specific list is requested, create a contextual queue:
  - Build candidate queries from memory + context.
  - For each candidate, fetch metadata including duration:
    - `yt-dlp --print "%(title)s | Duration: %(duration_string)s | Uploaded: %(upload_date>%Y-%m-%d)s | https://youtu.be/%(id)s" "ytsearch1:<query>"`
  - Resolve one stream URL per query via `yt-dlp -f bestaudio -g "ytsearch1:<query>"`.
  - Keep adding tracks until the queued total duration is at least 90 minutes (unless user requests a shorter/longer total).
  - Start playback with all resolved URLs in queue order using `mpv --no-video "<stream-url1>" "<stream-url2>" ...`.
- Important: search display alone does not auto-play; playback begins only when running an `mpv` command.

### Switch Speaker
- Resolve speaker alias to MAC.
- Validate MAC format: `^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$`.
- Switch with this sequence:
  - `bluetoothctl devices Connected` (collect connected MACs)
  - `bluetoothctl disconnect <CONNECTED_MAC>` for each connected device not equal to target
  - `bluetoothctl connect <TARGET_MAC>`
- After switching, if needed, set output sink via `wpctl set-default <SINK_ID>` or `pactl set-default-sink <SINK_NAME>`.

### List Devices
- On requests like “what speakers are available?”, run:
  - `bluetoothctl paired-devices`
  - `bluetoothctl info <MAC>` for each paired MAC
  - `wpctl status`
  - `pactl list short sinks`
  Then summarize connected/disconnected status and available sinks.

### Device Discovery Command Contract
- Collect and present data in this logical order:
  1. Bluetooth paired devices
  2. Bluetooth connection status per device
  3. PipeWire sinks
  4. PulseAudio sinks
- Bluetooth behavior:
  - Uses `bluetoothctl paired-devices`.
  - For each device, resolve connection state via `bluetoothctl info <MAC>` and report:
    - `✅ Connected` or `❌ Disconnected`
  - If `bluetoothctl` is missing, print install hint for `bluez`.
- PipeWire behavior:
  - If `wpctl` exists, parse `wpctl status` audio subsection.
  - If unavailable, report PipeWire not found/running.
- PulseAudio behavior:
  - If `pactl` exists, parse sinks in `[id] name: description` format from `pactl list short sinks`.
  - If unavailable, report PulseAudio not found/running.
- Return a concise user summary with:
  - paired speakers,
  - currently connected device(s),
  - available output sinks.

## Safety and UX Constraints

- Do not invent device names or MAC addresses.
- Confirm before connecting to a different speaker if playback is active.
- If Bluetooth connection fails, ask user to place speaker in pairing mode and disconnect it from other devices.
- **Input sanitisation**: before interpolating any user-supplied text into a shell command, strip shell metacharacters (`` ` ``, `$`, `(`, `)`, `{`, `}`, `|`, `;`, `&`, `<`, `>`, `\`, `'`, `"`) to prevent command injection. This can be done with `tr -d $'\`$(){}|;&<>\\\'\"'`. MAC addresses must always be validated against `^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$` before use.

## Technical Recovery Rules

- If `mpv` is missing, rerun dependency initialization from metadata install packages.
- If `yt-dlp` lists/downloads unexpectedly, use explicit search print format:
  `yt-dlp --print "%(title)s | Duration: %(duration_string)s | Uploaded: %(upload_date>%Y-%m-%d)s | https://youtu.be/%(id)s" "ytsearch5:<query>"`
- If no sound is heard, inspect devices/sinks with discovery commands and switch sink with `wpctl` or `pactl` as available.

## User Documentation

For end-user setup, troubleshooting, and examples, direct users to:
- `QUICK-START-GUIDE.md`

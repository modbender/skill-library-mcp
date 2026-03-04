# Kosmi Room UI Element Map

This reference documents the known UI elements, modal flows, and snapshot patterns for Kosmi rooms. Use this to calibrate `find_ref()` patterns in the automation scripts.

**Important:** Kosmi's UI is dynamic and may change between updates. If automation breaks, run `kosmi-snapshot-debug.sh` and update the patterns below.

## Room States

### 1. Guest Join Prompt

When entering a room as a guest (no account / not logged in), Kosmi shows a nickname prompt.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| textbox | `name`, `nickname`, `display name` | Enter guest display name |
| button | `join`, `enter`, `continue`, `go` | Submit name and join room |

**Flow:**
1. Fill the name textbox with bot name
2. Click join button (or press Enter)
3. Wait 1500ms for room to load

### 2. Login Prompt

If the room requires authentication, Kosmi shows a login form.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| textbox | `email`, `username` | Email/username input |
| textbox | `password` | Password input |
| button | `log in`, `login`, `sign in` | Submit login form |
| link | `sign up`, `create account` | Registration link (ignore) |
| link | `forgot password` | Password reset (ignore) |

**Flow:**
1. Fill email textbox
2. Fill password textbox
3. Click login button (or press Enter)
4. Wait 2000ms for auth + room load

### 3. Connected — Room Idle (No Media Playing)

The main room view with chat and an empty media area.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| textbox | `message`, `chat`, `type a message` | Chat input box |
| button | `send` | Send chat message |
| button | `apps`, `add`, `+`, `media` | Open the apps/media modal |
| link | `app`, `add media` | Alternative apps trigger |
| button | `settings`, `gear` | Room settings |
| button | `members`, `people`, `users` | Member list |

**Key indicator of connection:** Presence of a chat textbox (`message` or `chat` role=textbox).

### 4. Apps / Media Modal

After clicking the Apps/Add button, a modal appears with media source options.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| button | `url`, `link`, `web`, `custom url` | URL input mode (chain-link icon) |
| button | `youtube`, `video` | YouTube search mode |
| button | `screen`, `share`, `screenshare` | Screen share option |
| button | `file`, `upload` | File upload option |
| button | `close`, `x`, `back` | Close modal |

**Flow:**
1. Click the `url`/`link` button to enter URL mode
2. Wait 600ms for the URL input to appear

### 5. URL Input Mode (Inside Modal)

After selecting URL mode, a textbox appears for pasting a video URL.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| textbox | `url`, `link`, `http`, `paste`, `enter url` | URL input field |
| button | `play`, `start`, `submit`, `go`, `open` | Submit/play the URL |
| button | `cancel`, `back`, `close` | Cancel and go back |

**Flow:**
1. Fill the URL textbox with the video URL
2. Click play/submit button (or press Enter)
3. Wait 1500ms for video to load

### 6. Media Playing

While a video is playing in the room.

**Expected elements:**

| Role | Name Pattern(s) | Purpose |
|---|---|---|
| button | `pause`, `stop` | Pause/stop playback |
| button | `play` | Resume (when paused) |
| progressbar | `progress`, `time`, `seek`, `duration` | Video progress bar |
| video | `player`, `media` | The video element itself |
| button | `fullscreen`, `expand` | Fullscreen toggle |
| button | `volume`, `mute`, `sound` | Volume control |
| textbox | `message`, `chat` | Chat still available |

**Key indicator of playback:** Presence of a `pause` button OR a `progressbar` element.

**Key indicator video ended:** Absence of `pause` button AND absence of `progressbar`, OR presence of a `play` button (replay) without a `progressbar`.

## Common Element Matching Patterns

Use these in `find_ref()` and `find_ref_any()` calls:

```bash
# Chat input (verify connection)
find_ref_any "$SNAP" "textbox" "message" "chat" "type a message"

# Apps modal trigger
find_ref_any "$SNAP" "button" "apps" "add" "media" "+"

# URL mode selector
find_ref_any "$SNAP" "button" "url" "link" "web" "custom"

# URL input field
find_ref_any "$SNAP" "textbox" "url" "link" "http" "paste" "enter url"

# Play/submit button
find_ref_any "$SNAP" "button" "play" "start" "submit" "go" "open"

# Playback detection
find_ref_any "$SNAP" "button" "pause"
find_ref_any "$SNAP" "progressbar" "progress" "time" "seek"

# Video ended detection (replay button visible, no progress bar)
find_ref_any "$SNAP" "button" "play" "replay" "watch again"
```

## Calibration Workflow

When the scripts stop working (Kosmi UI update, new modal layout, etc.):

1. Connect manually: `bash kosmi-connect.sh`
2. Dump elements: `bash kosmi-snapshot-debug.sh`
3. Note the actual `role` and `name` values for each UI state
4. Update the patterns in this file AND in the scripts' `find_ref()` / `find_ref_any()` calls
5. Test each script individually before running the loop

## Known Quirks

- **Ref IDs are ephemeral** — They change on every page load and sometimes after DOM updates. Never hardcode ref IDs; always snapshot → find → act.
- **Kosmi uses WebRTC** — The video player may not expose standard `<video>` elements in the accessibility tree. Look for `progressbar` and control buttons instead.
- **Modal animations** — Kosmi uses CSS transitions on modals. Always wait 500-800ms after triggering a modal before taking a snapshot.
- **Iframes** — Some Kosmi media (YouTube embeds) run inside iframes. agent-browser's snapshot may not penetrate iframes by default. If URL mode works but YouTube search mode doesn't, this is likely why.
- **Rate limiting** — Rapid-fire clicks/fills can confuse Kosmi's React state. Add 200-300ms waits between form interactions.

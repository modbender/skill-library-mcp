# playwright-cli Command Reference (Music Playback Subset)

Only commands relevant to browser-based music playback are listed here. All commands below assume a named session; always prepend `-s=music_player`.

## Session Management

```bash
playwright-cli list                          # list all active sessions
playwright-cli -s=music_player open URL --headed              # create session (in-memory profile, lost on close)
playwright-cli -s=music_player open URL --headed --persistent # create session with persistent profile (survives close/reopen)
playwright-cli -s=music_player close         # close the session browser
playwright-cli -s=music_player delete-data   # delete persistent profile data for this session
playwright-cli close-all                     # close all sessions
playwright-cli kill-all                      # force-kill all browser processes
```

## Storage State (Backup / Restore)

```bash
playwright-cli -s=music_player state-save                 # save cookies + localStorage to auto-named JSON
playwright-cli -s=music_player state-save auth.json       # save to specific file
playwright-cli -s=music_player state-load auth.json       # restore cookies + localStorage from file
```

> **Note:** `state-save`/`state-load` only captures cookies and localStorage. For full profile persistence (including IndexedDB, cache, service workers), use `--persistent` on `open`.

## Core Interaction

```bash
playwright-cli -s=music_player snapshot                        # get page accessibility tree with element refs
playwright-cli -s=music_player snapshot --filename=debug.yaml  # save snapshot to file
playwright-cli -s=music_player goto URL                        # navigate to URL
playwright-cli -s=music_player click REF                       # click element (e.g. click e34)
playwright-cli -s=music_player fill REF "text"                 # clear + type into input (e.g. fill e34 "query")
playwright-cli -s=music_player type "text"                     # type text at current focus
playwright-cli -s=music_player eval "document.title"           # execute JS in browser context (page.evaluate)
playwright-cli -s=music_player eval "el => el.textContent" REF # execute JS on a specific element
playwright-cli -s=music_player screenshot                      # take a screenshot (for visual debugging)
playwright-cli -s=music_player screenshot --filename=page.png  # save screenshot to file
```

## Navigation

```bash
playwright-cli -s=music_player go-back
playwright-cli -s=music_player go-forward
playwright-cli -s=music_player reload
```

## Keyboard

```bash
playwright-cli -s=music_player press Enter
playwright-cli -s=music_player press ArrowDown
playwright-cli -s=music_player press ArrowUp
playwright-cli -s=music_player press PageDown
playwright-cli -s=music_player press PageUp
playwright-cli -s=music_player press Escape
playwright-cli -s=music_player press Tab
playwright-cli -s=music_player press Shift+n          # YouTube: next track
playwright-cli -s=music_player press Shift+p          # YouTube: previous track
playwright-cli -s=music_player press k                # YouTube: play/pause
playwright-cli -s=music_player press m                # YouTube: mute toggle
playwright-cli -s=music_player press f                # YouTube: fullscreen toggle
playwright-cli -s=music_player press j                # YouTube: rewind 10s
playwright-cli -s=music_player press l                # YouTube: forward 10s
```

## Tabs

```bash
playwright-cli -s=music_player tab-list
playwright-cli -s=music_player tab-new URL
playwright-cli -s=music_player tab-select INDEX       # 0-based index
playwright-cli -s=music_player tab-close
playwright-cli -s=music_player tab-close INDEX
```

## Dialog Handling

```bash
playwright-cli -s=music_player dialog-accept
playwright-cli -s=music_player dialog-dismiss
```

## Window

```bash
playwright-cli -s=music_player resize 1920 1080
```

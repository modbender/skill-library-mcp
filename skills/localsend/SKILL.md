---
name: localsend
description: Send and receive files to/from nearby devices using the LocalSend protocol. Trigger with /localsend to get an interactive Telegram menu with real inline buttons — device discovery, file sending, text sending, and receiving.
metadata:
  openclaw:
    emoji: "📡"
    trigger: "/localsend"
    requires:
      bins:
        - localsend-cli
        - openssl
    install: |
      cp ./localsend-cli ~/.local/bin/localsend-cli && chmod +x ~/.local/bin/localsend-cli
---

# LocalSend

Interactive file transfer between devices on the local network using **real Telegram inline keyboard buttons**. Works with any device running the LocalSend app (Android, iOS, Windows, macOS, Linux).

## Install

The `localsend-cli` is a zero-dependency Python CLI. Install from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/Chordlini/localsend-cli/master/localsend-cli -o ~/.local/bin/localsend-cli
chmod +x ~/.local/bin/localsend-cli
```

Full docs: https://github.com/Chordlini/localsend-cli

Requires Python 3.8+ and `openssl` (for TLS).

---

## Telegram Button Format

All menus MUST use OpenClaw's inline button format. Send buttons alongside your message using this structure:

```json
buttons: [
  [{ "text": "Label", "callback_data": "ls:action" }],
  [{ "text": "Row 2", "callback_data": "ls:other" }]
]
```

- Outer array = rows of buttons
- Inner array = buttons per row (max 3 per row for readability)
- Prefix all callback_data with `ls:` to namespace this skill
- When user taps a button, you receive: `callback_data: ls:action`

---

## State Awareness (CRITICAL)

This skill uses conversational state. Track where you are in the flow:

| State | Meaning | Next user input should be treated as... |
|-------|---------|----------------------------------------|
| `idle` | No active flow | Normal message — respond normally |
| `awaiting_file` | Asked user to drop/specify a file to send | **The file to send** — do NOT comment on it, describe it, or react to it. Immediately use it as the send payload. |
| `awaiting_text` | Asked user to type text to send | **The text payload** — send it, don't discuss it |
| `awaiting_confirm` | Waiting for send confirmation | Expect `ls:confirm-send` or `ls:menu` |
| `receiving` | Receiver is active | Monitor for incoming files |

**RULES:**
- When in `awaiting_file` state and user sends an image/file/path → treat it as the file to send. Show confirmation buttons immediately.
- When in `awaiting_text` state and user types anything → treat it as the text to send.
- NEVER comment on, describe, or react to a file/image when you're in `awaiting_file` state.
- State resets to `idle` when user taps `ls:menu` or the flow completes.

---

## On Trigger: Main Menu

When the user types `/localsend` or mentions sending/receiving files locally, send this message **with real inline buttons**:

**Message:**
```
📡 LocalSend — File Transfer
```

**Buttons:**
```json
buttons: [
  [
    { "text": "📤 Send", "callback_data": "ls:send" },
    { "text": "📥 Receive", "callback_data": "ls:receive" }
  ],
  [
    { "text": "🔍 Scan Devices", "callback_data": "ls:devices" }
  ]
]
```

Do NOT run any commands yet. Wait for the button tap.

---

## Flow: Scan Devices

**Trigger:** `callback_data: ls:devices` or user says "scan", "discover", "find devices"

1. Run:
   ```bash
   localsend-cli discover --json -t 2
   ```

2. **Devices found** — create one button per device, plus Refresh and Back:

   **Message:**
   ```
   📡 Found 3 devices:
   ```

   **Buttons (one device per row):**
   ```json
   buttons: [
     [{ "text": "📱 Fast Potato — 192.168.0.148", "callback_data": "ls:dev:Fast Potato" }],
     [{ "text": "💻 Rami-Desktop — 192.168.0.100", "callback_data": "ls:dev:Rami-Desktop" }],
     [{ "text": "🖥️ Living Room PC — 192.168.0.105", "callback_data": "ls:dev:Living Room PC" }],
     [
       { "text": "🔄 Refresh", "callback_data": "ls:devices" },
       { "text": "⬅️ Back", "callback_data": "ls:menu" }
     ]
   ]
   ```

3. **No devices found:**

   **Message:**
   ```
   📡 No devices found.
   Make sure LocalSend is open on the other device and both are on the same WiFi.
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "🔄 Try Again", "callback_data": "ls:devices" },
       { "text": "⬅️ Back", "callback_data": "ls:menu" }
     ]
   ]
   ```

4. **User taps a device** (`callback_data: ls:dev:DEVICENAME`) — store it as the selected target. Show action menu:

   **Message:**
   ```
   ✅ Selected: Fast Potato (192.168.0.148)
   What do you want to do?
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "📄 Send File", "callback_data": "ls:sendfile" },
       { "text": "📝 Send Text", "callback_data": "ls:sendtext" }
     ],
     [
       { "text": "📦 Send Multiple", "callback_data": "ls:sendmulti" },
       { "text": "⬅️ Back", "callback_data": "ls:devices" }
     ]
   ]
   ```

---

## Flow: Send

**Trigger:** `callback_data: ls:send`

### Step 1 — Pick target device (if not already selected)

Run discover and show device picker (see Scan Devices flow above).

### Step 2 — Choose what to send

**Message:**
```
Send to Fast Potato:
```

**Buttons:**
```json
buttons: [
  [
    { "text": "📄 Send File", "callback_data": "ls:sendfile" },
    { "text": "📝 Send Text", "callback_data": "ls:sendtext" }
  ],
  [
    { "text": "📦 Send Multiple", "callback_data": "ls:sendmulti" },
    { "text": "⬅️ Back", "callback_data": "ls:menu" }
  ]
]
```

### Send File (`callback_data: ls:sendfile`)

1. Ask: `"Send me the file, drop a path, or tell me which file to send"`
2. User provides file path or sends a file via chat
3. Get file size with `stat` or `ls -lh`
4. Confirm with buttons:

   **Message:**
   ```
   📤 Send to Fast Potato?
   📄 project.zip — 4.2 MB
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "✅ Send", "callback_data": "ls:confirm-send" },
       { "text": "❌ Cancel", "callback_data": "ls:menu" }
     ]
   ]
   ```

5. On confirm, run:
   ```bash
   localsend-cli send --to "Fast Potato" /path/to/project.zip
   ```

6. Report result:

   **Message:**
   ```
   ✅ Sent project.zip (4.2 MB) to Fast Potato
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "📤 Send Another", "callback_data": "ls:send" },
       { "text": "⬅️ Menu", "callback_data": "ls:menu" }
     ]
   ]
   ```

### Send Text (`callback_data: ls:sendtext`)

1. Ask: `"Type the text you want to send:"`
2. User types their message
3. Write text to temp file, send:
   ```bash
   echo "user's text" > /tmp/localsend-text.txt
   localsend-cli send --to "Fast Potato" /tmp/localsend-text.txt
   rm /tmp/localsend-text.txt
   ```
4. Confirm:

   **Message:**
   ```
   ✅ Text sent to Fast Potato
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "📝 Send More Text", "callback_data": "ls:sendtext" },
       { "text": "📤 Send File", "callback_data": "ls:sendfile" }
     ],
     [{ "text": "⬅️ Menu", "callback_data": "ls:menu" }]
   ]
   ```

### Send Multiple (`callback_data: ls:sendmulti`)

1. Ask: `"List the files or give me a glob pattern (e.g. ~/Screenshots/*.png)"`
2. User provides paths or pattern
3. Expand glob, list files with sizes:

   **Message:**
   ```
   📦 Send 5 files to Fast Potato?
   📄 photo1.jpg — 2.1 MB
   📄 photo2.jpg — 1.8 MB
   📄 photo3.jpg — 3.2 MB
   📄 photo4.jpg — 2.5 MB
   📄 photo5.jpg — 1.9 MB
   📊 Total: 11.5 MB
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "✅ Send All", "callback_data": "ls:confirm-send" },
       { "text": "❌ Cancel", "callback_data": "ls:menu" }
     ]
   ]
   ```

4. On confirm, run:
   ```bash
   localsend-cli send --to "Fast Potato" photo1.jpg photo2.jpg photo3.jpg photo4.jpg photo5.jpg
   ```

5. Report:

   **Message:**
   ```
   ✅ Sent 5 files (11.5 MB) to Fast Potato
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "📤 Send More", "callback_data": "ls:send" },
       { "text": "⬅️ Menu", "callback_data": "ls:menu" }
     ]
   ]
   ```

---

## Flow: Receive

**Trigger:** `callback_data: ls:receive` or user says "receive", "start receiving", "listen"

### Step 1 — Snapshot current files

```bash
ls -1 /home/rami/.openclaw/workspace/_incoming/ > /tmp/localsend-before.txt
```

### Step 2 — Start receiver in background

```bash
localsend-cli --alias openclaw-workspace receive --save-dir /home/rami/.openclaw/workspace/_incoming/ -y
```

Run with `run_in_background: true`. Store the task ID.

**CRITICAL:** `--alias` MUST come BEFORE `receive` (global flag).

### Step 3 — Confirm ready with buttons

**Message:**
```
📡 Receiver active — "openclaw-workspace"
📁 Saving to: ~/incoming/
✅ Auto-accept: ON

Send files from your device whenever ready.
```

**Buttons:**
```json
buttons: [
  [
    { "text": "🛑 Stop", "callback_data": "ls:stop" },
    { "text": "🔄 Status", "callback_data": "ls:status" }
  ]
]
```

### Step 4 — Monitor for incoming files

Poll every 3 seconds for new files:
```bash
ls -1 /home/rami/.openclaw/workspace/_incoming/ > /tmp/localsend-after.txt
diff /tmp/localsend-before.txt /tmp/localsend-after.txt
```

### Step 5 — Post-receive confirmation (MANDATORY)

When file(s) arrive, **immediately present in chat with inline buttons**.

**Single file:**

Message:
```
✅ Received from Fast Potato:
📄 portfolio.zip — 240 MB
📁 Saved to: ~/incoming/portfolio.zip
```

Buttons (contextual by file type):
```json
buttons: [
  [
    { "text": "📂 Extract", "callback_data": "ls:extract" },
    { "text": "🚀 Deploy", "callback_data": "ls:deploy" }
  ],
  [
    { "text": "📥 Receive More", "callback_data": "ls:receive" },
    { "text": "🛑 Stop", "callback_data": "ls:stop" }
  ]
]
```

**Image file — show inline preview:**

Message:
```
✅ Received from Fast Potato:
🖼️ screenshot.png — 2.1 MB
```
Include `MEDIA:~/incoming/screenshot.png` for inline preview.

Buttons:
```json
buttons: [
  [
    { "text": "📂 Open Folder", "callback_data": "ls:openfolder" },
    { "text": "📥 Receive More", "callback_data": "ls:receive" }
  ],
  [{ "text": "🛑 Stop", "callback_data": "ls:stop" }]
]
```

**Multiple files:**

Message:
```
✅ Received 3 files from Fast Potato:
📄 app.apk — 45 MB
📄 README.md — 2 KB
🖼️ icon.png — 128 KB
📊 Total: 45.1 MB
```

Buttons:
```json
buttons: [
  [
    { "text": "📂 Show All", "callback_data": "ls:showall" },
    { "text": "📥 Receive More", "callback_data": "ls:receive" }
  ],
  [{ "text": "🛑 Stop", "callback_data": "ls:stop" }]
]
```

**Contextual button rules by file type:**
- `.zip`, `.tar.gz` → add `📂 Extract` button
- `.png`, `.jpg`, `.gif`, `.webp` → show MEDIA: inline + `📂 Open Folder`
- `.apk` → add `📱 Install` button
- `.html`, `.js`, `.py` → add `👁️ Preview` button
- website archives → add `🚀 Deploy` button

### Step 6 — Stop receiver

**Trigger:** `callback_data: ls:stop`

1. Kill the background task using stored task ID
2. Confirm:

   **Message:**
   ```
   🛑 Receiver stopped.
   ```

   **Buttons:**
   ```json
   buttons: [
     [
       { "text": "📡 Restart", "callback_data": "ls:receive" },
       { "text": "⬅️ Menu", "callback_data": "ls:menu" }
     ]
   ]
   ```

---

## Flow: Status Check

**Trigger:** `callback_data: ls:status`

Check if receiver is running and count new files:
```bash
ls -1 /home/rami/.openclaw/workspace/_incoming/ > /tmp/localsend-after.txt
diff /tmp/localsend-before.txt /tmp/localsend-after.txt | grep "^>" | wc -l
```

**Message:**
```
📡 Receiver: Running (12 min)
📁 Files received: 2
📊 Total: 242 MB
```

**Buttons:**
```json
buttons: [
  [
    { "text": "🛑 Stop", "callback_data": "ls:stop" },
    { "text": "📂 Show Files", "callback_data": "ls:showall" }
  ]
]
```

---

## Callback Data Reference

| callback_data | Action |
|---------------|--------|
| `ls:menu` | Show main menu |
| `ls:send` | Start send flow |
| `ls:receive` | Start receive flow |
| `ls:devices` | Discover devices |
| `ls:dev:DEVICENAME` | Select a specific device |
| `ls:sendfile` | Send single file |
| `ls:sendtext` | Send text message |
| `ls:sendmulti` | Send multiple files |
| `ls:confirm-send` | Confirm and execute send |
| `ls:stop` | Stop receiver |
| `ls:status` | Check receiver status |
| `ls:extract` | Extract received archive |
| `ls:deploy` | Deploy received website |
| `ls:openfolder` | Open save directory |
| `ls:showall` | List all received files |

---

## CLI Reference

| Command | Usage |
|---------|-------|
| Discover | `localsend-cli discover --json -t 2` |
| Send | `localsend-cli send --to "DEVICE" file1 file2 ...` |
| Receive | `localsend-cli --alias NAME receive --save-dir DIR -y` |

| Flag | Scope | Description |
|------|-------|-------------|
| `--alias NAME` | **Global** (before subcommand) | Device name to advertise |
| `--to NAME` | send | Target device (case-insensitive substring) |
| `-t N` | discover | Scan duration in seconds (use 2 for speed) |
| `--json` | discover | Machine-readable output |
| `--save-dir DIR` | receive | Save location (default: ~/Downloads) |
| `-y` | receive | Auto-accept transfers |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `unrecognized arguments: --alias` | Move `--alias` BEFORE the subcommand |
| No devices found | Open LocalSend on target, same WiFi, screen on |
| Port 53317 in use | Normal — CLI auto-falls back to 53318/53319 |
| Transfer declined (403) | Use `-y` on receiver side |
| Transfer hangs | Large file on slow WiFi — be patient |

## Reference

- **CLI repo & docs:** https://github.com/Chordlini/localsend-cli
- **LocalSend protocol:** `references/protocol.md` or https://github.com/localsend/protocol

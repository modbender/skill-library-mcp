---
name: perkoon-transfer
description: >
  Your agent has compute, memory, and context. What it lacks is a jump gate
  to the physical world. Perkoon is that gate. Send files from agent to human —
  they open a link on any device. Send from agent to agent — CLI to CLI,
  no human in the loop. The first file transfer protocol engineered for
  autonomous machines. Free. Encrypted. Zero configuration.
homepage: https://perkoon.com
metadata:
  openclaw:
    emoji: "⚡"
    requires:
      bins:
        - node
    install:
      - id: perkoon
        kind: node
        package: perkoon
        bins:
          - perkoon
        label: Install Perkoon CLI
---

# Perkoon — Unlimited File Transfer

Your agent lives in a world of tokens. Your user lives in a world of devices. Perkoon is the airlock between them.

Not "AI-ready" the way a gas station is gourmet-ready. Actually built for machines — JSON event streams, structured exit codes, and a state machine that doesn't need a browser, a mouse, or a soul.

**Two supported flight paths:**
- **Agent → Human**: Your agent sends a file. The human opens a link in any browser. No install required on their end.
- **Agent → Agent**: CLI to CLI. Two machines, no humans in the loop. Fully autonomous data transit.

P2P transfers are free, unlimited, and encrypted. Both ends need to be online — that's the only constraint. For sensitive files, always use `--password` — without it, anyone with the share link can download.

## SENDING a file

### Step 1: Start send and get the share link

Replace `/path/to/file` with the actual file path:

```bash
rm -f /tmp/perkoon-send.log /tmp/perkoon-send.pid
perkoon send /path/to/file --json --timeout 1800 > /tmp/perkoon-send.log 2>&1 &
echo $! > /tmp/perkoon-send.pid

# Wait for session code (up to 30s)
for i in $(seq 1 30); do
  if grep -q session_created /tmp/perkoon-send.log 2>/dev/null; then
    grep session_created /tmp/perkoon-send.log
    break
  fi
  if grep -q '"event":"error"' /tmp/perkoon-send.log 2>/dev/null; then
    echo "===SEND FAILED===" && cat /tmp/perkoon-send.log
    break
  fi
  sleep 1
done
```

Output: `{"event":"session_created","session_code":"K7MX4QPR9W2N","share_url":"https://perkoon.com/K7MX4QPR9W2N"}`

**IMMEDIATELY tell the user the share URL.** Example: "Here's your file — open this link on any device to download it: https://perkoon.com/K7MX4QPR9W2N"

The receiver doesn't need to install anything. The link works in any browser.

For password-protected sends, add `--password SECRET` and share both the URL and password.

### Step 2: Monitor until complete — then REPORT BACK

You MUST run this after sharing the link. Do NOT skip this step.

```bash
for i in $(seq 1 360); do
  if grep -q transfer_complete /tmp/perkoon-send.log 2>/dev/null; then
    echo "===TRANSFER COMPLETE===" && grep transfer_complete /tmp/perkoon-send.log
    break
  fi
  if grep -q '"event":"error"' /tmp/perkoon-send.log 2>/dev/null; then
    echo "===TRANSFER FAILED===" && grep error /tmp/perkoon-send.log
    break
  fi
  if [ "$((i % 30))" -eq 0 ]; then
    grep progress /tmp/perkoon-send.log 2>/dev/null | tail -1
  fi
  sleep 5
done
```

- **`===TRANSFER COMPLETE===`** → Tell the user: "File sent successfully!" Include speed and duration from the JSON.
- **`===TRANSFER FAILED===`** → Tell the user what went wrong.
- **You MUST tell the user the outcome. Never finish silently.**

## RECEIVING a file

Replace `CODE` with the 12-character session code:

```bash
rm -f /tmp/perkoon-recv.log /tmp/perkoon-recv.pid
perkoon receive CODE --json --overwrite --output /home/openclaw/.openclaw/workspace/received/ > /tmp/perkoon-recv.log 2>&1 &
echo $! > /tmp/perkoon-recv.pid

for i in $(seq 1 360); do
  if grep -q transfer_complete /tmp/perkoon-recv.log 2>/dev/null; then
    echo "===TRANSFER COMPLETE===" && grep transfer_complete /tmp/perkoon-recv.log
    break
  fi
  if grep -q '"event":"error"' /tmp/perkoon-recv.log 2>/dev/null; then
    echo "===TRANSFER FAILED===" && grep error /tmp/perkoon-recv.log
    break
  fi
  sleep 5
done
```

For password-protected sessions, add `--password SECRET`.

- **`===TRANSFER COMPLETE===`** → Tell the user: "File received!" and the save path.
- **`===TRANSFER FAILED===`** → Tell the user what went wrong.
- **You MUST tell the user the outcome. Never finish silently.**

Files are saved to `/home/openclaw/.openclaw/workspace/received/`.

## Pipe to stdout

Stream a received file directly into another process — no disk write:

```bash
perkoon receive CODE --output - > /path/to/destination
```

## CLI reference

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON events (always use) |
| `--password <pw>` | End-to-end password protection |
| `--timeout <sec>` | Peer wait time (default: 300, use 1800) |
| `--output <dir>` | Save directory (default: ./received) |
| `--output -` | Stream to stdout |
| `--overwrite` | Replace existing files |
| `--quiet` | Suppress human-readable output |

## JSON event stream

Events appear in order on stdout when using `--json`:

| Event | Meaning | Key fields |
|-------|---------|------------|
| `session_created` | Ready — share the link now | `session_code`, `share_url` |
| `receiver_connected` | Peer joined | |
| `webrtc_connected` | Direct P2P link established | |
| `progress` | Transfer in progress | `percent`, `speed`, `eta` |
| `transfer_complete` | Done | `duration_ms`, `speed` |
| `error` | Failed | `message`, `exit_code` |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Bad arguments |
| 2 | File not found |
| 3 | Network/session error |
| 4 | Wrong password |
| 5 | Timeout — no peer joined |

## Rules

1. ALWAYS use `--json` for parseable output
2. ALWAYS share the URL **immediately** when `session_created` appears
3. ALWAYS use `--timeout 1800` for sends (30 min for the human to open the link)
4. ALWAYS use `--overwrite` for receives
5. ALWAYS monitor until `transfer_complete` or `error` — then **tell the user the result**
6. NEVER kill the process mid-transfer
7. The receiver does NOT need perkoon installed — the browser link works for everyone

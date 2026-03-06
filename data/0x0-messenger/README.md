# 0x0

> P2P disposable number messenger — no servers, no logs, no trace.

Share a number and a PIN. Message. Forget it ever happened.

---

## install

```bash
npm install -g @0x0contact/c0x0
```

requires Node.js 18+

---

## quick start

```bash
# initialize (generates your number)
c0x0 init

# --- share your number + PIN with someone ---
c0x0 pin new --label "for sale"   # creates e.g. "a3f9"
c0x0 whoami                       # shows your number to share

# --- or connect to someone who shared their number + PIN ---
c0x0 chat 0x0-293-4471-0038 a3f9

# done — revoke your PIN when finished
c0x0 pin revoke a3f9
```

---

## commands

### setup

```bash
c0x0 init          # generate your number
c0x0 whoami        # show your number
c0x0 renew         # generate a new number (resets all PINs)
```

### PIN management

```bash
c0x0 pin new                          # create a PIN
c0x0 pin new --label "label"          # with label
c0x0 pin new --expires 24h            # expires in 24h (also: 1w)
c0x0 pin new --public                 # create a public PIN (for requests)
c0x0 pin list                         # list all PINs
c0x0 pin rotate <pin>                 # change PIN value
c0x0 pin revoke <pin>                 # permanently revoke
```

### messaging

```bash
c0x0 chat <number> <pin>              # interactive chat
c0x0 send <number> <pin> "message"    # send once and exit
c0x0 inbox                            # view all inboxes
c0x0 read <pin>                       # read messages for a PIN
c0x0 listen                           # wait for incoming messages
c0x0 queue                            # show offline message queue
```

### requests (public PIN)

Share a public PIN openly — anyone can message you without knowing your number.
First reply creates a dedicated private channel automatically.

```bash
c0x0 pin new --public --label "open"  # create a public PIN to share
c0x0 requests                         # list incoming requests
c0x0 approve <pin> <pubkey>           # reply and convert to private chat
```

### contacts

```bash
c0x0 contact add 0x0://NUMBER/PIN     # add from URI
c0x0 contact add NUMBER PIN           # add manually
c0x0 contact list                     # list contacts
c0x0 contact label <id> "label"       # set label
c0x0 contact remove <id>              # remove
```

### QR code

```bash
c0x0 qr <pin>    # show QR code in terminal (scan to connect)
```

### web UI

```bash
c0x0 web              # open browser UI at localhost:3000
c0x0 web --port 8080
c0x0 web --lan        # expose on LAN (accessible from mobile on same WiFi)
c0x0 web --no-open
```

Starts a local web server with a chat interface.

---

## how it works

```
your number:  0x0-816-8172-8198   (generated locally, never sent anywhere)
your PIN:     a3f9                (you create and revoke it)

connection:   sha256("0x0:{number}:{pin}:0x0-v1-2026") → Hyperswarm topic
transport:    Hyperswarm (DHT-based P2P, Noise protocol)
storage:      ~/.0x0/ (local only)
```

No accounts. No servers. No registration. Messages route peer-to-peer via [Hyperswarm](https://github.com/holepunchto/hyperswarm).

---

## URI scheme

```
0x0://0x0-816-8172-8198/a3f9
```

Share as a link, QR code, or copy-paste. The other person adds it as a contact and connects directly.

---

## agent / pipe mode

For AI agents and automation:

```bash
c0x0 pipe <number> <pin>
```

Reads JSON commands from stdin, emits JSON events to stdout:

```bash
# stdin
{"type": "message", "content": "task complete"}

# stdout
{"type": "connected", "peer": "0x0-293-4471-0038", "pin": "a3f9"}
{"type": "message", "from": "0x0-293-4471-0038", "content": "got it"}
```

```python
import subprocess, json

proc = subprocess.Popen(
    ["c0x0", "pipe", "0x0-293-4471-0038", "a3f9"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
proc.stdin.write(json.dumps({"type": "message", "content": "done"}).encode() + b"\n")
proc.stdin.flush()
```

---

## data

Everything lives in `~/.0x0/`:

```
~/.0x0/
├── identity.json       # your number
├── pins.json           # your PINs
├── contacts.json       # saved contacts
├── queue.jsonl         # offline message queue (TTL: 72h)
└── messages/           # message history (per PIN)
```

Delete `~/.0x0/` to erase all traces.

---

## mobile

Android app available on Google Play. iOS coming soon.
The CLI and mobile apps are fully compatible — same number, same PINs, same P2P network.

[0x0.contact](https://0x0.contact)

---

## license

MIT

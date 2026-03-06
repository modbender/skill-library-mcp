---
name: neomutt-commander
description: Read, search, organise, and draft emails using neomutt — a terminal IMAP client. List inbox, search, read HTML email via w3m, mark read/unread, manage folders, archive messages, and compose drafts. If sending is not enabled or approved, always save as draft instead.
homepage: https://github.com/LogicalSapien/agent-skills/tree/main/clawhub/neomutt-commander
metadata: {"openclaw": {"emoji": "\ud83d\udce7", "requires": {"bins": ["neomutt", "w3m"]}, "homepage": "https://github.com/LogicalSapien/agent-skills/tree/main/clawhub/neomutt-commander"}}
---

# Neomutt Commander

Use when the user wants to read, search, or organise their email inbox, read message content, manage folders, archive messages, or draft a reply or new message — all from the terminal via IMAP. Works with Gmail, Fastmail, Outlook, and any IMAP provider.

> **If sending is not explicitly enabled or approved by the user, always save outgoing messages as a draft instead of sending.**

## Prerequisites

Install neomutt and w3m (HTML email renderer):

```bash
# macOS
brew install neomutt w3m

# Ubuntu / Debian
sudo apt install neomutt w3m
```

## Configuration

Create `~/.config/neomutt/neomuttrc` (or `~/.neomuttrc`):

```
set imap_user = "user@gmail.com"
set imap_pass = "*****"

set folder = "imaps://imap.gmail.com:993"
set spoolfile = "+INBOX"
set ssl_force_tls = yes
set imap_keepalive = 300
set mail_check = 60
set postponed = "+[Gmail]/Drafts"

set sort = reverse-date

# HTML handling
auto_view text/html
alternative_order text/plain text/html
```

For other providers change `imap.gmail.com:993` and `[Gmail]/Drafts` to match your server. For Gmail, `imap_pass` should be an **App Password** (Google Account → Security → 2-Step Verification → App Passwords).

Create `~/.config/neomutt/mailcap` so w3m renders HTML parts:

```
text/html; w3m -I %{charset} -T text/html; copiousoutput;
```

## Open neomutt

```bash
neomutt
```

Opens the inbox. To open a specific folder directly:

```bash
neomutt -f imaps://imap.gmail.com/INBOX
neomutt -f imaps://imap.gmail.com/[Gmail]/All%20Mail   # Gmail — All Mail
neomutt -f imaps://imap.fastmail.com/INBOX             # Fastmail example
```

## Navigate the inbox

| Key | Action |
|---|---|
| `j` / `k` | Move down / up |
| `Enter` | Open message |
| `q` | Back / quit |
| `?` | Full keybinding help |

## Search messages

| Key | Pattern | Example |
|---|---|---|
| `/` | Search visible list by subject/sender | `/invoice` |
| `l` | Limit view to a pattern | `l ~f boss@example.com` |
| `l .` | Clear limit (show all) | |

Search pattern syntax: `~f <from>` · `~s <subject>` · `~b <body>` · `~d <date>`

## Read a message

Press `Enter` on a message. HTML parts render automatically via w3m.

| Key | Action |
|---|---|
| `Space` / `-` | Page down / up |
| `h` | Toggle headers |
| `v` | View MIME attachments |
| `q` | Return to index |

## Mark as read / unread

| Key | Action |
|---|---|
| Automatic | Message is marked read when opened |
| `N` | Toggle unread on selected message |
| `t` | Tag message; then `;N` to mark tagged set |

## Archive a message

Move the message out of INBOX into your archive folder:

```
s  →  type folder name  →  Enter
```

On **Gmail** the archive folder is `[Gmail]/All Mail`. Add a macro for one-key archiving:

```
macro index A "<save-message>=[Gmail]/All Mail<enter><enter>" "Archive"
```

## Manage folders / labels

Folders in IMAP, labels in Gmail — same thing. Move or copy a message:

```
C  →  type folder name  →  Enter   # Copy (message stays in current folder too)
s  →  type folder name  →  Enter   # Move (removes from current folder)
```

## Compose a new message

```
m
```

Fill in `To:`, `Subject:`, write body, then:

| Key | Action |
|---|---|
| `Ctrl-X` (in editor) | Finish editing and go to send screen |
| `y` | **Send** (only if sending is approved) |
| `P` | **Postpone — saves to the drafts folder** |
| `q` | Abort / discard |

> **Default behaviour: press `P` to postpone (save draft) unless the user has explicitly asked to send.**

## Resume a draft

```bash
neomutt -f imaps://imap.gmail.com/[Gmail]/Drafts   # Gmail
neomutt -f imaps://imap.fastmail.com/Drafts        # Fastmail / generic
```

Open the draft and press `e` to edit, then `y` to send or `P` to re-postpone.

## Quit

```
q  →  confirm with y
```

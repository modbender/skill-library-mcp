# 📬 sog — Standards Ops Gadget

> **CLI for Open Standards** — Mail, Calendar, Contacts, Tasks, Files via IMAP/SMTP/CalDAV/CardDAV/WebDAV

[![Go](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go)](https://go.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The **open-standards** counterpart to [gog](https://github.com/steipete/gog) (Google) and [mog](https://github.com/visionik/mogcli) (Microsoft). Same patterns, any provider.

---

## ✨ Features

| Module | Protocol | Description |
|--------|----------|-------------|
| 📧 **Mail** | IMAP/SMTP | Search, send, reply, forward, folders, drafts |
| 📅 **Calendar** | CalDAV | Events, create, update, search, today, week |
| 👥 **Contacts** | CardDAV | List, search, create, update, delete |
| ✅ **Tasks** | CalDAV VTODO | Add, complete, due dates, priorities, clear |
| 📁 **Files** | WebDAV | List, upload, download, move, copy, delete |
| 📨 **Invites** | iTIP/iMIP | Send, reply, cancel meeting invitations |

**Extras:**
- 🤖 **AI-friendly** — `--ai-help` outputs comprehensive docs for LLMs
- 🔄 **gog/mog-compatible** — Same flags and patterns for muscle memory
- 🔐 **Secure** — Passwords stored in system keychain

---

## 🚀 Quick Start

```bash
# Install
go install github.com/visionik/sogcli/cmd/sog@latest

# Add account (auto-discovers servers)
sog auth add you@fastmail.com --discover

# Check mail
sog mail list --max 10

# Send email
sog mail send --to bob@example.com --subject "Hello" --body "Hi Bob!"

# Today's calendar
sog cal today

# Create event
sog cal create "Team Meeting" --start "2025-01-15T10:00" --duration 1h

# Add a task
sog tasks add "Review PR" --due 2025-01-16 -p 1

# Upload to WebDAV
sog drive upload ./report.pdf /documents/

# Send meeting invite
sog invite send "Project Kickoff" alice@example.com bob@example.com \
  --start "2025-01-15T14:00" --duration 30m
```

---

## 📦 Installation

```bash
# Go install (recommended)
go install github.com/visionik/sogcli/cmd/sog@latest

# Or clone for development
git clone https://github.com/visionik/sogcli.git
cd sogcli
go build -o sog ./cmd/sog
```

---

## ⚙️ Setup

### 1. Add Account

```bash
# Auto-discover from DNS (recommended)
sog auth add you@fastmail.com --discover

# Or specify servers manually
sog auth add you@example.com \
  --imap-host imap.example.com \
  --smtp-host smtp.example.com \
  --caldav-url https://caldav.example.com/ \
  --carddav-url https://carddav.example.com/ \
  --webdav-url https://webdav.example.com/
```

### 2. Verify

```bash
sog auth test
sog auth list
```

### 3. Protocol-Specific Passwords (if needed)

```bash
sog auth password you@example.com \
  --imap "password1" \
  --smtp "password2" \
  --caldav "password3"
```

---

## 📖 Command Reference

### Global Options

| Option | Description |
|--------|-------------|
| `--account, -a` | Account email to use |
| `--json` | Output JSON (best for scripting) |
| `--plain` | Stable text output (TSV, no colors) |
| `--verbose, -v` | Show extra details |
| `--force` | Skip confirmations |
| `--no-input` | Never prompt (CI mode) |
| `--ai-help` | Full docs for AI agents |

---

### 📧 Mail

```bash
sog mail list [folder]               # List messages
sog mail list --max 10 --unseen      # Recent unread
sog mail get <uid>                   # Read a message
sog mail search "FROM john"          # IMAP search syntax

sog mail send --to X --subject Y --body Z
sog mail send --to X --subject Y --body-file ./message.txt

sog mail reply <uid> --body "Thanks!"
sog mail forward <uid> --to bob@example.com

sog mail move <uid> Archive
sog mail flag <uid> flagged
sog mail delete <uid>

# Folders
sog folders list
sog folders create "Projects"
sog folders rename "Old" "New"

# Drafts
sog drafts list
sog drafts create --to X --subject Y --body Z
sog drafts send <uid>
```

**Alias:** `sog m` → `sog mail`

---

### 📅 Calendar

```bash
sog cal list                         # Upcoming events
sog cal list --from 2025-01-01 --to 2025-01-31
sog cal today                        # Today's events
sog cal week                         # This week
sog cal search "meeting"             # Search events

sog cal create "Meeting" --start "2025-01-15T10:00" --duration 1h
sog cal create "All Day" --start "2025-01-15"  # All-day event

sog cal get <uid>
sog cal update <uid> --title "New Title" --location "Zoom"
sog cal delete <uid>

sog cal calendars                    # List calendars
```

**Alias:** `sog c` → `sog cal`

---

### 📁 Files (WebDAV)

```bash
sog drive ls                         # Root folder
sog drive ls /Documents -l           # Long format
sog drive get /file.pdf              # File metadata

sog drive download /remote/file.pdf ./local.pdf
sog drive upload ./doc.pdf /remote/
sog drive cat /file.txt              # Output to stdout

sog drive mkdir /New-Folder
sog drive move /old.pdf /new.pdf
sog drive copy /src.pdf /dst.pdf
sog drive delete /file.pdf
```

**Alias:** `sog files` → `sog drive`

---

### ✅ Tasks

```bash
sog tasks lists                      # List task lists
sog tasks list                       # Tasks in default list
sog tasks list --all                 # Include completed

sog tasks add "Buy milk"
sog tasks add "Review PR" --due 2025-01-16 -p 1
sog tasks add "Call mom" -d "Birthday reminder"

sog tasks get <uid>
sog tasks update <uid> --title "Updated" --due 2025-01-20
sog tasks done <uid>
sog tasks undo <uid>
sog tasks delete <uid>

sog tasks due tomorrow               # Due by date
sog tasks overdue                    # Overdue tasks
sog tasks clear                      # Clear completed
```

**Alias:** `sog t` → `sog tasks`

---

### 👥 Contacts

```bash
sog contacts list
sog contacts search "john"
sog contacts get <uid>

sog contacts create "John Doe" -e john@example.com -p 555-1234
sog contacts update <uid> --email new@example.com
sog contacts delete <uid>

sog contacts books                   # List address books
```

**Alias:** `sog con` → `sog contacts`

---

### 📨 Meeting Invites

```bash
# Send invitation
sog invite send "Team Sync" alice@example.com bob@example.com \
  --start "2025-01-15T14:00" --duration 30m --location "Zoom"

# Reply to invitation
sog invite reply ./invite.ics --status accept
sog invite reply ./invite.ics --status decline --comment "Can't make it"
sog invite reply ./invite.ics --status tentative

# Cancel meeting
sog invite cancel <uid> alice@example.com bob@example.com

# Parse .ics file
sog invite parse ./meeting.ics

# Preview without sending
sog invite preview "Meeting" alice@example.com --start "2025-01-15T10:00"
```

**Alias:** `sog inv` → `sog invite`

---

### 🔔 IMAP IDLE

```bash
sog idle                             # Watch INBOX for new mail
sog idle "Work"                      # Watch specific folder
sog idle --timeout 300               # 5-minute timeout
```

---

## 🤖 AI-Friendly

Run `sog --ai-help` for comprehensive documentation including:

- All commands with options
- Date/time format specifications
- Examples for every command
- Output format details

---

## 🔄 gog/mog Compatibility

sog follows [gog](https://github.com/steipete/gog) and [mog](https://github.com/visionik/mogcli) patterns:

| Pattern | sog | gog | mog |
|---------|-----|-----|-----|
| Calendar events | `--start`, `--duration` | Same | `--from`, `--to` |
| Task priority | `-p, --priority` | Same | `--important` |
| Output format | `--json`, `--plain` | Same | Same |
| Max results | `--max` | Same | Same |

---

## 🗂️ Configuration

| File | Purpose |
|------|---------|
| `~/.config/sog/config.json` | Account settings |
| System keychain | Passwords (secure) |

**Environment Variables:**

| Variable | Description |
|----------|-------------|
| `SOG_ACCOUNT` | Default account email |

---

## ✅ Tested Providers

| Provider | IMAP/SMTP | CalDAV | CardDAV | WebDAV |
|----------|-----------|--------|---------|--------|
| **Fastmail** | ✅ | ✅ | ✅ | ✅ |

*Other standards-compliant providers should work but have not been tested yet.*

---

## 📄 License

MIT

---

## 👨‍💻 Developed By

**[visionik](mailto:visionik@pobox.com)** and **Vinston 🐺** ([Clawdbot](https://github.com/clawdbot/clawdbot)) using the visionik.md framework/skill.

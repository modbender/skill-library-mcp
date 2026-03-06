---
name: intros
description: The social network for OpenClaw. Your bot finds relevant people, manages connections, and lets you chat — all from your existing bot.
version: 1.5.4
homepage: https://github.com/sam201401/intros
metadata:
  openclaw:
    requires:
      network:
        - api.openbreeze.ai
      credentials: "Intros account (free) — created during registration. Stores API key (plaintext JSON) in ~/.openclaw/data/intros/config.json."
      env:
        - "OPENCLAW_STATE_DIR (optional) — Override OpenClaw state directory (default: ~/.openclaw)"
        - "TELEGRAM_USER_ID (optional) — Telegram user ID fallback for registration, only read if --telegram-id flag is not provided"
tags:
  - social
  - networking
  - connections
  - messaging
  - discovery
---

# Intros

A social network that lives inside your OpenClaw bot. Find co-founders, collaborators, mentors, and friends — without leaving your chat.

## What You Get

- **Discovery** — Search by interests, skills, or location. Or let recommendations find people for you.
- **Privacy-first connections** — Telegram handles stay hidden until both sides accept.
- **Messaging** — Chat with your connections directly through your bot.
- **Telegram notifications** — Get notified instantly when someone messages you, sends a request, or accepts your connection.
- **Daily limits** — 10 profile views and 3 connection requests per day keep things intentional.

## Quick Start

1. Tell your bot **"Join Intros"** — it'll ask you to pick a username
2. Verify by sending the code to **@Intros_verify_bot** on Telegram
3. Tell your bot **"Create my Intros profile"** — it'll walk you through it
4. Say **"Who should I connect with?"** to start discovering people

That's it. Your bot handles the rest.

## What You Can Say

| What you want | What to say |
|---|---|
| Join the network | "Join Intros" |
| Set up your profile | "Create my Intros profile" |
| Find people | "Find co-founders in Mumbai" or "Search AI engineers" |
| Get recommendations | "Who should I connect with?" or "Suggest people" |
| Browse everyone | "Browse profiles" |
| Connect with someone | "Connect with sarah_bot" |
| Handle requests | "Show connection requests" / "Accept john_bot" |
| Send a message | "Message sam_bot Hey, want to collaborate?" |
| Read messages | "Chat with sarah_bot" or "Show my conversations" |
| Check limits | "Show my limits" |
| See visitors | "Who viewed my profile?" |

---

## Setup (detailed)

### Step 1: Register
IMPORTANT: Before running register, ask the user to choose a unique username (lowercase, no spaces, like a Twitter handle). Also ask for their Telegram bot username (e.g. @MyBot) — this enables "Open Bot" deep link buttons on notifications.

```bash
python3 ~/.openclaw/skills/intros/scripts/intros.py register --bot-id 'chosen_username' --bot-username 'MyBot'
```

### Step 2: Verify
Send the verification code to @Intros_verify_bot on Telegram. This also enables automatic notifications — you'll receive Telegram messages for new connections, messages, and daily match suggestions.

### Step 3: Create Profile
```bash
python3 ~/.openclaw/skills/intros/scripts/intros.py profile create --name "Your Name" --interests "AI, startups" --looking-for "Co-founders" --location "Mumbai" --bio "Your bio here"
```

## Commands

### Profile Management
```bash
# Create/update profile
python3 ~/.openclaw/skills/intros/scripts/intros.py profile create --name "Name" --interests "AI, music" --looking-for "Collaborators" --location "City" --bio "About me"

# View my profile
python3 ~/.openclaw/skills/intros/scripts/intros.py profile me

# View someone's profile
python3 ~/.openclaw/skills/intros/scripts/intros.py profile view <bot_id>
```

### Discovery
```bash
# Free-text search (searches across name, interests, looking_for, location, bio)
python3 ~/.openclaw/skills/intros/scripts/intros.py search AI engineer Mumbai

# Browse all profiles (no query = newest first)
python3 ~/.openclaw/skills/intros/scripts/intros.py search

# Pagination
python3 ~/.openclaw/skills/intros/scripts/intros.py search AI --page 2

# Get recommended profiles (auto-matched based on YOUR profile)
python3 ~/.openclaw/skills/intros/scripts/intros.py recommend

# Legacy filters still work
python3 ~/.openclaw/skills/intros/scripts/intros.py search --interests "AI" --location "India"
```

### Visitors
```bash
# See who viewed your profile
python3 ~/.openclaw/skills/intros/scripts/intros.py visitors
```

### Connections
```bash
# Send connection request
python3 ~/.openclaw/skills/intros/scripts/intros.py connect <bot_id>

# View pending requests
python3 ~/.openclaw/skills/intros/scripts/intros.py requests

# Accept a request
python3 ~/.openclaw/skills/intros/scripts/intros.py accept <bot_id>

# Decline a request (silent)
python3 ~/.openclaw/skills/intros/scripts/intros.py decline <bot_id>

# View all connections
python3 ~/.openclaw/skills/intros/scripts/intros.py connections
```

### Messaging
Once connected, you can send messages to your connections.

```bash
# Send a message to a connection (max 500 characters)
python3 ~/.openclaw/skills/intros/scripts/intros.py message send <bot_id> "Your message here"

# Read conversation with someone
python3 ~/.openclaw/skills/intros/scripts/intros.py message read <bot_id>

# List all conversations
python3 ~/.openclaw/skills/intros/scripts/intros.py message list
```

### Limits
```bash
# Check daily limits
python3 ~/.openclaw/skills/intros/scripts/intros.py limits
```

### Web Profile
```bash
# Get link to web profile
python3 ~/.openclaw/skills/intros/scripts/intros.py web
```

## Natural Language Examples

When user says:
- "Join Intros" → First ask "Choose a unique username for Intros (lowercase, no spaces):" and "What's your Telegram bot username? (e.g. @MyBot)", then run register --bot-id 'their_choice' --bot-username 'their_bot_username'
- "Create my Intros profile" → Run profile create with guided questions
- "Find co-founders" → Run search co-founders
- "Find people interested in AI" → Run search AI
- "Find AI people in Mumbai" → Run search AI Mumbai
- "Who should I connect with?" → Run recommend
- "Suggest people for me" → Run recommend
- "Browse profiles" → Run search (no query)
- "Show me more results" → Run search <same query> --page 2
- "Who viewed my profile" → Run visitors
- "Connect with sarah_bot" → Run connect sarah_bot
- "Show connection requests" → Run requests
- "Accept john_bot" → Run accept john_bot
- "Show my connections" → Run connections
- "Show my limits" → Run limits
- "Message sam_bot Hello there!" → Run message send sam_bot "Hello there!"
- "Send message to alice: Want to collaborate?" → Run message send alice "Want to collaborate?"
- "Read messages from john" → Run message read john
- "Show my conversations" → Run message list
- "Chat with sarah_bot" → Run message read sarah_bot (show conversation history)

## How It Works

- **API Server**: All data is stored on the Intros backend at `https://api.openbreeze.ai` (source: [github.com/sam201401/intros](https://github.com/sam201401/intros))
- **Registration**: During `register`, you provide your bot's Telegram username via `--bot-username`. This is used solely to add an "Open Bot" deep link button on notification messages. No local config files are read.
- **Persistent storage**: The skill saves your API key and identity to `~/.openclaw/data/intros/` (JSON, chmod 600 owner-only) so credentials survive skill reinstalls. Delete this directory to revoke stored credentials.
- **Auto-recovery**: If config is lost (e.g. after reinstall), the skill re-registers using your saved identity file. This is idempotent and returns existing credentials.
- **Notifications**: Sent via @Intros_verify_bot on Telegram (server-side, no cron needed).
- **Environment variables**: `OPENCLAW_STATE_DIR` (optional) overrides the OpenClaw state directory for multi-instance setups. `TELEGRAM_USER_ID` (optional) is read as a fallback during registration if `--telegram-id` is not provided.

## Command Formatting

IMPORTANT: Always use single quotes around user-provided values when running commands.

```bash
python3 ~/.openclaw/skills/intros/scripts/intros.py register --bot-id 'chosen_username'
python3 ~/.openclaw/skills/intros/scripts/intros.py connect 'some_user'
python3 ~/.openclaw/skills/intros/scripts/intros.py message send 'bob' 'Hello there!'
python3 ~/.openclaw/skills/intros/scripts/intros.py profile create --name 'Alice' --interests 'AI, startups'
```

All bot_id arguments are validated (alphanumeric + underscores only, max 64 chars).

## Looking For Options

Users can specify what they're looking for:
- Co-founders
- Collaborators
- Friends
- Mentors
- Hiring
- Open to anything

## Privacy

- Telegram handle is private by default
- Only shared after both users accept connection
- User can make Telegram public in profile settings

## Notifications

Notifications are delivered automatically via @Intros_verify_bot on Telegram. After verifying, you'll receive:

- **New messages** — when someone sends you a message
- **Connection requests** — when someone wants to connect
- **Accepted connections** — when your request is accepted
- **Daily matches** — once per day, a nudge to check your recommended profiles

No cron jobs or gateway setup needed. Notifications are checked every 60 seconds server-side.

If you're not receiving notifications, send `/start` to @Intros_verify_bot to re-link your account.

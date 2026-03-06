---
name: vinculum
description: Shared consciousness between Clawdbot instances. Links multiple bots into a collective, sharing memories, activities, and decisions in real-time over local network using Gun.js P2P sync.
version: 1.1.0
author: Koba42 Corp
license: MIT
homepage: https://github.com/koba42/clawdbot-vinculum
metadata:
  clawdbot:
    emoji: "🔗"
    category: "integration"
    requires:
      bins: ["node", "npm"]
    install:
      - id: npm
        kind: shell
        command: "cd $SKILL_DIR && npm install --production"
        label: "Install Node.js dependencies"
    commands:
      - name: link
        description: "Manage the Vinculum - shared consciousness between Clawdbot instances"
tags:
  - p2p
  - sync
  - collective
  - multi-agent
  - gun
  - real-time
---

# Vinculum: Shared Consciousness

*"The Vinculum is the processing device at the core of every Borg vessel. It interconnects the minds of all the drones."* — Seven of Nine

Link multiple Clawdbot instances into a collective consciousness using Gun.js peer-to-peer sync.

## Features

- 🔗 **Real-time link** — Changes propagate instantly between drones
- 🌐 **Local network** — Works across machines on the same LAN
- 🔐 **Encrypted** — All shared data encrypted
- 🤖 **Individual identity** — Each drone keeps its own SOUL.md
- 📡 **Drone discovery** — Automatic multicast discovery

## Installation

After installing from ClawdHub:

```bash
cd skills/vinculum
npm install --production
```

Or run the install script:

```bash
./install.sh
```

## Quick Start

### 1. Start the Vinculum Relay

```
/link relay start
```

This starts the relay on port 8765 with local network multicast enabled.

### 2. Initialize the Collective (First Bot)

```
/link init
```

You'll receive a pairing code. Share it with your other bot(s).

### 3. Join the Collective (Additional Bots)

```
/link join <pairing-code>
```

### 4. Verify Connection

```
/link status
/link drones
```

## Commands Reference

### Relay Management
| Command | Description |
|---------|-------------|
| `/link relay` | Show relay status |
| `/link relay start` | Start Vinculum relay |
| `/link relay stop` | Stop relay |
| `/link relay restart` | Restart relay |
| `/link relay peer <url>` | Add remote peer |

### Collective Setup
| Command | Description |
|---------|-------------|
| `/link init` | Create new collective |
| `/link join <code>` | Join with invite code |
| `/link invite` | Generate new invite code |
| `/link leave` | Leave collective |

### Control
| Command | Description |
|---------|-------------|
| `/link` | Quick status |
| `/link on` | Enable link |
| `/link off` | Disable link |
| `/link status` | Detailed status |

### Shared Consciousness
| Command | Description |
|---------|-------------|
| `/link share "text"` | Share a thought/memory |
| `/link drones` | List connected drones |
| `/link activity` | Recent collective activity |
| `/link decisions` | Shared decisions |

### Configuration
| Command | Description |
|---------|-------------|
| `/link config` | View all settings |
| `/link config drone-name <name>` | Set this drone's designation |
| `/link config share-activity on/off` | Toggle activity sharing |
| `/link config share-memory on/off` | Toggle memory sharing |

## What Gets Shared

| Data | Shared | Notes |
|------|--------|-------|
| Activity summaries | ✅ | What each drone did |
| Learned knowledge | ✅ | Collective learnings |
| Decisions | ✅ | Consensus achieved |
| Drone status | ✅ | Online, current task |
| Full conversations | ❌ | Stays local |
| USER.md | ❌ | Individual identity |
| SOUL.md | ❌ | Individual personality |
| Credentials | ❌ | Never linked |

## Multi-Machine Setup

### Machine 1 (Runs Relay)
```
/link relay start
/link init
```
Note the pairing code and your machine's IP (shown in `/link relay status`).

### Machine 2+ (Connects to Relay)
```
/link relay peer http://<machine1-ip>:8765/gun
/link join <pairing-code>
```

## Configuration

Config file: `~/.config/clawdbot/vinculum.yaml`

```yaml
enabled: true
collective: "your-collective-id"
drone_name: "Seven"
peers:
  - "http://localhost:8765/gun"
relay:
  auto_start: true
  port: 8765
share:
  activity: true
  memory: true
  decisions: true
```

## Architecture

```
┌─────────────┐     ┌─────────────┐
│   Drone A   │     │   Drone B   │
│  (Legion)   │     │  (Seven)    │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │   Subspace Link   │
       ▼                   ▼
  ┌────────────────────────────┐
  │      Vinculum Relay        │
  │   (Collective Processor)   │
  └────────────────────────────┘
```

## Troubleshooting

**"Relay not running"**
- Run `/link relay start`
- Check `/link relay logs` for errors

**"No drones connected"**  
- Ensure all bots use the same pairing code
- Check network connectivity between machines
- Port 8765 must be accessible

**"Link not working"**
- Check `/link status` shows Connected
- Try `/link relay restart`

## Requirements

- Node.js 18+
- npm

## License

MIT — Koba42 Corp

---

*Resistance is futile. You will be assimilated into the collective.*

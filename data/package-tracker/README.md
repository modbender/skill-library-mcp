# 📦 OpenClaw Package Tracker

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.dev)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/joaoleitegmr/openclaw-package-tracker/pulls)

Track packages from 10+ carriers directly through your OpenClaw AI agent.

## Features

- 📮 **Multi-Carrier Support** — FedEx, UPS, DHL, CTT (Portugal), PostNL, USPS, Royal Mail, La Poste, Deutsche Post, China Post
- 🔍 **Auto Carrier Detection** — Automatically identifies carrier from tracking number format
- 🔗 **Tracking URLs** — Direct links to carrier tracking pages
- 💾 **SQLite Storage** — Local database for package history
- 🌐 **17track API** — Unified tracking API with free tier (100 packages/month)
- ⏰ **Cron Integration** — Set up automatic periodic checks
- 📱 **Any Messaging Channel** — Works with Telegram, Signal, Discord, WhatsApp, and more via OpenClaw

## Quick Start

Paste this into your OpenClaw agent to get started:

```
Install the package tracker skill - clone https://github.com/joaoleitegmr/openclaw-package-tracker to skills/, run setup.sh, and help me add a package to track.
```

## Installation

### 1. Clone the Repository

```bash
cd /path/to/openclaw/skills
git clone https://github.com/joaoleitegmr/openclaw-package-tracker.git
```

### 2. Run Setup

```bash
cd package-tracker
bash scripts/setup.sh
```

### 3. Add Your 17track API Key

Edit `scripts/.env` and add your API key:

```bash
SEVENTEEN_TRACK_API_KEY=YOUR_API_KEY_HERE
```

## Getting a 17track API Key

1. Go to **[admin.17track.net](https://admin.17track.net)** and register for a free account
2. After logging in, go to **"API"** or **"Developer"** section
3. Create a new API key
4. Copy the key and add it to your `scripts/.env` file

### Free Tier Limits
- **100 package registrations per month**
- Unlimited status check calls
- Perfect for personal use

## Usage

Activate the virtual environment and use the CLI:

```bash
cd package-tracker
source scripts/venv/bin/activate
python scripts/cli.py --help
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add <tracking_number>` | Add a package to track | `python scripts/cli.py add 1Z999AA10123456784` |
| `add <tn> -d "Description"` | Add with description | `python scripts/cli.py add AB123456789PT -d "USB-C cable from Amazon"` |
| `add <tn> -c <carrier>` | Force carrier | `python scripts/cli.py add 1234567890 -c DHL` |
| `check` | Check all packages for updates | `python scripts/cli.py check` |
| `list` | List active packages | `python scripts/cli.py list` |
| `list -a` | Include inactive packages | `python scripts/cli.py list -a` |
| `details <tracking_number>` | Show full tracking history | `python scripts/cli.py details 1Z999AA10123456784` |
| `remove <tracking_number>` | Stop tracking a package | `python scripts/cli.py remove 1Z999AA10123456784` |
| `quota` | Show API usage | `python scripts/cli.py quota` |

### Examples

```bash
# Add a FedEx package
python scripts/cli.py add 123456789012

# Add a USPS package with description
python scripts/cli.py add 9400111899223456789012 -d "New shoes from Nike"

# Check all packages
python scripts/cli.py check

# See full tracking details
python scripts/cli.py details 9400111899223456789012
```

## OpenClaw Integration

### Automatic Updates with Cron

Add a cron job to check for updates automatically:

```bash
# Check every hour
0 * * * * cd /path/to/package-tracker && /path/to/package-tracker/scripts/venv/bin/python scripts/check_updates.py --quiet >> /var/log/package-tracker.log 2>&1
```

```bash
# Check every 6 hours
0 */6 * * * cd /path/to/package-tracker && /path/to/package-tracker/scripts/venv/bin/python scripts/check_updates.py --quiet >> /var/log/package-tracker.log 2>&1
```

### How Notifications Work

The script outputs updates to stdout in a format that OpenClaw can relay. When run through OpenClaw, updates are automatically sent to your messaging channel (Telegram, Signal, etc.).

## Supported Carriers

| Carrier | Auto-Detect Pattern | Tracking URL |
|---------|---------------------|--------------|
| FedEx | `^\d{12}(\d{3})?(\d{5})?(\d{7})?$` | [fedex.com](https://www.fedex.com/fedextrack/) |
| UPS | `^1Z[A-Z0-9]{16}$` | [ups.com](https://www.ups.com/track) |
| DHL | `^\d{10,11}$` | [dhl.com](https://www.dhl.com) |
| USPS | `^(94\|92\|93\|94)\d{18,22}$` | [usps.com](https://tools.usps.com/go/TrackConfirmAction) |
| CTT Portugal | `^[A-Z]{2}\d{9}PT$` | [ctt.pt](https://www.ctt.pt) |
| PostNL | `^3S[A-Z0-9]{13,15}$` | [postnl.nl](https://jouw.postnl.nl) |
| Royal Mail | `^[A-Z]{2}\d{9}GB$` | [royalmail.com](https://www.royalmail.com) |
| La Poste | `^[A-Z]{2}\d{9}FR$` | [laposte.fr](https://www.laposte.fr) |
| Deutsche Post | `^[A-Z]{2}\d{9}DE$` | [deutschepost.de](https://www.deutschepost.de) |
| China Post | `^[A-Z]{2}\d{9}CN$` | [17track.net](https://t.17track.net) |

## Configuration

Configure via environment variables in `scripts/.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `SEVENTEEN_TRACK_API_KEY` | Yes | Your 17track API key from admin.17track.net |
| `TELEGRAM_BOT_TOKEN` | No | Bot token for Telegram notifications |
| `TELEGRAM_CHAT_ID` | No | Chat ID for Telegram notifications |

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  17track    │────▶│   tracker.py │────▶│  SQLite DB  │
│     API     │     │  (Python)    │     │ (local file)│
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    stdout    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  OpenClaw    │────▶│   Telegram  │
                    │    Agent     │     │   Signal    │
                    └──────────────┘     │   Discord   │
                                         │   WhatsApp  │
                                         └─────────────┘
```

1. **Add package** → CLI registers with 17track API and saves to SQLite
2. **Check updates** → Queries 17track for latest status
3. **Output** → Prints notifications to stdout
4. **Relay** → OpenClaw captures stdout and sends via your messaging channel

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This skill was entirely built by an OpenClaw AI agent — I'm not a developer and have not audited the code. I guided and customized the project, but all code was generated and written by the AI. Use at your own discretion, review the code yourself, and feel free to improve it via PRs.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">Built with 🤖 by OpenClaw</p>
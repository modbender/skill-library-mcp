# TestFlight Seat Monitor

> Monitor available TestFlight beta slots with smart lookups and silent batch checking. Get alerted only when slots actually open up.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)

## Features

- 🔍 **Smart Lookups** - Maps cryptic TestFlight codes → readable app names
- 🔕 **Silent by Default** - Only alerts when slots actually open (no spam)
- 📦 **Batch Monitoring** - Check multiple apps in one run
- 📊 **State Tracking** - Detects status changes (full → available)
- ⚙️ **Configurable** - CLI-based config, customizable intervals
- 🎯 **Community Data** - Uses 800+ app names from awesome-testflight-link

## Quick Start

### Install via ClawHub

```bash
clawhub install testflight-monitor
```

### Or Clone from GitHub

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/jon-xo/testflight-monitor-skill.git testflight-monitor
```

### Add URLs to Monitor

```bash
cd testflight-monitor
./testflight-monitor.sh add https://testflight.apple.com/join/BnjD4BEf
./testflight-monitor.sh list
```

### Set Up Automated Monitoring

```bash
openclaw cron add \
  --name "TestFlight Monitor" \
  --every 60m \
  --target isolated \
  --message "Run: ~/.openclaw/workspace/skills/testflight-monitor/testflight-monitor.sh batch. If output contains 'SILENT', reply NO_REPLY. Otherwise announce the findings."
```

## Usage

```bash
# Look up an app name
./testflight-monitor.sh lookup BnjD4BEf
# → OpenClaw iOS

# Check a single URL
./testflight-monitor.sh check https://testflight.apple.com/join/BnjD4BEf
# → Status: full | App: OpenClaw iOS

# Run batch check
./testflight-monitor.sh batch
# → SILENT: No status changes detected.
# OR
# → 🎉 **OpenClaw iOS** beta now has open slots! https://...

# List monitored apps
./testflight-monitor.sh list

# Add/remove URLs
./testflight-monitor.sh add <url>
./testflight-monitor.sh remove <url>
```

## How It Works

1. **Fetch** TestFlight page via curl
2. **Parse** HTML for availability indicators
3. **Track** status in `config/batch-state.json`
4. **Alert** only on transitions (full → available)
5. **Lookup** app names from community data

## Why This Exists

TestFlight betas fill up **fast**. You need:
- ✅ Automated monitoring (not manual checking)
- ✅ Smart notifications (only when slots open)
- ✅ Readable app names (not `BnjD4BEf`)
- ✅ Batch efficiency (one job for many apps)

This skill does all that.

## Architecture

```
testflight-monitor/
├── testflight-monitor.sh       # Main CLI
├── lib/                         # Modular components
│   ├── lookup.sh               # Code → name resolver
│   ├── check-single.sh         # Single URL checker
│   └── check-batch.sh          # Batch checker
├── config/                      # Config & state
│   ├── testflight-codes.json  # Community lookup (~859 apps)
│   ├── custom-codes.json      # User overrides
│   ├── batch-config.json      # Monitoring config
│   └── batch-state.json       # State tracking
└── tools/
    └── update-lookup.sh       # Refresh lookup table
```

## Configuration

### Add Private Beta

Edit `config/custom-codes.json`:
```json
{
  "YOUR_CODE": "Your App Name"
}
```

### Change Check Interval

Edit `config/batch-config.json`:
```json
{
  "links": [...],
  "interval_minutes": 30
}
```

Valid: 30-180 minutes

## Data Sources

- **Lookup table:** [awesome-testflight-link](https://github.com/pluwen/awesome-testflight-link) (800+ apps)
- **Custom codes:** User-defined in `config/custom-codes.json`

## Requirements

- **OpenClaw** (agent runtime)
- `curl` (fetch pages)
- `jq` (JSON processing)
- `bash` (macOS/Linux)

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file

## Credits

- Built for [OpenClaw](https://openclaw.ai)
- Lookup data from [awesome-testflight-link](https://github.com/pluwen/awesome-testflight-link)
- Inspired by the universal struggle to catch beta slots

## Links

- **ClawHub:** https://clawhub.com/jon-xo/testflight-monitor
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Report Issues:** https://github.com/jon-xo/testflight-monitor-skill/issues

---

Made with ❤️ for the OpenClaw community

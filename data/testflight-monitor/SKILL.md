---
name: testflight-seat-monitor
description: Monitor available TestFlight beta slots with smart app lookups and silent batch checking. Get alerted when slots open up.
metadata: {"clawdbot":{"emoji":"🎯","os":["darwin","linux"]}}
---

# TestFlight Seat Monitor

Monitor available TestFlight beta slots with smart app name lookups and silent batch checking. Get alerted only when seats open up.

## What It Does

- **Lookup TestFlight codes** → app names using community data
- **Check single URLs** for immediate status
- **Batch monitoring** with state tracking (silent by default)
- **Only alerts on changes** (full → available)
- **Configurable intervals** (30min - 3hr recommended)

## Why This Exists

TestFlight betas fill up fast. This skill:
- Monitors multiple betas in one job
- Stays silent unless something changes
- Uses human-readable app names (not cryptic codes)
- Tracks state across checks to detect transitions

## Installation

```bash
clawhub install testflight-monitor
```

Or clone from GitHub:
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/jon-xo/testflight-monitor-skill.git testflight-monitor
cd testflight-monitor
```

## Initial Setup

⚠️ **Important:** `config/batch-config.json` is user-specific and NOT shipped with defaults.

### 1. Initialize your config (one time)

```bash
cp config/batch-config.example.json config/batch-config.json
```

### 2. Add your TestFlight URLs

```bash
./testflight-monitor.sh add https://testflight.apple.com/join/YOUR_CODE_HERE
./testflight-monitor.sh add https://testflight.apple.com/join/ANOTHER_CODE
./testflight-monitor.sh list
```

### 3. Verify it works

```bash
./testflight-monitor.sh batch
# Output: SILENT: No status changes detected. (or alert if available)
```

## Quick Start

```bash
# Every hour check
openclaw cron add \
  --name "TestFlight Monitor" \
  --every 60m \
  --target isolated \
  --message "Run TestFlight batch check: ~/.openclaw/workspace/skills/testflight-monitor/testflight-monitor.sh batch. If output contains 'SILENT', reply NO_REPLY. Otherwise announce the findings."
```

## Quick Start

### 4. Set up automated monitoring (cron - optional)

```bash
# Check every hour, silent unless slots open
openclaw cron add \
  --name "TestFlight Monitor" \
  --every 60m \
  --target isolated \
  --message "Run: ~/.openclaw/workspace/skills/testflight-monitor/testflight-monitor.sh batch. If output contains 'SILENT', reply NO_REPLY. Otherwise announce the findings."
```

## Commands

### Core Commands

**lookup** `<code>`  
Look up app name by TestFlight code
```bash
./testflight-monitor.sh lookup BnjD4BEf
# Output: OpenClaw iOS
```

**check** `<url>`  
Check single TestFlight URL for availability
```bash
./testflight-monitor.sh check https://testflight.apple.com/join/BnjD4BEf
# Output: Status: full | App: OpenClaw iOS
```

**batch**  
Check all configured URLs (silent unless status changed)
```bash
./testflight-monitor.sh batch
# Output: SILENT: No status changes detected.
# Or: 🎉 **OpenClaw iOS** beta now has open slots! https://...
```

### Configuration Commands

**list**  
Show all monitored URLs with app names
```bash
./testflight-monitor.sh list
```

**add** `<url>`  
Add URL to batch monitoring
```bash
./testflight-monitor.sh add https://testflight.apple.com/join/Sq8bYSnJ
```

**remove** `<url>`  
Remove URL from batch monitoring
```bash
./testflight-monitor.sh remove https://testflight.apple.com/join/Sq8bYSnJ
```

**config**  
Show batch configuration (JSON)
```bash
./testflight-monitor.sh config
```

**state**  
Show current state (last known status for each app)
```bash
./testflight-monitor.sh state
```

### Maintenance Commands

**update-lookup**  
Refresh lookup table from awesome-testflight-link
```bash
./testflight-monitor.sh update-lookup
# Run weekly to keep app names current
```

## Architecture

```
testflight-monitor/
├── testflight-monitor.sh       # Main CLI (entry point)
├── lib/                         # Modular components
│   ├── lookup.sh               # Code → app name resolver
│   ├── check-single.sh         # Single URL checker
│   └── check-batch.sh          # Batch checker (silent mode)
├── config/                      # Configuration & state
│   ├── testflight-codes.json  # Community lookup table (~859 apps)
│   ├── custom-codes.json      # User overrides (private betas)
│   ├── batch-config.json      # Monitoring configuration
│   └── batch-state.json       # State tracking
├── tools/                       # Utilities
│   └── update-lookup.sh       # Refresh lookup table
└── SKILL.md                     # This file
```

## Configuration Files

### batch-config.json

**User-specific monitoring list.** Not shipped with defaults; created during initial setup.

Example structure:
```json
{
  "links": [
    "https://testflight.apple.com/join/YOUR_CODE_1",
    "https://testflight.apple.com/join/YOUR_CODE_2"
  ],
  "interval_minutes": 60
}
```

**Manage via CLI:**
```bash
./testflight-monitor.sh add <url>
./testflight-monitor.sh remove <url>
./testflight-monitor.sh list
```

**Or edit directly** (`config/batch-config.json`)

### custom-codes.json

Add private betas not in the community list:
```json
{
  "BnjD4BEf": "OpenClaw iOS",
  "YOUR_CODE": "Your App Name"
}
```

## Silent by Default

The batch checker only outputs when status changes:
- **full → available:** 🎉 Alert!
- **full → full:** Silent
- **available → full:** Silent (you already got in, or missed it)

This prevents notification spam while keeping you informed.

## Data Sources

**Lookup table:** [awesome-testflight-link](https://github.com/pluwen/awesome-testflight-link)  
- Community-maintained list of 800+ public TestFlight betas
- Updated via `update-lookup` command
- Recommended: refresh weekly

**Custom codes:** User-defined in `config/custom-codes.json`  
- For private betas not in the community list
- Higher priority than community list

## Dependencies

- `curl` - Fetch TestFlight pages
- `jq` - JSON processing
- `bash` - Shell scripting (macOS/Linux)

## Examples

### Monitor OpenClaw iOS Beta

```bash
cd ~/.openclaw/workspace/skills/testflight-monitor
./testflight-monitor.sh add https://testflight.apple.com/join/BnjD4BEf
./testflight-monitor.sh batch
```

### Check Multiple Apps

```bash
./testflight-monitor.sh add https://testflight.apple.com/join/Sq8bYSnJ  # Duolingo
./testflight-monitor.sh add https://testflight.apple.com/join/b9jMyOWt  # Reddit
./testflight-monitor.sh list
```

### Manual Status Check

```bash
./testflight-monitor.sh check https://testflight.apple.com/join/BnjD4BEf
```

## Contributing

**GitHub:** https://github.com/jon-xo/testflight-monitor-skill  
**Issues:** Report bugs or request features  
**Pull Requests:** Improvements welcome

## License

MIT License - see LICENSE file

## Credits

- Built for [OpenClaw](https://openclaw.ai)
- Lookup data from [awesome-testflight-link](https://github.com/pluwen/awesome-testflight-link)
- Inspired by the need to catch beta slots without notification spam

## Version History

**1.0.0** (2026-02-11)
- Initial release
- Unified architecture (lookup + single + batch in one skill)
- Silent-by-default batch monitoring
- CLI-based configuration
- Community lookup table integration

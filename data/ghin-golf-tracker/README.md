# GHIN Golf Tracker

[![ClawHub](https://img.shields.io/badge/ClawHub-ghin--golf--tracker-blue?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://clawhub.com/skills/ghin-golf-tracker)

OpenClaw skill for analyzing GHIN (Golf Handicap and Information Network) golf statistics and handicap tracking. **Analysis only** - reads local JSON file, no network access or credential handling. Data collection requires separate browser automation (see privacy notes below).

## Features

🏌️ **Comprehensive Golf Analytics**
- Current handicap index with trend analysis (improving/declining/stable based on last 5 revisions)
- Lifetime totals including round counts, best/worst scores
- Best 5 differentials with course and date information
- Most played courses with performance statistics

📊 **Detailed Performance Metrics**
- Year-by-year breakdown of rounds and scoring averages
- Par-specific scoring averages (Par 3, 4, 5) when available
- Performance statistics (GIR%, fairways hit%, average putts)
- Handicap range analysis with historical highs and lows

📈 **Multiple Output Formats**
- Human-readable text reports for quick review
- JSON output for programmatic processing and integration
- Detailed course-by-course performance analysis

🔒 **Privacy-First Design**
- No network connections or external API calls
- No credential storage or authentication required
- Local file processing only
- No data writes or persistent storage

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install ghin-golf-tracker
```

### Manual Installation

1. Clone this repository to your OpenClaw skills directory:
```bash
git clone https://github.com/pfrederiksen/ghin-golf-tracker.git
cd ghin-golf-tracker
```

2. The skill is ready to use - no additional dependencies required!

## Requirements

- Python 3.8+
- Standard library only (no external packages)
- GHIN data JSON file (collected separately by OpenClaw agent)

## Usage

### Basic Analysis

```bash
python3 scripts/ghin_stats.py /path/to/ghin-data.json
```

### JSON Output

```bash
python3 scripts/ghin_stats.py /path/to/ghin-data.json --format json
```

### Help

```bash
python3 scripts/ghin_stats.py --help
```

## Getting Your GHIN Data

**Data Collection Required:** GHIN does not offer a public API for score history. The data must be collected separately using browser automation or manual export before using this analysis skill.

**This skill does NOT perform data collection.** It only analyzes pre-existing JSON data files.

### Data Collection Options

1. **Manual Export** (Most Secure): Log into GHIN.com manually and export your data
2. **Browser Automation** (Privacy Risk): Use tools like browser-use, Selenium, or Playwright to scrape data
3. **OpenClaw Agent**: Let your OpenClaw agent handle the scraping using browser-use

⚠️ **Important:** Any automated data collection method will require transmitting your GHIN credentials to external services. This skill itself never handles credentials or performs network requests.

### Required Data Points

| Section | Data Needed |
|---------|-------------|
| Score History | Date, score + type, course, CR/slope, differential (per year) |
| Handicap Index | Current index, effective date |
| Revision History | Historical index values with revision dates |

**Note:** GHIN shows one year at a time — you'll need to cycle through each year filter to get complete lifetime data. Score types: `A` = adjusted, `C` = combined 9+9, `H` = home, `Ai` = imputed (exclude from stats).

## Expected Data Format

The script processes GHIN data in JSON format:

```json
{
  "handicap_index": 18.0,
  "lifetime_rounds": 83,
  "handicap_history": [
    {"date": "2026-02-02", "index": 18.0},
    {"date": "2026-01-15", "index": 17.8}
  ],
  "stats": {
    "par3_avg": 4.06,
    "par4_avg": 4.94,
    "par5_avg": 5.73,
    "gir_pct": 50,
    "fairways_pct": 65,
    "putts_avg": 31.2
  },
  "scores": [
    {
      "date": "2026-02-01",
      "score": "82A",
      "course": "Las Vegas Golf Club",
      "cr_slope": "68.0/117",
      "differential": 13.5
    }
  ]
}
```

## Sample Output

```
GHIN Golf Statistics Report
==============================

Current Handicap: 18.0
Trend (last 5): ↗️  Improving

LIFETIME TOTALS
---------------
Total Rounds: 83
Best Score: 72
Worst Score: 95

BEST DIFFERENTIALS
-----------------
1. 8.2 - Pebble Beach Golf Links (2025-08-15)
2. 9.1 - Augusta National Golf Club (2025-09-22)
3. 10.4 - St. Andrews Old Course (2025-07-10)

MOST PLAYED COURSES
-------------------
Las Vegas Golf Club: 12 rounds (avg 84.2)
Phoenix Country Club: 8 rounds (avg 86.1)
Scottsdale National: 6 rounds (avg 82.9)
```

## Data Collection

**Important Note**: This skill only processes already-collected GHIN data. It does NOT collect data from GHIN.com itself.

Data collection is handled separately by the OpenClaw agent using browser automation. This separation ensures:
- Better security (no credentials in this skill)
- Cleaner separation of concerns
- Offline analysis capabilities
- No rate limiting or blocking concerns

## What This Skill Does NOT Do

- ❌ No network access or web scraping
- ❌ No subprocess execution or shell commands  
- ❌ No file writes or data persistence
- ❌ No credential handling or authentication
- ❌ No external API calls or database connections

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 Bug reports: [GitHub Issues](https://github.com/pfrederiksen/ghin-golf-tracker/issues)
- 💬 Questions: [ClawHub Community](https://clawhub.com/community)
- 📧 Direct support: Open an issue on GitHub

---

Built with ❤️ for the OpenClaw community
# Arccos Golf Performance Analyzer

A comprehensive OpenClaw skill for analyzing Arccos Golf sensor data including club distances, strokes gained metrics, scoring patterns, and performance trends. **Analysis only** - reads local JSON file, no network access or credential handling. Data collection requires separate browser automation (see privacy notes below).

## 🏌️ Features

- **Strokes Gained Analysis**: Compare your performance to PGA Tour averages across all game categories
- **Club Distance Tracking**: Analyze average distances, shot counts, and consistency for each club
- **Scoring Patterns**: Understand your performance on different par values and score distribution
- **Putting Performance**: Track putts per round, GIR putting, and distance-based metrics
- **Approach Shot Analysis**: Analyze greens in regulation, miss patterns, and terrain performance
- **Round Tracking**: Monitor recent performance trends and course-specific analysis
- **Multiple Output Formats**: Human-readable reports and machine-readable JSON

## 🚀 Quick Start

### Installation

```bash
# Via ClawHub
clawhub install arccos-golf

# Or clone this repository
git clone https://github.com/pfrederiksen/arccos-golf.git
cd arccos-golf
```

### Basic Usage

```bash
# Full performance report
python3 scripts/arccos_golf.py data/arccos-data.json

# Summary statistics only
python3 scripts/arccos_golf.py data/arccos-data.json --summary

# Strokes gained analysis
python3 scripts/arccos_golf.py data/arccos-data.json --strokes-gained

# Club distance analysis
python3 scripts/arccos_golf.py data/arccos-data.json --clubs iron

# JSON output for further processing
python3 scripts/arccos_golf.py data/arccos-data.json --format json
```

## 📊 Example Output

```
🏌️ Arccos Golf Performance Report
========================================
Golfer: Paul Frederiksen
Total Shots Tracked: 7,057
Total Rounds: 75
Longest Drive: 308 yards

📊 STROKES GAINED ANALYSIS
------------------------------
Overall: -12.0
Approach: -5.0
Driving: -3.3
Short Game: -2.7
Putting: -1.1

🎯 Priority Areas:
  1. Approach
  2. Driving  
  3. Short Game

🏌️ CLUB DISTANCES
--------------------
Driver: 234 yds avg (533 shots, longest: 281)
3 Wood: 204 yds avg (57 shots, longest: 320)
7 Iron: 140 yds avg (43 shots, longest: 168)
```

## 📋 Getting Your Arccos Data

**Data Collection Required:** Arccos Golf does not offer a public API, so data must be collected separately from **https://dashboard.arccosgolf.com** before using this analysis skill.

**This skill does NOT perform data collection.** It only analyzes pre-existing JSON data files.

### Data Collection Options

1. **Manual Export** (Most Secure): Log into Arccos dashboard manually and export your data
2. **Browser Automation** (Privacy Risk): Use tools like browser-use, Selenium, or Playwright to scrape data
3. **OpenClaw Agent**: Let your OpenClaw agent handle the scraping using browser-use

⚠️ **Important:** Any automated data collection method will require transmitting your Arccos credentials to external services. This skill itself never handles credentials or performs network requests.

### Required Data Sections

The Arccos dashboard has two versions — collect data from both for complete analysis:

| Section | Dashboard | Data Needed |
|---------|-----------|-------------|
| SG Breakdown | New (`/stats/overall`) | Driving, Approach, Short Game, Putting |
| Driving | New (`/stats/driving`) | Fairways %, distance, SG by hole length |
| Approach | New (`/stats/approach`) | GIR %, miss patterns, SG by distance |
| Short Game | New (`/stats/short`) | Up & Down %, sand saves |
| Putting | New (`/stats/putting`) | Putts/hole, SG by putt length |
| Scoring Mix | v1 (`/overall performance`) | Birdie/par/bogey/double+ % |
| Club Distances | v1 (`/clubs` → Distance) | Average distance per club |
| Round History | v1 (`/rounds`) | Scores + per-category breakdown |

See [SKILL.md](SKILL.md) for the complete expected JSON format.

## 🔒 Security & Privacy

This skill is designed with security in mind:

- ✅ **Read-only**: Only reads provided data files, never modifies anything
- ✅ **No network access**: All processing done locally
- ✅ **No subprocess calls**: Uses only Python standard library
- ✅ **No credentials**: Does not handle or store authentication data
- ✅ **Standard library only**: No external dependencies

Data collection from Arccos must be performed separately using browser automation tools.

## 📖 Available Commands

| Command | Description |
|---------|-------------|
| `--summary` | Show basic statistics summary |
| `--strokes-gained` | Analyze strokes gained performance |
| `--clubs [type]` | Show club distances (optionally filtered) |
| `--format json` | Output as JSON instead of text |
| `--recent-rounds N` | Show N most recent rounds |

## 🎯 Golf Metrics Explained

### Strokes Gained
Measures your performance relative to PGA Tour averages:
- **Positive values**: Better than tour average
- **Negative values**: Worse than tour average
- **Overall**: Combined performance across all categories

### Categories
- **Driving**: Tee shots to landing position
- **Approach**: Shots to the green from fairway/rough
- **Short Game**: Chipping and pitching around the green
- **Putting**: Performance on the green

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Related Projects

- [OpenClaw](https://github.com/openclaw/openclaw) - AI-powered CLI assistant
- [GHIN Golf Tracker](https://github.com/pfrederiksen/ghin-golf-tracker) - GHIN handicap analysis skill

---

**Note**: This skill analyzes pre-collected Arccos data. See the [Data Collection Guide](#-getting-your-arccos-data) above for how to scrape your stats from `dashboard.arccosgolf.com` using browser-use.
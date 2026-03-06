# Aerobase OpenClaw Skill

Search, score, and compare flights with jetlag impact analysis for healthier travel.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue)](https://pypi.org/project/aerobase/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What It Does

This OpenClaw skill integrates the Aerobase Flight API into any OpenClaw-compatible AI agent. It exposes tools that agents can call directly:

- **Search Flights** - Find flights with jetlag scoring
- **Score Flights** - Get detailed jetlag analysis
- **Compare Flights** - Compare multiple flight options
- **Recovery Plans** - Generate personalized jetlag recovery plans
- **Travel Deals** - Find jetlag-friendly deals
- **Airport Info** - Get airport facilities and lounges
- **Hotel Search** - Find jetlag-friendly hotels
- **Itinerary Analysis** - Analyze multi-leg trips

## Why Use Aerobase?

- **Jetlag Scoring** - Every flight gets a 0-100 score (higher = less jetlag)
- **Recovery Estimates** - Know how many days you'll need to recover
- **Healthier Travel** - Find flights that minimize jetlag impact
- **Recovery Plans** - Get personalized pre/post-flight recommendations

## Installation

### Prerequisites

- Python 3.9+
- Aerobase API key from https://aerobase.app/connect

### Setup

```bash
# Clone this repo
git clone https://github.com/aerobase/aerobase-openclaw-skill.git
cd aerobase-openclaw-skill

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.dist .env
# Edit .env with your API key
```

## OpenClaw Integration

This skill ships with a `SKILL.md` file that defines all tools in the OpenClaw skill format. OpenClaw-compatible agents automatically discover and invoke the tools.

## CLI Usage

```bash
# Set your API key
export AEROBASE_API_KEY="ak_xxxxxxxx"

# Search flights with jetlag scoring
python tools/aerobase.py search --from LAX --to NRT --date 2026-04-15

# Score a flight
python tools/aerobase.py score \
  --from LAX --to NRT \
  --departure "2026-04-15T08:00:00-07:00" \
  --arrival "2026-04-16T14:30:00+09:00"

# Get travel deals
python tools/aerobase.py deals --from LAX --max-price 600

# Generate recovery plan
python tools/aerobase.py recovery \
  --from LAX --to NRT \
  --departure "2026-04-15T08:00:00-07:00" \
  --arrival "2026-04-16T14:30:00+09:00"

# Get airport info
python tools/aerobase.py airport JFK

# Search hotels
python tools/aerobase.py hotels --airport NRT --jetlag-friendly

# Search lounges
python tools/aerobase.py lounges --airport LHR
```

### Output Formats

```bash
# Default: Human-readable output
python tools/aerobase.py search --from LAX --to NRT --date 2026-04-15

# JSON output for automation
python tools/aerobase.py search --from LAX --to NRT --date 2026-04-15 --json
```

## Jetlag Score Guide

| Score | Tier | Recovery |
|-------|------|----------|
| 80-100 | Excellent | 0-2 days |
| 60-79 | Good | 2-3 days |
| 40-59 | Moderate | 3-5 days |
| 20-39 | Poor | 5-7 days |
| 0-19 | Severe | 7+ days |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AEROBASE_API_KEY` | Yes | Your API key from aerobase.app/connect |

## API Reference

See [SKILL.md](SKILL.md) for complete API documentation.

## Rate Limits

| Tier | Daily Calls |
|------|-------------|
| Free | 100 |
| Pro | 1,000 |
| Concierge | 10,000 |
| API | Unlimited |

## Related Resources

- [Aerobase API Documentation](https://aerobase.readme.io)
- [Aerobase Dashboard](https://aerobase.app)
- [OpenClaw Documentation](https://docs.openclaw.ai)

## License

MIT License - see [LICENSE](LICENSE)

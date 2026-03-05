# Race Finder

Find upcoming races — running, trail, triathlon, cycling, swimming, and obstacle courses. Search by location, distance, sport, and date.

Powered by **[RaceFinder](https://racefinder.net)**

## Quick Start

Try it right now — no API key needed:

```bash
curl "https://api.racefinder.net/api/v1/races?city=Austin&state=TX"
```

---

## Two Ways to Use This

### 1. Claude Code / OpenClaw Skill (Recommended)

The simplest option. Claude reads the skill file and calls the API directly — no binary, no MCP protocol, just HTTP. Also available on [OpenClaw](https://openclaw.com).

```bash
# Clone into your skills directory
git clone https://github.com/nftechie/race-finder.git ~/.claude/skills/race-finder
```

Now in Claude Code, you can say things like:
- "Find me a half marathon in Austin this spring"
- "What trail races are happening in Colorado this summer?"
- "Find 5Ks near zipcode 78701 within 25 miles"
- "Search for triathlons in California"
- "What marathons are coming up in New York?"

Claude reads `SKILL.md` and knows how to call every endpoint.

### 2. Direct API

Use the API from scripts, automations, or any HTTP client. See [SKILL.md](SKILL.md) for complete endpoint documentation with curl examples.

```bash
# Search races by city and state
curl "https://api.racefinder.net/api/v1/races?city=Denver&state=CO&sport=running"

# Find marathons near a zipcode
curl "https://api.racefinder.net/api/v1/races?zipcode=78701&radius=50&distance=marathon"

# Trail races in Colorado this summer
curl "https://api.racefinder.net/api/v1/races?state=CO&sport=trail&start_date=2026-06-01&end_date=2026-08-31"
```

No authentication required. Completely open API.

## License

MIT

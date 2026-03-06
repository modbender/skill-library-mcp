# Astrology API Skill

[![Get API Key](https://img.shields.io/badge/Get%20API%20Key-6C63FF?style=for-the-badge&logoColor=white)](https://dashboard.astrology-api.io/)
[![API Documentation](https://img.shields.io/badge/API%20Documentation-FCC624?style=for-the-badge&logoColor=black)](https://api.astrology-api.io/rapidoc)
[![Postman Collection](https://img.shields.io/badge/Postman%20Collection-FF6C37?style=for-the-badge&logo=postman&logoColor=white)](https://api.astrology-api.io/best-astrology-api-postman.json)


An [Agent Skills](https://agentskills.io/) skill for the [Astrology API](https://api.astrology-api.io/) — works across OpenClaw, Claude Code, OpenAI Codex, GitHub Copilot, Cursor, and other compatible platforms.

## What It Does

Provides AI agents with access to professional astrological calculations:

- **Charts** — natal, synastry, composite, transit, solar/lunar return, progressions, directions
- **Analysis** — natal reports, career, psychological, karmic, spiritual, compatibility
- **Horoscopes** — daily/weekly/monthly/yearly by sign or personalized
- **Tarot** — card draws, single/three-card/Celtic cross spreads, birth cards
- **Numerology** — core numbers, comprehensive readings, compatibility
- **Lunar** — phases, void of course, mansions, events, calendar
- **Vedic** — birth details, kundli matching, doshas, dashas, panchang
- **Chinese** — BaZi, ming gua, compatibility, luck pillars
- **Human Design** — bodygraph, type, compatibility, transits
- **Kabbalah** — tree of life, birth angels, tikkun, gematria
- **Astrocartography** — maps, power zones, relocation analysis
- **And more** — eclipses, fixed stars, palmistry, horary, feng shui

240+ API endpoints powered by Swiss Ephemeris.

## Prerequisites

- `curl` installed (pre-installed on macOS/Linux)
- API key from [dashboard.astrology-api.io](https://dashboard.astrology-api.io/)

```bash
export ASTROLOGY_API_KEY="your_token_here"
```

## Installation

### From ClawHub (recommended)

```bash
clawhub install astroapi-skill
```

### Manual — OpenClaw

```bash
git clone https://github.com/astro-api/astroapi-skill ~/skills/astroapi-skill
ln -s ~/skills/astroapi-skill ~/.openclaw/skills/astroapi-skill
```

### Manual — Claude Code

```bash
git clone https://github.com/astro-api/astroapi-skill ~/skills/astroapi-skill
ln -s ~/skills/astroapi-skill ~/.claude/skills/astroapi-skill
```

### Manual — OpenAI Codex

```bash
git clone https://github.com/astro-api/astroapi-skill ~/skills/astroapi-skill
ln -s ~/skills/astroapi-skill ~/.codex/skills/astroapi-skill
```

### Other Agent Skills Platforms

Symlink or copy the `astroapi-skill` directory to your platform's skills directory.

## Project Structure

```
astroapi-skill/
├── SKILL.md                          # Skill definition (frontmatter + instructions)
├── README.md                         # This file (for humans / GitHub)
├── scripts/
│   └── astro-api.sh                  # curl wrapper with auth
├── references/
│   ├── api-endpoints.md              # Full 240+ endpoint reference
│   └── use-cases.md                  # User intent → endpoint mapping
├── assets/
│   └── openapi-astrology.json        # Canonical OpenAPI 3.1.0 spec
├── chatgpt/                          # ChatGPT GPT Actions setup
│   ├── openapi-gpt-actions.json      # Trimmed OpenAPI spec (32 endpoints)
│   ├── instructions.md               # GPT system prompt
│   └── README.md                     # Setup guide
├── .clawhubignore                    # Files excluded from ClawHub publish
└── .env.example
```

## Quick Test

```bash
# Set your API key
export ASTROLOGY_API_KEY="your_token_here"

# Get current sky data
bash scripts/astro-api.sh GET /api/v3/data/now

# Generate a natal chart
bash scripts/astro-api.sh POST /api/v3/charts/natal '{
  "subject": {
    "name": "Test",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic", "language": "EN"}
}'
```

## Publishing to ClawHub

### First-time setup

```bash
npm i -g clawhub
clawhub login
```

### Publish

```bash
clawhub publish . --slug astroapi-skill --name "Astrology API" \
  --version 1.0.0 --tags latest --changelog "Initial release"
```

### Update an existing version

Bump the `version` field in `SKILL.md` frontmatter, then:

```bash
clawhub publish . --slug astroapi-skill \
  --version 1.1.0 --changelog "Description of changes"
```

### Verify

```bash
clawhub inspect astroapi-skill
```

> Files listed in `.clawhubignore` (`chatgpt/`, `.env.example`, `.git/`) are excluded from the published bundle. Only `SKILL.md`, `scripts/`, and `references/` are shipped to ClawHub.

## ChatGPT Integration

For ChatGPT GPT Actions (separate from Agent Skills), see [chatgpt/README.md](chatgpt/README.md).

## API Documentation

- [Full API docs](https://api.astrology-api.io/rapidoc)
- [OpenAPI spec](https://api.astrology-api.io/api/v3/openapi.json)
- [Developer dashboard](https://dashboard.astrology-api.io/)

## License

MIT

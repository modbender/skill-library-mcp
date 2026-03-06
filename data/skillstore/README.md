# SkillStore - Intelligent OpenClaw Skill Manager

Smart skill search with semantic matching and relevance threshold filtering.

## Features

- **Semantic Matching** - Analyzes actual skill functionality, not just keywords
- **Relevance Threshold** - Only shows skills with 30%+ match score
- **Multi-source Search** - Known skills, local skills, GitHub repos
- **Scoring System** - Shows match percentage with visual bar

## How It Works

### Matching Algorithm

1. **Tokenization** - Breaks query into keywords
2. **Jaccard Similarity** - Measures word overlap
3. **Keyword Boost** - Extra points for exact keyword matches
4. **Name Boost** - Extra points for name matches
5. **Threshold Filter** - Only shows scores >= 30%

### Match Threshold

```
Score >= 50% = Strong match (green bar)
Score >= 30% = Weak match (yellow bar)
Score < 30% = Not shown
```

## Quick Start

```bash
# Search with threshold filtering
skillstore smart home
skillstore weather forecast
skillstore email gmail

# List / Known
skillstore list
skillstore known
skillstore create my-skill
```

## Search Example

```
$ skillstore smart home

Search Results for "smart home"
Match threshold: 30% | Found: 3

1. [KNOWN] homeassistant ████████░░ 85% (STRONG)
   Control smart home devices like lights switches...
2. [LOCAL] homeassistant ███████░░░ 78%
   Home Assistant skill for OpenClaw
3. [GIT] openclaw-homeassistant ██████░░░░ 62%
   Control smart home devices

Enter number to install or 'n' to create new
```

## Why Threshold?

Prevents irrelevant results. A skill named "weather" won't show up for "email" just because it has some matching letters.

## Commands

| Command | Description |
|---------|-------------|
| `skillstore <query>` | Search with threshold |
| `skillstore list` | List installed |
| `skillstore known` | Show all known skills |
| `skillstore create <name>` | New skill |

## Configuration

- **Threshold**: 30% (configurable in code)
- **Search Sources**: Known → Local → GitHub
- **Deduplication**: Keeps highest score duplicate

## Files

```
skillstore/
├── SKILL.md       # OpenClaw docs
├── README.md      # This file
├── main.js        # CLI with matching
└── config.json   # Install history
```

## License

MIT

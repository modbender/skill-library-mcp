---
name: SkillStore - OpenClaw Skill Manager
description: Search, install, and create OpenClaw skills with intelligent matching.
---

# SkillStore - OpenClaw Skill Manager

Search, install, and create OpenClaw skills with intelligent matching.

## Skill Metadata

- **Name**: skillstore
- **Type**: OpenClaw Skill
- **Purpose**: Search existing skills, install from GitHub, or create new ones

## Setup Commands

No setup required. Works out of the box.

## Usage Commands

### Search & Install

```bash
# Search for a skill (applies 30% threshold)
skillstore <query>

# Examples:
skillstore home assistant
skillstore weather
skillstore smart home
skillstore email gmail
skillstore github
```

### List & Show

```bash
# List installed skills
skillstore list

# Show all known skills (20 built-in)
skillstore known
```

### Create New

```bash
# Create new skill with templates
skillstore create <name>
skillstore new <name>

# Examples:
skillstore create my-awesome-skill
skillstore new weather-widget
```

## How Search Works

### Matching Algorithm

1. **Tokenize** - Split query into keywords
2. **Calculate** - Jaccard similarity + keyword boost
3. **Filter** - Remove results below 30% threshold
4. **Rank** - Sort by relevance score
5. **Display** - Show with visual score bar

### Match Score

```
Score >= 50% = Strong match (green bar)
Score >= 30% = Weak match (yellow bar)  
Score < 30% = Not shown (filtered)
```

### Search Sources (in order)

1. **Known Skills** - Built-in database of 20 skills
2. **Local Skills** - Skills in ~/.openclaw/workspace/skills/
3. **GitHub** - Search openclaw repositories

## Interaction Flow

```
1. User runs: skillstore home assistant
2. System searches all 3 sources
3. System filters by threshold
4. Results shown with scores:

   1. [KNOWN] homeassistant ████████░░ 85%
      Control smart home devices...
   2. [LOCAL] homeassistant ███████░░░ 78%
   3. [GIT] openclaw-homeassistant ██████░░░░ 62%

5. User chooses:
   - Enter number → Install from GitHub
   - n → Create new skill
   - q → Quit
```

## Known Skills Database

Built-in skills (searchable):

| Skill | Description |
|-------|-------------|
| homeassistant | Smart home control (HA API) |
| gog | Google Workspace (Gmail, Calendar, Drive) |
| weather | Weather forecasts |
| github | GitHub CLI integration |
| himalaya | Email via IMAP/SMTP |
| obsidian | Obsidian vault integration |
| sonoscli | Sonos speaker control |
| blucli | BluOS speaker control |
| eightctl | Eight Sleep pod control |
| ordercli | Food delivery orders |
| blogwatcher | RSS feed monitoring |
| gifgrep | GIF search/download |
| video-frames | Video frame extraction |
| youtube-summarizer | YouTube transcript summary |
| ga4 | Google Analytics 4 |
| gsc | Google Search Console |
| wacli | WhatsApp messaging |
| browser | Browser automation |
| healthcheck | Security hardening |

## Error Handling

- No results above threshold: Offer to create new skill
- GitHub search fails: Fall back to local/known
- Install fails: Show error with reason

## Related Skills

- homeassistant
- openclaw-migrate
- skill-templates (legacy, use skillstore)

## Files

```
skillstore/
├── SKILL.md       # This file
├── README.md      # User docs
├── main.js        # CLI with intelligent search
└── config.json    # Install history
```

# Visual Prompt Engine

Generate diverse, non-repetitive image prompts powered by real visual references from Dribbble.

AI agents tend to reuse the same visual patterns when writing image prompts. This skill breaks that cycle by grounding prompts in real, trending design work collected from Dribbble.

## How It Works

```
Dribbble Scraper → Style Cards → Prompt Generator → Quality Reviewer → Final Prompt
```

1. **Scrape** trending designs from Dribbble (RSS or HTML)
2. **Analyze** each design into a structured style card (colors, composition, mood, textures, lighting)
3. **Generate** image prompts using 12+ distinct patterns to prevent repetition
4. **Review** prompts against history to ensure diversity

## Installation

### ClawHub (OpenClaw)

```bash
clawhub install visual-prompt-engine
```

### OpenClaw (Manual)

Copy the skill folder to your OpenClaw skills directory:

```bash
cp -r visual-prompt-engine ~/.openclaw/skills/
```

### Codex CLI

Copy the skill folder to your Codex skills directory:

```bash
cp -r visual-prompt-engine ~/.codex/skills/
```

### Other AI Agent Tools

This skill follows the standard AgentSkill format (SKILL.md + scripts + references). Copy the folder to wherever your agent tool loads skills from. The `SKILL.md` frontmatter provides the trigger description; the body provides the workflow instructions.

### GitHub

```bash
git clone https://github.com/Abdullah4AI/visual-prompt-engine.git
```

## Quick Start

### 1. Install Dependencies (Optional)

The scraper works with Python standard library via RSS. For HTML scraping:

```bash
pip install requests beautifulsoup4
```

### 2. Collect Visual References

```bash
python3 scripts/scrape_dribbble.py --output data/references.json --count 20
```

### 3. Build Style Cards

```bash
python3 scripts/style_card.py build --input data/references.json --output data/style_cards.json
```

### 4. Ask Your Agent

Tell your AI agent: "Generate an image prompt for [your goal]" and it will use the style cards and prompt patterns to create a unique, design-informed prompt.

## Skill Structure

```
visual-prompt-engine/
├── SKILL.md                          # Agent instructions (trigger + workflow)
├── README.md                         # This file (human documentation)
├── scripts/
│   ├── scrape_dribbble.py            # Collect designs from Dribbble
│   └── style_card.py                 # Build and manage style cards
├── references/
│   ├── prompt-patterns.md            # 12+ diverse prompt structures
│   ├── visual-vocabulary.md          # Precise design terminology
│   └── style-card-schema.md          # Style card JSON schema
└── data/                             # Created at runtime
    ├── references.json               # Raw scrape results
    ├── style_cards.json              # Processed style cards
    └── prompt_history.json           # Prompt dedup history
```

## Scripts

### scrape_dribbble.py

```
Usage: scrape_dribbble.py [--output PATH] [--count N] [--feed popular|recent|animated] [--method rss|html] [--append]

Options:
  --output, -o    Output JSON path (default: data/references.json)
  --count, -c     Number of designs to fetch (default: 20)
  --feed          RSS feed type: popular, recent, animated (default: popular)
  --method        Scraping method: rss (no deps) or html (needs requests+bs4)
  --append        Append to existing file instead of overwriting
```

### style_card.py

```
Commands:
  build    Build style cards from references
  select   Select relevant cards for a prompt goal
  prompt   Generate AI analysis prompt for a card
  stats    Show style card statistics

Examples:
  style_card.py build --input data/references.json --output data/style_cards.json
  style_card.py select --goal "futuristic dashboard" --count 3
  style_card.py prompt --id sc_0001
  style_card.py stats
```

## Automation

Set up a daily cron to keep references fresh:

```bash
# Daily refresh
python3 scripts/scrape_dribbble.py --output data/references.json --count 20 --append
python3 scripts/style_card.py build --input data/references.json --output data/style_cards.json --append
```

## Compatibility

- **Python**: 3.9+
- **Dependencies**: Standard library only (optional: requests, beautifulsoup4)
- **Agent tools**: Any tool supporting the AgentSkill format (OpenClaw, Codex CLI, or custom)
- **Platforms**: macOS, Linux, Windows

## License

MIT

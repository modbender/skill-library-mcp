# TechNews Skill for OpenClaw

A OpenClaw skill that fetches top tech stories from TechMeme, summarizes linked articles, and highlights social media reactions.

## Features

- 📰 Scrapes top stories from TechMeme.com
- 📝 AI-generated summaries of article content
- 💬 Hacker News integration (shows points and comments)
- 🔥 Extracts notable quotes and "spicy" takes
- ⚡ Parallel fetching for speed

## Installation

```bash
# Clone or add to your OpenClaw skills
cd /path/to/openclaw/skills
git clone https://github.com/yourusername/technews-skill.git

# Install dependencies
pip install requests beautifulsoup4
```

## Usage

In OpenClaw, simply type:

```
/technews
```

This will fetch the top 10 stories and present them with:
- Story titles and links
- AI-generated summaries
- Hacker News engagement data
- Notable quotes and reactions

## Architecture

```
technews/
├── SKILL.md              # OpenClaw skill definition
├── README.md            # This file
├── scripts/
│   ├── techmeme_scraper.py    # Fetches stories from TechMeme
│   ├── article_fetcher.py     # Parallel article fetching
│   ├── social_reactions.py    # HN and Twitter integration
│   └── technews.py            # Main orchestrator
```

## Extending

This skill is designed to be extended to other sources:

- `/hn` - Hacker News top stories
- `/reddit` - Reddit tech threads
- `/verge` - The Verge coverage
- `/wired` - WIRED articles

Add new sources by creating additional scraper modules and updating the orchestrator.

## Requirements

- Python 3.9+
- `requests`
- `beautifulsoup4`
- OpenClaw (any recent version)

## License

MIT

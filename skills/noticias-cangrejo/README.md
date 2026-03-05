# NoticiasCangrejo

NoticiasCangrejo is an OpenClaw skill that fetches news from GNews (`gnews.io`) for any topic and outputs a Markdown summary of the top articles.

## Features

- Works with any topic provided by the user
- Uses GNews Search API
- Pulls up to 20 articles and returns the 15 most relevant
- Outputs clean Markdown with date, greeting, titles, and URLs
- Includes dashboard API key metadata for ClawHub/OpenClaw publishing
- No third-party Python packages required

## Installation

Install the skill from ClawHub or from its repository path. The packaged skill uses only:

- `SKILL.md`
- `README.md`
- `requirements.txt`
- `_meta.json`
- `scripts/fetch_news.py`

## Environment Variable Setup

Set your GNews API key:

```bash
export GNEWS_API_KEY="your_api_key_here"
```

Do not commit real API keys to source control.

## Canonical Run Command

The canonical command is defined in `_meta.json` (`run`):

```bash
python3 scripts/fetch_news.py "<topic>"
```

## CLI Usage

Basic:

```bash
python3 scripts/fetch_news.py "space exploration"
```

Custom language and result size:

```bash
python3 scripts/fetch_news.py "renewable energy" --lang en --max-articles 20
```

Save summary to a file:

```bash
python3 scripts/fetch_news.py "cybersecurity" --output ./cybersecurity-news.md
```

## OpenClaw Usage

When this skill is installed, ask for a topic summary, for example:

- "Usa noticias-cangrejo para Terpel Colombia"
- "Resume las noticias sobre Formula 1"

The skill reads `GNEWS_API_KEY` from dashboard/environment configuration and returns Markdown output.

## Publishing Notes (ClawHub)

- Skill folder name is slug-friendly: `noticias-cangrejo`
- `_meta.json` defines explicit `run` behavior for packaged installs
- No hardcoded API credentials are included
- Runtime is dependency-free (standard library only)

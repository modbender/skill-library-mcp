---
name: aeo-prompt-question-finder
description: Find question-based Google Autocomplete suggestions for any topic. Prepends question modifiers (what, how, why) to a seed topic and returns real autocomplete suggestions — useful for AEO prompt research, content ideation, and understanding what people ask about a topic. Use when the user wants to discover questions people search for, find content angles, or do keyword/prompt research for a topic.
---

# Prompt Question Finder

Discover what questions people ask about a topic by querying Google Autocomplete with question modifiers.

## Usage

Run the script from the skill directory:

```bash
python3 scripts/find_questions.py "travel itinerary"
```

### Options

- `--modifiers what how why should` — override default modifiers (default: what how why should can does is when where which will are do)
- `--delay 0.5` — seconds between requests (use 0.5–1.0 when running many topics in batch)
- `--json` — output as JSON for programmatic use
- `--volume` — fetch avg monthly search volume via DataForSEO (reads creds from macOS Keychain: `dataforseo-login` / `dataforseo-password`, or env vars `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`)
- `--location 2840` — DataForSEO location code (default: 2840 = US)
- `--lang en` — language code for volume lookup (default: en)

### Examples

```bash
# Default modifiers (what, how, why)
python3 scripts/find_questions.py "protein powder"

# Custom modifiers
python3 scripts/find_questions.py "travel itinerary" --modifiers what how why should when

# JSON output
python3 scripts/find_questions.py "travel itinerary" --json
```

## Rate Limits

Google Autocomplete is an unofficial endpoint. Single-topic runs (10 requests) are safe. When running multiple topics in batch or parallel, always use `--delay 0.5` or higher to avoid temporary IP blocks.

## How It Works

For each modifier, the script queries `https://suggestqueries.google.com/complete/search` with `"{modifier} {topic}"` and returns the autocomplete suggestions. No API key required.

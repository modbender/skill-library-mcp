# feed-to-md Skill

This skill converts RSS/Atom feed URLs into Markdown using a bundled local script.

## Files

- `SKILL.md`: skill definition and usage instructions
- `scripts/feed_to_md.py`: secure feed-to-markdown converter

## Requirements

- Python 3

## Usage

```bash
python3 scripts/feed_to_md.py "https://example.com/feed.xml"
python3 scripts/feed_to_md.py "https://example.com/feed.xml" --limit 5
python3 scripts/feed_to_md.py "https://example.com/feed.xml" --output result.md
```

## Regression Test

```bash
bash scripts/test_feed_to_md.sh
```

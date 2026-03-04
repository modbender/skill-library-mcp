# 🐾 CRM Intelligence — Smart Contact Filtering

> by Odin's Eye Enterprises — Ancient Wisdom. Modern Intelligence.

2-stage Berman-style filtering and contact scoring for your personal CRM. Learns what matters to you.

## What It Does

1. **Stage 1** — Quick keyword/pattern filter (fast, cheap)
2. **Stage 2** — AI-powered relevance scoring (deeper analysis)
3. **Learns** from your feedback to improve over time

## Trigger Phrases

- "filter my contacts"
- "score this lead"
- "who should I reach out to"
- "CRM filter"
- "prioritize contacts"

## Usage

```bash
# Filter contacts from a CSV/JSON
python crm_filter.py filter contacts.json

# Score a specific contact
python crm_filter.py score "John Doe" --context "met at conference"

# Show learning stats
python crm_filter.py stats
```

## Files

- `crm_filter.py` — main filtering engine
- `learning.json` — learned preferences (auto-updated)

## Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable (for Stage 2 AI scoring)

## For Agents

Run from the skill directory. Filter results come as JSON on stdout.

```bash
python crm_filter.py filter contacts.json --top 10
```

<!-- 🐾 Huginn watches, Muninn remembers -->

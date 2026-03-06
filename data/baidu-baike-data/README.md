# Baidu Baike Skill

Query Baidu Baike encyclopedia entries from OpenClaw.

## Purpose

This skill enables two main scenarios:

1. **Direct search by keyword** - Get the default matching entry for a term
2. **Homonym resolution** - When multiple entries share the same name, list them and let user select specific one

## Quick Start

```bash
export BAIDU_API_KEY="your_api_key"

# Scenario 1: Direct search
python3 scripts/baidu_baike.py --search_type=lemmaTitle --search_key="Andy Lau"

# Scenario 2: List homonyms
python3 scripts/baidu_baike.py --search_type=lemmaList --search_key="Liu Dehua" --top_k=5

# Then query specific entry by ID
python3 scripts/baidu_baike.py --search_type=lemmaId --search_key="114923"
```

## API

- `LemmaList`: List entries with same title (for homonym resolution)
- `LemmaContent`: Get detailed entry content by title or ID

## Workflow for OpenClaw Agent

1. Extract noun from user query
2. If term likely has homonyms (common names, ambiguous terms), call `LemmaList` first
3. Show user the list with IDs and descriptions
4. User selects entry ID (or agent uses default entry)
5. Call `LemmaContent` with selected ID
6. Return structured entry data to user

## Response Format

Returns JSON with:
- `lemma_id`: Entry ID
- `lemma_title`: Entry title
- `lemma_desc`: Short description
- `url`: Baike page URL
- `abstract_plain`: Plain text summary
- `card`: Information cards (attributes)
- `albums`: Image albums
- `pic_url`: Main image URL
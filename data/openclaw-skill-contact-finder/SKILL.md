---
name: contact-finder
description: Find professional emails and contacts from a name + company/domain using SerpAPI + OpenAI GPT-4o-mini.
license: MIT
metadata:
  author: Jack2
  version: 1.0.0
  tags: prospecting, email, contacts, serpapi, openai, lead-generation
---

# contact-finder

Find professional emails and contacts from a name + company/domain. Combines SerpAPI (Google Search) and OpenAI GPT-4o-mini to search, extract, and validate contacts.

## Usage

```bash
python3 scripts/find_contacts.py --company "Acme Corp" --domain "acme.com" --name "John Doe"
python3 scripts/find_contacts.py --company "Stripe" --domain "stripe.com"
python3 scripts/find_contacts.py --company "OpenAI" --domain "openai.com" --name "Sam Altman" --output json
```

## Options

| Flag | Description | Required |
|------|-------------|----------|
| `--company` | Company name | ✅ |
| `--domain` | Email domain (e.g. acme.com) | ✅ |
| `--name` | Full name to search (optional) | ❌ |
| `--output` | Output format: `table` (default) or `json` | ❌ |

## Output

Returns a list of contacts with:
- **email** — Found or guessed email address
- **linkedin** — LinkedIn profile URL (if found)
- **title** — Job title (if found)
- **confidence** — `high` / `medium` / `low`

## Setup

```bash
pip3 install openai requests
```

Set credentials in environment or edit `scripts/find_contacts.py`:
- `SERPAPI_KEY`
- `OPENAI_API_KEY`

## How It Works

1. Search Google via SerpAPI: `"name" site:domain email`, LinkedIn profiles
2. Generate common email format guesses (firstname@, f.lastname@, firstname.lastname@...)
3. Use GPT-4o-mini to extract/validate emails from search snippets
4. Score confidence based on source (direct find = high, pattern guess = low/medium)

## References

See `references/patterns.md` for email pattern documentation and sources.

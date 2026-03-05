---
name: swiss-phone-directory
description: "Swiss phone directory lookup via search.ch API. Search for businesses, people, or reverse-lookup phone numbers. Use when: (1) finding contact details for Swiss companies or people, (2) looking up addresses by name or phone number, (3) reverse phone number lookup, (4) finding business categories. Requires SEARCHCH_API_KEY."
metadata:
  openclaw:
    requires:
      env:
        - SEARCHCH_API_KEY
---

# Swiss Phone Directory Skill

Search the Swiss phone directory (search.ch) for businesses, people, and phone numbers.

## Quick Start

```bash
# Search for a business
python3 scripts/searchch.py search "Migros" --location "Zürich"

# Search for a person
python3 scripts/searchch.py search "Müller Hans" --type person

# Reverse phone number lookup
python3 scripts/searchch.py search "+41442345678"

# Business-only search
python3 scripts/searchch.py search "Restaurant" --location "Bern" --type business --limit 5
```

## Commands

### search
Search for businesses, people, or phone numbers.

```bash
python3 scripts/searchch.py search <query> [options]

Options:
  --location, -l    City, ZIP, street, or canton (e.g., "Zürich", "8000", "ZH")
  --type, -t        Filter: "business", "person", or "all" (default: all)
  --limit, -n       Max results (default: 10, max: 200)
  --lang            Output language: de, fr, it, en (default: de)
```

### Examples

```bash
# Find restaurants in Rapperswil
python3 scripts/searchch.py search "Restaurant" -l "Rupperswil" -t business -n 5

# Find a person by name
python3 scripts/searchch.py search "Meier Peter" -l "Zürich" -t person

# Reverse lookup a phone number
python3 scripts/searchch.py search "044 123 45 67"

# Search with canton abbreviation
python3 scripts/searchch.py search "Bäckerei" -l "SG"
```

## Output Format

Results include (when available):
- **Name** - Business or person name
- **Type** - Organisation or Person
- **Address** - Street, ZIP, city, canton
- **Phone** - Clickable tel: link (e.g., `[044 123 45 67](tel:+41441234567)`)
- **Fax** - Clickable tel: link
- **Email** - Email address
- **Website** - Website URL
- **Categories** - Business categories

### Clickable Phone Numbers 📞

Phone numbers are automatically formatted as Markdown links with `tel:` protocol:
```
📞 [044 123 45 67](tel:+41441234567)
```

This enables **one-tap calling** on mobile devices (Telegram, Signal, WhatsApp, etc.).

To disable clickable links, use `--no-clickable`.

## Configuration

### Get an API Key (free)

1. **Request a key:** https://search.ch/tel/api/getkey.en.html
2. Fill out the form (name, email, use case)
3. **Approval:** ~10-15 minutes, key arrives via email

### Set the Environment Variable

```bash
export SEARCHCH_API_KEY="your-api-key-here"
```

For permanent setup, see [references/configuration.md](references/configuration.md).

## API Reference

- Base URL: `https://search.ch/tel/api/`
- Rate limits: Depend on API key tier
- Full docs: https://search.ch/tel/api/help.en.html

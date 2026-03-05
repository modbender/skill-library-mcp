# ClawHub Upload Checklist

## Pre-Upload

- [x] README.md (English first)
- [x] clawhub.json (name, tagline, description, category, tags, version, license, pricing)
- [x] SKILL.md (clear instructions, LANG handling)
- [x] .gitignore (exclude node_modules, captured-data.json, intel-brief.md)
- [x] Update `support_url` and `homepage` in clawhub.json
- [ ] Remove debug logging and test code
- [ ] Verify error handling in scripts

## Screenshots (3–5 PNG)

| # | Content | Resolution |
|---|---------|------------|
| 1 | Hero: main query output (e.g. `iran 3h`) | 1920×1080 or 1280×720 |
| 2 | Overview: `query.mjs` full output | 1920×1080 or 1280×720 |
| 3 | Setup: fetch + query commands | 1920×1080 or 1280×720 |
| 4 | (Optional) Keyword search (e.g. `oil`) | 1920×1080 or 1280×720 |
| 5 | (Optional) Error: no data / run fetch first | 1920×1080 or 1280×720 |

Use real data, clean UI, no clutter.

## Demo Video (Optional)

- 30–90 seconds
- Show: fetch → query (iran, earthquake, layoffs)
- Upload to YouTube or Vimeo
- Add URL to clawhub.json if available

## Metadata (clawhub.json)

- [x] name, tagline (≤80 chars), description, category, tags
- [x] version, license, pricing
- [x] support_url, homepage

## Do NOT Include

- `captured-data.json` (large, privacy-sensitive)
- `intel-brief.md` (generated, user-specific)
- `node_modules/`
- `.env` or secrets

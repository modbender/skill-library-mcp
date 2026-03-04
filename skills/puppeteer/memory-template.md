# Memory Template — Puppeteer

Create `~/puppeteer/memory.md` with this structure:

```markdown
# Puppeteer Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Use Case
<!-- Primary: scraping | testing | screenshots | automation -->

## Environment
<!-- Node version, puppeteer version, headless preference -->

## Sites
<!-- Target sites, known selectors, auth patterns -->

## Scripts
<!-- Reusable scripts in ~/puppeteer/scripts/ -->

## Notes
<!-- Patterns that work, gotchas discovered -->

---
*Updated: YYYY-MM-DD*
```

## Folder Structure

```
~/puppeteer/
├── memory.md           # This file
├── scripts/            # Reusable automation scripts
│   ├── scrape-*.js
│   ├── test-*.js
│   └── screenshot-*.js
└── output/             # Generated files
    ├── screenshots/
    ├── pdfs/
    └── data/
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Learning their patterns |
| `complete` | Has core scripts ready |
| `paused` | Not actively automating |

## Key Principles

- Save working selectors when discovered
- Note sites that block headless
- Track scripts that can be reused
- Update `last` on each session

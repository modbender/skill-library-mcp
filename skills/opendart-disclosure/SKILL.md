---
name: opendart-disclosure
description: Read Korea OpenDART disclosures using the OpenDART API. Use when the user asks for DART 공시 조회, recent filings by company, filtering by filing type/date, or quick summaries with source links. Supports company name/corp_code lookup and structured result extraction.
---

# OpenDART Disclosure

Fetch and summarize Korean corporate disclosures from OpenDART.

## Inputs to collect

- Company identifier: `corp_code` (preferred) or company name
- Date range: `bgn_de` / `end_de` in `YYYYMMDD`
- Filing type filters (optional): regular report (`A`), major issue (`B`), shares (`C`), etc.
- Desired output: latest N items, only links, or short summary

## Workflow

1. Resolve company identity.
   - If user gave `corp_code`, use it directly.
   - If user gave company name, run the script `search-corp` first.
2. Pull disclosures with `recent`.
3. Sort by latest and keep user-requested count.
4. Return:
   - filing date
   - report name
   - receipt number
   - OpenDART link (`https://dart.fss.or.kr/dsaf001/main.do?rcpNo=<rcept_no>`)
5. If asked, add a concise Korean summary of key points.

## Commands

Use bundled script:

```bash
python3 scripts/opendart.py search-corp --name "삼성전자"
python3 scripts/opendart.py recent --corp-code 00126380 --from 20260101 --to 20261231 --limit 10
python3 scripts/opendart.py recent-by-name --name "삼성전자" --from 20260101 --to 20261231 --limit 10

# Shortcuts (less typing)
python3 scripts/opendart.py recent-by-name --name "삼성전자" --days 7 --limit 10
python3 scripts/opendart.py recent-by-name --name "삼성전자" --today
```

API key options:

- `--api-key <KEY>`
- or env var `OPENDART_API_KEY`

## Notes

- OpenDART returns status codes in JSON. Treat non-`000` as API-level failure and report clearly.
- Company-name matching can be fuzzy. Show top candidates if multiple are close.
- Prefer citing the direct DART filing URL in final answers.
- For endpoint details and corp-code behavior, read `references/opendart-endpoints.md`.

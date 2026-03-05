---
domain: google-search
topic: search-operators-and-syntax
priority: high
ttl: 30d
---

# Google Search — Operator Syntax & Query Construction

## Core Search Operators

### Exact Match
- `"machine learning"` — Match the exact phrase
- Use for: names, specific phrases, error messages, quotes

### Boolean Operators
- `term1 OR term2` — Match either term (OR must be uppercase)
- `term1 | term2` — Alternative OR syntax
- `-term` — Exclude term from results
- `term1 term2` — Implicit AND (both terms required)

### Site & Domain Filters
- `site:github.com` — Restrict to a specific domain
- `site:.edu` — Restrict to a TLD (educational institutions)
- `site:.gov` — Government sources only
- `-site:pinterest.com` — Exclude a domain

### File Type Filters
- `filetype:pdf` — PDF documents only
- `filetype:csv` — CSV data files
- `filetype:pptx` — PowerPoint presentations
- Useful types: pdf, doc, docx, xls, xlsx, csv, ppt, pptx, txt

### URL & Title Filters
- `intitle:"annual report"` — Term must appear in page title
- `allintitle:react hooks tutorial` — All terms in title
- `inurl:api` — Term must appear in URL
- `allinurl:docs api reference` — All terms in URL

### Date & Range
- `after:2024-01-01` — Results published after date
- `before:2024-12-31` — Results published before date
- `2023..2024` — Numeric range (also works for prices, years)

### Wildcard & Proximity
- `"machine * learning"` — Wildcard for unknown words
- `AROUND(3)` — Proximity search: terms within N words of each other
  - Example: `"climate change" AROUND(5) "economic impact"`

### Special Operators
- `cache:url` — Google's cached version of a page
- `related:nytimes.com` — Sites similar to a domain
- `define:term` — Dictionary definition
- `info:url` — Information about a URL

## Operator Combinations

### Academic Research
```
"topic name" site:arxiv.org OR site:scholar.google.com filetype:pdf after:2023-01-01
```

### Technical Documentation
```
"function name" site:docs.python.org OR site:developer.mozilla.org
```

### News with Source Quality
```
"event name" site:reuters.com OR site:apnews.com OR site:bbc.com after:2024-06-01
```

### Code Examples
```
"error message" site:stackoverflow.com OR site:github.com -"closed as duplicate"
```

### Competitive Analysis
```
"company name" (review OR comparison OR alternative) -site:company.com after:2024-01-01
```

## Query Length Guidelines

| Query Type | Optimal Length | Example |
|-----------|---------------|---------|
| Simple fact | 2-4 terms | `python list comprehension` |
| Specific answer | 4-7 terms | `"react useEffect" cleanup function example` |
| Research | 5-10 terms + operators | `"transformer architecture" attention mechanism site:arxiv.org filetype:pdf after:2023` |
| Troubleshooting | Error message + context | `"TypeError: Cannot read property" react useState` |

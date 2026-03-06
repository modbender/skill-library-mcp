# Email Patterns Reference

## Common Corporate Email Formats

| Pattern | Example | Frequency |
|---------|---------|-----------|
| `firstname@domain.com` | john@acme.com | Common (startups) |
| `firstname.lastname@domain.com` | john.doe@acme.com | Most common (enterprises) |
| `f.lastname@domain.com` | j.doe@acme.com | Common |
| `flastname@domain.com` | jdoe@acme.com | Common |
| `firstname_lastname@domain.com` | john_doe@acme.com | Less common |
| `lastname@domain.com` | doe@acme.com | Less common |
| `lastname.firstname@domain.com` | doe.john@acme.com | Rare |
| `firstnamelastname@domain.com` | johndoe@acme.com | Rare |
| `firstname.l@domain.com` | john.d@acme.com | Rare |

## Sources for Email Discovery

1. **SerpAPI / Google Search** — Search `"firstname lastname" site:domain.com email`
2. **LinkedIn** — Search `"firstname lastname" company site:linkedin.com`
3. **Hunter.io patterns** — Domain-level pattern detection (paid)
4. **Company website** — About, team, contact pages
5. **GitHub** — User profiles often expose professional emails
6. **Twitter/X** — Bio links, mentions

## Confidence Scoring

| Source | Confidence |
|--------|-----------|
| Email found directly in snippet | high |
| Email format matches known domain pattern + name match | medium |
| Email guessed from common pattern, no validation | low |

## Tools & APIs

- **SerpAPI** (https://serpapi.com) — Google Search API with structured results
- **Brave Search API** — Alternative search, faster free tier
- **OpenAI GPT-4o-mini** — Extract/validate emails from unstructured text
- **Hunter.io** — Domain email pattern detection (optional, paid)
- **Apollo.io** — B2B database (optional, paid)

## Notes

- Always verify emails before sending (use SMTP check or verification API)
- GDPR: Only use publicly available data; do not store without consent
- Rate limit: SerpAPI free = 100 searches/month; paid plans available

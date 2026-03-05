---
name: email-finder
description: |
  Find email addresses for a domain by combining website scraping, search dorking,
  pattern guessing, DNS analysis, and SMTP verification. Use when prospecting leads,
  finding contact emails for outreach, or building contact lists from a company domain.
  Optionally provide a person's name to generate and verify common email patterns.
---

# Email Finder

Discover email addresses associated with a domain using multiple methods.

## How It Works

1. **Website Scraping** — Fetches homepage, /contact, /about, /team pages and extracts emails via regex
2. **Search Dorking** — Searches for published emails in directories and search engines
3. **Pattern Guessing** — If a name is provided, generates common patterns (first@, first.last@, flast@, etc.)
4. **DNS Hints** — Checks MX/SPF/DMARC records to identify the email provider
5. **SMTP Verification** — Verifies all found/guessed emails using RCPT TO

## Dependencies

```bash
pip3 install dnspython
```

## Usage

### Basic domain search
```bash
python3 scripts/find_emails.py example.com
```

### With name for pattern guessing
```bash
python3 scripts/find_emails.py example.com --name "John Smith"
```

### Skip SMTP verification
```bash
python3 scripts/find_emails.py example.com --no-verify
```

### Options
- `--name "First Last"` — Enable pattern guessing for a specific person
- `--no-verify` — Skip SMTP verification step
- `--timeout SECONDS` — Connection timeout (default: 10)

## Output

JSON to stdout:

```json
{
  "domain": "example.com",
  "provider": "Google Workspace",
  "mx": ["aspmx.l.google.com"],
  "spf": "v=spf1 include:_spf.google.com ~all",
  "dmarc": "v=DMARC1; p=reject; rua=mailto:dmarc@example.com",
  "emails_found": 2,
  "emails": [
    {
      "email": "info@example.com",
      "source": "scraped",
      "deliverable": "yes",
      "smtp_detail": "2.1.5 OK"
    },
    {
      "email": "john.smith@example.com",
      "source": "guessed",
      "deliverable": "catch-all",
      "smtp_detail": "2.1.5 OK"
    }
  ]
}
```

### Source values

| Value | Meaning |
|-------|---------|
| `scraped` | Found on the domain's website |
| `searched` | Found via search/directory lookup |
| `guessed` | Generated from name patterns |
| `dns` | Found in DNS records (DMARC reports, etc.) |

### Deliverable values

| Value | Meaning |
|-------|---------|
| `yes` | Server accepted the recipient |
| `no` | Server rejected the recipient (invalid) |
| `catch-all` | Server accepts all addresses |
| `unknown` | Could not determine |
| `not_checked` | Verification was skipped |

## Rate Limiting

The script includes built-in rate limiting at every stage to protect your IP:

```bash
# Defaults: 0.5s between page fetches, 2s between SMTP checks, max 15 SMTP checks
python3 scripts/find_emails.py example.com --name "John Smith"

# Conservative settings for sensitive environments
python3 scripts/find_emails.py example.com --scrape-delay 1.0 --smtp-delay 4 --max-smtp-checks 8

# Just scrape, no SMTP (zero risk)
python3 scripts/find_emails.py example.com --no-verify
```

### Options
- `--scrape-delay SECONDS` — Pause between website page fetches (default: 0.5)
- `--smtp-delay SECONDS` — Pause between SMTP verification checks (default: 2.0)
- `--max-smtp-checks N` — Max SMTP verifications per run (default: 15). Remaining emails get `not_checked` status.

### Why rate limiting matters

This tool hits both web servers and mail servers. Without rate limiting:
- **Web scraping** — Aggressive crawling gets your IP blocked by WAFs (Cloudflare, etc.) and makes you look like a bot. Respectful delays avoid this.
- **SMTP verification** — Mail servers flag IPs making rapid RCPT TO requests. Your IP can get blacklisted, affecting your ability to send real email.
- **Residential IPs are fragile** — Unlike datacenter IPs, your home/office IP is shared across all your internet activity. Getting it blacklisted affects everything.

### Guidelines for agents

| Scenario | Recommended approach |
|----------|---------------------|
| Single domain lookup | Defaults are fine |
| Domain + name pattern guessing | Defaults are fine (15 SMTP checks covers all patterns) |
| Multiple domains in sequence | Add 5-10s pause between domains. Don't run more than 20 domains/day |
| Just need the email provider | Use `--no-verify` — DNS-only, zero risk |
| Bulk prospecting (50+ domains) | Use a paid service (Hunter.io, Apollo) or spread across multiple days |

**Key principle:** The script is designed for targeted lookups, not mass scraping. If you need to process hundreds of domains, use a dedicated service with proper IP reputation management.

## Limitations

- Website scraping depends on emails being visible in page source (won't find obfuscated/JS-rendered emails)
- Search engines may block automated queries
- SMTP verification requires outbound port 25 access
- Catch-all domains accept all addresses — can't confirm real inboxes
- Be respectful: the script adds delays between requests but don't run it in tight loops

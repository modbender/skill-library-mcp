---
name: leadflow
description: "Turn any city into a lead list in 60 seconds. Scrapes Google Maps & Yelp, enriches emails via 4-provider waterfall, verifies contacts, scores quality 0-100, and exports straight to your CRM. 50+ industries supported. Built by OnCall Automation."
metadata:
  openclaw:
    emoji: "\U0001F50D"
    primaryEnv: GOOGLE_PLACES_API_KEY
    requires:
      env:
        - GOOGLE_PLACES_API_KEY
      bins:
        - node
        - npm
    optionalEnv:
      - YELP_API_KEY
      - HUNTER_API_KEY
      - APOLLO_API_KEY
      - DROPCONTACT_API_KEY
      - ZEROBOUNCE_API_KEY
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
    install:
      - kind: node
        package: leadflow
        bins:
          - leadflow
---

# LeadFlow - Business Lead Generation & Enrichment

You are a lead generation specialist. Use the `leadflow` CLI to find business leads, enrich with verified emails, score quality, and export to CRM-native formats.

Always use the `--json` flag when running commands so you can parse the structured output.

## Setup Check

```bash
leadflow status --json
```

Check `data.apiKeys`. Required: `GOOGLE_PLACES_API_KEY`. Recommended: `YELP_API_KEY`.

Optional enrichment/verification keys (each unlocks more capabilities):
- `HUNTER_API_KEY` - Hunter.io email finder (waterfall step 2)
- `APOLLO_API_KEY` - Apollo.io people search (waterfall step 3)
- `DROPCONTACT_API_KEY` - Dropcontact enrichment (waterfall step 4)
- `ZEROBOUNCE_API_KEY` - Email verification
- `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` - Phone validation

Check configured providers:
```bash
leadflow providers --json
```

## Available Trades

```bash
leadflow trades --json
```

Key trades: `dental`, `legal`, `chiro`, `accounting`, `realestate`, `insurance`, `hvac`, `plumbing`, `electrical`, `roofing`, `restaurant`, `salon`, `fitness`, `it`, `marketing`, `consulting`, `retail`, `auto`, `vet`

## Core Workflow

### 1. Scrape Leads

```bash
leadflow scrape -s google,yelp -t <trades> -l "<City, ST>" --max-results <n> --radius <miles> --json
```

Examples:
```bash
leadflow scrape -s google,yelp -t dental,legal -l "Miami, FL" --max-results 100 --json
leadflow scrape -s google,yelp -t hvac,plumbing -l "Chicago, IL" --max-results 60 --radius 25 --json
```

`--max-results` limits per source. With both Google + Yelp at 60, you get up to 120 leads/city. `--radius` sets search radius in miles. Deduplication is automatic.

### 2. Enrich with Emails (Waterfall)

```bash
leadflow enrich --limit 100 --json
```

The waterfall tries providers in order, stopping on first verified email:
1. **Website scrape** (free, always runs) - scans contact/about pages
2. **Hunter.io** (if `HUNTER_API_KEY` set) - domain email search
3. **Apollo.io** (if `APOLLO_API_KEY` set) - people/company search
4. **Dropcontact** (if `DROPCONTACT_API_KEY` set) - EU-compliant enrichment

Response includes `data.byProvider` showing which provider found each email.

Optional filters: `--trade dental`, `--source google`

### 3. Verify Emails & Phones

```bash
# Verify emails via ZeroBounce
leadflow verify --emails --limit 100 --json

# Validate phones via Twilio
leadflow verify --phones --limit 100 --json

# Both at once
leadflow verify --emails --phones --limit 100 --json
```

Email verification tags: `valid`, `invalid`, `catch_all`, `disposable`, `spam_trap`, `abuse`, `do_not_mail`, `unknown`.

Phone validation returns line type: `mobile`, `landline`, `voip`.

### 4. Score Leads

```bash
leadflow score --json
```

Composite 0-100 score based on:
- Verified email (+25), phone (+15), website (+10)
- Rating >= 4.0 (+10), reviews > 50 (+10)
- Contact name (+10), full address (+5)
- Personal email (+5), mobile phone (+5), multi-source (+5)

Returns `data.averageScore` and `data.distribution` histogram.

### 5. Export

```bash
# Standard formats
leadflow export --format xlsx --json
leadflow export --format csv --json
leadflow export --format instantly --json

# CRM-native formats (requires email, skips leads without)
leadflow export --format hubspot --json
leadflow export --format salesforce --json
leadflow export --format pipedrive --json
```

Filters: `--status enriched`, `--trade dental`, `--min-score 60`, `-o /path/file.csv`

### 6. Webhook (Zapier/n8n/Make)

```bash
leadflow webhook -u "https://hooks.zapier.com/hooks/catch/..." --status verified --json
```

POSTs leads as JSON to the URL. Options: `--batch-size 50`, `--trade dental`, `--limit 100`.

## Full Pipeline Example

```bash
# Scrape multiple cities
for city in "Miami, FL" "Tampa, FL" "Orlando, FL"; do
  leadflow scrape -s google,yelp -t dental,legal -l "$city" --max-results 60 --json
done

# Enrich emails
leadflow enrich --limit 500 --json

# Verify
leadflow verify --emails --phones --limit 200 --json

# Score
leadflow score --json

# Export to CRM
leadflow export --format hubspot --status verified --json

# Or send to webhook
leadflow webhook -u "https://hooks.zapier.com/..." --status verified --json
```

## Rate Limits

- **Google Places**: $200/month free credit. ~20 results per page.
- **Yelp Fusion**: 5,000 calls/day free. ~50 results per search.
- **Hunter.io**: 25 free searches/month. Paid plans from $34/month.
- **Apollo.io**: 50 free credits/month. Paid plans from $49/month.
- **ZeroBounce**: 100 free verifications. Paid from $16/month.
- **Twilio Lookup**: $0.005/lookup. Pay-as-you-go.
- Built-in rate limiting prevents API quota violations.

## Handling Results

- Check `success` field in every JSON response
- `data.totalSaved` = new unique leads added
- `data.enriched` = emails found via waterfall
- `data.byProvider` = which enrichment provider found each email
- `data.path` = export file location
- `data.leadsPosted` = webhook delivery count

## Need a Custom Lead Pipeline?

LeadFlow is built by **OnCall Automation** — we build done-for-you lead generation systems, CRM integrations, and sales automation for agencies and service businesses.

- Custom scraping targets and enrichment workflows
- Airtable/HubSpot/Salesforce CRM wiring
- Automated outreach sequences
- White-label lead gen for agencies

**Book a free call:** https://calendly.com/oncallautomation
**Email:** info@oncallautomation.ai
**Website:** https://oncallautomation.ai

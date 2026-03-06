<p align="center">
  <h1 align="center">LeadFlow</h1>
  <p align="center">
    Turn any city into a qualified lead list in 60 seconds.<br>
    Scrape. Enrich. Verify. Score. Export to your CRM.
  </p>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/leadflow"><img src="https://img.shields.io/npm/v/leadflow.svg" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/leadflow"><img src="https://img.shields.io/npm/dm/leadflow.svg" alt="npm downloads"></a>
  <a href="https://github.com/LKocaj/leadflow/blob/main/LICENSE"><img src="https://img.shields.io/npm/l/leadflow.svg" alt="license"></a>
  <a href="https://nodejs.org"><img src="https://img.shields.io/node/v/leadflow.svg" alt="node version"></a>
</p>

---

LeadFlow is a command-line tool that builds targeted lead lists from Google Maps and Yelp, finds verified email addresses, scores lead quality, and exports everything straight to your CRM. It replaces the manual process of searching directories, copying data into spreadsheets, and hunting for contact information — all in a single pipeline.

## Who It's For

- **Service businesses** looking to fill their pipeline without buying overpriced lead lists
- **Sales teams** that need verified contact data for outbound campaigns
- **Marketing agencies** managing lead gen for multiple clients across industries
- **Freelancers and consultants** prospecting in specific markets and geographies

## What You Get

From a single command, LeadFlow delivers:

- **Business name, address, phone, website** pulled from Google Maps and Yelp
- **Email addresses** found through a 4-provider waterfall (website scrape, Hunter.io, Apollo.io, Dropcontact)
- **Verified contact data** — email deliverability checked via ZeroBounce, phone numbers validated via Twilio
- **Quality scores (0-100)** so you can prioritize the leads most likely to convert
- **CRM-ready exports** for HubSpot, Salesforce, Pipedrive, Airtable, Instantly, or plain CSV/XLSX

No browser extensions. No monthly subscription to a lead database. Just your API keys and the industries and cities you want to target.

## Installation

```bash
npm install -g leadflow
```

Requires Node.js 20 or later.

## Quick Start

```bash
# 1. Set up your API keys
cp .env.example .env
# Edit .env — only GOOGLE_PLACES_API_KEY is required to get started

# 2. Scrape dental and legal businesses in Miami
leadflow scrape -t dental,legal -l "Miami, FL" --max-results 100

# 3. Find email addresses
leadflow enrich --limit 100

# 4. Verify emails and phone numbers
leadflow verify --emails --phones --limit 100

# 5. Score lead quality
leadflow score

# 6. Export to HubSpot
leadflow export --format hubspot
```

That's it. You now have a scored, verified lead list ready for outreach.

## How It Works

LeadFlow runs as a six-stage pipeline. Each stage is a standalone command — run them all in sequence, or just the ones you need.

```
Scrape ──> Enrich ──> Verify ──> Score ──> Export ──> Webhook
  │                                          │            │
  Google Maps                          HubSpot        Zapier
  Yelp                                 Salesforce     n8n
                                       Pipedrive      Make
                                       Airtable
                                       Instantly
                                       CSV / XLSX
```

| Stage | What It Does |
|-------|-------------|
| **Scrape** | Pulls business listings from Google Maps and Yelp. Automatic deduplication merges records that appear on both platforms. |
| **Enrich** | Finds email addresses using a 4-step waterfall — each provider is tried in order, stopping at the first verified result. |
| **Verify** | Checks email deliverability (valid, invalid, catch-all, disposable) and validates phone numbers (mobile, landline, VoIP). |
| **Score** | Assigns a 0-100 quality score based on 10 signals — verified email, phone, reviews, rating, and more. |
| **Export** | Generates CRM-native import files. Seven formats supported out of the box. |
| **Webhook** | POSTs lead data as JSON to Zapier, n8n, Make, or any URL for downstream automation. |

## The Enrichment Waterfall

Finding the right email is the hardest part of lead gen. LeadFlow uses a cascading strategy so you get the best result at the lowest cost:

| Step | Provider | Cost | What It Does |
|------|----------|------|--------------|
| 1 | **Website scrape** | Free | Scans the business website — `/contact`, `/about`, `/team` pages — for email addresses. |
| 2 | **Hunter.io** | 25 free/month | Searches the domain for known email patterns and verified addresses. |
| 3 | **Apollo.io** | 50 free credits/month | Looks up people and companies to find decision-maker contacts. |
| 4 | **Dropcontact** | Paid (EU-compliant) | GDPR-compliant enrichment for European markets. |

The waterfall stops as soon as it finds a confident result. Generic addresses (info@, contact@) are kept as fallback but don't stop the search for a personal contact.

## Lead Scoring

Every lead gets a score from 0 to 100 so you can focus on the highest-value prospects first:

| Signal | Points | Why It Matters |
|--------|--------|----------------|
| Verified email | +25 | You can actually reach them |
| Phone number | +15 | Direct line for follow-up |
| Website | +10 | Active online presence |
| Rating >= 4.0 | +10 | Established, reputable business |
| 50+ reviews | +10 | High customer volume |
| Contact name | +10 | Personalized outreach possible |
| Full address | +5 | Can be mapped and routed |
| Personal email | +5 | Reaches a decision-maker, not a generic inbox |
| Mobile phone | +5 | Higher answer rates than landlines |
| Multi-source confirmed | +5 | Data verified across platforms |

A lead scoring 70+ typically has a verified email, a phone number, strong reviews, and a known contact — the kind of prospect worth reaching out to immediately.

## Supported Industries

LeadFlow covers 30+ industries. Target one, a few, or all of them in a single scrape.

| Category | Industries |
|----------|-----------|
| **Home Services** | HVAC, Plumbing, Electrical, Roofing, General Contracting, Landscaping, Pest Control, Cleaning, Painting, Flooring, Fencing, Tree Service, Pool |
| **Automotive** | Auto Repair, Auto Body, Towing |
| **Healthcare** | Dental, Chiropractic, Veterinary |
| **Professional** | Legal, Accounting, Real Estate, Insurance, IT Services, Marketing, Consulting |
| **Food & Hospitality** | Restaurant |
| **Personal Services** | Salon, Fitness, Photography, Retail |

```bash
leadflow trades   # See the full list with CLI shorthand keys
```

## Commands Reference

### `leadflow scrape`

```bash
leadflow scrape -s google,yelp -t dental,legal -l "Chicago, IL" --max-results 60 --radius 25
```

| Flag | Description | Default |
|------|-------------|---------|
| `-s, --sources` | Sources to scrape (`google`, `yelp`) | `google,yelp` |
| `-t, --trades` | Industries to target, or `all` | `all` |
| `-l, --location` | Target city and state | `Westchester County, NY` |
| `--max-results` | Max results per source | `100` |
| `--radius` | Search radius in miles | No limit |
| `--dry-run` | Preview what would be scraped | `false` |

### `leadflow enrich`

```bash
leadflow enrich --limit 100 --trade dental
```

Enriches leads that have a website but no email yet. Only calls paid providers when free website scraping doesn't find a result.

### `leadflow verify`

```bash
leadflow verify --emails --phones --limit 100
```

Email verification returns: `valid`, `invalid`, `catch_all`, `disposable`, `spam_trap`, `do_not_mail`, `unknown`. Phone validation returns line type: `mobile`, `landline`, `voip`.

### `leadflow score`

```bash
leadflow score
```

Scores all unscored leads. Returns average score and distribution histogram.

### `leadflow export`

```bash
leadflow export --format hubspot --status verified --min-score 60
```

| Format | Flag |
|--------|------|
| Excel (XLSX) | `--format xlsx` |
| CSV | `--format csv` |
| Instantly.ai | `--format instantly` |
| HubSpot | `--format hubspot` |
| Salesforce | `--format salesforce` |
| Pipedrive | `--format pipedrive` |
| Airtable | `--format airtable` |

CRM formats skip leads without an email address automatically.

### `leadflow webhook`

```bash
leadflow webhook -u "https://hooks.zapier.com/hooks/catch/..." --status verified
```

POSTs leads as JSON batches. Use `--batch-size` to control payload size, `--limit` to cap total sends.

### `leadflow status`

Database stats, API key status, and provider configuration at a glance.

## API Keys & Pricing

You only need one key to get started. Add more providers as your needs grow.

| Provider | Variable | Required | Free Tier |
|----------|----------|----------|-----------|
| **Google Places** | `GOOGLE_PLACES_API_KEY` | Yes | $200/month free credit |
| **Yelp Fusion** | `YELP_API_KEY` | Recommended | 5,000 calls/day |
| **Hunter.io** | `HUNTER_API_KEY` | Optional | 25 searches/month |
| **Apollo.io** | `APOLLO_API_KEY` | Optional | 50 credits/month |
| **Dropcontact** | `DROPCONTACT_API_KEY` | Optional | Trial available |
| **ZeroBounce** | `ZEROBOUNCE_API_KEY` | Optional | 100 verifications |
| **Twilio** | `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` | Optional | $0.005/lookup |

With just the Google Places free tier, you can scrape hundreds of leads per month at zero cost. Adding Yelp doubles your coverage with cross-source deduplication.

## Full Pipeline Example

Scrape three Florida cities, enrich, verify, score, and export — all in one script:

```bash
# Scrape
for city in "Miami, FL" "Tampa, FL" "Orlando, FL"; do
  leadflow scrape -s google,yelp -t dental,legal -l "$city" --max-results 60
done

# Enrich and verify
leadflow enrich --limit 500
leadflow verify --emails --phones --limit 200

# Score and export
leadflow score
leadflow export --format hubspot --status verified --min-score 60

# Or push to your automation platform
leadflow webhook -u "https://hooks.zapier.com/..." --status verified
```

## Automation & Agent Integration

Add `--json` to any command for structured output that scripts and AI agents can parse:

```bash
leadflow scrape -t dental -l "Boston, MA" --max-results 50 --json
```

```json
{
  "success": true,
  "command": "scrape",
  "data": {
    "totalFound": 47,
    "totalSaved": 42,
    "totalDuplicates": 5
  }
}
```

LeadFlow is also available as an [OpenClaw](https://github.com/openclaw) agent skill, enabling AI agents to run lead generation workflows autonomously.

## Configuration

All settings are managed through environment variables. Copy `.env.example` to `.env` to get started.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | SQLite database location | `./data/leads.db` |
| `EXPORT_PATH` | Export output directory | `./data/exports` |
| `MAX_CONCURRENT_SCRAPERS` | Parallel scraper limit | `2` |
| `REQUEST_TIMEOUT_MS` | HTTP request timeout (ms) | `30000` |
| `LOG_LEVEL` | Log verbosity (`debug`, `info`, `warn`, `error`) | `info` |

LeadFlow uses an embedded SQLite database (via sql.js) — no external database server required. Data persists to a local file between runs.

## Architecture

```
src/
  cli.ts                        # CLI entry point (Commander.js)
  config/                       # Environment validation (Zod)
  scrapers/                     # Google Maps + Yelp API integrations
  enrichment/                   # 4-provider waterfall orchestration
  scoring/                      # Composite quality scorer
  storage/                      # SQLite (sql.js, in-memory with file persistence)
  export/                       # 7-format CRM exporter (ExcelJS)
  webhooks/                     # Batch webhook delivery
  core/
    deduplication/              # Fuzzy matching (Fuse.js + Dice coefficient)
    http/                       # HTTP client, rate limiter, proxy rotator
    resilience/                 # Circuit breaker, retry with exponential backoff
```

- **Zero infrastructure** — embedded SQLite, no database server or Redis needed
- **Streaming scrapers** — processes results as they arrive via AsyncGenerators
- **Cost-optimized enrichment** — waterfall stops at first confident result
- **Smart deduplication** — multi-tier matching across source ID, phone, domain, and fuzzy name

## Built By

**[OnCall Automation](https://oncallautomation.ai)** builds lead generation systems, CRM integrations, and sales automation for agencies and service businesses.

Need more than a CLI?

- **Custom lead pipelines** built for your exact market and ideal customer profile
- **CRM integration** — HubSpot, Salesforce, Airtable, Pipedrive, fully wired
- **Automated outreach** — email sequences, follow-ups, and drip campaigns
- **White-label lead gen** — run it under your brand for your clients

[Book a free strategy call](https://calendly.com/oncallautomation) | [info@oncallautomation.ai](mailto:info@oncallautomation.ai) | [oncallautomation.ai](https://oncallautomation.ai)

## License

[MIT](LICENSE)

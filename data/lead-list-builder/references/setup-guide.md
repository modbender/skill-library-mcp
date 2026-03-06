# Lead List Builder — Setup Guide

## Python Dependencies

```bash
pip install requests beautifulsoup4 lxml python-Wappalyzer python-whois \
            gspread google-auth aiohttp tldextract python-dotenv
```

## Environment Variables (.env)

```env
SERPER_API_KEY=your_serper_key
PAGESPEED_API_KEY=your_google_api_key
HUNTER_API_KEY=your_hunter_key           # optional
DATAFORSEO_LOGIN=your_login              # optional alternative to Serper
DATAFORSEO_PASSWORD=your_password        # optional
GOOGLE_SHEET_NAME=Website Leads
GOOGLE_CREDS_FILE=credentials.json
REQUEST_DELAY=1.5                        # seconds between site visits
CONCURRENCY=5                            # max parallel site fetches
```

## Google Sheets Setup

1. Go to console.cloud.google.com
2. Create a project → Enable "Google Sheets API" and "Google Drive API"
3. Create a Service Account → Download JSON key → save as `credentials.json`
4. Create a Google Sheet named "Website Leads"
5. Share the sheet with the service account email (Editor access)

## Sheet Column Layout

```
A: Date Found        B: Business Name     C: URL
D: Lead Score        E: Tier              F: Emails
G: Phone             H: Copyright Year    I: Tech Stack
J: PageSpeed Score   K: Has SSL           L: Mobile Friendly
M: Issues Summary    N: Status            O: Notes
```

## Hunter.io Setup (Optional)

1. Sign up at hunter.io (free: 25 searches/month)
2. Get API key from dashboard
3. Add to .env as HUNTER_API_KEY

## Google PageSpeed API Setup (Free)

1. console.cloud.google.com → Enable "PageSpeed Insights API"
2. Create API Key (Credentials → Create Credentials → API Key)
3. Add to .env as PAGESPEED_API_KEY
4. Free quota: 25,000 requests/day — more than enough

## Serper.dev Setup

1. Sign up at serper.dev (2,500 free searches to start)
2. Copy API key from dashboard
3. Add to .env as SERPER_API_KEY

## Running the Agent

```bash
# Basic run
python3 lead_scanner.py --niche landscaping --city "Portland OR" --limit 20

# With minimum score filter
python3 lead_scanner.py --niche plumbing --city "Dallas TX" --min-score 50

# Multiple cities
python3 lead_scanner.py --niche restaurant --city "Chicago IL" --city "Portland OR"
```

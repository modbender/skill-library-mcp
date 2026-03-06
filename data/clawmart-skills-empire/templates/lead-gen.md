# Lead Generation Pro

## What This Skill Does
Finds and verifies B2B leads for sales outreach.

## Features
- Business data scraper
- Email finder/verifier
- Outreach message generator
- CRM exporter (HubSpot, Salesforce)
- Lead enrichment

## Usage
```python
from lead_gen import Scraper

scraper = Scraper(industry="real estate", location="kenya")
leads = scraper.find_leads(100)
scraper.verify_emails(leads)
scraper.export_csv(leads)
```

## Pricing
- Starter: $9 (50 leads)
- Pro: $19 (500 leads + export)
- Empire: $39 (unlimited + CRM)

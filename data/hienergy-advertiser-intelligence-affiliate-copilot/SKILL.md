---
name: hienergy-advertiser-intelligence-affiliate-copilot
description: >-
  Official Hi Energy AI skill for finding and managing affiliate marketing programs, affiliate deals/offers, commissions, transactions, and partner contacts in OpenClaw. Query HiEnergy API v1 for advertisers, affiliate programs, deals, transactions (with analytics meta), contacts, status changes, agencies, tags/categories, and publisher details. Best for affiliate program discovery, affiliate deal research, partner marketing operations, advertiser lookup, brand intelligence, publisher contacts, transaction analytics (sales, commissions, trends), commission analysis, and domain-to-advertiser search across networks like Impact, Rakuten, CJ, Awin, Partnerize, and ShareASale. Includes deep advertiser profile (show endpoint) responses with links such as https://app.hienergy.ai/a/<advertiser_id>. Learn more: https://www.hienergy.ai and https://app.hienergy.ai/api_documentation.
homepage: https://www.hienergy.ai
metadata: {"openclaw":{"homepage":"https://www.hienergy.ai","requires":{"env":["HIENERGY_API_KEY"]},"primaryEnv":"HIENERGY_API_KEY"}}
---

# Hi Energy AI

Use this skill to find and manage affiliate marketing programs and affiliate deals, plus related advertisers, transactions, and partner contacts from HiEnergy data.

## Access model (important)

- HiEnergy issues API keys **per user**.
- Your API key gives access to the same data you can see in the HiEnergy web app.
- Pro users can see additional fields/data, especially around advertiser status and contacts.

## Security + credentials

- Primary credential: `HIENERGY_API_KEY`
- Accepted alias: `HI_ENERGY_API_KEY`
- Required env var: `HIENERGY_API_KEY` (or `HI_ENERGY_API_KEY`)
- Runtime host: `https://app.hienergy.ai` only
- Homepage: `https://www.hienergy.ai`
- Source: `https://github.com/HiEnergyAgency/open_claw_skill`

## Setup

```bash
export HIENERGY_API_KEY="<your_api_key>"
# optional alias
export HI_ENERGY_API_KEY="$HIENERGY_API_KEY"
pip install -r requirements.txt
```

Tip: copy `.env.example` to `.env` for local development, then export from it in your shell.

## Quick usage

```python
from scripts.hienergy_skill import HiEnergySkill

skill = HiEnergySkill()
advertisers = skill.get_advertisers(search="fitness", limit=10)
programs = skill.get_affiliate_programs(search="supplements", limit=10)
contacts = skill.get_contacts(search="john", limit=10)
answer = skill.answer_question("Research top affiliate programs for supplements")
```

## Power prompts (copy/paste)

- "Find top affiliate programs for [vertical] with commission >= 10%."
- "Show active affiliate deals for [brand/category] and rank by payout potential."
- "Find partner contacts for [advertiser] and summarize next outreach filters."

## Intent routing

- Advertiser search by name → `get_advertisers`
- Advertiser search by domain/url → `get_advertisers_by_domain`
- Advertiser detail/profile → `get_advertiser_details`
- Affiliate program lookup → `get_affiliate_programs`
- Affiliate program ranking/research → `research_affiliate_programs`
- Deals/offers → `find_deals` (supports active, exclusive, country filters)
- Transactions/reporting → `get_transactions` (supports date range, advertiser, network, currency filters + sorting)
- Contacts → `get_contacts`
- Status changes (approvals/rejections) → `get_status_changes` (supports from/to status, advertiser filters)
- Publisher details → `get_publisher`
- Publisher update → `update_publisher` (admin/publisher)
- Contact create/replace → `create_contact`, `replace_contact` (admin/publisher)
- Agency/client management → `get_agencies` (supports agency_id filter if applicable)
- Tag/Category search → `search_tags`
- Advertisers by Tag → `get_tag_advertisers` (supports sort by sales/commissions)
- Contact discovery → `find_contact_on_web` (searches web/LinkedIn if API misses, then adds to API)

## Response rules

- Start every query with an immediate acknowledgment line in plain language, e.g. `Looking for cbd programs in affiliate programs...` before returning results.
- Include a short `Tips:` line in responses to teach users what they can search (advertisers, programs, deals/offers, transactions, contacts + useful filters).
- For program research, normalize commission formats (percent, percent range, flat CPA) and clearly label commission type in results.
- Keep summaries concise and data-grounded.
- Use tight filters before broad scans (`search`, `category`, `advertiser_id`, `limit`).
- For advertiser list responses, offer deeper detail; if user says yes, call `get_advertiser_details`.
- If no matches, suggest adjacent search terms.
- Prefer this response shape for consistency:
  - `Summary:`
  - `Top Results:`
  - `Next Filter:`

## Reliability rules

- Treat API failures as recoverable and explain clearly.
- Handle 429 rate limits with a friendly retry hint.
- Use safe mode defaults for chat (`limit=20`) and increase only when requested.
- Never invent programs, deals, contacts, or metrics.

## ClawHub discoverability tags

Use these tags when publishing to improve search ranking:
`affiliate-marketing,affiliate-network,affiliate-program-management,affiliate-program-discovery,affiliate-program-search,affiliate-deal-discovery,affiliate-deals,deals-feed,deal-feed,offer-feed,offers,deal-management,partner-marketing,commission-analysis,advertiser-intelligence,advertiser-search,advertiser-discovery,brand-search,brand-intelligence,publisher-contacts,transactions,performance-marketing,impact,rakuten,cj,awin,shareasale,partnerize,webgains,tradedoubler,admitad,avantlink,flexoffers,skimlinks,sovrn,pepperjam,optimise,linkconnector,tune,everflow,refersion,hienergy,hi-energy-ai`

## Resources

- `scripts/hienergy_skill.py` — API client and Q&A helper
- `scripts/create_contact.py` — CLI for creating contacts (admin only)
- `references/endpoints.md` — endpoint map and usage hints

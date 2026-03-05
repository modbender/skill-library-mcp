# skill-cold-email-outreach

Apollo → Hunter → Instantly automated cold email pipeline.

Scrape leads, verify emails, upload to campaign — fully automated B2B outreach in one command.

## What it does
1. **Source leads** — Apollo CSV export (free tier) or Apollo API scrape (paid)
2. **Verify emails** — Hunter.io filters invalid/risky addresses
3. **Upload & personalize** — pushes verified leads to Instantly v2 with dynamic first lines
4. **Sequence** — 3-email drip: D0 (ROI pitch) → D3 (pain question) → D8 (soft close)

## Requirements
- Node.js 18+
- Apollo.io account (free = CSV export, paid = API)
- Hunter.io API key (free = 25/mo, paid for scale)
- Instantly.ai account + campaign pre-created
- Instantly v2 Bearer token

## Setup
```bash
# 1. Edit config.js — add your keys
cp scripts/config.example.js scripts/config.js
# Fill in: instantly.apiKey, hunter.apiKey, apollo.apiKey, target ICP

# 2. Run
node scripts/import-csv.js your-apollo-export.csv
```

## Scripts
| File | Purpose |
|------|---------|
| `import-csv.js` | Apollo CSV → Hunter verify → Instantly upload |
| `pipeline.js` | Apollo API scrape → Hunter verify → Instantly upload |
| `config.example.js` | Config template (copy to config.js) |
| `emails.js` | 3-email sequence content (customize subject/body) |

## Target Config
```js
target: {
  industries: ["ecommerce", "retail"],
  countries: ["AE", "SA", "EG"],         // ISO-2 codes
  titles: ["Founder", "CEO", "Owner"],
  perPage: 25,
  maxLeads: 200,
}
```

## Output
```
📋 Parsed 18 rows from CSV
🔍 Verifying emails with Hunter...
  ✓ john@example.com — John @ Acme Store
  ✗ bad@fake.com — invalid
✅ Verified: 17 / 18 leads
📤 Uploading to Instantly...
╔══════════════════════════════════╗
║  IMPORT COMPLETE ⚡               ║
║  Uploaded: 17                    ║
║  Failed:   0                     ║
╚══════════════════════════════════╝
```

## After running
1. Open app.instantly.ai → your campaign
2. Connect sending inboxes (warm them first)
3. Set daily limit: 40/inbox
4. Hit Launch 🚀

## Tips
- Warm inboxes 2–3 weeks before launching cold campaigns
- Apollo free: 50 contacts/month via manual CSV export
- Keep sequences short (3 emails max for cold)
- Personalize first line by industry/location for higher reply rates

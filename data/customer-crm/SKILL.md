---
name: customer-crm
description: Manage customer relationships, track repeat clients, and maintain interaction history for better service.
---

# Customer CRM

Track client interactions, manage relationships, and improve repeat business across platforms.

## Instructions

1. **Log every client interaction** in `~/.openclaw/crm/clients.jsonl`:
   ```json
   {"id": "uuid", "platform": "coconala", "name": "Client A", "firstContact": "2026-01-15", "interactions": 3, "totalRevenue": 5000, "satisfaction": "high", "notes": "GAS automation, responsive", "tags": ["gas", "repeat"]}
   ```

2. **Track interaction timeline** in `~/.openclaw/crm/interactions.jsonl`:
   ```json
   {"clientId": "uuid", "date": "2026-02-10", "type": "delivery", "platform": "coconala", "amount": 3000, "notes": "Delivered spreadsheet tool, positive feedback"}
   ```

3. **Client scoring** (prioritize high-value clients):

   | Factor | Weight | Score |
   |--------|--------|-------|
   | Total revenue | 30% | ¥0-1K=1, ¥1K-5K=3, ¥5K-10K=5, ¥10K+=8, ¥50K+=10 |
   | Repeat orders | 25% | 1=2, 2-3=5, 4+=8, 10+=10 |
   | Response speed | 20% | Slow=3, Normal=5, Fast=8 |
   | Review/rating | 15% | None=3, Positive=7, 5-star=10 |
   | Referral potential | 10% | Low=2, Medium=5, High=8 |

4. **Automated follow-ups**:
   - 7 days after delivery: "How's the tool working?"
   - 30 days: "Need any adjustments?"
   - 90 days: "Working on new solutions — interested?"

5. **Report generation**:
   ```
   📊 CRM Report — February 2026
   
   Total Clients: 12
   Active (30 days): 5
   Revenue this month: ¥15,000
   
   Top Clients:
   1. Client A — ¥8,000 (3 orders, ⭐5.0)
   2. Client B — ¥5,000 (2 orders, ⭐4.5)
   
   Follow-up Due:
   - Client C — 7-day check-in (delivered Feb 4)
   - Client D — 30-day follow-up (delivered Jan 11)
   ```

## Platform-Specific Notes

| Platform | Client ID Format | Fee | Communication |
|----------|-----------------|-----|---------------|
| Coconala | Order number | 22% | In-platform DM |
| Fiverr | Username | 20% | In-platform chat |
| Upwork | Contract ID | 10-20% | In-platform chat |
| Direct | Email/name | 0% | Email |

## Security

- **Never store payment details** — platforms handle payments
- **Anonymize in logs** — use client IDs, not real names in shared files
- **Platform rules** — don't contact clients outside platform (ToS violation)
- **GDPR/privacy** — delete client data if requested

## Requirements

- File system access for `~/.openclaw/crm/`
- `jq` for querying JSONL files
- No external API keys needed

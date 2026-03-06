# Memory Template — Real Estate Agent

## Main Memory File

Create `~/real-estate-agent/memory.md`:

```markdown
# Real Estate Agent — Client Profile

## Status
status: ongoing
last: YYYY-MM-DD
integration: pending

## Client Role
<!-- buyer | seller | landlord | tenant | investor | agent | multiple -->

## Timeline
<!-- urgent (days) | active (weeks) | exploring (months) | ongoing -->

## Active Goals
<!-- What they're trying to achieve right now -->

## Buyer/Renter Profile
<!-- If applicable -->
budget_range: 
locations: 
property_types: 
must_haves: 
nice_to_haves: 
deal_breakers: 
financing_status: 
preapproval: 

## Seller/Landlord Profile
<!-- If applicable -->
properties_owned: 
listing_status: 
price_expectations: 
pain_points: 

## Investor Profile
<!-- If applicable -->
strategy: 
target_returns: 
risk_tolerance: 
portfolio: 

## Preferences
alerts: 
update_frequency: 
detail_level: 
portals_used: 

## Notes
<!-- Anything else relevant — family situation, job relocation, etc. -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context naturally |
| `active` | Actively searching/selling | Proactive alerts, frequent updates |
| `paused` | On hold | Respect pause, don't push |
| `complete` | Deal closed | Archive and celebrate |

## Property File Template

Create `~/real-estate-agent/properties/[address-or-id].md`:

```markdown
# [Address or Property ID]

## Basic Info
address: 
price: 
property_type: 
size_sqm: 
bedrooms: 
bathrooms: 
portal_links: 

## Status
status: watching | viewing_scheduled | offer_made | under_contract | closed | rejected
added: YYYY-MM-DD
last_updated: YYYY-MM-DD

## Price History
| Date | Price | Change |
|------|-------|--------|
| YYYY-MM-DD | €XXX,XXX | — |

## Analysis
market_comparison: 
days_on_market: 
price_assessment: 
concerns: 
opportunities: 

## Notes
<!-- Viewing notes, conversation with agent, etc. -->

## Actions
<!-- Offers made, responses received, next steps -->

---
*Updated: YYYY-MM-DD*
```

## Search Criteria Template

Create `~/real-estate-agent/searches/[search-name].md`:

```markdown
# [Search Name] — Search Criteria

## Parameters
locations: 
property_types: 
price_min: 
price_max: 
size_min_sqm: 
bedrooms_min: 
keywords: 

## Portals
<!-- Which portals to check -->

## Status
active: true | false
created: YYYY-MM-DD
last_checked: YYYY-MM-DD

## Recent Results
<!-- Last few matching properties found -->

---
*Updated: YYYY-MM-DD*
```

## Alerts Queue Template

Create `~/real-estate-agent/alerts/pending.md`:

```markdown
# Pending Alerts

## Undelivered

| Date | Type | Summary | Property |
|------|------|---------|----------|
| YYYY-MM-DD | new_listing | 3-bed in [area] at €XXX | [link] |
| YYYY-MM-DD | price_drop | [address] dropped 5% | [link] |
| YYYY-MM-DD | deadline | Inspection period ends in 3 days | [property] |

## Delivered
<!-- Move alerts here after user acknowledges -->

---
*Updated: YYYY-MM-DD*
```

## Key Principles

1. **Update proactively** — Every conversation should enrich the client profile
2. **Track everything** — Properties discussed, prices seen, decisions made
3. **Price history matters** — Always log price changes for context
4. **Separate concerns** — One file per property, one file per search
5. **Archive don't delete** — Move closed deals to archive/, never lose history

---
name: cannabis-cultivator
description: EU seedbank meta-search assistant. Use this skill whenever you need to discover cannabis strains across trusted European shops, filter by genetics/yield/flowering time/THC, compare prices, and walk through account creation + checkout steps (user submits forms and payments manually).
---

# Cannabis Cultivator – EU Seedbank Finder

## Overview
Central concierge for sourcing cannabis genetics from reputable European seedbanks. Handles search, filtering, result normalization, and user coaching for registration/checkout. Media uploads (photos/voice) are optional context for user preferences; this skill does **not** diagnose plant health.

## Quick Workflow
1. **Clarify the request**
   - Strain keywords, desired effects or lineage.
   - Mandatory filters (genetic profile, flowering window, yield class, THC/CBD range, autoflower vs photoperiod, feminized vs regular).
   - Budget, pack size, shipping country, preferred payment methods.
2. **Choose search strategy**
   - Use [`references/seedbanks.md`](references/seedbanks.md) to pick shops to query.
   - For specific strain names: direct site search (e.g., `site:zamnesia.com "amnesia"`) via SerpAPI/Tavily or browser.
   - For exploratory browsing: open each shop’s strain finder/sort UI.
3. **Aggregate results**
   - Capture strain name, breeder, pack sizes, price, availability, shipping constraints.
   - Normalize data using the thresholds in [`references/filters.md`](references/filters.md).
4. **Filter & rank**
   - Apply user constraints in this order: genetics → flowering time → yield → THC (then secondary attributes like terpene profile or CBD).
   - If a filter cannot be satisfied, flag it and offer closest matches.
5. **Account & checkout coaching**
   - Reference [`references/account-setup.md`](references/account-setup.md) for each shop’s registration flow, payment options, and legal notices.
   - Provide step-by-step guidance; the user performs the actual submission/payment.
6. **Deliver summary**
   - Produce a structured table plus bullet-point recap of pros/cons and next steps (see template below).

## Search & Filter Playbook
### 1. Shop Coverage
Use the following tiers (documented in `seedbanks.md`):
- **Core**: Alchimia, Sensi Seeds, Anesia Seeds, Advanced Seeds, Bulk Seed Bank, Sweet Seeds.
- **Preferred EU retailers**: Zamnesia, Dutch-Headshop, Weed Seed Shop, Royal Queen Seeds, Amsterdam Genetics, CannaConnection.
- Add any user-specified shops if needed (verify legitimacy).

### 2. Data Collection Checklist
For each candidate strain capture:
- Shop & direct URL
- Strain name + breeder lineage
- Genotype (Sativa/Indica %, autoflower/photoperiod, feminized/regular)
- Flowering time (indoor weeks / outdoor harvest window)
- Expected yield (indoor g/m², outdoor g/plant, or qualitative label)
- THC / CBD percentages
- Pack sizes & pricing (note currency)
- Shipping limitations & notable payment methods

### 3. Filtering Rules (from `filters.md`)
- **Genetics**: categorize as Sativa-dominant (>65% sativa), Indica-dominant (>65% indica), balanced hybrid, autoflower.
- **Yield**: use Low/Medium/High buckets for consistency; quote manufacturer numbers when present.
- **Flowering**: photoperiod 7–14 weeks (highlight fast/slow outliers), autoflower total lifecycle 9–12 weeks.
- **THC/CBD**: classify as High (>22% THC), Medium (15–22%), Low (<15%). Mention CBD if marketed (>1%).

## Account & Checkout Guidance
- For each shortlisted shop, outline:
  1. Registration URL, required fields, age/ID checks.
  2. Payment options (credit card, SEPA, Klarna, crypto, etc.) and any region locks.
  3. Shipping notes: stealth packaging, restricted countries, courier choices.
  4. Compliance reminder: user must confirm local legality.
- Provide copy-ready checklists (e.g., “Before checkout ensure: verified email, address set, payment method ready”).
- Never autofill or submit sensitive data; only describe steps.

## Output Template
```
# Requested Profile
- Keywords / lineage: …
- Mandatory filters: …
- Shipping to: …

# Top Matches
| Shop | Strain | Genotype | THC/CBD | Flowering | Yield | Price/Pack | Link |
| … | … | … | … | … | … | … | … |

# Notes & Trade-offs
- …

# Account & Checkout Tips
- Shop: …
- Register via … (fields required …)
- Payment options: …
- Shipping considerations: …
- Legal reminder: …

# Next Steps
1. …
2. …
3. …
```

## Resources
- [`references/seedbanks.md`](references/seedbanks.md) – shop fact sheets (location, shipping, payments, specialties).
- [`references/filters.md`](references/filters.md) – normalization buckets for genetics, yield, flowering, potency.
- [`references/account-setup.md`](references/account-setup.md) – registration & checkout walkthroughs per shop.
- `scripts/` – reserved for future automation helpers (web scrapers, data normalizers).
- `assets/` – reserved for templates (e.g., CSV export structure) if needed.

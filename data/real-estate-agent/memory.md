# Client Memory — Template

> This file is created in `~/real-estate-agent/memory.md` when you first use the skill.
> Contains your client profile, preferences, and active goals.

## Example Entries

```markdown
# Real Estate Agent — Client Profile

## Status
status: active
last: 2026-02-26
integration: done

## Client Role
buyer

## Timeline
active (looking to close within 3 months)

## Active Goals
Find 3-bedroom apartment in Madrid centro, budget 350-400k

## Buyer Profile
budget_range: 350,000 - 400,000 EUR
locations: Madrid Centro, Salamanca, Chamberi
property_types: apartment
must_haves: elevator, natural light, quiet street
nice_to_haves: balcony, parking, storage
deal_breakers: ground floor, busy street, no elevator
financing_status: pre-approved
preapproval: 380,000 EUR from Santander

## Preferences
alerts: yes, when new listings match
update_frequency: daily digest preferred
detail_level: detailed analysis
portals_used: Idealista, Fotocasa

## Notes
Relocating from Barcelona for work
Start date March 15 - needs to close by then or temporary rental
Prefers modern/renovated over character properties
```

## Usage

The agent will:
1. Create this file on first use
2. Update after every conversation
3. Check before any property discussion
4. Add new preferences as they emerge
5. Track all properties discussed and their status

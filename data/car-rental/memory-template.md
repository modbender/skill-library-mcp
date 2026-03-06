# Memory Template — Car Rental

Create `~/car-rental/memory.md` with this structure:

```markdown
# Car Rental Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Preferences
<!-- Add as you learn from conversations -->

### Vehicle
<!-- car class, transmission, fuel type, features -->

### Insurance
<!-- own coverage, preferred options, excess tolerance -->

### Budget
<!-- price sensitivity, willing to pay more for... -->

## Loyalty Programs
<!-- memberships, tiers, benefits -->

## Frequent Locations
<!-- airports, cities, countries they commonly rent in -->

## Active Alerts
<!-- ongoing price monitoring -->

## Past Rentals
<!-- history for context and comparison -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Add info when user shares it |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Search Configuration

For saved searches in `~/car-rental/searches/`:

```markdown
# Search: [Name]

## Details
pickup: Location, Date, Time
return: Location, Date, Time
car_class: economy | compact | midsize | suv | luxury
transmission: auto | manual | any
fuel: petrol | diesel | electric | hybrid | any

## Alert Settings
alert_type: price_drop | availability | deal_quality
threshold: [price or percentage]
frequency: immediate | daily | weekly
active: true | false

## Price History
<!-- snapshots for comparison -->
YYYY-MM-DD: €XX (Site)
YYYY-MM-DD: €XX (Site)

---
*Created: YYYY-MM-DD*
```

## Key Principles

- **Store what user explicitly shares** — preferences, locations, alerts
- **Update `last`** on each use
- **Track price history** to identify good deals

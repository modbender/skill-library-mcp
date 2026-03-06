---
name: property-search
description: Search property.com.au for Australian property research — valuations, sold history, suburb profiles, and property details. Use when researching property values, sale history, or suburb data in Australia via property.com.au. Owned by REA Group — active listings link to realestate.com.au.
---

# property.com.au Property Research

Construct property.com.au URLs for Australian property research. Best for valuations, sold history, and suburb data — not primary listing search. No API key required.

## Property Profile (by address)

Look up any property's history, estimate, and details:

```
https://www.property.com.au/{state}/{suburb}-{postcode}/{street-name}/{number}-pid-{propertyId}/
```

**Street format:** lowercase, hyphens for spaces, abbreviate street types (`st`, `rd`, `ave`, `pl`, `ct`, `dr`, `cres`, `tce`)

### Examples

```
https://www.property.com.au/vic/malvern-3144/como-st/4-pid-6510692/
https://www.property.com.au/vic/armadale-3143/elgin-ave/5-pid-1234567/
```

**Unit/apartment format:** `{unit}-{number}-pid-{id}`
```
https://www.property.com.au/vic/malvern-3144/high-st/203-1269-pid-12345678/
```

## Suburb Profile

Median prices, demographics, schools, transport, market data:

```
https://www.property.com.au/{state}/{suburb}-{postcode}/
```

### Examples

```
https://www.property.com.au/vic/malvern-3144/
https://www.property.com.au/vic/armadale-3143/
```

## Buy Listings (by location)

property.com.au aggregates listings from realestate.com.au. Browse by state or region:

```
https://www.property.com.au/{state}/buy/
https://www.property.com.au/{state}/{suburb}-{postcode}/buy/
```

### Examples

```
https://www.property.com.au/vic/buy/
https://www.property.com.au/vic/malvern-3144/buy/
https://www.property.com.au/vic/melbourne-city-greater-region/buy/
```

**By property type:**
```
https://www.property.com.au/{state}/{suburb}-{postcode}/{type}/buy/
```

Types: `house`, `townhouse`, `apartment-unit`, `villa`, `land`, `acreage`, `rural`, `block-of-units`, `retirement`

Example — townhouses for sale in Malvern:
```
https://www.property.com.au/vic/malvern-3144/townhouse/buy/
```

**Note:** Price and bedroom filters use JS-based UI — they don't persist in the URL. For filtered search, use realestate.com.au instead.

## Sold History

Browse recent sales by suburb:

```
https://www.property.com.au/{state}/{suburb}-{postcode}/sold/
```

Example:
```
https://www.property.com.au/vic/malvern-3144/sold/
```

## Street Browse

See all properties on a street:

```
https://www.property.com.au/{state}/{suburb}-{postcode}/{street-name}/
```

Example:
```
https://www.property.com.au/vic/malvern-3144/como-st/
```

## School Insights

Schools near a suburb, with grades, sector, and student count:

```
https://www.property.com.au/{state}/{suburb}-{postcode}/schools/{school-name}-sid-{schoolId}/
```

School data is shown on suburb profile pages automatically.

## When to Use property.com.au vs Others

| Need | Best site |
|------|-----------|
| **Search listings with filters** | realestate.com.au or domain.com.au |
| **Property value estimate** | property.com.au |
| **Sold price history** | property.com.au |
| **Suburb median prices** | property.com.au or domain.com.au |
| **Compare properties** | realestate.com.au |

## Limitations

- Listing search filters (price, beds, type) are JS-only — not URL-constructable
- Active listings redirect to realestate.com.au
- Property IDs (pid) may need to be discovered via search or suburb browse
- `web_fetch` may be blocked (same REA Group anti-bot as realestate.com.au)

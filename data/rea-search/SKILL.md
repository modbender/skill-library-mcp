---
name: rea-search
description: Search realestate.com.au property listings by constructing search and listing URLs. Use when searching for Australian properties to buy, rent, or sold via realestate.com.au. Supports building filtered search URLs (suburb, price, bedrooms, property type, multiple suburbs) and individual listing URLs.
---

# realestate.com.au Search

Construct realestate.com.au search URLs. No API key required.

## Buy Search URL

```
https://www.realestate.com.au/buy/property-{types}-{filters}-in-{location}/list-{page}
```

### Property types

Join with `+`: `house`, `townhouse`, `unit+apartment`, `villa`, `land`, `rural`, `unitblock`, `acreage`

### Filters (in the path)

- Bedrooms: `with-{n}-bedrooms` (minimum)
- Price: `between-{min}-{max}` (omit min for no floor, omit max for no ceiling)

### Location format

- Single suburb: `{suburb},+{state}+{postcode}`
- Multiple suburbs: separate with `%3b+` (encoded semicolon + space)
- Postcode only: `{postcode}`

### Examples

Townhouses in Malvern:
```
https://www.realestate.com.au/buy/property-townhouse-in-malvern,+vic+3144/list-1
```

3+ bed townhouses in Malvern:
```
https://www.realestate.com.au/buy/property-townhouse-with-3-bedrooms-in-malvern,+vic+3144/list-1
```

Houses + townhouses under $2.5M in Malvern:
```
https://www.realestate.com.au/buy/property-house-townhouse-between-1000000-2500000-in-malvern,+vic+3144/list-1
```

Multiple suburbs with price range:
```
https://www.realestate.com.au/buy/property-house-townhouse-between-1000000-2000000-in-malvern,+vic+3144%3b+armadale,+vic+3143/list-1
```

By postcode only:
```
https://www.realestate.com.au/buy/property-house-townhouse-in-3144/list-1
```

## Sold Properties

Replace `/buy/` with `/sold/`:
```
https://www.realestate.com.au/sold/property-house-in-malvern,+vic+3144/list-1
```

## Individual Listing URL

```
https://www.realestate.com.au/property-{type}-{state}-{suburb}-{listingId}
```

Example:
```
https://www.realestate.com.au/property-house-vic-malvern-143160680
```

## Suburb Profile

```
https://www.realestate.com.au/neighbourhoods/{suburb}-{postcode}-{state}
```

Example:
```
https://www.realestate.com.au/neighbourhoods/malvern-3144-vic
```

## Pagination

Change `/list-1` to `/list-2`, `/list-3`, etc.

## Fetching via web_fetch

Direct fetching is typically blocked (429 rate limit / anti-bot).

**Workaround — use DDG site search:**
```
web_fetch(url="https://lite.duckduckgo.com/lite/?q=site%3Arealestate.com.au+malvern+vic+3144+house+3+bedroom&kl=au-en", extractMode="text", maxChars=8000)
```

This returns REA listing URLs and basic descriptions.

## Limitations

- `web_fetch` on REA pages usually returns 429 (rate limited)
- Anti-bot: TLS fingerprinting, geo-blocking from non-AU IPs
- For browsing results, construct the URL and open in browser
- DDG site search workaround provides URLs but not full listing data

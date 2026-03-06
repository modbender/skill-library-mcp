---
name: Country Info
description: Get country data — population, languages, currencies, capital,
  flag, and more using REST Countries API.
---

# Country Info

Get country data — population, languages, currencies, capital, flag, and more using REST Countries API.

**Category:** education
**API Key Required:** No

## When to use

- User asks about a country (population, capital, language, currency)
- User wants to compare countries
- User asks "what currency does X use?" or "what language do they speak in X?"

## How it works

Base URL: `https://restcountries.com/v3.1`

### 1. Search by name

```bash
curl -s "https://restcountries.com/v3.1/name/france"
```

### 2. Get by country code

```bash
curl -s "https://restcountries.com/v3.1/alpha/GB"
```

### 3. Filter specific fields (reduce response size)

```bash
curl -s "https://restcountries.com/v3.1/name/japan?fields=name,capital,population,currencies,languages,flags"
```

### 4. Search by currency

```bash
curl -s "https://restcountries.com/v3.1/currency/eur"
```

### 5. Search by language

```bash
curl -s "https://restcountries.com/v3.1/lang/spanish"
```

### 6. Get all countries in a region

```bash
curl -s "https://restcountries.com/v3.1/region/europe?fields=name,capital,population"
```

Regions: africa, americas, asia, europe, oceania.

## Examples

**User:** "Tell me about Japan"
→ Query by name. Reply with capital, population, languages, currency, region, flag emoji.

**User:** "What countries use the Euro?"
→ Query by currency/eur. List the countries.

## Constraints

- Free, no key needed, no strict rate limit
- Country names are flexible (partial matches work)
- Some fields are deeply nested — parse carefully

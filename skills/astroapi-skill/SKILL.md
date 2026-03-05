---
name: astroapi-skill
description: >-
  Astrology API: generate natal charts, synastry, composite, transits, solar/lunar
  returns, progressions, directions, planetary positions, house cusps, aspects, lunar
  metrics, horoscopes, analysis reports, SVG/render charts, tarot, numerology, Vedic,
  Chinese astrology, human design, kabbalah, astrocartography, eclipses, palmistry,
  and fixed stars. Use when user asks about birth charts, horoscopes, zodiac signs,
  compatibility, planetary positions, moon phases, transits, astrological calculations,
  tarot readings, numerology, or any esoteric/astrological topic.
license: MIT
compatibility: Requires curl
allowed-tools: Bash(curl:*) Read
version: 1.0.2
metadata:
  openclaw:
    emoji: ⭐
    homepage: https://github.com/astro-api/astroapi-skill
    requires:
      bins: ['curl']
      env: ['ASTROLOGY_API_KEY']
    primaryEnv: ASTROLOGY_API_KEY
---

# Astrology API Skill

## When to Use

Use this skill when the user asks about:

- Birth charts, natal charts, horoscopes
- Zodiac compatibility, synastry, relationship analysis
- Planetary positions, transits, aspects
- Moon phases, lunar metrics, void of course
- Solar/lunar returns, progressions, directions
- Tarot card readings, spreads, interpretations
- Numerology (core numbers, compatibility, comprehensive)
- Vedic astrology (kundli, doshas, dashas, panchang)
- Chinese astrology (bazi, ming gua, feng shui)
- Human design (bodygraph, type, channels, gates)
- Kabbalah (tree of life, birth angels, gematria)
- Astrocartography (relocation, power zones, lines)
- Fixed stars (positions, conjunctions)
- Eclipses (upcoming, natal impact)
- Palmistry (palm analysis, reading)
- Daily/weekly/monthly/yearly horoscopes
- Career, health, spiritual, psychological analysis
- Chart rendering (SVG, PNG images)

## Prerequisites

Before making any API call, verify:

1. `$ASTROLOGY_API_KEY` environment variable is set
2. `curl` is available on PATH

If the API key is missing, ask the user to set it:

```
export ASTROLOGY_API_KEY="your_token_here"
```

## How It Works

1. **Gather data** from the user depending on the request type:
   - For natal/personal: name, birth date (year, month, day), birth time (hour, minute), birth city + country code (2-letter ISO)
   - For synastry/compatibility: birth data for TWO people
   - For transits: natal data + transit date/time
   - For horoscopes by sign: just the zodiac sign name
   - For tarot: question or spread type
   - For numerology: full name + birth date

2. **Call the API** using `{baseDir}/scripts/astro-api.sh`:

   ```
   bash {baseDir}/scripts/astro-api.sh POST /api/v3/charts/natal '{ ... }'
   ```

3. **Present results** in a human-friendly format, highlighting key findings.

## API Call Patterns

### Natal Chart (most common)

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/charts/natal '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {
    "house_system": "P",
    "zodiac_type": "Tropic",
    "language": "EN"
  }
}'
```

### Synastry (compatibility)

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/charts/synastry '{
  "subject": {
    "name": "Person A",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "partner": {
    "name": "Person B",
    "year": 1992, "month": 7, "day": 20,
    "hour": 9, "minute": 0, "second": 0,
    "city": "London", "country_code": "GB"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic", "language": "EN"}
}'
```

### Transit Snapshot

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/charts/transit '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "transit": {
    "year": 2026, "month": 2, "day": 12,
    "hour": 12, "minute": 0, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic", "language": "EN"}
}'
```

### Current Sky Data (no parameters needed)

```bash
bash {baseDir}/scripts/astro-api.sh GET /api/v3/data/now
```

### Planetary Positions

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/data/positions '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic"}
}'
```

### Lunar Metrics

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/data/lunar-metrics '{
  "subject": {
    "name": "now",
    "year": 2026, "month": 2, "day": 12,
    "hour": 12, "minute": 0, "second": 0,
    "city": "New York", "country_code": "US"
  }
}'
```

### Daily Horoscope by Sign

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/horoscope/sign/daily '{
  "sign": "aries",
  "language": "EN"
}'
```

### Personal Daily Horoscope

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/horoscope/personal/daily '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "language": "EN"
}'
```

### Natal Analysis Report (AI-generated interpretation)

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/analysis/natal-report '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic", "language": "EN"}
}'
```

### Render Chart as SVG

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/svg/natal '{
  "subject": {
    "name": "John",
    "year": 1990, "month": 3, "day": 15,
    "hour": 14, "minute": 30, "second": 0,
    "city": "New York", "country_code": "US"
  },
  "options": {"house_system": "P", "zodiac_type": "Tropic"}
}'
```

### Tarot Card Draw

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/tarot/cards/draw '{
  "count": 3
}'
```

### Numerology Core Numbers

```bash
bash {baseDir}/scripts/astro-api.sh POST /api/v3/numerology/core-numbers '{
  "full_name": "John Smith",
  "birth_date": "1990-03-15"
}'
```

> **Full endpoint reference:** Read `{baseDir}/references/api-endpoints.md` for all 190+ endpoints with detailed parameters.

## Default Options

When the user doesn't specify preferences, use these defaults:

- **House system:** `P` (Placidus) — most common in Western astrology
- **Zodiac type:** `Tropic` (Tropical) — Western standard
- **Language:** `EN` (English) — override based on user's language
- **Tradition:** `universal` — broadest coverage

## Output Format

When presenting results to the user:

1. **Start with the highlights**: Sun sign, Moon sign, Ascendant (Rising)
2. **Use plain language** — translate astrological jargon
3. **Format positions as tables** when showing multiple planets
4. **Highlight notable aspects** (conjunctions, oppositions, squares, trines)
5. **For compatibility**: lead with the overall score/summary
6. **For horoscopes**: present the text naturally, don't dump raw JSON
7. **For chart images (SVG/render)**: save to a file and inform the user

## Edge Cases

- **Birth time unknown**: Use noon (12:00) and note that house positions and Moon degree may be less accurate
- **City not found**: Ask for latitude/longitude instead. Use `latitude` and `longitude` fields instead of `city`/`country_code`
- **API errors (400/422)**: Parse the error message and explain to the user what's wrong (e.g., invalid date, missing field)
- **Large responses**: For analysis reports, summarize the key points rather than showing everything
- **Language support**: The API supports EN, RU, FR, DE, ES, IT, PT, and more — match the user's language when possible

---
name: aviation-agent
description: Aviation weather briefing and FAA reference assistant for pilots. Fetches real-time METAR, TAF, and PIREPs from aviationweather.gov (no API key required). Provides FAR Part 61/91 quick reference, VFR/IFR weather minimums, and go/no-go decision support. Use when user asks about METAR, TAF, PIREP, aviation weather, can I fly today, VFR/IFR conditions, flight weather briefing, FAR regulations for pilots, PPL/IFR training weather, or queries with ICAO airport codes.
---

# Aviation Agent

Aviation weather briefing and FAA reference assistant. Fetches live weather data from aviationweather.gov and provides FAR/AIM quick reference for flight planning and go/no-go decisions.

## Quick Start

```bash
# Get current METAR for Los Angeles International
python3 scripts/metar.py --metar KLAX

# Full briefing: METAR + TAF forecast for two airports
python3 scripts/metar.py --metar KLAX KSFO --taf KLAX KSFO

# Check PIREPs (pilot reports) near Chicago O'Hare, last 4 hours
python3 scripts/metar.py --pirep KORD --hours 4
```

## scripts/metar.py — Weather Data Fetcher

Queries the aviationweather.gov public API (no API key needed). Returns formatted, decoded weather reports with flight category classification.

### Arguments

| Flag | Description | Example |
|------|-------------|---------|
| `--metar ICAO [ICAO ...]` | Fetch current METAR for one or more airports | `--metar KLAX KJFK` |
| `--taf ICAO [ICAO ...]` | Fetch TAF forecast for one or more airports | `--taf KORD` |
| `--pirep ICAO` | Fetch PIREPs within 200 nm of airport | `--pirep KSFO` |
| `--hours N` | Hours of data to retrieve (1-24, default: 2) | `--hours 6` |

Flags can be combined in a single call:
```bash
python3 scripts/metar.py --metar KLAX --taf KLAX --pirep KLAX --hours 3
```

### Output Includes

- Raw report text and decoded fields
- Wind direction/speed/gusts, visibility, cloud layers
- Weather phenomena decoded to plain English (e.g., `+TSRA` -> Heavy Thunderstorm Rain)
- Automatic flight category classification (VFR/MVFR/IFR/LIFR)
- Temperature, dewpoint, altimeter setting

### ICAO Code Format

Codes must be exactly 4 uppercase letters. Common US airports use `K` prefix (e.g., `KLAX`, `KJFK`, `KORD`). International examples: `EGLL` (London Heathrow), `RJTT` (Tokyo Haneda).

## When to Read Which Reference

| User Question | Read This File |
|---------------|----------------|
| "What does BKN025 mean?" / "Decode this METAR" | `references/metar-codes.md` |
| "What does TEMPO mean in this TAF?" / "Explain TAF format" | `references/taf-codes.md` |
| "How many landings do I need to be current?" / "What are VFR minimums in Class D?" | `references/far-quickref.md` |
| "Can I fly today?" / "Is this weather safe for a student pilot?" | `references/decision-guide.md` |
| Go/no-go decision with specific weather data | Run `scripts/metar.py` first, then read `references/decision-guide.md` |

For a full weather briefing workflow:
1. Run `scripts/metar.py` with `--metar` and `--taf` for the departure and destination airports
2. Run `scripts/metar.py` with `--pirep` to check for turbulence/icing reports
3. Read `references/decision-guide.md` to evaluate the weather against personal minimums
4. Read `references/far-quickref.md` if the user needs regulatory specifics

## Flight Category Legend

| Category | Ceiling | Visibility | Marker | Meaning |
|----------|---------|------------|--------|---------|
| **VFR** | > 3,000 ft AGL | > 5 SM | Green | Visual flight rules — clear conditions |
| **MVFR** | 1,000 – 3,000 ft | 3 – 5 SM | Blue | Marginal VFR — proceed with caution |
| **IFR** | 500 – 999 ft | 1 – < 3 SM | Red | Instrument flight rules required |
| **LIFR** | < 500 ft | < 1 SM | Magenta | Low IFR — extremely restricted visibility |

The **more restrictive** of ceiling or visibility determines the category. For example, 10 SM visibility but a 900 ft ceiling is **IFR** (ceiling is the limiting factor).

**Ceiling** is defined as the lowest cloud layer reported as BKN (Broken) or OVC (Overcast). FEW and SCT layers are not ceilings.

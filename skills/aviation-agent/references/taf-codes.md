# TAF Code Reference

## TAF Format Overview

TAF (Terminal Aerodrome Forecast) provides a 24-30 hour weather forecast for an airport within a 5 SM radius.

```
TAF KLAX 251130Z 2512/2618 25010KT P6SM FEW250
     │    │       │         │       │    │
     │    │       │         │       │    Cloud layers
     │    │       │         │       Visibility
     │    │       │         Wind
     │    │       Valid period (from/to)
     │    Issue time (DDHHMMz)
     Station ICAO
```

## Time Format — DDHHhh

TAFs use `DDHHhh` to denote time ranges:
- **DD** = Day of the month
- **HH** = Start hour (UTC)
- **hh** = End hour (UTC)

Example: `2512/2618` = valid from 25th day 12:00Z to 26th day 18:00Z

Issue time uses standard `DDHHMMz` format: `251130Z` = 25th day at 11:30 UTC.

## Change Indicators

### FM — From (Permanent Change)

A complete, permanent change in conditions at the specified time.

```
FM251800 31015G25KT P6SM SKC
```
From 25th at 18:00Z: wind 310° at 15 gusting 25 kt, visibility >6 SM, sky clear.

**Key**: All conditions after FM replace the previous forecast entirely.

### TEMPO — Temporary (< 60 minutes)

Temporary fluctuations expected to last less than 60 minutes each occurrence, and in aggregate less than half the period.

```
TEMPO 2512/2516 3SM -SHRA BKN020
```
Between 12Z and 16Z on 25th: temporarily 3 SM visibility with light rain showers and broken clouds at 2,000 ft.

### BECMG — Becoming (Gradual Change)

Conditions gradually changing during the specified period and remaining changed thereafter.

```
BECMG 2514/2516 21012KT 4SM BR
```
Between 14Z and 16Z on 25th: wind gradually shifting to 210° at 12 kt, visibility decreasing to 4 SM in mist, and remaining that way.

### INTER — Intermittent (ICAO)

Similar to TEMPO but used in some ICAO regions. Intermittent conditions that may occur for brief periods.

```
INTER 2506/2510 2SM TSRA BKN010CB
```
Between 06Z and 10Z on 25th: intermittently 2 SM with thunderstorms and rain.

## Probability Codes

### PROB30

30% probability of the stated conditions occurring during the time period. Generally not used for flight planning as threshold of occurrence is low.

```
PROB30 2502/2506 1SM +TSRA
```
30% chance between 02Z and 06Z on 25th: 1 SM visibility with heavy thunderstorms and rain.

### PROB40

40% probability of the stated conditions. Worth noting in flight planning; consider as a possible scenario.

```
PROB40 2518/2524 2SM -FZRA OVC010
```
40% chance between 18Z on 25th and 00Z on 26th: 2 SM with light freezing rain and overcast at 1,000 ft.

**Note**: PROB30 and PROB40 are only used with TEMPO in US TAFs. Probabilities below 30% or above 50% are not issued — conditions above 50% probability become the base forecast.

## Wind Shear (WS)

Low-level wind shear forecast below 2,000 ft AGL.

```
WS020/18040KT
│     │
│     Wind at shear altitude: 180° at 40 kt
Shear altitude: 2,000 ft AGL (hundreds of feet)
```

Example in context:
```
FM251200 VRB03KT P6SM SKC WS010/21045KT
```
From 12Z on 25th: surface wind variable at 3 kt, but wind shear at 1,000 ft AGL with 210° at 45 kt.

## Visibility in TAF

| Format | Meaning |
|--------|---------|
| `P6SM` | Greater than 6 SM |
| `6SM` | Exactly 6 SM |
| `3SM` | 3 SM |
| `1/2SM` | Half SM |
| `M1/4SM` | Less than 1/4 SM |

## Complete TAF Example — Line by Line

```
TAF KJFK 251130Z 2512/2618 33012G22KT P6SM SCT040 BKN250
     FM252000 28008KT P6SM FEW050
     TEMPO 2520/2602 4SM -SHRA BKN030
     FM260200 21015KT 3SM BR OVC015
     BECMG 2608/2610 P6SM SCT025
     PROB40 2604/2608 1SM +TSRA OVC008CB
```

### Line-by-line decode:

**Line 1 — Header & Initial Forecast**
`TAF KJFK 251130Z 2512/2618 33012G22KT P6SM SCT040 BKN250`
- Station: KJFK (JFK International)
- Issued: 25th at 11:30Z
- Valid: 25th 12:00Z through 26th 18:00Z
- Initial: Wind 330° at 12 kt gusting 22 kt, visibility >6 SM, scattered clouds at 4,000 ft, broken at 25,000 ft
- Category: **VFR**

**Line 2 — FM (Permanent Change)**
`FM252000 28008KT P6SM FEW050`
- From 25th at 20:00Z: wind shifts to 280° at 8 kt, visibility >6 SM, few clouds at 5,000 ft
- Category: **VFR**

**Line 3 — TEMPO (Temporary)**
`TEMPO 2520/2602 4SM -SHRA BKN030`
- Between 20:00Z on 25th and 02:00Z on 26th: temporarily 4 SM with light rain showers, broken at 3,000 ft
- Temporary category: **MVFR**

**Line 4 — FM (Permanent Change)**
`FM260200 21015KT 3SM BR OVC015`
- From 26th at 02:00Z: wind 210° at 15 kt, visibility 3 SM in mist, overcast at 1,500 ft
- Category: **MVFR**

**Line 5 — BECMG (Gradual Change)**
`BECMG 2608/2610 P6SM SCT025`
- Between 08Z and 10Z on 26th: visibility gradually improving to >6 SM, clouds breaking to scattered at 2,500 ft
- Category: **MVFR** (ceiling at 2,500 ft is still ≤ 3,000 ft)

**Line 6 — PROB40**
`PROB40 2604/2608 1SM +TSRA OVC008CB`
- 40% chance between 04Z and 08Z on 26th: 1 SM with heavy thunderstorms and rain, overcast at 800 ft with cumulonimbus
- If it occurs: **IFR** — avoid this weather

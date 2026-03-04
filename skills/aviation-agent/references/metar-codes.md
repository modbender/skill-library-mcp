# METAR Code Reference

## METAR Format

```
METAR KJFK 251753Z 31015G25KT 10SM FEW040 SCT250 05/M03 A3012 RMK AO2 SLP205
│     │    │        │           │    │          │       │     │
│     │    │        │           │    │          │       │     Remarks
│     │    │        │           │    │          │       Altimeter (inHg×100)
│     │    │        │           │    │          Temp/Dewpoint (°C)
│     │    │        │           │    Cloud layers
│     │    │        │           Visibility (SM)
│     │    │        Wind (dir/speed/gust in KT)
│     │    Day+Time (DDHHMMz)
│     Station ICAO
Report type
```

## Wind

| Format | Meaning |
|--------|---------|
| `31015KT` | From 310° at 15 knots |
| `31015G25KT` | From 310° at 15 gusting 25 knots |
| `VRB03KT` | Variable direction at 3 knots |
| `00000KT` | Calm |
| `180V240` | Wind direction variable between 180° and 240° |

## Visibility

| Format | Meaning |
|--------|---------|
| `10SM` | 10 statute miles |
| `P6SM` | Greater than 6 SM (TAF) |
| `1/2SM` | Half statute mile |
| `1 1/4SM` | 1.25 statute miles |
| `M1/4SM` | Less than 1/4 SM |
| `R24L/4000FT` | Runway 24L RVR 4000 feet |

## Cloud Cover

| Code | Meaning | Coverage (oktas) |
|------|---------|-----------------|
| `SKC` | Sky Clear (manual) | 0 |
| `CLR` | Clear (automated, no clouds below 12,000 ft) | 0 |
| `FEW` | Few | 1-2/8 |
| `SCT` | Scattered | 3-4/8 |
| `BKN` | Broken | 5-7/8 |
| `OVC` | Overcast | 8/8 |
| `VV` | Vertical Visibility (sky obscured) | N/A |

Cloud height is AGL in hundreds of feet: `BKN025` = Broken at 2,500 ft AGL.

### Cloud Types
| Suffix | Meaning |
|--------|---------|
| `CB` | Cumulonimbus |
| `TCU` | Towering Cumulus |

## Weather Phenomena

### Intensity Prefix
| Symbol | Meaning |
|--------|---------|
| `-` | Light |
| (none) | Moderate |
| `+` | Heavy |
| `VC` | In the Vicinity (5-10 SM) |

### Descriptor
| Code | Meaning |
|------|---------|
| `MI` | Shallow |
| `PR` | Partial |
| `BC` | Patches |
| `DR` | Low Drifting |
| `BL` | Blowing |
| `SH` | Showers |
| `TS` | Thunderstorm |
| `FZ` | Freezing |

### Precipitation
| Code | Meaning |
|------|---------|
| `RA` | Rain |
| `DZ` | Drizzle |
| `SN` | Snow |
| `SG` | Snow Grains |
| `IC` | Ice Crystals |
| `PL` | Ice Pellets |
| `GR` | Hail (≥ 1/4 inch) |
| `GS` | Small Hail / Snow Pellets |
| `UP` | Unknown Precipitation (automated) |

### Obscuration
| Code | Meaning |
|------|---------|
| `FG` | Fog (visibility < 5/8 SM) |
| `BR` | Mist (visibility ≥ 5/8 SM) |
| `HZ` | Haze |
| `FU` | Smoke |
| `SA` | Sand |
| `DU` | Widespread Dust |
| `VA` | Volcanic Ash |
| `PY` | Spray |

### Other
| Code | Meaning |
|------|---------|
| `SQ` | Squall |
| `FC` | Funnel Cloud / Tornado / Waterspout |
| `SS` | Sandstorm |
| `DS` | Duststorm |
| `PO` | Dust/Sand Whirls |

### Common Combinations
| Code | Meaning |
|------|---------|
| `+TSRA` | Heavy Thunderstorm with Rain |
| `-FZRA` | Light Freezing Rain |
| `FZFG` | Freezing Fog |
| `-SHRA` | Light Rain Showers |
| `BLSN` | Blowing Snow |
| `+FZRA` | Heavy Freezing Rain (hazardous) |
| `VCSH` | Showers in Vicinity |

## Temperature / Dewpoint

Format: `TT/DD` in Celsius. Prefix `M` = minus.
- `05/M03` → Temp 5°C, Dewpoint -3°C
- `M02/M05` → Temp -2°C, Dewpoint -5°C

**Spread rule**: When temp/dewpoint spread ≤ 3°C, expect fog or low visibility.

## Altimeter Setting

Format: `Axxxx` (inHg × 100)
- `A3012` → 30.12 inHg
- `A2992` → 29.92 inHg (standard pressure)

## Flight Categories

| Category | Ceiling | Visibility | Color |
|----------|---------|------------|-------|
| **VFR** | > 3,000 ft AGL | > 5 SM | Green |
| **MVFR** | 1,000-3,000 ft | 3-5 SM | Blue |
| **IFR** | 500-999 ft | 1-<3 SM | Red |
| **LIFR** | < 500 ft | < 1 SM | Magenta |

**Ceiling** = lowest BKN or OVC layer (not FEW or SCT).

## Common Remarks (RMK)

| Code | Meaning |
|------|---------|
| `AO1` | Automated, no precipitation discriminator |
| `AO2` | Automated, with precipitation discriminator |
| `SLPxxx` | Sea Level Pressure (hPa, add 10 or 9 prefix) |
| `Txxxxxxx` | Precise temp/dewpoint (tenths °C) |
| `$` | Station needs maintenance |
| `PRESRR` | Pressure rising rapidly |
| `PRESFR` | Pressure falling rapidly |
| `VIRGA` | Precipitation not reaching ground |
| `CIG xxx V xxx` | Ceiling variable between values |

---
name: unit-convert
description: "Comprehensive unit converter for length, weight, temperature, area, volume, speed, time, and data. Use when: (1) converting between measurement units, (2) calculating unit equivalencies, (3) working with different measurement systems, or (4) any unit conversion needs. Supports metric, imperial, and digital units."
---

# Unit Converter

Convert between different measurement units. Supports length, weight, temperature, area, volume, speed, time, and data units.

## When to Use

- Convert between metric and imperial units
- Calculate unit equivalencies
- Work with different measurement systems
- Convert digital storage sizes

## Quick Start

### Basic Conversions
```bash
python3 scripts/unit-convert.py 100 cm m
# Output: 100 cm = 1 m

python3 scripts/unit-convert.py 10 kg lb
# Output: 10 kg = 22.05 lb

python3 scripts/unit-convert.py 25 C F
# Output: 25 C = 77 F
```

### List Units
```bash
python3 scripts/unit-convert.py list length
# Shows all length units
```

### Show Categories
```bash
python3 scripts/unit-convert.py categories
```

## Commands

### `<value> <from_unit> <to_unit>`
Convert between units.

**Examples:**
```bash
# Length
python3 scripts/unit-convert.py 100 cm m
python3 scripts/unit-convert.py 5 ft cm
python3 scripts/unit-convert.py 1 mi km

# Weight
python3 scripts/unit-convert.py 10 kg lb
python3 scripts/unit-convert.py 1000 g kg
python3 scripts/unit-convert.py 16 oz lb

# Temperature
python3 scripts/unit-convert.py 25 C F
python3 scripts/unit-convert.py 98.6 F C
python3 scripts/unit-convert.py 300 K C

# Area
python3 scripts/unit-convert.py 100 m2 ft2
python3 scripts/unit-convert.py 1 acre m2

# Volume
python3 scripts/unit-convert.py 1000 ml l
python3 scripts/unit-convert.py 1 gal l

# Speed
python3 scripts/unit-convert.py 100 km/h mph
python3 scripts/unit-convert.py 10 m/s km/h

# Time
python3 scripts/unit-convert.py 3600 s h
python3 scripts/unit-convert.py 7 day h

# Data
python3 scripts/unit-convert.py 1024 B KB
python3 scripts/unit-convert.py 1 GB MB
```

### `list <category>`
List all units in a category.

**Examples:**
```bash
python3 scripts/unit-convert.py list length
python3 scripts/unit-convert.py list weight
python3 scripts/unit-convert.py list temperature
```

### `categories`
Show all supported categories.

```bash
python3 scripts/unit-convert.py categories
```

### `help <category>`
Show help for a specific category.

```bash
python3 scripts/unit-convert.py help temperature
python3 scripts/unit-convert.py help length
```

## Supported Categories

### Length
- **Metric**: mm, cm, m, km
- **Imperial**: in, ft, yd, mi, inch, foot, yard, mile

### Weight
- **Metric**: mg, g, kg, t (tonne)
- **Imperial**: oz, lb, stone, ounce, pound

### Temperature
- **C** - Celsius
- **F** - Fahrenheit
- **K** - Kelvin

### Area
- **Metric**: mm², cm², m², km²
- **Imperial**: in², ft², yd², acre, mi²

### Volume
- **Metric**: ml, l, kl
- **Imperial**: fl oz, cup, pt, qt, gal

### Speed
- **Metric**: m/s, km/h
- **Imperial**: ft/s, mph
- **Nautical**: knot

### Time
- **Short**: ms, s, min
- **Long**: h, day, week, year

### Data
- **Binary**: B, KB, MB, GB, TB, PB
- (Uses 1024-based conversion)

## Unit Aliases

The converter accepts common aliases:

| Standard | Aliases |
|----------|---------|
| in | inch, inches |
| ft | foot, feet |
| yd | yard, yards |
| mi | mile, miles |
| oz | ounce, ounces |
| lb | pound, pounds |
| pt | pint, pints |
| qt | quart, quarts |
| gal | gallon, gallons |
| ml | milliliter, milliliters |
| l | liter, liters |
| kl | kiloliter, kiloliters |
| h | hour, hours |
| min | minute, minutes |
| s | second, seconds |
| ms | millisecond, milliseconds |

## Examples

### Everyday Conversions
```bash
# Height conversions
python3 scripts/unit-convert.py 180 cm ft
python3 scripts/unit-convert.py 6 ft cm

# Weight conversions
python3 scripts/unit-convert.py 70 kg lb
python3 scripts/unit-convert.py 150 lb kg

# Temperature
python3 scripts/unit-convert.py 32 F C
python3 scripts/unit-convert.py 100 C F

# Area (room size)
python3 scripts/unit-convert.py 100 m2 ft2
python3 scripts/unit-convert.py 1000 ft2 m2
```

### Cooking & Recipes
```bash
# Volume conversions
python3 scripts/unit-convert.py 1 cup ml
python3 scripts/unit-convert.py 250 ml cup
python3 scripts/unit-convert.py 1 gal l

# Weight conversions
python3 scripts/unit-convert.py 500 g lb
python3 scripts/unit-convert.py 1 lb g
```

### Travel & Distance
```bash
# Distance
python3 scripts/unit-convert.py 100 km mi
python3 scripts/unit-convert.py 50 mi km

# Speed limits
python3 scripts/unit-convert.py 60 mph km/h
python3 scripts/unit-convert.py 100 km/h mph
```

### Digital Storage
```bash
# File sizes
python3 scripts/unit-convert.py 1 GB MB
python3 scripts/unit-convert.py 1024 KB MB
python3 scripts/unit-convert.py 1 TB GB
```

### Science & Engineering
```bash
# Precise measurements
python3 scripts/unit-convert.py 25.4 mm in
python3 scripts/unit-convert.py 1000 mg g

# Time calculations
python3 scripts/unit-convert.py 365 day h
python3 scripts/unit-convert.py 86400 s day
```

## Tips

- Use the `list` command to see all available units for a category
- Temperature units are case-sensitive (C, F, K)
- For compound units like m/s, use the slash notation
- The converter handles both short and long unit names
- Results are formatted for readability

## Troubleshooting

**"Cannot convert" error:**
- Check unit spelling
- Ensure units are from the same category (e.g., don't convert length to weight)
- Use `list` command to see available units

**Unexpected results:**
- Temperature conversions use standard formulas
- Data conversions use 1024-based (binary) units
- Double-check unit case sensitivity

## Notes

- Temperature conversions use standard formulas
- Data conversions use binary (1024-based) units
- All other conversions use decimal (1000-based) units
- Results are automatically formatted for readability

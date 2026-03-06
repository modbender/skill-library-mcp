---
name: seasonal-planting-guide
description: "Seasonal planting calendar for gardeners. Find what to plant each
  month in your growing zone. Use when planning your garden, checking planting
  schedules, or finding plants for the current season. Security: file exports
  restricted to safe directories. Perfect for home gardeners, small farmers, and
  anyone planning a productive garden."
---


# Seasonal Planting Guide

Plan your garden with region-specific planting schedules for every month.

## Quick Start

### See what to plant this month
```bash
seasonal_planting.py now --zone "8a"
```

### Get planting calendar for a month
```bash
seasonal_planting.py month --month "april" --zone "6b"
```

### Get full year calendar
```bash
seasonal_planting.py year --zone "7a"
```

### Search for plants
```bash
seasonal_planting.py search "tomato"
```

### Get plant details
```bash
seasonal_planting.py show "tomato"
```

### Add custom plants to your calendar
```bash
seasonal_planting.py add "tomato" --planting "april,may" --zone "6a,6b,7a,7b,8a,8b"
```

## Usage Patterns

### For new gardeners
```bash
# Check what to plant right now
seasonal_planting.py now --zone "7a"

# Get full calendar for your zone
seasonal_planting.py year --zone "7a"

# Learn about specific plants
seasonal_planting.py show "lettuce"
seasonal_planting.py show "tomato"
```

### For experienced gardeners planning ahead
```bash
# Check what to plant next month
seasonal_planting.py month --month "may" --zone "7a"

# Plan succession planting
seasonal_planting.py month --month "april" --zone "7a"
seasonal_planting.py month --month "june" --zone "7a"

# Add your local varieties
seasonal_planting.py add "local-corn" --planting "may,june" --zone "7a" --notes "Silver Queen variety"
```

### For small farmers
```bash
# Get full production schedule
seasonal_planting.py year --zone "6b" > planting-schedule.txt

# Plan staggered planting
seasonal_planting.py month --month "march" --zone "6b"  # Early crops
seasonal_planting.py month --month "april" --zone "6b"  # Main crops
seasonal_planting.py month --month "may" --zone "6b"   # Late crops

# Export calendar for team
seasonal_planting.py year --zone "6b" --export "~/farm-calendar.md"
```

### For container/indoor gardeners
```bash
# Search for container-friendly plants
seasonal_planting.py search "lettuce"
seasonal_planting.py search "herbs"

# Check planting windows
seasonal_planting.py show "basil"
```

## Planting Zones

Understanding your **USDA Hardiness Zone** helps plan correctly:

| Zone | Temperature | Typical Plants |
|------|-------------|----------------|
| 3-4 | Very cold | Kale, peas, lettuce, carrots |
| 5-6 | Cold | Tomatoes, peppers, beans, squash |
| 7-8 | Mild | Tomatoes, peppers, eggplant, corn |
| 9-10 | Warm | Year-round growing, tropical plants |
| 11+ | Tropical | Everything year-round |

**How to find your zone:**
- Search online for "USDA hardiness zone [your city]"
- Most garden resources reference zones
- Use neighboring zone if unsure

## Plant Categories

### Cool-Season Crops
Plant in spring (March-May) or fall (August-October):
- Lettuce, spinach, kale, arugula
- Peas, radishes, carrots
- Broccoli, cauliflower, Brussels sprouts

### Warm-Season Crops
Plant after last frost (May-June):
- Tomatoes, peppers, eggplant
- Beans, corn, squash
- Cucumbers, melons, zucchini

### Herbs (Year-Round or Seasonal)
- Perennial: Rosemary, thyme, oregano, sage, chives
- Annual: Basil, cilantro, dill, parsley

### Root Vegetables
- Early spring: Radishes, turnips
- Mid-season: Carrots, beets, parsnips
- Late season: Garlic (fall planting), onions

## Examples

### Spring garden planning
```bash
# Zone 6b - April
seasonal_planting.py month --month "april" --zone "6b"
# Output: tomatoes, peppers, beans, squash, cucumbers

# Zone 8a - April
seasonal_planting.py month --month "april" --zone "8a"
# Output: tomatoes, peppers, eggplant, corn, okra (earlier start)

# Plan succession planting
seasonal_planting.py month --month "april" --zone "6b"
seasonal_planting.py month --month "may" --zone "6b"
seasonal_planting.py month --month "june" --zone "6b"
```

### Fall garden planning
```bash
# Zone 7a - August (fall crops)
seasonal_planting.py month --month "august" --zone "7a"
# Output: lettuce, spinach, kale, radishes, peas

# Zone 5a - September (fall crops)
seasonal_planting.py month --month "september" --zone "5a"
# Output: lettuce, spinach, kale, garlic (for overwintering)
```

### Year-round planning
```bash
# Get full calendar for your zone
seasonal_planting.py year --zone "7a"

# Export for reference
seasonal_planting.py year --zone "7a" --export "~/garden-calendar-2026.md"
```

### Adding local knowledge
```bash
# Add your region-specific advice
seasonal_planting.py add "corn" --planting "may,june" --zone "7a" \
  --notes "Silver Queen variety best, plant in blocks for pollination"

# Add heirloom varieties
seasonal_planting.py add "heirloom-tomato" --planting "april,may" --zone "6b,7a" \
  --notes "Brandywine, Cherokee Purple - start indoors 6 weeks before last frost"
```

## Search Features

- Find plants by name or category
- See planting windows for each plant
- Get zone-specific recommendations
- Find similar plants (e.g., "tomato" finds all tomato varieties)

## Security

### Path Validation
The `export` function validates output paths to prevent malicious writes:
- ✅ Allowed: `~/.openclaw/workspace/`, `/tmp/`, and home directory
- ❌ Blocked: System paths (`/etc/`, `/usr/`, `/var/`, etc.)
- ❌ Blocked: Sensitive dotfiles (`~/.bashrc`, `~/.ssh`, etc.)

## Data Storage

- Planting calendar stored in: `~/.openclaw/workspace/planting_calendar.json`
- Custom plants tracked alongside built-in database
- JSON format makes it easy to backup or extend
- Zone-specific recommendations for each plant

## Best Practices

1. **Know your zone** - Determines planting windows
2. **Watch last frost date** - Zone is guide, local weather matters
3. **Plan succession planting** - Stagger plantings for continuous harvest
4. **Use plant-tracker** - Combine with plant-tracker skill for full garden management
5. **Add local knowledge** - Customize calendar with regional varieties
6. **Export for reference** - Keep planting schedule handy

## Companion Planting Tips

Combine with **companion planting** for better results:

| Plant | Good Companions | Avoid |
|-------|----------------|--------|
| Tomatoes | Basil, carrots, onions | Cabbage, potatoes |
| Lettuce | Carrots, radishes, strawberries | Parsley |
| Beans | Corn, carrots, cucumbers | Onions, garlic |
| Peppers | Basil, onions, carrots | Fennel, kohlrabi |

## Related Skills

- **plant-tracker** - Manage individual plants, care schedules, harvest tracking
- **garden-layout-planner** (planned) - Design your garden layout

Use together for complete garden management!

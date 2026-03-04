---
name: garden-layout-planner
description: Garden design and layout planning for gardeners. Plan your garden with companion planting, spacing, and sun requirements. Use when designing a new garden, planning crop rotation, or optimizing space. Security: file exports restricted to safe directories. Perfect for home gardeners, small farmers, and anyone maximizing their growing space.
---

# Garden Layout Planner

Design your garden with smart planning tools for companion planting, spacing, and sun requirements.

## Quick Start

### Add a garden bed to your layout
```bash
garden_layout.py add-bed "<bed_name>" --width <feet> --length <feet> --sun "full/partial/shade"
```

### Add plants to a bed
```bash
garden_layout.py add-plant "<bed_name>" "<plant>" --row <row> --col <col>
```

### Get companion planting suggestions
```bash
garden_layout.py companions "<plant>"
```

### Get spacing requirements
```bash
garden_layout.py spacing "<plant>"
```

### Show complete garden layout
```bash
garden_layout.py layout
```

### Export layout to markdown
```bash
garden_layout.py export "<output_file>"
```

## Usage Patterns

### For new garden setup
```bash
# Define your beds
garden_layout.py add-bed "Bed 1" --width 4 --length 8 --sun "full"
garden_layout.py add-bed "Bed 2" --width 3 --length 6 --sun "partial"

# Check companion planting
garden_layout.py companions "tomato"  # Best with basil, carrots, onions
garden_layout.py companions "cucumber"   # Best with beans, corn, peas

# Add plants with proper spacing
garden_layout.py add-plant "Bed 1" "tomato" --row 1 --col 1
garden_layout.py add-plant "Bed 1" "basil" --row 1 --col 3  # Companion!
garden_layout.py add-plant "Bed 2" "beans" --row 1 --col 1
garden_layout.py add-plant "Bed 2" "corn" --row 2 --col 1  # Companion!

# Review your layout
garden_layout.py layout
```

### For companion planting optimization
```bash
# Check what grows well together
garden_layout.py companions "carrots"  # Good with tomatoes, onions, lettuce
garden_layout.py companions "onions"   # Good with carrots, tomatoes, beets

# Avoid bad combinations
garden_layout.py incompatible "potatoes"  # Avoid with tomatoes, cucumbers
```

### For small space maximization
```bash
# Use vertical growing for space efficiency
garden_layout.py add-bed "Trellis" --width 1 --length 6 --sun "full"
garden_layout.py add-plant "Trellis" "cucumber" --row 1 --col 1
garden_layout.py add-plant "Trellis" "peas" --row 2 --col 1

# Intensive planting with succession
garden_layout.py add-bed "Intensive Bed" --width 3 --length 4 --sun "full"
garden_layout.py add-plant "Intensive Bed" "lettuce" --row 1 --col 1
garden_layout.py add-plant "Intensive Bed" "radishes" --row 1 --col 2  # Fast harvest
```

### For crop rotation planning
```bash
# Track what you planted each year
garden_layout.py add-season "2026"  # Starts fresh layout
garden_layout.py add-plant "Bed 1" "tomatoes" --row 1 --col 1
garden_layout.py add-plant "Bed 2" "beans" --row 1 --col 1

# Next year, change families
garden_layout.py add-season "2027"  # New layout
garden_layout.py add-plant "Bed 1" "carrots" --row 1 --col 1  # Different family
garden_layout.py add-plant "Bed 2" "corn" --row 1 --col 1      # Different family
```

## Companion Planting Guide

### Best Combinations (Good Together)
| Plant | Good With | Why |
|-------|-----------|------|
| Tomatoes | Basil, carrots, onions, marigolds | Basil enhances flavor, carrots repel pests |
| Cucumbers | Beans, corn, peas, radishes | Beans fix nitrogen, corn provides support |
| Lettuce | Carrots, radishes, onions | Radishes mark rows, carrots break soil |
| Peppers | Basil, onions, carrots | Basil repels aphids |
| Beans | Corn, potatoes, cucumbers | Nitrogen fixation benefits neighbors |
| Carrots | Tomatoes, onions, lettuce | Onions repel carrot fly |
| Corn | Beans, squash, cucumbers | Three Sisters method |
| Squash | Corn, beans, radishes | Beans repel squash beetles |

### Incompatible Plants (Avoid Together)
| Plant | Avoid With | Why |
|-------|-----------|------|
| Tomatoes | Potatoes, cucumbers, fennel | Same pests/diseases |
| Beans | Onions, garlic | Inhibit growth |
| Carrots | Dill, parsnips | Dill attracts carrot fly |
| Cucumbers | Potatoes, sage | Potatoes compete for space |
| Onions | Beans, peas | Inhibit bean growth |

## Spacing Requirements

### Small Plants (6-12 inches apart)
- Lettuce: 6-8 inches
- Spinach: 4-6 inches
- Radishes: 2-3 inches
- Onions: 4-6 inches
- Carrots: 2-3 inches

### Medium Plants (12-24 inches apart)
- Peppers: 18-24 inches
- Eggplant: 18-24 inches
- Beans (bush): 12-18 inches
- Cabbage: 18-24 inches

### Large Plants (24+ inches apart)
- Tomatoes: 24-36 inches
- Squash: 24-48 inches (or trellis)
- Corn: 12-18 inches (in blocks for pollination)
- Potatoes: 12-15 inches

## Sun Requirements

### Full Sun (6-8+ hours daily)
- Tomatoes, peppers, eggplant, squash, corn, beans, cucumbers

### Partial Sun (4-6 hours daily)
- Lettuce, spinach, kale, peas, carrots, beets

### Shade (<4 hours daily)
- Some leafy greens, herbs like mint, chives

## Examples

### Three Sisters Garden (Traditional)
```bash
# Classic Native American companion planting
garden_layout.py add-bed "Three Sisters" --width 8 --length 8 --sun "full"

# Plant corn in center (support)
garden_layout.py add-plant "Three Sisters" "corn" --row 4 --col 4

# Plant beans around corn (nitrogen)
garden_layout.py add-plant "Three Sisters" "beans" --row 4 --col 2
garden_layout.py add-plant "Three Sisters" "beans" --row 4 --col 6

# Plant squash at edges (ground cover)
garden_layout.py add-plant "Three Sisters" "squash" --row 1 --col 1
garden_layout.py add-plant "Three Sisters" "squash" --row 1 --col 8
garden_layout.py add-plant "Three Sisters" "squash" --row 8 --col 1
garden_layout.py add-plant "Three Sisters" "squash" --row 8 --col 8
```

### Tomato-Basil Garden
```bash
# Simple companion planting
garden_layout.py add-bed "Tomato Patch" --width 4 --length 6 --sun "full"

garden_layout.py add-plant "Tomato Patch" "tomato" --row 1 --col 1
garden_layout.py add-plant "Tomato Patch" "basil" --row 1 --col 3  # Companion!
garden_layout.py add-plant "Tomato Patch" "carrots" --row 2 --col 1  # Under tomatoes
garden_layout.py add-plant "Tomato Patch" "carrots" --row 2 --col 3
```

### Mixed Bed for Small Spaces
```bash
# Intensive planting
garden_layout.py add-bed "Small Space" --width 3 --length 4 --sun "partial"

garden_layout.py add-plant "Small Space" "lettuce" --row 1 --col 1
garden_layout.py add-plant "Small Space" "radishes" --row 1 --col 2  # Fast, marks row
garden_layout.py add-plant "Small Space" "lettuce" --row 1 --col 3

garden_layout.py add-plant "Small Space" "spinach" --row 2 --col 1
garden_layout.py add-plant "Small Space" "onions" --row 2 --col 2
garden_layout.py add-plant "Small Space" "spinach" --row 2 --col 3
```

## Search Features

- Find compatible plants for companion planting
- Get spacing requirements for any plant
- Search layouts by plant name
- Filter by sun requirements

## Security

### Path Validation
The `export` function validates output paths to prevent malicious writes:
- ✅ Allowed: `~/.openclaw/workspace/`, `/tmp/`, and home directory
- ❌ Blocked: System paths (`/etc/`, `/usr/`, `/var/`, etc.)
- ❌ Blocked: Sensitive dotfiles (`~/.bashrc`, `~/.ssh`, etc.)

## Data Storage

- Garden layouts stored in: `~/.openclaw/workspace/garden_layout_db.json`
- Each bed tracks: dimensions, sun exposure, plants with positions
- Companion database built-in with 50+ plant relationships
- JSON format makes it easy to backup or migrate

## Best Practices

1. **Plan before planting** - Use layout planner to visualize before putting seeds in ground
2. **Use companion planting** - Plant compatible species together
3. **Check spacing** - Don't overcrowd, plants need room to grow
4. **Track sun exposure** - Different beds have different sun requirements
5. **Plan for rotation** - Track what you plant where each year
6. **Export for reference** - Keep a backup of your garden plan

## Related Skills

- **plant-tracker** - Track individual plants with care schedules and harvests
- **seasonal-planting-guide** - What to plant when in your growing zone

Use together for complete garden management!

---
name: plant-tracker
description: "Personal plant and garden management for gardeners. Track your
  plants, set care schedules, and monitor growth. Use when you need to manage
  your garden, track watering/fertilizing schedules, or maintain plant
  inventories. Security: file exports are restricted to safe directories only
  (workspace, home, /tmp). Perfect for home gardeners, indoor plant enthusiasts,
  and anyone growing their own food."
---


# Plant Tracker

Manage your plants and garden with structured tracking and care schedules.

## Quick Start

### Add a plant to your collection
```bash
plant_tracker.py add "<plant_name>" --species "<species>" --location "<location>"
```

### List all plants
```bash
plant_tracker.py list
```

### Show plant details
```bash
plant_tracker.py show "<plant_name>"
```

### Record care (watering, fertilizing, etc.)
```bash
plant_tracker.py care "<plant_name>" --action "<action>" [notes]
```

### Search plants
```bash
plant_tracker.py search "<query>"
```

### Export plant data
```bash
plant_tracker.py export "<output_file>"
```

## Usage Patterns

### For indoor plant collections
Track houseplants with care schedules:
```bash
# Add your plants
plant_tracker.py add "Snake Plant" --species "Sansevieria trifasciata" --location "Living Room - North Window"
plant_tracker.py add "Monstera" --species "Monstera deliciosa" --location "Bedroom - East Window"
plant_tracker.py add "Pothos" --species "Epipremnum aureum" --location "Bathroom"

# Record watering
plant_tracker.py care "Snake Plant" --action "water" "Watered thoroughly, let drain"
plant_tracker.py care "Monstera" --action "water" "Watered until runoff, humidity 60%"

# Check what needs attention
plant_tracker.py list
```

### For vegetable gardens
Track your edible plants with planting dates and harvests:
```bash
# Add vegetables
plant_tracker.py add "Tomatoes" --species "Solanum lycopersicum" --location "Backyard - Bed 3" --planted "2026-04-15"
plant_tracker.py add "Basil" --species "Ocimum basilicum" --location "Backyard - Container" --planted "2026-05-01"
plant_tracker.py add "Lettuce" --species "Lactuca sativa" --location "Front Yard - Raised Bed" --planted "2026-04-20"

# Record care and harvests
plant_tracker.py care "Tomatoes" --action "water" "Deep watering, weather hot"
plant_tracker.py care "Tomatoes" --action "fertilize" "Added organic tomato fertilizer"
plant_tracker.py care "Basil" --action "harvest" "Harvested 20 leaves for pesto"

# See what's ready to harvest
plant_tracker.py search "harvest"
```

### For flower gardens
Track ornamental plants and seasonal care:
```bash
# Add flowers
plant_tracker.py add "Roses" --species "Rosa" --location "Front Garden" --planted "2025-03-10"
plant_tracker.py add "Lavender" --species "Lavandula" --location "Side Garden" --planted "2025-04-20"
plant_tracker.py add "Sunflowers" --species "Helianthus annuus" --location "Backyard" --planted "2026-05-15"

# Record seasonal care
plant_tracker.py care "Roses" --action "prune" "Spring pruning, removed dead wood"
plant_tracker.py care "Lavender" --action "prune" "Post-bloom pruning to encourage new growth"
plant_tracker.py care "Sunflowers" --action "harvest" "Harvested seeds for next year"
```

### For multi-garden management
Track plants across different locations:
```bash
# Indoor plants
plant_tracker.py add "Peace Lily" --location "Living Room"
plant_tracker.py add "Fiddle Leaf Fig" --location "Bedroom"

# Outdoor beds
plant_tracker.py add "Peppers" --location "Backyard - Bed 1"
plant_tracker.py add "Carrots" --location "Backyard - Bed 2"

# Community garden plot
plant_tracker.py add "Squash" --location "Community Plot A - Row 3"

# Filter by location
plant_tracker.py search "Bedroom"
plant_tracker.py search "Backyard"
```

## Actions Reference

### Available care actions
- `water` - Watering schedule
- `fertilize` - Adding nutrients/compost
- `prune` - Trimming and shaping
- `harvest` - Collecting fruits/vegetables/herbs
- `repot` - Moving to a larger container
- `plant` - Initial planting or transplanting
- `pesticide` - Pest treatment
- `inspect` - General health check
- `note` - General observation

## Security

### Path Validation
The `export` function validates output paths to prevent malicious writes:
- ✅ Allowed: `~/.openclaw/workspace/`, `/tmp/`, and home directory
- ❌ Blocked: System paths (`/etc/`, `/usr/`, `/var/`, etc.)
- ❌ Blocked: Sensitive dotfiles (`~/.bashrc`, `~/.ssh`, etc.)

## Data Storage

- All plant data is stored in: `~/.openclaw/workspace/plants_db.json`
- Each plant tracks: name, species, location, planting date, care history
- Care history includes: action, timestamp, notes
- JSON format makes it easy to backup or migrate

## Search Features

- Case-insensitive search across all plants
- Matches plant names, species, locations, and care notes
- Shows full plant details with care history
- Perfect for finding specific plants or care patterns

## Examples

### New garden setup
```bash
# Plan and track your new garden
plant_tracker.py add "Tomatoes - Beefsteak" --species "Solanum lycopersicum" --location "Backyard - Bed 1" --planted "2026-04-15"
plant_tracker.py add "Tomatoes - Cherry" --species "Solanum lycopersicum" --location "Backyard - Bed 1" --planted "2026-04-15"
plant_tracker.py add "Bell Peppers" --species "Capsicum annuum" --location "Backyard - Bed 2" --planted "2026-04-20"
plant_tracker.py add "Cucumbers" --species "Cucumis sativus" --location "Trellis - South Wall" --planted "2026-05-01"

# Export your garden plan
plant_tracker.py export "~/garden-planting-plan.md"
```

### Weekly garden maintenance
```bash
# Check your garden
plant_tracker.py list

# Record this week's care
plant_tracker.py care "Tomatoes - Beefsteak" --action "water" "Deep watering, mulch added"
plant_tracker.py care "Bell Peppers" --action "fertilize" "Added compost, plants look healthy"
plant_tracker.py care "Cucumbers" --action "inspect" "Found aphids on some leaves, treated with neem oil"
```

### Track growth and yields
```bash
# Record harvests
plant_tracker.py care "Tomatoes - Cherry" --action "harvest" "Harvested 2 cups, sweet and juicy"
plant_tracker.py care "Bell Peppers" --action "harvest" "Harvested 3 peppers, good size"
plant_tracker.py care "Cucumbers" --action "harvest" "Harvested 5 cucumbers, about 15cm each"

# Review harvest history
plant_tracker.py search "harvest"
```

## Best Practices

1. **Use descriptive names** - "Tomatoes - Beefsteak" not just "Tomatoes"
2. **Include planting dates** - helps track age and harvest windows
3. **Be specific with locations** - "Backyard - Bed 1" not just "Garden"
4. **Record care regularly** - builds history for future reference
5. **Note observations** - pests, diseases, flowering, fruiting
6. **Export regularly** - backup your plant data

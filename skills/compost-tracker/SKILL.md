---
name: compost-tracker
description: Track compost piles, monitor temperature, record turns, and manage your organic waste decomposition. Perfect for home gardeners and small farms.
author: johstracke
version: 1.0.0
license: MIT
tags:
  - gardening
  - compost
  - farm
  - organic
  - recycling
  - sustainability
  - soil
  - outdoor

# Compost Tracker

Track your compost piles and monitor decomposition progress.

## Features

- **Add compost piles** with size, location, materials, and notes
- **Temperature monitoring** - track heat levels (key decomposition indicator)
- **Turn history** - record when you aerate each pile
- **Status tracking** - Active → Ready (harvest ready)
- **Search** across piles, locations, materials, and notes
- **Export** to markdown for backup and sharing

## Usage

### Add a compost pile

```bash
compost_tracker.py add "Kitchen Pile" --size "Large" --location "Garden Corner" --materials "kitchen scraps,leaves,grass"
```

### List all piles

```bash
compost_tracker.py list
```

### Show pile details

```bash
compost_tracker.py show "Kitchen Pile"
```

### Add temperature reading

```bash
compost_tracker.py temp "Kitchen Pile" 55
```

### Record a turn

```bash
compost_tracker.py turn "Kitchen Pile" --notes "Aerated with pitchfork"
```

### Mark as ready to harvest

```bash
compost_tracker.py harvest "Kitchen Pile"
```

### Search piles

```bash
compost_tracker.py search "ready"
```

### Export data

```bash
compost_tracker.py export ~/compost-backup.md
```

## Temperature Guide

- **Below 20°C (68°F):** Decomposition slow, need more green material (nitrogen)
- **20-40°C (68-104°F):** Good decomposition, bacteria active
- **40-55°C (104-131°F):** Optimal range, fast decomposition
- **55-65°C (131-149°F):** Hot composting, kills most pathogens and weed seeds
- **Above 65°C (149°F):** Too hot, need to turn and add water

## Composting Tips

- **Turn every 1-2 weeks** to add oxygen and speed decomposition
- **Keep moist like a wrung-out sponge** (not soaking, not dry)
- **Balance carbon (browns) and nitrogen (greens)** - aim for 30:1 ratio
- **Chop materials** into smaller pieces for faster breakdown
- **Add variety** - mix kitchen scraps, yard waste, leaves, cardboard

## Materials to Include

**Greens (Nitrogen-rich):**
- Kitchen scraps (vegetable peels, fruit scraps, coffee grounds)
- Grass clippings
- Plant trimmings
- Manure (from herbivores only)

**Browns (Carbon-rich):**
- Dry leaves
- Sawdust
- Cardboard (plain, no plastic tape)
- Paper (shredded)
- Straw

## Materials to Avoid

- Meat, fish, dairy (attracts pests)
- Pet waste (cats, dogs)
- Diseased plants
- Weeds with seeds
- Treated wood or sawdust
- Glossy paper or plastic

## Integration with Other Skills

- **Plant Tracker** - Use finished compost to nourish your plants
- **Seasonal Planting Guide** - Plan compost timing for spring planting
- **Garden Layout Planner** - Position compost piles near garden beds

---

*Part of IOU's Gardening Suite* 🌱

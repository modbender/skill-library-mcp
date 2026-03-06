# Memory Setup — Fishing

## Initial Setup

Create on first use:
```bash
mkdir -p ~/fishing/archive
touch ~/fishing/memory.md
touch ~/fishing/catches.md
touch ~/fishing/spots.md
```

## memory.md Template

Copy to `~/fishing/memory.md`:

```markdown
# Fishing Memory

## Profile
- **Skill level:** beginner | intermediate | advanced
- **Preferred species:** 
- **Home waters:** 
- **License:** state, expiration

## Gear Inventory

### Rods
| Name | Type | Power | Length | Notes |
|------|------|-------|--------|-------|

### Reels
| Name | Type | Line capacity | Gear ratio |
|------|------|---------------|------------|

### Tackle
- Soft plastics: 
- Hard baits: 
- Terminal tackle: 
- Line types/weights: 

## Preferences
- Favorite techniques: 
- Preferred fishing times: 
- Catch and release: yes/no
- Target size: any | trophy

## Local Regulations
- Season dates: 
- Catch limits: 
- Size limits: 
- Protected species: 

---
*Last updated: YYYY-MM-DD*
```

## catches.md Template

Copy to `~/fishing/catches.md`:

```markdown
# Catch Log

## 2026

| Date | Species | Size | Spot | Conditions | Technique | Notes |
|------|---------|------|------|------------|-----------|-------|

## Stats
- Total catches: 0
- Best day: 
- Biggest fish: 
- Most productive spot: 
- Most productive technique: 

---
*Last updated: YYYY-MM-DD*
```

## spots.md Template

Copy to `~/fishing/spots.md`:

```markdown
# Fishing Spots

## Active Spots

### [Spot Name]
- **Location:** coordinates or description
- **Access:** public/private, parking, fees
- **Best for:** species list
- **Best times:** dawn, dusk, tide info
- **Best techniques:** what works here
- **Structure:** weeds, rocks, drop-offs, docks
- **Notes:** 

### [Another Spot]
...

## Spots to Try
- [ ] Location — reason to try

## Retired Spots
Spots no longer productive or accessible.

---
*Last updated: YYYY-MM-DD*
```

## Archive Structure

Move old season data to `~/fishing/archive/`:
```
archive/
├── catches-2025.md
├── catches-2024.md
└── spots-retired.md
```

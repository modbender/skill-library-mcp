# Setup — Italy Skill

## Requirements

No external dependencies. This skill uses file-based knowledge only.

## Memory Configuration

Create `~/italy/` directory for user preferences:

```bash
mkdir -p ~/italy
```

Copy the memory template:

```bash
cp memory-template.md ~/italy/preferences.md
```

## File Structure

```
italy/
├── SKILL.md                 # Main entry point
├── setup.md                 # This file
├── memory-template.md       # Template for user preferences
│
├── rome.md                  # City guide
├── florence.md              # City guide  
├── venice.md                # City guide
├── naples.md                # City guide
│
├── food-guide.md            # Regional cuisine
├── wine.md                  # Wine regions & experiences
│
├── beaches.md               # Beach guide by region
├── hiking.md                # Trails and mountain info
├── nightlife.md             # Bars, clubs, aperitivo
├── experiences.md           # Activities to book
│
├── regions.md               # 20 regions overview
├── culture.md               # Etiquette and customs
├── itineraries.md           # Sample trip plans
├── accommodation.md         # Where to stay
├── with-kids.md             # Family travel
│
├── apps.md                  # Essential apps
├── transport.md             # Trains, buses, driving, ZTL
├── telecoms.md              # SIM cards, WiFi
└── emergencies.md           # Emergency contacts & healthcare
```

## Usage Notes

### When to Load Which File

| User Intent | Files to Load |
|-------------|---------------|
| General Italy trip | SKILL.md → itineraries.md |
| Specific city | rome.md / florence.md / venice.md / naples.md |
| Food questions | food-guide.md |
| Wine trip | wine.md |
| Beach vacation | beaches.md |
| Hiking plans | hiking.md |
| Practical logistics | transport.md, apps.md, telecoms.md |
| Family travel | with-kids.md |
| Emergency | emergencies.md |
| Cultural questions | culture.md |

### Memory System

User preferences stored in `~/italy/preferences.md`:
- Food restrictions
- Travel style
- Budget level
- Visited places
- Favorite experiences

Check preferences file before making recommendations.

### Quality Standards

Every recommendation should include:
- **Specific name** — Restaurant, beach, hotel name
- **Address** — Actual street address when available
- **Price** — € amounts or range
- **Hours** — When relevant (riposo!)
- **Warnings** — Tourist traps, common mistakes

### Updating Information

This skill contains information current as of early 2024-2025. Things that change frequently:

- Restaurant prices (inflation)
- Train fares
- Museum ticket prices
- ZTL hours
- Entry fees

When in doubt, recommend user verifies current prices/hours.

## Verification

Test the skill by asking:
1. "Where should I eat pizza in Naples?" → Should get specific pizzerias with addresses
2. "How do I get from Rome to Florence?" → Train options with times and prices
3. "Best gelato in Florence?" → Specific shop names, not generic advice

If answers are vague, skill isn't being used correctly.

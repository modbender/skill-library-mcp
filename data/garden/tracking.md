# Plant & Activity Tracking

## Plant File Template

Create `plants/{name}.md` for each plant:

```markdown
# Tomato Cherry

## Identity
- **Variety:** Cherry Bomb
- **Type:** Indeterminate
- **Planted:** 2026-03-15 (seedling)
- **Location:** raised-bed-1, position B3
- **Source:** Local nursery

## Care Schedule
- **Water:** Every 2-3 days, deep soak
- **Fertilizer:** Tomato feed every 2 weeks (started June)
- **Pruning:** Remove suckers weekly
- **Support:** Staked, needs tie-up as grows

## Harvest Window
- **Expected:** July-October
- **Signs of ripeness:** Full red color, slight give

## Health Log
| Date | Issue | Treatment | Outcome |
|------|-------|-----------|---------|
| 2026-05-20 | Aphids on new growth | Neem spray | Cleared in 3 days |
| 2026-06-10 | Blossom end rot | Calcium + consistent water | Resolved |

## Notes
- This variety produces well but needs consistent moisture
- Companion: basil nearby helps with pests
```

## Zone File Template

Create `zones/{name}.md` for each garden area:

```markdown
# Raised Bed 1

## Conditions
- **Size:** 4x8 feet
- **Sun:** Full sun (8+ hours)
- **Soil:** Amended clay, pH 6.5
- **Irrigation:** Drip system, zone 2
- **Microclimate:** Protected from north wind by fence

## Current Plantings (2026)
| Position | Plant | Planted | Status |
|----------|-------|---------|--------|
| A1-A4 | Peppers | 2026-04-01 | Fruiting |
| B1-B4 | Tomatoes | 2026-03-15 | Producing |
| C1-C4 | Basil | 2026-04-15 | Harvesting |

## Rotation History
| Year | Spring | Summer | Fall |
|------|--------|--------|------|
| 2025 | Lettuce | Squash | Garlic |
| 2024 | Tomatoes | Tomatoes | Cover crop |

## Notes
- Avoid tomatoes here until 2027 (2 years since last)
- Good spot for heavy feeders (amended annually)
```

## Activity Log Format

Monthly file `log/YYYY-MM.md`:

```markdown
# 2026-06

## Week 1 (June 1-7)
- 🌱 Direct sowed beans in bed-3
- 💧 Installed rain gauge
- 📸 Monthly photos taken

## Week 2 (June 8-14)
- 🐛 Japanese beetles on roses, handpicked
- ✂️ Pruned tomato suckers
- 🌡️ Heat wave: extra evening water all beds

## Week 3 (June 15-21)
- 🍅 First tomato harvest: 0.5 kg
- 💀 Lost 2 pepper plants to unknown wilt
- 📝 Soil test sent to lab
```

## Log Icons
- 🌱 Planting/seeding
- 💧 Watering/irrigation
- 🐛 Pest activity
- 🍅 Harvest
- ✂️ Pruning/maintenance
- 🌡️ Weather event
- 💀 Plant death/loss
- 📸 Documentation
- 📝 Testing/analysis

## Quick Logging

When user mentions garden activity, log it:
1. Parse date (default: today)
2. Identify action type
3. Link to affected plant/zone
4. Append to current month's log

"I watered the tomatoes" →
```
- 💧 Watered tomatoes (raised-bed-1)
```

"Harvested 3 zucchinis" →
```
- 🍅 Harvested zucchini x3
```
Plus update `harvests.md` with yield estimate.

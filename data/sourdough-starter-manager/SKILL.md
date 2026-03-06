---
name: sourdough-starter-manager
description: Manage sourdough starters with feeding schedules, hydration calculations, health tracking, and baking preparation. Use when the user wants to maintain a sourdough starter, plan feedings, calculate ratios, troubleshoot starter problems, or prepare for baking.
metadata:
  openclaw:
    emoji: "🍞"
    version: "1.0.0"
    author: "AM"
    tags: ["baking", "sourdough", "cooking", "food", "fermentation"]
    requires:
      bins: []
      env: []
      config: []
---

# Sourdough Starter Manager

## Description

The Sourdough Starter Manager helps bakers maintain healthy, active sourdough starters through intelligent feeding schedules, precise hydration calculations, health monitoring, and baking preparation planning. Whether you're a beginner or experienced baker, this skill ensures your starter stays healthy and ready for any baking project.

## Core Capabilities

### 1. Feeding Schedule Management
- Calculate feeding ratios (starter:flour:water)
- Generate maintenance schedules (daily, weekly, refrigerated)
- Create pre-bake preparation timelines
- Track feeding history and patterns
- Set reminders for upcoming feedings

### 2. Hydration Calculations
- Calculate current starter hydration percentage
- Convert between different hydration levels (e.g., 100% to 75%)
- Adjust recipes for different starter hydrations
- Calculate flour and water needed for target amounts

### 3. Health Monitoring & Troubleshooting
- Diagnose common starter problems
- Track rise times and peak activity
- Monitor smell, consistency, and appearance
- Provide recovery protocols for neglected starters
- Identify contamination vs. normal fermentation

### 4. Baking Preparation
- Calculate starter amounts needed for recipes
- Generate feeding schedules to reach target amounts
- Plan multi-day preparation timelines
- Adjust for room temperature variations
- Optimize timing for specific bake schedules

## Usage Examples

### Example 1: Daily Maintenance Feeding
**User**: "I need to feed my starter. I have 50g of starter right now."

**Assistant Response**:
- Suggests 1:1:1 ratio feeding (50g starter : 50g flour : 50g water)
- Notes this will yield 150g total
- Recommends discarding excess if not baking soon
- Provides timeline: feed now, ready in 4-8 hours at room temp (68-75°F)

### Example 2: Pre-Bake Preparation
**User**: "I want to bake bread on Saturday morning. My recipe needs 200g of active starter."

**Assistant Response**:
- Calculates backward timeline from Saturday morning
- Suggests feeding schedule: Thursday night and Friday evening
- Provides specific amounts to feed at each stage
- Warns about room temperature considerations
- Offers contingency plan if starter doesn't rise as expected

### Example 3: Hydration Conversion
**User**: "My starter is at 100% hydration but the recipe calls for 75% hydration. How do I convert?"

**Assistant Response**:
- Explains hydration percentage concept
- Calculates flour/water adjustments needed
- Provides step-by-step conversion process
- Suggests how to maintain a 75% starter vs. one-time conversion
- Notes texture and consistency differences

### Example 4: Troubleshooting
**User**: "My starter smells like nail polish remover and hasn't risen in days."

**Assistant Response**:
- Identifies likely cause: hooch formation and starvation
- Diagnoses: needs more frequent feeding
- Provides recovery protocol:
  1. Pour off liquid (hooch)
  2. Discard 75% of starter
  3. Feed with 1:2:2 ratio (more food to revive it)
  4. Feed every 12 hours for 3-4 days
  5. Monitor for sweet-sour smell and doubling
- Sets realistic recovery timeline
- Explains when to discard and start fresh

### Example 5: Long-Term Storage
**User**: "I'm going on vacation for 2 weeks. How do I store my starter?"

**Assistant Response**:
- Recommends refrigeration method
- Feeding protocol before storage: 1:5:5 ratio (well-fed)
- Storage instructions: airtight container with room to expand
- Revival instructions for return
- Alternative: dehydration method for longer storage
- Notes on starter resilience (can survive months in fridge)

## Key Formulas & Calculations

### Hydration Percentage
```
Hydration % = (Water Weight / Flour Weight) × 100

Example:
50g flour + 50g water = 100% hydration
50g flour + 37.5g water = 75% hydration
```

### Feeding Ratio Notation
```
1:1:1 = 1 part starter : 1 part flour : 1 part water
1:2:2 = 1 part starter : 2 parts flour : 2 parts water

Example with 50g starter:
1:2:2 = 50g starter + 100g flour + 100g water = 250g total
```

### Target Amount Calculation
```
To get X grams of starter at ratio R:S:F:W

If ratio is 1:2:2 and you need 200g:
- Total parts = 1+2+2 = 5
- Starter needed = 200/5 × 1 = 40g
- Flour needed = 200/5 × 2 = 80g
- Water needed = 200/5 × 2 = 80g
```

## Troubleshooting Guide

### Common Issues

**Not Rising / Slow Activity**
- Likely causes: Too cold, needs more frequent feeding, weak starter
- Solutions: Move to warmer spot (75-80°F), increase feeding frequency, try 1:2:2 ratio

**Liquid on Top (Hooch)**
- Cause: Starter is hungry and has consumed available food
- Solution: Stir back in or pour off, then feed immediately

**Mold Growth**
- Identification: Fuzzy colored spots (green, pink, orange)
- Action: Discard entire starter, sanitize container, start fresh
- Prevention: Regular feeding, clean utensils, proper ratios

**Acetone/Nail Polish Smell**
- Cause: Starvation and alcohol production
- Solution: Feed more frequently with higher flour ratios

**No Bubbles After Several Days**
- Possible causes: Chlorinated water, non-organic flour, too cold
- Solutions: Use filtered water, try organic flour, increase temperature

### Health Indicators

**Healthy Starter Signs:**
- Doubles in size within 4-8 hours of feeding
- Pleasant sweet-sour smell
- Bubbles throughout
- Passes float test (drop in water and it floats)
- Elastic, stretchy consistency

**Unhealthy Starter Signs:**
- No rise after 12+ hours
- Offensive smell (not just sour)
- No bubbles
- Watery consistency that doesn't improve
- Colored spots or mold

## Storage Methods

### Refrigeration (Best for 1-4 week breaks)
1. Feed with 1:5:5 ratio
2. Let rise to peak (4-8 hours)
3. Seal in container with room to expand
4. Refrigerate
5. Can last months with occasional feeding (every 2-4 weeks)

### Dehydration (Best for long-term storage)
1. Feed starter and wait until peak rise
2. Spread thin layer on parchment paper
3. Air dry completely (2-3 days) or use dehydrator
4. Break into flakes and store in airtight container
5. Rehydrate with equal parts flour and water

### Freezing (Not recommended)
- Can damage yeast and bacterial cultures
- May not revive successfully

## Temperature Guidelines

| Temperature | Activity Level | Feeding Frequency |
|-------------|----------------|-------------------|
| 65-70°F     | Slow           | Every 24 hours    |
| 70-75°F     | Moderate       | Every 12-24 hours |
| 75-80°F     | Active         | Every 8-12 hours  |
| 80-85°F     | Very Active    | Every 6-8 hours   |
| 85°F+       | Too Hot        | Risk of bad bacteria |

## Baking Preparation Timeline

### Same-Day Bake (8-12 hours notice)
- Take refrigerated starter out
- Feed 1:2:2 ratio
- Use when doubled (4-8 hours depending on temp)

### Next-Day Bake
- **Evening before**: Feed refrigerated starter 1:1:1
- **Morning of bake**: Starter should be at peak, ready to use

### Weekend Bake Planning
- **Thursday evening**: Remove from fridge, feed 1:2:2
- **Friday morning**: Discard all but 50g, feed 1:2:2
- **Friday evening**: Check rise, feed 1:1:1 (or according to recipe needs)
- **Saturday morning**: Use at peak rise

## Best Practices

1. **Consistency is Key**: Try to feed at similar times each day
2. **Ratios Matter**: Adjust feeding ratios based on schedule and temperature
3. **Trust Your Senses**: Smell and appearance tell you more than the clock
4. **Keep Records**: Track feedings and outcomes for better understanding
5. **Don't Stress**: Sourdough starters are resilient and forgiving
6. **The Float Test**: Not perfect but helpful - drop starter in water, it should float when ready
7. **Room Temperature**: Affects everything - adjust expectations accordingly
8. **Discard Uses**: Don't waste - use in pancakes, crackers, pizza dough

## Recipe Adjustments

When a recipe calls for different starter than you maintain:

**Your starter is 100% hydration, recipe calls for stiff (50-60%)**:
- Reduce water in recipe by 10-20%
- Or convert portion of your starter temporarily

**Your starter is 100%, recipe calls for liquid (125%)**:
- Add extra water to recipe
- Or adjust your starter for one feeding

## Advanced Tips

- **Peak vs. Past Peak**: Use at peak for maximum rise, past peak for more sour flavor
- **Flour Types**: Whole wheat and rye ferment faster than white flour
- **Water Quality**: Chlorinated water can inhibit growth - use filtered if possible
- **Seasonal Variations**: May need more frequent feeding in summer, less in winter
- **Whole Grain Boost**: Add 10-20% whole wheat/rye to feeding for more activity
- **Starter Names**: Many bakers name their starters - it's tradition!

## When to Use This Skill

Use the Sourdough Starter Manager when users:
- Ask about feeding their sourdough starter
- Need help calculating hydration or ratios
- Want to prepare starter for baking
- Have questions about starter health or troubleshooting
- Need storage advice for vacations or breaks
- Want to convert between different starter hydrations
- Ask about timelines for baking preparation
- Need help reviving a neglected or weak starter
- Want to understand fermentation schedules
- Ask about temperature effects on starter activity

## Important Notes

- Every starter is unique and may behave slightly differently
- Trust your senses (smell, sight, texture) over rigid timing
- Room temperature significantly affects all timelines
- When in doubt, feed your starter - it's hard to overfeed
- Starters can survive weeks of neglect in the refrigerator
- Start fresh if you see mold (colored fuzzy spots) - don't risk it

---

*Remember: Sourdough baking is an art and a science. These guidelines are starting points - adjust based on your environment, schedule, and starter's unique personality!*

---
name: Nutrition
description: Build a personal nutrition system for tracking meals, calories, macros, vitamins, and minerals.
metadata: {"clawdbot":{"emoji":"🥗","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User logs meal → calculate and store nutrition data
- User asks about nutrients → surface totals and gaps
- User tracks over time → show patterns and progress
- Create `~/nutrition/` as workspace

## File Structure
```
~/nutrition/
├── daily/
│   └── 2024-02/
│       ├── 2024-02-10.md
│       └── 2024-02-11.md
├── foods/
│   └── common.md
├── targets.md
├── supplements.md
└── insights.md
```

## Daily Log
```markdown
# 2024-02-11.md
## Breakfast — 8:00 AM
Oatmeal with banana
- Oats 80g: 300 cal, 10g protein, 54g carbs, 5g fat
- Banana: 105 cal, 1g protein, 27g carbs, 0g fat
- Almond milk 200ml: 30 cal, 1g protein, 1g carbs, 2.5g fat

## Lunch — 1:00 PM
Chicken salad
- Chicken breast 150g: 165 cal, 31g protein, 0g carbs, 3.6g fat
- Mixed greens 100g: 20 cal, 2g protein, 3g carbs, 0g fat
- Olive oil 15ml: 120 cal, 0g protein, 0g carbs, 14g fat

## Dinner — 7:30 PM
Salmon with vegetables
- Salmon 200g: 400 cal, 40g protein, 0g carbs, 25g fat
- Broccoli 150g: 50 cal, 4g protein, 10g carbs, 0.5g fat

## Snacks
- Apple: 95 cal, 0g protein, 25g carbs, 0g fat
- Greek yogurt 150g: 100 cal, 17g protein, 6g carbs, 0.7g fat

## Daily Totals
Calories: 1,385
Protein: 106g | Carbs: 126g | Fat: 51g

## Micronutrients Notable
- Vitamin D: salmon (high)
- Potassium: banana, salmon
- Vitamin C: broccoli
- Omega-3: salmon (high)
```

## Targets
```markdown
# targets.md
## Daily Goals
Calories: 2,000
Protein: 150g
Carbs: 200g
Fat: 65g

## Micronutrient Focus
- Vitamin D: 600 IU (often low)
- Iron: 8mg
- Omega-3: 1,000mg

## Notes
Higher protein for muscle building
Limiting added sugars to 25g
```

## Common Foods Reference
```markdown
# foods/common.md
## Quick Reference
| Food | Cal | Protein | Carbs | Fat |
|------|-----|---------|-------|-----|
| Egg | 70 | 6g | 0g | 5g |
| Chicken 100g | 165 | 31g | 0g | 3.6g |
| Rice 100g cooked | 130 | 2.7g | 28g | 0.3g |
| Banana | 105 | 1g | 27g | 0g |

## Micronutrient Stars
- Vitamin D: salmon, eggs, fortified milk
- Iron: red meat, spinach, lentils
- Vitamin C: citrus, peppers, broccoli
- Potassium: bananas, potatoes, salmon
- Omega-3: salmon, sardines, walnuts
```

## Supplements
```markdown
# supplements.md
## Daily
- Vitamin D3: 2000 IU (morning)
- Omega-3: 1000mg (with food)

## As Needed
- Magnesium: before bed if needed
```

## Insights
```markdown
# insights.md
## Patterns
- Usually low on Vitamin D without supplements
- Protein higher on workout days
- Weekends: higher calories, less consistent

## Adjustments
- Added salmon twice weekly for Omega-3
- Morning eggs improved protein start
```

## What To Surface
- "You've had 80g protein so far, 70g to go"
- "Low on Vitamin D today — salmon or eggs?"
- "Weekly average: 1,900 cal, under target"
- "Iron looks low this week — more spinach or red meat"

## Logging Meals
When user describes meal:
- Estimate portions if not specified
- Calculate macros and calories
- Flag notable micronutrients
- Add to daily log

## What To Track
- Calories and macros per meal
- Notable micronutrients
- Supplements taken
- Patterns over time

## Progressive Enhancement
- Start: log meals with macros
- Add micronutrient awareness
- Track supplements
- Build common foods reference

## What NOT To Do
- Obsess over exact gram accuracy
- Judge food choices
- Push restrictive eating
- Ignore that estimates are approximate

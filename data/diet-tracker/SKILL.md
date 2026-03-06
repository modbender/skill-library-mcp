---
name: diet-tracker
description: Tracks daily diet and calculates nutrition information to help achieve weight loss goals. Use when user provides meal information, asks about calorie intake, requests remaining calorie budget, or needs meal logging reminders. Automatically reminds user to log meals via cron job at lunch and dinner times.
---

# Diet Tracker

This skill helps track daily diet and achieve weight loss goals with automated meal reminders.

## Trigger Conditions

User might say:
- "I had [food] for lunch/dinner"
- "What's my remaining calorie budget?"
- "How many calories have I eaten today?"
- "Log my meal"
- "Check my diet progress"

Or automatically triggered by cron job for meal reminders.

## Cron Job Integration

This skill works with automated cron jobs:

- **Lunch reminder**: ~12:30 (checks if lunch logged, sends reminder if not)
- **Dinner reminder**: ~18:00 (checks if dinner logged, sends reminder if not)

Cron job system event: `饮食记录检查:午餐` or `饮食记录检查:晚餐`

## User Profile (Required)

The skill reads from `USER.md`:
- Daily calorie target (default: 1650 kcal)
- Macronutrient targets (protein/carbs/fat)
- Height, weight, age, gender, activity level (for TDEE calculation)

**Activity levels**:
- Sedentary (little or no exercise)
- Lightly active (light exercise 1-3 days/week)
- Moderately active (moderate exercise 3-5 days/week)
- Very active (hard exercise 6-7 days/week)
- Extra active (very hard exercise + physical job)

## Workflow

### When User Logs a Meal:

1. **Identify food items** from user's description
2. **Fetch nutrition data** via `scripts/get_food_nutrition.py`
   - **MUST GET**: calories(kcal), protein(g), carbs(g), fat(g)
   - Searches web for calorie/protein/carbs/fat info
   - Falls back to `references/food_database.json` if needed
   - **If complete nutrition data cannot be found, MUST clearly inform user of estimated values**
3. **Update daily log** via `scripts/update_memory.py`
   - Saves to `memory/YYYY-MM-DD.md`
   - **RECORD FORMAT**: `Food Name - XX kcal (P: XXg, C: XXg, F: XXg)`
   - Calculates meal totals
   - Updates daily running totals
4. **Report to user**:
   - **MUST REPORT**: calories + protein/carbs/fat grams
   - Today's consumed / remaining calories
   - **MUST REPORT**: Remaining macronutrient budgets
   - Predicted weight change based on deficit/surplus

### When User Asks for Status:

1. Read current day's memory file
2. Calculate totals consumed
3. Report:
   - Remaining calorie budget
   - Remaining protein/carbs/fat (if targets set)
   - Weight change prediction

## Scripts

- `scripts/get_food_nutrition.py`: Fetches nutrition info + calculates TDEE
- `scripts/update_memory.py`: Updates daily memory file with meal data
- `references/food_database.json`: Fallback database of common foods

## Error Handling

### Common Issues

**Issue**: "Cannot read USER.md" or missing user data
- **Cause**: User profile not configured
- **Solution**: Ask user for height, weight, age, gender, activity level, and calorie target

**Issue**: Nutrition lookup fails for uncommon foods
- **Cause**: Food not found in online databases
- **Solution**: Ask user for approximate calorie count or use similar food from database

**Issue**: Multiple food items in one meal
- **Cause**: User says "I had pizza, salad, and coke"
- **Solution**: Process each item separately, sum the nutrition values

## Data Format

### Daily Memory Entry (memory/YYYY-MM-DD.md)

**REQUIRED FORMAT** — Must include calories + macronutrients:

```markdown
## Diet Log

**Breakfast**: [food] - [X] kcal (P: [X]g, C: [X]g, F: [X]g)
**Lunch**: [food] - [X] kcal (P: [X]g, C: [X]g, F: [X]g)
**Dinner**: [food] - [X] kcal (P: [X]g, C: [X]g, F: [X]g)

**Daily Total**: [X] / [target] kcal
- Protein: [X] / [target]g (remaining: [X]g)
- Carbs: [X] / [target]g (remaining: [X]g)
- Fat: [X] / [target]g (remaining: [X]g)
**Predicted weight change**: [-/+ X] kg
```

**⚠️ Strictly prohibited to record only calories while omitting macronutrient grams!**

## Progressive Disclosure

- **Level 1 (frontmatter)**: Skill activation criteria
- **Level 2 (SKILL.md)**: Full workflow instructions (this file)
- **Level 3 (references/)**: Food database and nutrition guidelines

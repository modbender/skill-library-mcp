---
name: luna-calorie-tracker
description: Track daily caloric intake by sending food photos. Luna analyzes images using vision AI, estimates calories and macros, and stores everything in memory for daily/weekly summaries.
metadata: {"openclaw": {"requires": {"env": ["OPENAI_API_KEY"]}, "primaryEnv": "OPENAI_API_KEY", "emoji": "🍽️"}}
---

# Luna Calorie Tracker Skill

You are Luna's calorie tracking module. When the user sends a food image, analyze it and track their nutrition.

## When the user sends a food image

1. **Analyze the image** using your vision capabilities:
   - Identify every food item visible in the image
   - Estimate portion sizes (weight in grams or volume in ml)
   - Calculate: Calories, Protein (g), Carbs (g), Fat (g), Fiber (g)
   - Assign a confidence score (0-1) for the estimate

2. **Respond with a structured summary:**
   ```
   🍽️ Meal Logged!
   
   📸 Items detected:
   - [Food item 1]: [portion] — [calories] kcal (P: [x]g | C: [x]g | F: [x]g)
   - [Food item 2]: [portion] — [calories] kcal (P: [x]g | C: [x]g | F: [x]g)
   
   📊 Meal Total: [total] kcal
   Protein: [x]g | Carbs: [x]g | Fat: [x]g | Fiber: [x]g
   Confidence: [score]
   
   📅 Daily Running Total: [X] kcal ([meals] meals logged today)
   ```

3. **Store in memory** — append to today's daily log file at `memory/YYYY-MM-DD.md` with this format:
   ```markdown
   ## Meal [N] — [HH:MM]
   - **Items**: [comma-separated food items]
   - **Calories**: [total] kcal
   - **Protein**: [x]g | **Carbs**: [x]g | **Fat**: [x]g | **Fiber**: [x]g
   - **Confidence**: [score]
   ```

4. **Update the running daily summary** at the TOP of that day's memory file:
   ```markdown
   # Daily Nutrition Log — [YYYY-MM-DD]
   **Total Calories**: [X] kcal | **Meals**: [N]
   **Protein**: [X]g | **Carbs**: [X]g | **Fat**: [X]g | **Fiber**: [X]g
   ---
   ```

## Slash Commands

When the user types these commands, respond accordingly:

### /calories today
Read `memory/YYYY-MM-DD.md` for today and return the daily summary with all meals.

### /calories week
Read the last 7 days of `memory/YYYY-MM-DD.md` files, compute weekly totals, daily averages, and show a mini bar chart of daily calories:
```
📊 Weekly Summary ([start] to [end])
Total: [X] kcal | Daily Avg: [X] kcal
Avg Protein: [X]g | Avg Carbs: [X]g | Avg Fat: [X]g

Mon: ████████░░ 1,850 kcal
Tue: ██████████ 2,200 kcal
Wed: ███████░░░ 1,600 kcal
...
```

### /calories goal [number]
Save the user's daily calorie goal to `MEMORY.md` under a `## Calorie Goal` section. Use this goal to show progress in daily summaries (e.g., "1,450 / 2,000 kcal — 72% of daily goal").

### /calories history [food]
Search memory files for past entries containing [food] and show when the user last ate it, average calories for that food, and frequency.

### /calories undo
Remove the last logged meal from today's memory file and update the daily summary.

## Vision Analysis Guidelines

- When estimating portions, consider plate size as reference (standard dinner plate ~10 inches)
- Account for hidden calories: cooking oils, sauces, dressings, butter
- For packaged foods, try to read labels if visible in the image
- If a food item is ambiguous, state your assumption (e.g., "assuming whole milk, not skim")
- For restaurant meals, estimate on the higher side (restaurants use more oil/butter)
- If you truly cannot identify a food, ask the user to clarify

## Memory Integration

- Always read today's existing log before appending to get accurate running totals
- Use `memory_search` to find past entries when the user asks about history
- Store the calorie goal in `MEMORY.md` so it persists across sessions
- When compaction runs, ensure daily totals are preserved even if individual meal details are summarized

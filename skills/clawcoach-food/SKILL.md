---
name: clawcoach-food
description: Food photo analysis and meal logging for ClawCoach. Send a photo of your meal and get instant macro breakdown via Claude Vision.
emoji: "\U0001F4F8"
user-invocable: true
homepage: https://github.com/clawcoach/clawcoach
metadata:
  openclaw: {"requires": {"env": ["ANTHROPIC_API_KEY"]}}
---

# ClawCoach Food — Photo Analysis & Meal Logging

This skill handles food photo analysis via Claude Vision, text-based meal logging, and the confirmation flow.

## When to Activate

- User sends a photo — assume it is food unless context clearly suggests otherwise
- User types a food description ("I had 2 eggs and toast for breakfast")
- User says "log [food]" or "I ate [food]"
- User wants to edit or delete a previous meal

## Data Storage

All meals are stored in `~/.clawcoach/food-log.json` with this structure:

```json
{
  "meals": [
    {
      "id": "2026-02-22-lunch-001",
      "date": "2026-02-22",
      "type": "lunch",
      "status": "confirmed",
      "items": [
        {
          "name": "grilled chicken breast",
          "portion": "6 oz",
          "calories": 280,
          "protein_g": 52,
          "fat_g": 6,
          "carbs_g": 0
        }
      ],
      "total_calories": 520,
      "total_protein_g": 62,
      "total_fat_g": 14,
      "total_carbs_g": 48,
      "source": "photo",
      "timestamp": "2026-02-22T12:35:00Z"
    }
  ]
}
```

## Photo Analysis Flow

When the user sends a photo:

1. **Analyze the image** using your vision capabilities. Identify every distinct food item visible. For each item estimate:
   - Name (be specific: "grilled chicken breast" not just "chicken")
   - Portion in common units (oz, cups, pieces, slices)
   - Calories and macros (protein, fat, carbs in grams)

   Use your nutritional knowledge. For common foods, these are well-established values. Be conservative with portions if uncertain.

2. **Present the results** in the user's persona voice:
   - List each item with portion and macros
   - Show meal total
   - Show daily running totals (consumed / target / remaining)
   - Ask: "confirm? (yes / edit / redo)"

3. **Handle response:**
   - **"yes" / "confirm"** — Write the meal to `~/.clawcoach/food-log.json` with status "confirmed"
   - **Correction** (e.g., "the rice was brown rice" or "it was more like 8oz") — recalculate and present updated totals
   - **"redo"** — ask for a new photo or text description

4. After confirmation, always show updated daily totals.

## Text-Based Logging

When the user describes food in text:

1. Parse the food items and estimate portions from the description
2. Calculate macros for each item using your nutritional knowledge
3. Follow the same confirmation flow as photo analysis

## Meal Type Auto-Detection

Categorize meals by time:
- Before 10:00 = breakfast
- 10:00 - 14:00 = lunch
- 14:00 - 17:00 = snack
- After 17:00 = dinner

The user can override: "log this as a snack"

## Editing and Deleting

- "Delete my lunch" — find today's lunch entry, remove it from food-log.json
- "I think that was more like 400 calories" — update the specific meal entry
- "What did I eat today?" — list all confirmed meals for today with totals

## Daily Totals

After any meal is confirmed, calculate and show:
1. Read profile from `~/.clawcoach/profile.json` for targets
2. Sum all confirmed meals for today from food-log.json
3. Display:
   - **Consumed**: X cal | Xg protein | Xg fat | Xg carbs
   - **Target**: X cal | Xg protein | Xg fat | Xg carbs
   - **Remaining**: X cal | Xg protein | Xg fat | Xg carbs

## Edge Cases

- **Blurry or unclear photo**: "I can't quite make out the food. Try a better lit photo, or just tell me what you had."
- **Non-food photo**: "That doesn't look like food! Send a photo of your meal, or type what you ate."
- **Unknown food**: Ask the user for clarification rather than guessing wildly.
- **Multiple items unclear**: "I can see chicken and something else — is that rice or pasta?"
- **No portion visible**: Use standard serving sizes and note: "I estimated a standard portion — let me know if it was more or less."

## Nutritional Reference (Common Foods per 100g)

Use these as a baseline. Scale by estimated portion size.

| Food | Cal | Protein | Fat | Carbs |
|------|-----|---------|-----|-------|
| Chicken breast (grilled) | 165 | 31 | 3.6 | 0 |
| Salmon (baked) | 208 | 20 | 13 | 0 |
| White rice (cooked) | 130 | 2.7 | 0.3 | 28 |
| Brown rice (cooked) | 123 | 2.7 | 1.0 | 26 |
| Pasta (cooked) | 131 | 5 | 1.1 | 25 |
| Broccoli (steamed) | 35 | 2.4 | 0.4 | 7 |
| Egg (whole, large ~50g) | 155 | 13 | 11 | 1.1 |
| Avocado | 160 | 2 | 15 | 9 |
| Sweet potato (baked) | 90 | 2 | 0.1 | 21 |
| Greek yogurt (plain) | 59 | 10 | 0.7 | 3.6 |
| Banana (~120g) | 89 | 1.1 | 0.3 | 23 |
| Oats (cooked) | 68 | 2.4 | 1.4 | 12 |
| Bread (white, per slice ~30g) | 265 | 9 | 3.2 | 49 |
| Cheese (cheddar) | 403 | 25 | 33 | 1.3 |
| Almonds | 579 | 21 | 50 | 22 |
| Olive oil (1 tbsp ~14ml) | 884 | 0 | 100 | 0 |
| Pizza (pepperoni, per slice) | 298 | 12 | 14 | 30 |
| Burger (quarter lb w/ bun) | ~550 | 30 | 30 | 40 |
| Steak (sirloin) | 206 | 26 | 11 | 0 |
| Tofu (firm) | 144 | 17 | 9 | 3 |
| Lentils (cooked) | 116 | 9 | 0.4 | 20 |
| Milk (whole, 250ml) | 61 | 3.2 | 3.3 | 4.8 |
| Protein shake (~1 scoop) | ~120 | 25 | 1.5 | 3 |

For foods not on this list, use your general nutritional knowledge. Be transparent when estimating.

## Important

- Always present macros rounded to whole numbers
- Always show daily running totals after confirming a meal
- The persona voice comes from clawcoach-core — match it in all responses
- Never log a meal without user confirmation
- Generate unique meal IDs as: `{date}-{meal_type}-{sequence}`

---
description: Japanese meal planning with nutrition balance, seasonal ingredients, and budget optimization.
---

# Meal Planner JP

Japanese meal planning with nutrition balance and budget optimization.

**Triggers**: "meal plan", "献立", "今日の晩ごはん", "what should I eat", "1週間の献立", "recipe suggestion"

## Requirements

- `web_search` tool access (for recipe lookup)
- No API keys needed

## Instructions

1. **Gather preferences** (use defaults if not specified):
   | Setting | Default | Options |
   |---------|---------|---------|
   | Servings | 1人 | 1-6人 |
   | Budget | ¥500/meal | ¥300-1000 |
   | Period | 1 day | 1日/3日/1週間 |
   | Restrictions | None | Allergies, vegetarian, halal |
   | Skill level | 普通 | 初心者/普通/料理好き |
   | Cook time | 30 min | 15分/30分/1時間 |

2. **Search for recipes**:
   ```
   web_search("簡単 晩ごはん レシピ [季節の食材]")
   web_search("一人暮らし 節約 レシピ [食材名]")
   ```

3. **Balance nutrition** per meal (一汁三菜 principle):
   - 🟤 **主食** — rice, noodles, bread
   - 🔴 **主菜** — meat, fish, egg, tofu (protein)
   - 🟢 **副菜** — vegetables, seaweed, mushrooms (2 types ideally)
   - 🟡 **汁物** — miso soup, clear soup

4. **Output format**:
   ```
   ## 🍱 Meal Plan
   **Period:** MM/DD–MM/DD | **Budget:** ~¥X,XXX | **Servings:** X人

   ### Monday (MM/DD)
   🌅 Breakfast — Toast, fried egg, salad (¥150, 10min)
   🌞 Lunch — Onigiri ×2, miso soup (¥200, 15min)
   🌙 Dinner — Chicken teriyaki, spinach ohitashi, miso soup (¥400, 25min)

   ### 🛒 Shopping List
   | Item | Amount | Est. Price |
   |------|--------|-----------|
   | Chicken thigh | 300g | ¥300 |
   | Spinach | 1 bunch | ¥150 |
   | Tofu | 1 block | ¥80 |

   **Weekly total: ~¥X,XXX**
   ```

5. **Recipe details** (on request) — step-by-step with cooking tips.

## Seasonal Ingredients (旬の食材)

| Season | Vegetables | Fish/Seafood |
|--------|-----------|-------------|
| Spring (3-5月) | Bamboo shoots, cabbage, peas | Bonito, sea bream |
| Summer (6-8月) | Eggplant, tomato, cucumber | Eel, squid |
| Autumn (9-11月) | Sweet potato, mushrooms, kabocha | Salmon, sanma |
| Winter (12-2月) | Daikon, hakusai, leek | Yellowtail, cod |

## Edge Cases

- **Convenience store mix**: Include konbini options for busy days (mark with 🏪).
- **Leftovers optimization**: Plan meals that reuse ingredients (e.g., extra chicken for lunch next day).
- **No kitchen access**: Suggest no-cook meals or rice cooker-only recipes.
- **Dietary restrictions**: For vegetarian Japanese meals, focus on tofu, natto, vegetables, and seaweed.
- **Budget breakdown mismatch**: Prices vary by region. Note that prices are Tokyo supermarket estimates.

## Security

- No personal health data is stored — meal plans are generated per-request.

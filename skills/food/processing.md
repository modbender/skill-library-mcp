# Food Input Processing

Reference only — how to handle each input type.

## Auto-Classification

| Input | Type | Action |
|-------|------|--------|
| Photo + "ate/had/just" | meal | log + offer analysis |
| Photo with barcode/label | product | extract nutrition, store |
| Photo of raw ingredients | inventory | list items |
| Photo of menu | restaurant | extract options, suggest |
| Photo with recipe/steps | recipe | extract and save |
| "I ate X" | meal | log, infer context |
| "allergic/avoid X" | preference | store permanently |
| "find restaurant" | restaurant | suggest |
| "what can I cook" | recipe | suggest from ingredients |
| "plan my week" | plan | generate meal plan |

## Meal Photo Pipeline
1. Identify food items and portions
2. Detect context: home/restaurant/takeout (plate style, setting)
3. Tag: #meal #[context] #[meal_type]
4. Prompt: "Want nutrition estimate?"
5. Store with timestamp

## Label Photo Pipeline
1. OCR: brand, product, nutrition facts, ingredients
2. Normalize to standard units
3. Tag: #product #[brand]
4. Store for quick-log reuse
5. "Next time just say 'had [product]'"

## Recipe Photo/Text Pipeline
1. Extract: title, ingredients, steps
2. Parse ingredient quantities
3. Tag: #recipe #[cuisine]
4. Link to inventory if tracking
5. Calculate approximate nutrition per serving

## Text Input Pipeline
1. Classify intent: log / query / plan / edit
2. Route to appropriate handler
3. Confirm action taken

## Tagging System
- #meal — something eaten
- #product — packaged food with nutrition
- #recipe — how to make something
- #restaurant — place to eat
- #inventory — what's in stock
- #preference — likes/dislikes/restrictions

## Context Inference
- 6-10am: breakfast
- 12-14: lunch
- 19-22: dinner
- "ordered/takeout": restaurant
- "cooked/made": home

## Weekly Insights (computed)
- Variety score: unique foods / total entries
- Frequent foods: top 5 this week
- Meal timing: average times per meal type
- Eating out ratio: restaurant / total
- Nutrition trends: if tracking enabled

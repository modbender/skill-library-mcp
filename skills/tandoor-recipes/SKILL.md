---
name: tandoor-recipes
description: Manage recipes, meal plans, and shopping lists in Tandoor Recipe Manager. Use when the user wants to create recipes, plan meals, search for recipes, or manage their shopping list.
metadata: { "openclaw": { "emoji": "🍽️", "requires": { "bins": ["node"], "env": ["TANDOOR_URL", "TANDOOR_API_TOKEN"] }, "primaryEnv": "TANDOOR_API_TOKEN" } }
---

# Tandoor Recipe Manager

Interact with the user's Tandoor Recipe Manager to manage recipes, meal plans, and shopping lists.

## How to Use

**Required env vars:** `TANDOOR_URL` (Tandoor instance URL) and `TANDOOR_API_TOKEN`

```bash
node ./scripts/tandoor.js <command> [args...]
```

---

## What You Can Do

### 🔍 Find Recipes

**Search by name:**
```bash
node ./scripts/tandoor.js search-recipes "pasta"
node ./scripts/tandoor.js search-recipes "chicken" 20  # limit to 20 results
```

**Get full recipe details:**
```bash
node ./scripts/tandoor.js get-recipe 42
```

---

### 📅 Meal Planning

**See available meal types (Breakfast, Lunch, Dinner, etc.):**
```bash
node ./scripts/tandoor.js get-meal-types
```

**Add a recipe to the meal plan:**
```bash
node ./scripts/tandoor.js add-to-meal-plan <recipe_id> "<meal_type>" "<YYYY-MM-DD>"
# Example: Add recipe 42 as Dinner on Feb 10th
node ./scripts/tandoor.js add-to-meal-plan 42 "Dinner" "2025-02-10"
```

**View meal plans for a date range:**
```bash
node ./scripts/tandoor.js get-meal-plans "2025-02-08" "2025-02-14"
```

---

### 🛒 Shopping List

**View current shopping list:**
```bash
node ./scripts/tandoor.js get-shopping-list
node ./scripts/tandoor.js get-shopping-list "true"   # show checked items
node ./scripts/tandoor.js get-shopping-list "both"   # show all
```

**Add an item to the shopping list:**
```bash
node ./scripts/tandoor.js add-shopping-item "<food>" "<amount>" "<unit>" "[note]"
# Example:
node ./scripts/tandoor.js add-shopping-item "Chicken Breast" "500" "g" "For stir fry"
```

**Check off an item:**
```bash
node ./scripts/tandoor.js check-shopping-item <item_id>
```

**Remove an item:**
```bash
node ./scripts/tandoor.js remove-shopping-item <item_id>
```

---

### ➕ Create New Recipes

```bash
node ./scripts/tandoor.js create-recipe "<name>" "<ingredients>" "<instructions>" [servings]
```

Example:
```bash
node ./scripts/tandoor.js create-recipe "Grilled Cheese" \
  "2 slices bread
2 slices cheese
1 tbsp butter" \
  "1. Butter the bread
2. Add cheese between slices
3. Grill until golden brown" \
  2
```

---

### 📚 Browse Reference Data

```bash
node ./scripts/tandoor.js get-keywords          # all keywords
node ./scripts/tandoor.js get-keywords "italian" # search keywords
node ./scripts/tandoor.js get-foods "chicken"    # search foods
node ./scripts/tandoor.js get-units              # all units
```

---

## Workflows

### Plan Dinner for the Week

1. **Search for recipes** the user might enjoy:
   ```bash
   node ./scripts/tandoor.js search-recipes "chicken"
   ```
2. **Note the recipe IDs** from the results
3. **Get available meal types** (to confirm "Dinner" exists):
   ```bash
   node ./scripts/tandoor.js get-meal-types
   ```
4. **Add each recipe to a day** (repeat for each day):
   ```bash
   node ./scripts/tandoor.js add-to-meal-plan 42 "Dinner" "2025-02-10"
   node ./scripts/tandoor.js add-to-meal-plan 15 "Dinner" "2025-02-11"
   # ... continue for each day
   ```

---

### Check Today's Meal Plan

1. **Get today's meal plans**:
   ```bash
   node ./scripts/tandoor.js get-meal-plans "2025-02-08"
   ```
2. **If user wants recipe details**, get the full recipe:
   ```bash
   node ./scripts/tandoor.js get-recipe <recipe_id>
   ```

---

### Add Recipe Ingredients to Shopping List

1. **Get the recipe details** to see all ingredients:
   ```bash
   node ./scripts/tandoor.js get-recipe <recipe_id>
   ```
2. **Parse the ingredients** from the response (look at `steps[].ingredients[]`)
3. **Add each ingredient** to the shopping list:
   ```bash
   node ./scripts/tandoor.js add-shopping-item "Chicken Breast" "500" "g"
   node ./scripts/tandoor.js add-shopping-item "Onion" "2" "piece"
   # ... continue for each ingredient
   ```

---

### Create and Schedule a New Recipe

1. **Create the recipe**:
   ```bash
   node ./scripts/tandoor.js create-recipe "Pasta Carbonara" \
     "200g spaghetti
   100g pancetta
   2 eggs
   50g parmesan" \
     "1. Cook pasta
   2. Fry pancetta
   3. Mix eggs with parmesan
   4. Combine all and serve" \
     2
   ```
2. **Note the recipe ID** from the response
3. **Add to meal plan**:
   ```bash
   node ./scripts/tandoor.js add-to-meal-plan <new_recipe_id> "Dinner" "2025-02-12"
   ```

---

### Clear Checked Items from Shopping List

1. **View checked items**:
   ```bash
   node ./scripts/tandoor.js get-shopping-list "true"
   ```
2. **Remove each checked item** by ID:
   ```bash
   node ./scripts/tandoor.js remove-shopping-item <item_id>
   ```

---

## Troubleshooting

**"Food not found" or "Unit not found"**  
Search for the correct name in Tandoor first:
```bash
node ./scripts/tandoor.js get-foods "chicken"
node ./scripts/tandoor.js get-units "gram"
```

**"Meal type not found"**  
Run `get-meal-types` to see exact names (case-insensitive match).

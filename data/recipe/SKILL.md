---
name: Recipes
description: Build a personal recipe collection with ingredients, scaling, and meal planning.
metadata: {"clawdbot":{"emoji":"🍳","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User shares a recipe → capture in standard format, save to collection
- User asks "what can I make with X" → search by ingredient
- User plans meals → help organize week and generate shopping list
- Create `~/recipes/` as workspace

## When User Shares a Recipe
- URL → fetch and extract into standard format
- Photo of recipe → extract text, structure it
- Voice/text description → format into recipe structure
- Handwritten family recipe → preserve original, add structured version

## Recipe File Structure
- One Markdown file per recipe: `chicken-tikka-masala.md`
- Frontmatter: prep_time, cook_time, servings, tags, source
- Sections: ingredients, instructions, notes
- Keep readable — someone should cook from this file

## Key Fields
- Title and brief description
- Prep time, cook time, total time
- Servings (base for scaling)
- Ingredients with quantities and units
- Step-by-step instructions
- Tags: cuisine, meal-type, dietary, difficulty
- Source: URL, book, or "family recipe"
- Notes: substitutions, tips, variations tried

## Ingredient Format
- Quantity, unit, ingredient, prep: "2 cups chicken, diced"
- Consistent units — pick metric or imperial, stick with it
- Group by section if complex: "For the sauce:", "For the marinade:"
- Note optional ingredients clearly

## Scaling
- Store base servings in frontmatter
- Calculate scaled quantities on request
- Flag ingredients that don't scale linearly (salt, yeast, baking powder)
- Round to practical measurements — no "0.37 cups"

## Progressive Enhancement
- Week 1: dump recipes as they come, minimal formatting
- Week 2: standardize format, add tags
- Week 3: build index by cuisine/meal type
- Month 2: meal planning and shopping lists
- Month 3: ingredient inventory integration

## Folder Structure
```
~/recipes/
├── mains/
├── sides/
├── desserts/
├── basics/          # sauces, stocks, staples
├── index.md         # master list with tags
└── meal-plans/      # weekly plans
```

## Searching and Filtering
- By ingredient: "recipes with chickpeas"
- By tag: "quick weeknight", "vegetarian", "mexican"
- By time: "under 30 minutes"
- Favorites: tag or star system for go-to recipes

## Meal Planning
- Weekly plan: 7 dinners, optional lunches/breakfasts
- Balance variety — not three pasta dishes in a row
- Consider ingredient overlap — buy once, use twice
- Generate combined shopping list from plan

## Shopping List Generation
- Aggregate ingredients across selected recipes
- Combine same ingredients: 2 cups + 1 cup = 3 cups
- Group by store section: produce, dairy, pantry
- Exclude pantry staples user always has (configurable)

## What To Capture From URLs
- Recipe title and description
- Ingredients list (structured)
- Instructions (numbered steps)
- Times and servings
- Skip the life story — just the recipe

## Notes and Variations
- "Made this 2024-03-15, added more garlic, family loved it"
- Track modifications that worked
- Rate recipes after making them
- Flag recipes never actually made vs tested

## What NOT To Suggest
- Complex recipe management app — files work fine
- Nutrition calculation — too complex, use dedicated tool if needed
- Automated meal planning — user knows their preferences
- Social features — this is personal collection

## Family Recipe Preservation
- Scan or photograph original handwritten recipes
- Link image in the markdown file
- Keep original measurements even if odd ("coffee cup of flour")
- Note the source: "Grandma's recipe, circa 1960"

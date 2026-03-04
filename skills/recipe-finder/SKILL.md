# Recipe Finder

Find recipes by ingredients, cuisine, or dietary preferences using TheMealDB free API.

## Triggers

Use this skill when the user:
- Asks "what can I make with [ingredient]"
- Requests "recipes for dinner" or "Italian recipes"
- Says "vegetarian options" or "vegan meals"
- Asks for meal ideas based on ingredients they have

## Tools

- `web_fetch` - Fetch recipe data from TheMealDB API

## Instructions

1. Parse the user's request to identify:
   - Main ingredient (e.g., chicken, eggs, pasta)
   - Cuisine type (e.g., Italian, Mexican, Chinese)
   - Dietary restriction (e.g., vegetarian, vegan, gluten-free)

2. Call TheMealDB API:
   - By ingredient: `https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}`
   - By cuisine: `https://www.themealdb.com/api/json/v1/1/filter.php?a={cuisine}`
   - Search by name: `https://www.themealdb.com/api/json/v1/1/search.php?s={query}`

3. For each recipe found, optionally fetch details:
   - `https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}`

4. Format response with:
   - Recipe name
   - Thumbnail image (if available)
   - Category and cuisine
   - Key ingredients
   - Brief instructions (or link to full recipe)

## Response Format

Present recipes in a clean, scannable format:
- Recipe name (bold)
- Image thumbnail (if available)
- Category | Cuisine
- Main ingredients list
- Brief description

## Notes

- TheMealDB is free, no API key required
- Results are limited but reliable
- Combine multiple queries for best results (ingredient + cuisine)

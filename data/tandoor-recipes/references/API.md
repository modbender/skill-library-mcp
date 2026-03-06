# Tandoor API Quick Reference

Base URL: `${TANDOOR_URL}/api/`  
Auth: `Authorization: Bearer ${TANDOOR_API_TOKEN}`

## Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/recipe/` | GET, POST | List/create recipes |
| `/api/recipe/{id}/` | GET, PATCH, DELETE | Recipe details |
| `/api/meal-plan/` | GET, POST | List/create meal plans |
| `/api/meal-plan/{id}/` | GET, PATCH, DELETE | Meal plan entry |
| `/api/meal-type/` | GET | Available meal types |
| `/api/keyword/` | GET | Recipe keywords |
| `/api/food/` | GET | Available foods |
| `/api/unit/` | GET | Available units |
| `/api/shopping-list-entry/` | GET, POST | Shopping list |
| `/api/shopping-list-entry/{id}/` | GET, PATCH, DELETE | Shopping item |

## Common Query Parameters

### `/api/recipe/`
- `query` - Search by name (fuzzy match)
- `keywords_or` - Filter by keyword ID (repeatable)
- `foods_or` - Filter by food ID (repeatable)
- `rating` - Minimum rating (0-5)
- `page_size` - Results per page (default: 10)

### `/api/meal-plan/`
- `from_date` - Start date filter (YYYY-MM-DD)
- `to_date` - End date filter (YYYY-MM-DD)
- `meal_type` - Meal type ID

### `/api/shopping-list-entry/`
- `checked` - Filter: "true", "false", "both", "recent"

### `/api/keyword/`, `/api/food/`
- `query` - Search by name
- `root` - Get first-level children (0 for root)
- `tree` - Get all children in tree

## Request Body Formats

### Create Recipe
```json
{
  "name": "string",
  "description": "string (optional)",
  "servings": number,
  "steps": [{
    "instruction": "string",
    "ingredients": [{
      "food": {"name": "string"},
      "unit": {"name": "string"},
      "amount": "string"
    }]
  }]
}
```

### Create Meal Plan
```json
{
  "recipe": {"id": number, "name": "string", "keywords": []},
  "meal_type": {"id": number, "name": "string"},
  "from_date": "YYYY-MM-DDTHH:MM:SS",
  "servings": "string",
  "title": "string (optional)",
  "note": "string (optional)"
}
```

### Add Shopping Item
```json
{
  "food": {"id": number, "name": "string"},
  "unit": {"id": number, "name": "string"},
  "amount": "string",
  "note": "string (optional)"
}
```

## Notes

- `from_date` in meal plans must include time: `YYYY-MM-DDTHH:MM:SS`
- `servings` in meal plans must be a string, not number
- Shopping list items require both food and unit IDs (lookup first)

# FatSecret API Reference

## Authentication

FatSecret uses OAuth1 for authentication. Required credentials:
- `consumer_key`: Your API consumer key
- `consumer_secret`: Your API consumer secret

Get credentials at: https://platform.fatsecret.com/register

## Configuration

Store credentials in `$CONFIG_DIR/config.json`:
```json
{
  "consumer_key": "your_key_here",
  "consumer_secret": "your_secret_here"
}
```

Where `$CONFIG_DIR` is:
- Default: `~/.config/fatsecret/`
- Or set `FATSECRET_CONFIG_DIR` env var (recommended for containers)

## API Methods

### Food Search & Lookup

#### foods.search
Search foods by keyword.

Parameters:
- `search_expression`: Search query (required)
- `page_number`: Page index, 0-based (default: 0)
- `max_results`: Results per page, max 50 (default: 20)

Response contains `foods.food[]` array with:
- `food_id`: Unique identifier
- `food_name`: Name
- `brand_name`: Brand (if applicable)
- `food_type`: "Brand" or "Generic"
- `food_description`: Brief nutrition summary

#### food.get.v4
Get detailed food information.

Parameters:
- `food_id`: FatSecret food ID (required)

Response contains `food` object with:
- Basic info (name, brand, type)
- `servings.serving[]`: Array of serving sizes with full nutrition data

Serving nutrition fields:
- `calories`, `protein`, `carbohydrate`, `fat`
- `saturated_fat`, `polyunsaturated_fat`, `monounsaturated_fat`
- `cholesterol`, `sodium`, `potassium`
- `fiber`, `sugar`
- `vitamin_a`, `vitamin_c`, `calcium`, `iron`

#### food.find_id_for_barcode
Lookup food by UPC/EAN barcode.

Parameters:
- `barcode`: Product barcode (required)

Response contains `food_id.value` with the food ID.

#### foods.autocomplete
Get search suggestions.

Parameters:
- `expression`: Partial search term
- `max_results`: Max suggestions (default: 10)

### Recipe Methods

#### recipes.search.v3
Search recipes.

Parameters:
- `search_expression`: Search query
- `page_number`: Page index
- `max_results`: Results per page

#### recipe.get.v2
Get recipe details.

Parameters:
- `recipe_id`: Recipe ID

Response includes ingredients, directions, and nutrition.

## Rate Limits

- Basic tier: 5,000 calls/day
- Premier tier: Unlimited

## Error Codes

| Code | Meaning |
|------|---------|
| 2 | Missing required parameter |
| 3 | Invalid parameter value |
| 4 | Invalid API method |
| 5 | Invalid consumer key |
| 8 | Invalid signature |
| 9 | Rate limit exceeded |
| 106 | Food/barcode not found |
| 107 | Recipe not found |

## Regional Data

Basic tier: US dataset only
Premier tier: 56+ countries including Italy (IT)

To request Italian data, add `region=IT` parameter (Premier only).

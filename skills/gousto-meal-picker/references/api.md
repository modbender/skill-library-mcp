# Gousto API Reference

Base URL: `https://production-api.gousto.co.uk`

All endpoints require `Authorization: Bearer <token>` header.

## Authentication

Tokens are stored in browser cookies (`v1_oauth_token`). Auth endpoints (`/oauth/access-token`, `/oauth/refresh-token`, `/login`) are **WAF-protected** and cannot be called from curl/fetch — only from a real browser context.

### Token structure (from cookie)

```
v1_oauth_token: {"access_token": "<token>"}
v1_oauth_expiry: {"expires_at": "<ISO datetime>"}
v1_oauth_refresh: {"refresh_token": "<token>"}
```

Tokens expire ~10 hours after login.

## Endpoints

### GET /user/current

Returns user profile. Use to verify auth and discover `auth_user_id` and numeric `id`.

### GET /user/current/orders?limit=10&sort_order=desc&state=pending

Returns pending orders (v1 format). Use to get order IDs.

### GET /order/v2/orders/{orderId}

Returns full order details (JSON:API format) including:
- `data.attributes`: state, phase, prices, menu_active_from, cut_off_date
- `data.relationships.components.data[]`: selected recipes
- `data.relationships.shipping_address`, `delivery_slot`, `delivery_day`, `day_slot_lead_time`, `delivery_tariff`
- `included[]`: full recipe objects with allergens, cook times, calories, ingredients

**Key fields in recipe objects:**
- `attributes.name` — recipe name
- `attributes.prep_times.for2` — cook time for 2 portions
- `attributes.calories.for2` — kcal for 2 portions
- `attributes.allergens[]` — `{contain_type: "contains"|"may_contain", slug: "nut"|"peanut"|...}`
- `attributes.dish_types[]` — `{name: "Pasta"|"Stir Fry"|...}`
- `attributes.diet_type.slug` — "meat", "vegetarian", "plant-based"
- `attributes.health_attributes[]` — `{slug: "healthy"|"not-healthy"}`

### GET /menu/v3/menus?delivery_date=YYYY-MM-DD&num_portions=2&user_id=<auth_user_id>

Returns all available recipes for a delivery week. Response has `recipes` object keyed by UUID with fields: `id`, `name`, `prep_time`, `nutritional_information.per_portion.energy_kcal`, `is_available`, `dietary_claims[]`, `food_brand`, `rating`.

Additional useful params: `include_core_recipe_id=true`, `option_types=none&option_types=recipes&option_types=ingredients`

### GET /menu/v3/boxes?user_id=<auth_user_id>

Returns available box sizes. Format: `{id: "SKU-GMT-{recipes}-{portions}", number_of_portions, number_of_recipes}`.

### GET /subscriptionquery/v1/projected-deliveries/{numericUserId}

Returns projected delivery dates and order IDs.

### GET /subscriptionquery/v1/subscriptions/{numericUserId}

Returns subscription details.

### PUT /order/v2/orders/{orderId}

**Updates an order with recipe selections.** This is the key endpoint.

#### Payload format

```json
{
  "data": {
    "type": "order",
    "id": "<orderId>",
    "attributes": {
      "menu_id": "<menu core_id>"
    },
    "relationships": {
      "components": {
        "data": [
          {
            "id": "<recipe-uuid>",
            "type": "recipe",
            "meta": { "portion_for": 2 }
          }
        ]
      },
      "shipping_address": {
        "data": { "type": "shipping-address", "id": "<addressId>" }
      },
      "delivery_slot": {
        "data": { "id": "<slotId>", "type": "delivery-slot", "meta": {} }
      },
      "day_slot_lead_time": {
        "data": { "id": "<leadTimeId>", "type": "day-slot-lead-time", "meta": {} }
      },
      "delivery_day": {
        "data": { "id": "<dayId>", "type": "delivery-day", "meta": {} }
      },
      "delivery_tariff": {
        "data": { "type": "delivery-tariff", "id": "<tariffId>" }
      }
    }
  }
}
```

All relationship fields must be included (copied from the existing order). Components should include **all** recipes for the order (existing + new).

#### Important notes

- The box type auto-adjusts based on number of recipes in components
- Recipe IDs are UUIDs from the menu endpoint, not core_recipe_ids
- `portion_for` should match your plan (typically 2)
- Returns 200 with updated order on success, or `{errors: [...]}` on failure

### POST /order/v2/prices

Calculates pricing for a given set of recipes. Not needed for selection but useful for cost estimates.

## Menu timing

- Menus open **Tuesdays at 12pm UK**
- Each menu opens **13 days** before its Monday delivery date
- Orders can be edited until the `cut_off_date` (typically the Thursday before delivery)

# Shopify Inventory & Locations

## Get Inventory Levels

```graphql
query GetInventoryLevels($inventoryItemId: ID!) {
  inventoryItem(id: $inventoryItemId) {
    id
    sku
    inventoryLevels(first: 10) {
      nodes {
        id
        quantities(names: ["available", "incoming", "committed", "on_hand"]) {
          name
          quantity
        }
        location {
          id
          name
        }
      }
    }
  }
}
```
Variables: `{ "inventoryItemId": "gid://shopify/InventoryItem/123" }`

Quantity names:
- `available` - quantity available for sale
- `incoming` - quantity being transferred in
- `committed` - quantity committed to orders
- `on_hand` - total physical quantity

## List Locations

```graphql
query ListLocations {
  locations(first: 10) {
    nodes {
      id
      name
      address {
        address1
        city
        province
        country
      }
      isActive
    }
  }
}
```

## Adjust Inventory

> REQUIRES PERMISSION: Adjusting inventory levels directly affects product availability and stock counts. This can result in overselling or incorrect stock levels. Always ask the user for explicit confirmation, show the current quantity, the delta, and the final quantity before executing this operation.

```graphql
mutation AdjustInventory($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    inventoryAdjustmentGroup {
      reason
      changes {
        name
        delta
      }
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "input": {
    "reason": "correction",
    "name": "available",
    "changes": [
      {
        "inventoryItemId": "gid://shopify/InventoryItem/123",
        "locationId": "gid://shopify/Location/456",
        "delta": 10
      }
    ]
  }
}
```

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `inventoryAdjustQuantities` | Directly modifies stock levels, affecting product availability | Partial - Can adjust again, but changes are immediate |

Permission Protocol: Before executing `inventoryAdjustQuantities`:
1. Show the inventory item ID and SKU
2. Display the current quantity at the location
3. Show the delta (change amount: positive or negative)
4. Calculate and show the resulting quantity
5. Indicate the reason for the adjustment
6. Wait for explicit user confirmation with "yes", "confirm", or "proceed"
7. Warn that changes are immediate and affect customer-facing availability

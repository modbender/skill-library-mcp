# Shopify Discounts

Manage discount codes, automatic discounts, Buy X Get Y promotions, and free shipping offers via the GraphQL Admin API.

## Discount Types

| Type | Description | Code Required |
|------|-------------|---------------|
| **Basic** | Percentage or fixed amount off | Optional (code or automatic) |
| **BXGY** | Buy X Get Y promotions | Optional (code or automatic) |
| **Free Shipping** | Waive shipping costs | Optional (code or automatic) |
| **App** | Custom logic via Shopify Functions | Optional (code or automatic) |

## List Discounts

```graphql
query ListDiscounts($first: Int!, $after: String, $query: String) {
  discountNodes(first: $first, after: $after, query: $query) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      discount {
        ... on DiscountCodeBasic {
          title
          status
          startsAt
          endsAt
        }
        ... on DiscountAutomaticBasic {
          title
          status
          startsAt
          endsAt
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Discount by ID

```graphql
query GetDiscount($id: ID!) {
  discountNode(id: $id) {
    id
    discount {
      ... on DiscountCodeBasic {
        title
        status
        startsAt
        endsAt
        usageLimit
        appliesOncePerCustomer
        combinesWith {
          orderDiscounts
          productDiscounts
          shippingDiscounts
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/DiscountCodeNode/123" }`

## Create Code Discount (Percentage Off)

```graphql
mutation CreateBasicCodeDiscount($basicCodeDiscount: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
    codeDiscountNode {
      id
      codeDiscount {
        ... on DiscountCodeBasic {
          title
          codes(first: 1) {
            nodes {
              code
            }
          }
        }
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
  "basicCodeDiscount": {
    "title": "20% Off Summer Sale",
    "code": "SUMMER20",
    "startsAt": "2025-06-01T00:00:00Z",
    "endsAt": "2025-08-31T23:59:59Z",
    "usageLimit": 1000,
    "appliesOncePerCustomer": true,
    "customerGets": {
      "value": {
        "percentage": 0.20
      },
      "items": {
        "all": true
      }
    },
    "context": {
      "allBuyers": true
    },
    "combinesWith": {
      "shippingDiscounts": true
    }
  }
}
```

## Create Automatic Discount (Fixed Amount)

```graphql
mutation CreateAutomaticDiscount($automaticBasicDiscount: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicCreate(automaticBasicDiscount: $automaticBasicDiscount) {
    automaticDiscountNode {
      id
      automaticDiscount {
        ... on DiscountAutomaticBasic {
          title
          status
        }
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
  "automaticBasicDiscount": {
    "title": "$10 Off Orders Over $50",
    "startsAt": "2025-01-01T00:00:00Z",
    "minimumRequirement": {
      "subtotal": {
        "greaterThanOrEqualToSubtotal": "50.00"
      }
    },
    "customerGets": {
      "value": {
        "discountAmount": {
          "amount": "10.00",
          "appliesOnEachItem": false
        }
      },
      "items": {
        "all": true
      }
    },
    "context": {
      "allBuyers": true
    }
  }
}
```

## Create Buy X Get Y Discount

```graphql
mutation CreateBxgyDiscount($automaticBxgyDiscount: DiscountAutomaticBxgyInput!) {
  discountAutomaticBxgyCreate(automaticBxgyDiscount: $automaticBxgyDiscount) {
    automaticDiscountNode {
      id
      automaticDiscount {
        ... on DiscountAutomaticBxgy {
          title
          startsAt
        }
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
  "automaticBxgyDiscount": {
    "title": "Buy 2 Get 1 Free",
    "startsAt": "2025-01-01T00:00:00Z",
    "customerBuys": {
      "items": {
        "collections": {
          "add": ["gid://shopify/Collection/123"]
        }
      },
      "value": {
        "quantity": "2"
      }
    },
    "customerGets": {
      "items": {
        "collections": {
          "add": ["gid://shopify/Collection/123"]
        }
      },
      "value": {
        "discountOnQuantity": {
          "quantity": "1",
          "effect": {
            "percentage": 1.0
          }
        }
      }
    },
    "usesPerOrderLimit": "1",
    "context": {
      "allBuyers": true
    }
  }
}
```

## Create Free Shipping Discount

```graphql
mutation CreateFreeShippingDiscount($freeShippingCodeDiscount: DiscountCodeFreeShippingInput!) {
  discountCodeFreeShippingCreate(freeShippingCodeDiscount: $freeShippingCodeDiscount) {
    codeDiscountNode {
      id
      codeDiscount {
        ... on DiscountCodeFreeShipping {
          title
          codes(first: 1) {
            nodes {
              code
            }
          }
        }
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
  "freeShippingCodeDiscount": {
    "title": "Free Shipping Over $75",
    "code": "FREESHIP75",
    "startsAt": "2025-01-01T00:00:00Z",
    "minimumRequirement": {
      "subtotal": {
        "greaterThanOrEqualToSubtotal": "75.00"
      }
    },
    "context": {
      "allBuyers": true
    }
  }
}
```

## Update Discount

```graphql
mutation UpdateCodeDiscount($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
  discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
    codeDiscountNode {
      id
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
  "id": "gid://shopify/DiscountCodeNode/123",
  "basicCodeDiscount": {
    "endsAt": "2025-12-31T23:59:59Z"
  }
}
```

## Activate/Deactivate Discount

> REQUIRES PERMISSION: Activating or deactivating a discount changes its status immediately and affects pricing for all customers. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation ActivateCodeDiscount($id: ID!) {
  discountCodeActivate(id: $id) {
    codeDiscountNode {
      id
      codeDiscount {
        ... on DiscountCodeBasic {
          status
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

```graphql
mutation DeactivateCodeDiscount($id: ID!) {
  discountCodeDeactivate(id: $id) {
    codeDiscountNode {
      id
    }
    userErrors {
      field
      message
    }
  }
}
```

## Delete Discount

> REQUIRES PERMISSION: Deleting a discount is permanent and cannot be undone. Customers will no longer be able to use this discount code. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation DeleteCodeDiscount($id: ID!) {
  discountCodeDelete(id: $id) {
    deletedCodeDiscountId
    userErrors {
      field
      message
    }
  }
}
```

## Bulk Delete Discounts

> REQUIRES PERMISSION: Bulk deletion permanently removes multiple discounts at once and cannot be undone. Always ask the user for explicit confirmation and show the list of discounts to be deleted before executing this operation.

```graphql
mutation BulkDeleteDiscounts($ids: [ID!]) {
  discountCodeBulkDelete(ids: $ids) {
    job {
      id
      done
    }
    userErrors {
      field
      message
    }
  }
}
```
Variables: `{ "ids": ["gid://shopify/DiscountCodeNode/123", "gid://shopify/DiscountCodeNode/456"] }`

## Target Customer Segments

To target specific customer segments with discounts, use the `context` field:

```json
{
  "context": {
    "customerSegments": {
      "add": ["gid://shopify/Segment/123"]
    }
  }
}
```

## API Scopes Required

- `read_discounts` - Read discount information
- `write_discounts` - Create, update, delete discounts

## Status Values

| Status | Description |
|--------|-------------|
| `ACTIVE` | Discount is currently active |
| `EXPIRED` | Discount has passed its end date |
| `SCHEDULED` | Discount has a future start date |

## Discount Combinations

Control which discount types can combine using `combinesWith`:

```json
{
  "combinesWith": {
    "orderDiscounts": true,
    "productDiscounts": false,
    "shippingDiscounts": true
  }
}
```

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `discountCodeActivate` | Makes discount active and available to customers immediately | Yes (can deactivate) |
| `discountCodeDeactivate` | Makes discount inactive and unavailable to customers immediately | Yes (can reactivate) |
| `discountAutomaticActivate` | Makes automatic discount active immediately | Yes (can deactivate) |
| `discountAutomaticDeactivate` | Makes automatic discount inactive immediately | Yes (can reactivate) |
| `discountCodeDelete` | Permanently deletes discount code | No |
| `discountCodeBulkDelete` | Permanently deletes multiple discount codes at once | No |
| `discountAutomaticDelete` | Permanently deletes automatic discount | No |

Permission Protocol: Before executing any of these operations, describe what will be changed (discount ID, title, current status) and wait for explicit user confirmation.

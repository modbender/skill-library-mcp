# Shopify Refunds

Process refunds for orders via the GraphQL Admin API.

## Overview

Refunds return money to customers for returned items, cancelled orders, or service issues. Refunds can include restocking items and refunding shipping.

## Get Refund

```graphql
query GetRefund($id: ID!) {
  refund(id: $id) {
    id
    createdAt
    note
    totalRefundedSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    refundLineItems(first: 20) {
      nodes {
        lineItem {
          title
          sku
        }
        quantity
        restockType
        subtotalSet {
          shopMoney {
            amount
          }
        }
      }
    }
    transactions(first: 5) {
      nodes {
        id
        kind
        status
        amountSet {
          shopMoney {
            amount
          }
        }
        gateway
      }
    }
    order {
      id
      name
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Refund/123" }`

## List Refunds on Order

```graphql
query GetOrderRefunds($orderId: ID!) {
  order(id: $orderId) {
    id
    name
    refunds(first: 10) {
      id
      createdAt
      totalRefundedSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      refundLineItems(first: 10) {
        nodes {
          lineItem {
            title
          }
          quantity
        }
      }
    }
  }
}
```

## Create Refund

> REQUIRES PERMISSION: Creating a refund is a PERMANENT financial transaction that returns money to the customer and CANNOT BE UNDONE. Always ask the user for explicit confirmation, show the refund amount and items, and wait for approval before executing this operation.

```graphql
mutation CreateRefund($input: RefundInput!) {
  refundCreate(input: $input) {
    refund {
      id
      totalRefundedSet {
        shopMoney {
          amount
          currencyCode
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
  "input": {
    "orderId": "gid://shopify/Order/123",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/456",
        "quantity": 1,
        "restockType": "RETURN"
      }
    ],
    "notify": true,
    "note": "Customer returned item - wrong size"
  }
}
```

## Create Full Refund

```graphql
mutation CreateFullRefund($input: RefundInput!) {
  refundCreate(input: $input) {
    refund {
      id
      totalRefundedSet {
        shopMoney {
          amount
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
  "input": {
    "orderId": "gid://shopify/Order/123",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/456",
        "quantity": 2,
        "restockType": "RETURN"
      },
      {
        "lineItemId": "gid://shopify/LineItem/789",
        "quantity": 1,
        "restockType": "RETURN"
      }
    ],
    "shipping": {
      "fullRefund": true
    },
    "notify": true
  }
}
```

## Refund Shipping Only

```graphql
mutation RefundShipping($input: RefundInput!) {
  refundCreate(input: $input) {
    refund {
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
  "input": {
    "orderId": "gid://shopify/Order/123",
    "shipping": {
      "amount": {
        "amount": "9.99",
        "currencyCode": "USD"
      }
    },
    "note": "Shipping refund - delayed delivery"
  }
}
```

## Refund Without Restock

For items not being returned:

```graphql
mutation RefundNoRestock($input: RefundInput!) {
  refundCreate(input: $input) {
    refund {
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
  "input": {
    "orderId": "gid://shopify/Order/123",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/456",
        "quantity": 1,
        "restockType": "NO_RESTOCK"
      }
    ],
    "note": "Item damaged - no return required"
  }
}
```

## Refund Duties

```graphql
mutation RefundDuties($input: RefundInput!) {
  refundCreate(input: $input) {
    refund {
      id
      totalRefundedSet {
        shopMoney {
          amount
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
  "input": {
    "orderId": "gid://shopify/Order/123",
    "refundDuties": [
      {
        "dutyId": "gid://shopify/Duty/456",
        "refundType": "FULL"
      }
    ]
  }
}
```

## Calculate Suggested Refund

Before creating a refund, calculate the suggested amounts:

```graphql
mutation CalculateSuggestedRefund($input: SuggestedRefundInput!) {
  suggestedRefund(input: $input) {
    suggestedTransactions {
      kind
      amount
      gateway
    }
    subtotalSet {
      shopMoney {
        amount
      }
    }
    totalTaxSet {
      shopMoney {
        amount
      }
    }
    totalCartDiscountAmountSet {
      shopMoney {
        amount
      }
    }
    refundLineItems {
      lineItem {
        title
      }
      quantity
      subtotalSet {
        shopMoney {
          amount
        }
      }
    }
  }
}
```
Variables:
```json
{
  "input": {
    "orderId": "gid://shopify/Order/123",
    "refundLineItems": [
      {
        "lineItemId": "gid://shopify/LineItem/456",
        "quantity": 1
      }
    ],
    "refundShipping": true
  }
}
```

## Restock Types

| Type | Description |
|------|-------------|
| `RETURN` | Item returned, add back to inventory |
| `CANCEL` | Item cancelled, add back to inventory |
| `NO_RESTOCK` | Don't add back to inventory |
| `LEGACY_RESTOCK` | Legacy restock behavior |

## Refund Transaction Kinds

| Kind | Description |
|------|-------------|
| `REFUND` | Money returned to customer |
| `VOID` | Authorization voided |
| `CHANGE` | Refund as store credit |

## Transaction Status

| Status | Description |
|--------|-------------|
| `SUCCESS` | Refund processed |
| `PENDING` | Processing |
| `FAILURE` | Refund failed |
| `ERROR` | Error occurred |

## Duty Refund Types

| Type | Description |
|------|-------------|
| `FULL` | Full duty refund |
| `PROPORTIONAL` | Proportional to items |

## API Scopes Required

- `read_orders` - Read order and refund information
- `write_orders` - Create refunds

## Best Practices

1. **Calculate first** - Use `suggestedRefund` before creating
2. **Notify customers** - Set `notify: true` for email confirmation
3. **Add notes** - Document refund reasons
4. **Choose restock type** - Match business logic (return vs damage)
5. **Handle partial refunds** - Refund specific quantities

## Notes

- Refunds are final and cannot be undone
- Multiple refunds can be issued for one order
- Restocking automatically adjusts inventory
- Shipping can be refunded separately from items
- Duties are refunded separately for international orders

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `refundCreate` | Permanently refunds money to customer (financial transaction) | No - IRREVERSIBLE |
| `suggestedRefund` | Calculates refund amounts (read-only, safe) | N/A - Read-only |

Permission Protocol: Before executing `refundCreate`:
1. Show the order ID and customer information
2. List all items being refunded with quantities and amounts
3. Show total refund amount including shipping and taxes
4. Indicate whether inventory will be restocked
5. Wait for explicit user confirmation with "yes", "confirm", or "proceed"
6. Emphasize that this action CANNOT be undone

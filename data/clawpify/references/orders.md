# Shopify Orders

## List Orders

```graphql
query ListOrders($first: Int!, $after: String, $query: String) {
  orders(first: $first, after: $after, query: $query) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      name
      createdAt
      displayFinancialStatus
      displayFulfillmentStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
      customer {
        id
        displayName
        defaultEmailAddress {
          emailAddress
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

Order query syntax:
- `financial_status:paid` - PENDING, AUTHORIZED, PARTIALLY_PAID, PAID, PARTIALLY_REFUNDED, REFUNDED, VOIDED
- `fulfillment_status:unfulfilled` - UNFULFILLED, PARTIALLY_FULFILLED, FULFILLED
- `created_at:>2024-01-01` - date filters
- `name:#1001` - by order number

## Get Order by ID

```graphql
query GetOrder($id: ID!) {
  order(id: $id) {
    id
    name
    email
    createdAt
    displayFinancialStatus
    displayFulfillmentStatus
    totalPriceSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    subtotalPriceSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    totalShippingPriceSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    totalTaxSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    lineItems(first: 50) {
      nodes {
        id
        title
        quantity
        sku
        originalUnitPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        variant {
          id
          title
        }
      }
    }
    shippingAddress {
      address1
      address2
      city
      province
      country
      zip
      phone
    }
    customer {
      id
      displayName
      email
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Order/123" }`

## Cancel Order

> REQUIRES PERMISSION: Cancelling an order may trigger automatic refunds to the customer and affects inventory if restocking is enabled. This is a significant business operation. Always ask the user for explicit confirmation, show the order details and refund method, and wait for approval before executing this operation.

```graphql
mutation CancelOrder($orderId: ID!, $reason: OrderCancelReason!, $restock: Boolean!, $refundMethod: OrderCancelRefundMethodInput) {
  orderCancel(orderId: $orderId, reason: $reason, restock: $restock, refundMethod: $refundMethod) {
    job {
      id
    }
    orderCancelUserErrors {
      field
      message
    }
  }
}
```
Variables:
```json
{
  "orderId": "gid://shopify/Order/123",
  "reason": "CUSTOMER",
  "restock": true,
  "refundMethod": {
    "originalPaymentMethodsRefund": true
  }
}
```
Reasons: CUSTOMER, FRAUD, INVENTORY, DECLINED, OTHER

Refund options:
- `originalPaymentMethodsRefund: true` - refund to original payment method
- `storeCreditRefund: { fullAmount: true }` - refund as store credit

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `orderCancel` | Cancels order and may trigger automatic refunds to customer | Partial - Order status change is permanent, but new order can be created |

Permission Protocol: Before executing `orderCancel`:
1. Show the order ID, order number, and customer information
2. Display the order total and line items
3. Indicate whether inventory will be restocked
4. Show the refund method (original payment vs store credit)
5. Explain the cancellation reason being used
6. Wait for explicit user confirmation with "yes", "confirm", or "proceed"
7. Warn that refunds cannot be reversed once processed

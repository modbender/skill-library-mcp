# Shopify Draft Orders

Create and manage draft orders for phone, in-person, or B2B sales via the GraphQL Admin API.

## Overview

Draft orders are orders created by merchants on behalf of customers. They can be sent as invoices or completed directly. Once paid, they convert to regular orders.

## List Draft Orders

```graphql
query ListDraftOrders($first: Int!, $after: String, $query: String) {
  draftOrders(first: $first, after: $after, query: $query, sortKey: UPDATED_AT, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      name
      status
      totalPrice
      currencyCode
      createdAt
      customer {
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

## Get Draft Order

```graphql
query GetDraftOrder($id: ID!) {
  draftOrder(id: $id) {
    id
    name
    status
    createdAt
    invoiceUrl
    totalPrice
    subtotalPrice
    totalTax
    currencyCode
    customer {
      id
      displayName
      defaultEmailAddress {
        emailAddress
      }
    }
    shippingAddress {
      address1
      city
      provinceCode
      countryCode
      zip
    }
    billingAddress {
      address1
      city
      provinceCode
      countryCode
      zip
    }
    lineItems(first: 20) {
      nodes {
        id
        title
        quantity
        originalUnitPrice
        product {
          id
        }
        variant {
          id
        }
      }
    }
    appliedDiscount {
      title
      value
      valueType
    }
    shippingLine {
      title
      price
    }
  }
}
```
Variables: `{ "id": "gid://shopify/DraftOrder/123" }`

## Create Draft Order

```graphql
mutation CreateDraftOrder($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      name
      invoiceUrl
      status
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
    "customerId": "gid://shopify/Customer/123",
    "lineItems": [
      {
        "variantId": "gid://shopify/ProductVariant/456",
        "quantity": 2
      },
      {
        "variantId": "gid://shopify/ProductVariant/789",
        "quantity": 1
      }
    ],
    "shippingAddress": {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main St",
      "city": "New York",
      "provinceCode": "NY",
      "countryCode": "US",
      "zip": "10001"
    },
    "note": "Customer requested gift wrapping"
  }
}
```

## Create Draft Order with Custom Item

```graphql
mutation CreateDraftOrderCustomItem($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      lineItems(first: 5) {
        nodes {
          title
          originalUnitPrice
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
    "lineItems": [
      {
        "title": "Custom Engraving Service",
        "quantity": 1,
        "originalUnitPriceSet": {
          "shopMoney": {
            "amount": "25.00",
            "currencyCode": "USD"
          }
        },
        "taxable": true
      }
    ]
  }
}
```

## Create Draft Order with Discount

```graphql
mutation CreateDraftOrderWithDiscount($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      appliedDiscount {
        title
        value
      }
      totalPrice
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
    "lineItems": [
      {
        "variantId": "gid://shopify/ProductVariant/456",
        "quantity": 1
      }
    ],
    "appliedDiscount": {
      "title": "VIP Discount",
      "value": 15,
      "valueType": "PERCENTAGE"
    }
  }
}
```

## Update Draft Order

```graphql
mutation UpdateDraftOrder($id: ID!, $input: DraftOrderInput!) {
  draftOrderUpdate(id: $id, input: $input) {
    draftOrder {
      id
      lineItems(first: 10) {
        nodes {
          title
          quantity
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
  "id": "gid://shopify/DraftOrder/123",
  "input": {
    "lineItems": [
      {
        "variantId": "gid://shopify/ProductVariant/456",
        "quantity": 3
      }
    ]
  }
}
```

## Calculate Draft Order

Preview pricing without creating:

```graphql
mutation CalculateDraftOrder($input: DraftOrderInput!) {
  draftOrderCalculate(input: $input) {
    calculatedDraftOrder {
      subtotalPrice
      totalPrice
      totalTax
      lineItems {
        title
        quantity
        discountedTotal
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

## Send Invoice

```graphql
mutation SendDraftOrderInvoice($id: ID!, $email: EmailInput) {
  draftOrderInvoiceSend(id: $id, email: $email) {
    draftOrder {
      id
      invoiceSentAt
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
  "id": "gid://shopify/DraftOrder/123",
  "email": {
    "to": "customer@example.com",
    "subject": "Your Order Invoice",
    "customMessage": "Thank you for your order! Please complete your payment."
  }
}
```

## Complete Draft Order

> REQUIRES PERMISSION: Completing a draft order converts it to a real order, commits the transaction, and may deduct inventory. This action cannot be reversed. Always ask the user for explicit confirmation, show the draft order details and total, and wait for approval before executing this operation.

Convert to a real order:

```graphql
mutation CompleteDraftOrder($id: ID!) {
  draftOrderComplete(id: $id) {
    draftOrder {
      id
      status
      order {
        id
        name
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

## Complete with Payment Pending

```graphql
mutation CompleteDraftOrderPending($id: ID!) {
  draftOrderComplete(id: $id, paymentPending: true) {
    draftOrder {
      order {
        id
        displayFinancialStatus
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

## Delete Draft Order

> REQUIRES PERMISSION: Deleting a draft order is PERMANENT and cannot be undone. All draft order data will be lost. Always ask the user for explicit confirmation, show the draft order details, and wait for approval before executing this operation.

```graphql
mutation DeleteDraftOrder($input: DraftOrderDeleteInput!) {
  draftOrderDelete(input: $input) {
    deletedId
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
    "id": "gid://shopify/DraftOrder/123"
  }
}
```

## Duplicate Draft Order

```graphql
mutation DuplicateDraftOrder($id: ID!) {
  draftOrderDuplicate(id: $id) {
    draftOrder {
      id
      name
    }
    userErrors {
      field
      message
    }
  }
}
```

## Bulk Delete Draft Orders

> REQUIRES PERMISSION: Bulk deleting draft orders is PERMANENT and removes multiple draft orders at once. This cannot be undone. Always ask the user for explicit confirmation, list the draft orders to be deleted, and wait for approval before executing this operation.

```graphql
mutation BulkDeleteDraftOrders($ids: [ID!]) {
  draftOrderBulkDelete(ids: $ids) {
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

## Add Tags to Draft Orders

```graphql
mutation AddTagsToDraftOrders($ids: [ID!], $tags: [String!]!) {
  draftOrderBulkAddTags(ids: $ids, tags: $tags) {
    job {
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
  "ids": ["gid://shopify/DraftOrder/123", "gid://shopify/DraftOrder/456"],
  "tags": ["wholesale", "priority"]
}
```

## Draft Order Status

| Status | Description |
|--------|-------------|
| `OPEN` | Not yet completed |
| `INVOICE_SENT` | Invoice emailed to customer |
| `COMPLETED` | Converted to order |

## Discount Value Types

| Type | Description |
|------|-------------|
| `FIXED_AMOUNT` | Fixed dollar/currency amount |
| `PERCENTAGE` | Percentage off |

## Reserve Inventory

```json
{
  "input": {
    "lineItems": [...],
    "reserveInventoryUntil": "2025-01-20T00:00:00Z"
  }
}
```

## API Scopes Required

- `read_draft_orders` - Read draft orders
- `write_draft_orders` - Create, update, delete draft orders

## Notes

- Draft orders don't deduct inventory until completed
- Use `reserveInventoryUntil` to hold inventory temporarily
- Invoice URLs are secure checkout links
- Custom line items don't require product variants
- Completing a draft order creates a real order

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `draftOrderComplete` | Converts draft to real order, commits transaction, may deduct inventory | No - Creates permanent order |
| `draftOrderDelete` | Permanently deletes draft order | No - IRREVERSIBLE |
| `draftOrderBulkDelete` | Permanently deletes multiple draft orders at once | No - IRREVERSIBLE |

Permission Protocol: 
- For completion: Show draft order ID, customer, line items, and total amount
- For deletions: Show draft order details, emphasize permanence, wait for explicit "yes", "confirm", or "proceed"

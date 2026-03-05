# Shopify Fulfillments

Manage order fulfillment, tracking, and fulfillment orders via the GraphQL Admin API.

## Overview

Fulfillment orders represent line items to be fulfilled from specific locations. Fulfillments are the actual shipments created to fulfill those orders.

## List Fulfillment Orders

```graphql
query ListFulfillmentOrders($first: Int!, $query: String) {
  fulfillmentOrders(first: $first, query: $query) {
    nodes {
      id
      status
      requestStatus
      assignedLocation {
        name
        address1
        city
      }
      order {
        id
        name
      }
      lineItems(first: 10) {
        nodes {
          id
          totalQuantity
          remainingQuantity
          lineItem {
            title
            sku
          }
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Fulfillment Order

```graphql
query GetFulfillmentOrder($id: ID!) {
  fulfillmentOrder(id: $id) {
    id
    status
    requestStatus
    createdAt
    updatedAt
    assignedLocation {
      name
      address1
      city
      countryCode
    }
    destination {
      firstName
      lastName
      address1
      city
      provinceCode
      countryCode
    }
    order {
      id
      name
      customer {
        displayName
      }
    }
    lineItems(first: 20) {
      nodes {
        id
        totalQuantity
        remainingQuantity
        lineItem {
          title
          sku
          variant {
            id
          }
        }
      }
    }
    fulfillments(first: 5) {
      nodes {
        id
        status
        trackingInfo {
          number
          url
          company
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/FulfillmentOrder/123" }`

## Create Fulfillment

> REQUIRES PERMISSION: Creating a fulfillment marks items as shipped and sends shipping notification emails to customers. This affects the customer experience and order status. Always ask the user for explicit confirmation, show the items being fulfilled and tracking info, and wait for approval before executing this operation.

```graphql
mutation CreateFulfillment($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment {
      id
      status
      trackingInfo {
        number
        url
        company
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
  "fulfillment": {
    "lineItemsByFulfillmentOrder": [
      {
        "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/123",
        "fulfillmentOrderLineItems": [
          {
            "id": "gid://shopify/FulfillmentOrderLineItem/456",
            "quantity": 2
          }
        ]
      }
    ],
    "trackingInfo": {
      "number": "1Z999AA10123456784",
      "url": "https://www.ups.com/track?tracknum=1Z999AA10123456784",
      "company": "UPS"
    },
    "notifyCustomer": true
  }
}
```

## Create Fulfillment (Full Order)

```graphql
mutation CreateFullFulfillment($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment {
      id
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
  "fulfillment": {
    "lineItemsByFulfillmentOrder": [
      {
        "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/123"
      }
    ],
    "trackingInfo": {
      "number": "9400111899223033335301",
      "company": "USPS"
    },
    "notifyCustomer": true
  }
}
```

## Cancel Fulfillment

> REQUIRES PERMISSION: Cancelling a fulfillment reverses the shipment status and may confuse customers who already received shipping notifications. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation CancelFulfillment($id: ID!) {
  fulfillmentCancel(id: $id) {
    fulfillment {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Add Tracking Information

```graphql
mutation CreateFulfillmentEvent($fulfillmentEvent: FulfillmentEventInput!) {
  fulfillmentEventCreate(fulfillmentEvent: $fulfillmentEvent) {
    fulfillmentEvent {
      id
      status
      happenedAt
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
  "fulfillmentEvent": {
    "fulfillmentId": "gid://shopify/Fulfillment/123",
    "status": "IN_TRANSIT",
    "happenedAt": "2025-01-15T14:30:00Z"
  }
}
```

## Hold Fulfillment Order

> REQUIRES PERMISSION: Holding a fulfillment order pauses order processing and may delay shipments to customers. Always ask the user for explicit confirmation, show the reason for the hold, and wait for approval before executing this operation.

```graphql
mutation HoldFulfillmentOrder($id: ID!, $fulfillmentHold: FulfillmentOrderHoldInput!) {
  fulfillmentOrderHold(id: $id, fulfillmentHold: $fulfillmentHold) {
    fulfillmentOrder {
      id
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
  "id": "gid://shopify/FulfillmentOrder/123",
  "fulfillmentHold": {
    "reason": "INVENTORY_OUT_OF_STOCK",
    "reasonNotes": "Waiting for restock shipment"
  }
}
```

## Release Hold

```graphql
mutation ReleaseFulfillmentOrderHold($id: ID!) {
  fulfillmentOrderReleaseHold(id: $id) {
    fulfillmentOrder {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Move Fulfillment Order to Different Location

```graphql
mutation MoveFulfillmentOrder($id: ID!, $newLocationId: ID!) {
  fulfillmentOrderMove(id: $id, newLocationId: $newLocationId) {
    movedFulfillmentOrder {
      id
      assignedLocation {
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

## Cancel Fulfillment Order

> REQUIRES PERMISSION: Cancelling a fulfillment order stops the order from being fulfilled and affects the entire fulfillment workflow. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation CancelFulfillmentOrder($id: ID!) {
  fulfillmentOrderCancel(id: $id) {
    fulfillmentOrder {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

## Split Fulfillment Order

```graphql
mutation SplitFulfillmentOrder($fulfillmentOrderSplits: [FulfillmentOrderSplitInput!]!) {
  fulfillmentOrderSplit(fulfillmentOrderSplits: $fulfillmentOrderSplits) {
    fulfillmentOrderSplits {
      fulfillmentOrder {
        id
      }
      remainingFulfillmentOrder {
        id
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
  "fulfillmentOrderSplits": [
    {
      "fulfillmentOrderId": "gid://shopify/FulfillmentOrder/123",
      "fulfillmentOrderLineItems": [
        {
          "id": "gid://shopify/FulfillmentOrderLineItem/456",
          "quantity": 1
        }
      ]
    }
  ]
}
```

## Fulfillment Order Status

| Status | Description |
|--------|-------------|
| `OPEN` | Ready to fulfill |
| `IN_PROGRESS` | Being fulfilled |
| `CANCELLED` | Cancelled |
| `INCOMPLETE` | Partially fulfilled, remaining cancelled |
| `CLOSED` | Fully fulfilled |
| `SCHEDULED` | Scheduled for future date |
| `ON_HOLD` | On hold |

## Fulfillment Event Status

| Status | Description |
|--------|-------------|
| `CONFIRMED` | Shipment confirmed |
| `IN_TRANSIT` | Package in transit |
| `OUT_FOR_DELIVERY` | Out for delivery |
| `DELIVERED` | Delivered |
| `FAILURE` | Delivery failed |
| `ATTEMPTED_DELIVERY` | Delivery attempted |

## Hold Reasons

| Reason | Description |
|--------|-------------|
| `AWAITING_PAYMENT` | Waiting for payment |
| `HIGH_RISK_OF_FRAUD` | Fraud risk detected |
| `INCORRECT_ADDRESS` | Address needs verification |
| `INVENTORY_OUT_OF_STOCK` | Item out of stock |
| `OTHER` | Custom reason |

## Assigned Fulfillment Orders

For fulfillment service apps:

```graphql
query AssignedFulfillmentOrders($first: Int!) {
  assignedFulfillmentOrders(first: $first, assignmentStatus: FULFILLMENT_REQUESTED) {
    nodes {
      id
      status
      requestStatus
      order {
        name
      }
    }
  }
}
```

## API Scopes Required

- `read_orders` - Read fulfillment orders
- `write_orders` - Create fulfillments
- `read_assigned_fulfillment_orders` - For fulfillment service apps
- `write_assigned_fulfillment_orders` - For fulfillment service apps

## Notes

- Fulfillment orders are created automatically when orders are placed
- Multiple fulfillments can be created for one fulfillment order
- Use `notifyCustomer: true` to send shipping confirmation emails
- Tracking companies: UPS, USPS, FedEx, DHL, etc.
- Fulfillment orders can be moved between locations

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `fulfillmentCreate` | Marks items as shipped, sends customer notifications | Partial (can cancel) |
| `fulfillmentCancel` | Reverses shipment status, may confuse customers | Partial (can create new) |
| `fulfillmentOrderHold` | Pauses order processing, delays shipments | Yes (can release) |
| `fulfillmentOrderReleaseHold` | Resumes order processing | N/A |
| `fulfillmentOrderCancel` | Stops fulfillment workflow completely | No - Status change is permanent |

Permission Protocol: 
- For fulfillment creation: Show order ID, items, quantities, tracking info, and whether customer will be notified
- For cancellations/holds: Show fulfillment/order ID, current status, and impact on customer experience
- Wait for explicit "yes", "confirm", or "proceed"

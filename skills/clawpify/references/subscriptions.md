# Shopify Subscriptions

Manage subscription contracts and billing via the GraphQL Admin API.

## Overview

Subscriptions enable recurring orders for products. Subscription contracts define the billing schedule, products, and delivery details.

## List Subscription Contracts

```graphql
query ListSubscriptionContracts($first: Int!, $query: String) {
  subscriptionContracts(first: $first, query: $query, sortKey: CREATED_AT, reverse: true) {
    nodes {
      id
      status
      createdAt
      nextBillingDate
      customer {
        displayName
        defaultEmailAddress {
          emailAddress
        }
      }
      deliveryPolicy {
        interval
        intervalCount
      }
      billingPolicy {
        interval
        intervalCount
      }
      lines(first: 5) {
        nodes {
          title
          quantity
          currentPrice {
            amount
            currencyCode
          }
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Subscription Contract

```graphql
query GetSubscriptionContract($id: ID!) {
  subscriptionContract(id: $id) {
    id
    status
    createdAt
    updatedAt
    nextBillingDate
    customer {
      id
      displayName
    }
    customerPaymentMethod {
      id
      instrument {
        ... on CustomerCreditCard {
          brand
          lastDigits
          expiryMonth
          expiryYear
        }
      }
    }
    deliveryPolicy {
      interval
      intervalCount
    }
    billingPolicy {
      interval
      intervalCount
      minCycles
      maxCycles
    }
    deliveryPrice {
      amount
      currencyCode
    }
    lines(first: 10) {
      nodes {
        id
        title
        variantId
        quantity
        currentPrice {
          amount
          currencyCode
        }
        sellingPlanId
        sellingPlanName
      }
    }
    orders(first: 5) {
      nodes {
        id
        name
        createdAt
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/SubscriptionContract/123" }`

## Get Billing Cycles

```graphql
query GetBillingCycles($contractId: ID!, $first: Int!) {
  subscriptionBillingCycles(contractId: $contractId, first: $first) {
    nodes {
      cycleIndex
      cycleStartAt
      cycleEndAt
      status
      skipped
      billingAttemptExpectedDate
    }
  }
}
```
Variables: `{ "contractId": "gid://shopify/SubscriptionContract/123", "first": 12 }`

## Get Specific Billing Cycle

```graphql
query GetBillingCycle($billingCycleInput: SubscriptionBillingCycleInput!) {
  subscriptionBillingCycle(billingCycleInput: $billingCycleInput) {
    cycleIndex
    cycleStartAt
    cycleEndAt
    status
    skipped
    billingAttemptExpectedDate
    sourceContract {
      id
    }
  }
}
```
Variables:
```json
{
  "billingCycleInput": {
    "contractId": "gid://shopify/SubscriptionContract/123",
    "selector": {
      "index": 3
    }
  }
}
```

## List Billing Attempts

```graphql
query ListBillingAttempts($first: Int!) {
  subscriptionBillingAttempts(first: $first, sortKey: CREATED_AT, reverse: true) {
    nodes {
      id
      createdAt
      ready
      errorMessage
      subscriptionContract {
        id
      }
      order {
        id
        name
      }
    }
  }
}
```

## Create Subscription Draft

```graphql
mutation CreateSubscriptionDraft($input: SubscriptionDraftInput!) {
  subscriptionDraftCreate(input: $input) {
    draft {
      id
    }
    userErrors {
      field
      message
    }
  }
}
```

## Update Subscription Draft

```graphql
mutation UpdateSubscriptionDraft($draftId: ID!, $input: SubscriptionDraftInput!) {
  subscriptionDraftUpdate(draftId: $draftId, input: $input) {
    draft {
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
  "draftId": "gid://shopify/SubscriptionDraft/123",
  "input": {
    "deliveryPolicy": {
      "interval": "MONTH",
      "intervalCount": 2
    }
  }
}
```

## Add Line to Draft

```graphql
mutation AddLineToDraft($draftId: ID!, $input: SubscriptionLineInput!) {
  subscriptionDraftLineAdd(draftId: $draftId, input: $input) {
    draft {
      id
      lines(first: 10) {
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
  "draftId": "gid://shopify/SubscriptionDraft/123",
  "input": {
    "productVariantId": "gid://shopify/ProductVariant/456",
    "quantity": 1,
    "currentPrice": {
      "amount": "29.99",
      "currencyCode": "USD"
    }
  }
}
```

## Commit Draft (Activate)

```graphql
mutation CommitSubscriptionDraft($draftId: ID!) {
  subscriptionDraftCommit(draftId: $draftId) {
    contract {
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

## Pause Subscription

```graphql
mutation PauseSubscription($subscriptionContractId: ID!) {
  subscriptionContractPause(subscriptionContractId: $subscriptionContractId) {
    contract {
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

## Resume Subscription

```graphql
mutation ActivateSubscription($subscriptionContractId: ID!) {
  subscriptionContractActivate(subscriptionContractId: $subscriptionContractId) {
    contract {
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

## Cancel Subscription

```graphql
mutation CancelSubscription($subscriptionContractId: ID!) {
  subscriptionContractCancel(subscriptionContractId: $subscriptionContractId) {
    contract {
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

## Skip Billing Cycle

```graphql
mutation SkipBillingCycle($billingCycleInput: SubscriptionBillingCycleInput!) {
  subscriptionBillingCycleSkip(billingCycleInput: $billingCycleInput) {
    billingCycle {
      cycleIndex
      skipped
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
  "billingCycleInput": {
    "contractId": "gid://shopify/SubscriptionContract/123",
    "selector": {
      "index": 5
    }
  }
}
```

## Contract Status

| Status | Description |
|--------|-------------|
| `ACTIVE` | Subscription is active |
| `PAUSED` | Temporarily paused |
| `CANCELLED` | Permanently cancelled |
| `EXPIRED` | Reached max cycles |
| `FAILED` | Billing failed |

## Billing/Delivery Intervals

| Interval | Description |
|----------|-------------|
| `DAY` | Daily |
| `WEEK` | Weekly |
| `MONTH` | Monthly |
| `YEAR` | Yearly |

## Billing Cycle Status

| Status | Description |
|--------|-------------|
| `UNBILLED` | Not yet billed |
| `BILLED` | Successfully billed |
| `SKIPPED` | Skipped by customer/merchant |

## Add Discount to Draft

```graphql
mutation AddDiscountToDraft($draftId: ID!, $input: SubscriptionManualDiscountInput!) {
  subscriptionDraftDiscountAdd(draftId: $draftId, input: $input) {
    draft {
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
  "draftId": "gid://shopify/SubscriptionDraft/123",
  "input": {
    "title": "Loyalty Discount",
    "value": {
      "percentage": 10
    },
    "recurringCycleLimit": 3
  }
}
```

## API Scopes Required

- `read_own_subscription_contracts` - Read contracts
- `write_own_subscription_contracts` - Manage contracts
- `read_customer_payment_methods` - Read payment methods

## Notes

- Subscriptions require selling plans on products
- Billing attempts are processed automatically
- Customers can manage subscriptions via customer portal
- Failed billing triggers retry logic
- Drafts must be committed to create/update contracts
- Skipped cycles don't charge the customer

# Shopify Gift Cards

Create and manage gift cards via the GraphQL Admin API.

## Overview

Gift cards are prepaid store credit that customers can use for purchases. They can be created by merchants or purchased by customers.

## List Gift Cards

```graphql
query ListGiftCards($first: Int!, $after: String, $query: String) {
  giftCards(first: $first, after: $after, query: $query, sortKey: CREATED_AT, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      lastCharacters
      initialValue {
        amount
        currencyCode
      }
      balance {
        amount
        currencyCode
      }
      enabled
      expiresOn
      createdAt
      customer {
        displayName
      }
    }
  }
}
```
Variables: `{ "first": 20 }`

## Get Gift Card

```graphql
query GetGiftCard($id: ID!) {
  giftCard(id: $id) {
    id
    lastCharacters
    maskedCode
    initialValue {
      amount
      currencyCode
    }
    balance {
      amount
      currencyCode
    }
    enabled
    expiresOn
    createdAt
    disabledAt
    note
    customer {
      id
      displayName
      defaultEmailAddress {
        emailAddress
      }
    }
    order {
      id
      name
    }
    transactions(first: 20) {
      nodes {
        id
        amount {
          amount
          currencyCode
        }
        processedAt
        note
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/GiftCard/123" }`

## Get Gift Cards Count

```graphql
query GetGiftCardsCount($query: String) {
  giftCardsCount(query: $query) {
    count
  }
}
```
Variables: `{ "query": "enabled:true" }`

## Create Gift Card

```graphql
mutation CreateGiftCard($input: GiftCardCreateInput!) {
  giftCardCreate(input: $input) {
    giftCard {
      id
      lastCharacters
      initialValue {
        amount
      }
      balance {
        amount
      }
    }
    giftCardCode
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
    "initialValue": "50.00",
    "customerId": "gid://shopify/Customer/123",
    "note": "Birthday gift card"
  }
}
```

## Create Gift Card with Custom Code

```graphql
mutation CreateGiftCardWithCode($input: GiftCardCreateInput!) {
  giftCardCreate(input: $input) {
    giftCard {
      id
      lastCharacters
    }
    giftCardCode
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
    "initialValue": "100.00",
    "code": "HAPPY2025GIFT",
    "note": "Promotional gift card"
  }
}
```

## Create Gift Card with Expiration

```graphql
mutation CreateExpiringGiftCard($input: GiftCardCreateInput!) {
  giftCardCreate(input: $input) {
    giftCard {
      id
      expiresOn
    }
    giftCardCode
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
    "initialValue": "25.00",
    "expiresOn": "2025-12-31",
    "note": "Holiday promotional card"
  }
}
```

## Create Gift Card with Recipient

```graphql
mutation CreateGiftCardForRecipient($input: GiftCardCreateInput!) {
  giftCardCreate(input: $input) {
    giftCard {
      id
    }
    giftCardCode
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
    "initialValue": "75.00",
    "recipientAttributes": {
      "email": "recipient@example.com",
      "message": "Happy Birthday! Enjoy shopping!",
      "sendNotificationAt": "2025-03-15T09:00:00Z"
    }
  }
}
```

## Update Gift Card

```graphql
mutation UpdateGiftCard($id: ID!, $input: GiftCardUpdateInput!) {
  giftCardUpdate(id: $id, input: $input) {
    giftCard {
      id
      note
      expiresOn
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
  "id": "gid://shopify/GiftCard/123",
  "input": {
    "note": "Updated note for tracking",
    "expiresOn": "2026-06-30"
  }
}
```

## Credit Gift Card (Add Balance)

> REQUIRES PERMISSION: Adding balance to a gift card affects customer funds and creates a transaction record. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation CreditGiftCard($id: ID!, $creditInput: GiftCardCreditInput!) {
  giftCardCredit(id: $id, creditInput: $creditInput) {
    giftCard {
      id
      balance {
        amount
      }
    }
    giftCardCreditTransaction {
      id
      amount {
        amount
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
  "id": "gid://shopify/GiftCard/123",
  "creditInput": {
    "creditAmount": {
      "amount": "25.00",
      "currencyCode": "USD"
    },
    "note": "Bonus credit for loyalty"
  }
}
```

## Debit Gift Card (Remove Balance)

> REQUIRES PERMISSION: Removing balance from a gift card affects customer funds and cannot be easily reversed. Always ask the user for explicit confirmation before executing this operation.

```graphql
mutation DebitGiftCard($id: ID!, $debitInput: GiftCardDebitInput!) {
  giftCardDebit(id: $id, debitInput: $debitInput) {
    giftCard {
      id
      balance {
        amount
      }
    }
    giftCardDebitTransaction {
      id
      amount {
        amount
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
  "id": "gid://shopify/GiftCard/123",
  "debitInput": {
    "debitAmount": {
      "amount": "10.00",
      "currencyCode": "USD"
    },
    "note": "Balance adjustment"
  }
}
```

## Deactivate Gift Card

> REQUIRES PERMISSION: Deactivating a gift card is PERMANENT and IRREVERSIBLE. The gift card cannot be reactivated and any remaining balance will be lost. Always ask the user for explicit confirmation and show the current balance before executing this operation.

Permanently disable a gift card:

```graphql
mutation DeactivateGiftCard($id: ID!) {
  giftCardDeactivate(id: $id) {
    giftCard {
      id
      enabled
      disabledAt
    }
    userErrors {
      field
      message
    }
  }
}
```

Note: Deactivation is permanent and cannot be reversed.

## Send Customer Notification

```graphql
mutation SendGiftCardNotification($id: ID!) {
  giftCardSendNotificationToCustomer(id: $id) {
    giftCard {
      id
    }
    userErrors {
      field
      message
    }
  }
}
```

## Send Recipient Notification

```graphql
mutation SendRecipientNotification($id: ID!) {
  giftCardSendNotificationToRecipient(id: $id) {
    giftCard {
      id
    }
    userErrors {
      field
      message
    }
  }
}
```

## Search Gift Cards

```graphql
query SearchGiftCards($query: String!) {
  giftCards(first: 10, query: $query) {
    nodes {
      id
      lastCharacters
      balance {
        amount
      }
      enabled
    }
  }
}
```
Variables: `{ "query": "last_characters:ABC1 AND enabled:true" }`

## Search Query Filters

| Filter | Example | Description |
|--------|---------|-------------|
| `last_characters` | `last_characters:ABC1` | Last 4 characters of code |
| `enabled` | `enabled:true` | Active/inactive status |
| `balance` | `balance:>0` | Balance amount |
| `initial_value` | `initial_value:>=50` | Initial value |
| `created_at` | `created_at:>2024-01-01` | Creation date |

## Gift Card Configuration

```graphql
query GetGiftCardConfiguration {
  giftCardConfiguration {
    expiresAfter {
      months
      years
    }
    isEnabled
  }
}
```

## API Scopes Required

- `read_gift_cards` - Read gift cards
- `write_gift_cards` - Create, update, deactivate gift cards

## Notes

- Gift card codes are only shown once at creation
- `lastCharacters` shows last 4 digits for identification
- Deactivation is permanent
- Gift cards can be assigned to customers or remain unassigned
- Recipient notifications can be scheduled for future delivery
- Balance adjustments create transaction history

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `giftCardDeactivate` | Permanently disables gift card, making balance unrecoverable | No - IRREVERSIBLE |
| `giftCardCredit` | Adds balance to gift card (affects customer funds) | Partial (requires debit) |
| `giftCardDebit` | Removes balance from gift card (affects customer funds) | Partial (requires credit) |

Permission Protocol: Before executing any of these operations:
1. Show the gift card ID, masked code, and current balance
2. Describe the impact (especially for deactivation - warn about permanent loss)
3. Wait for explicit user confirmation with "yes", "confirm", or "proceed"

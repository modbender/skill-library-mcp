# Shopify Marketing

Manage marketing activities, events, and customer marketing consent via the GraphQL Admin API.

## Marketing Activities

Marketing activities track promotional campaigns like email marketing, social media ads, and other marketing efforts.

### List Marketing Activities

```graphql
query ListMarketingActivities($first: Int!, $after: String) {
  marketingActivities(first: $first, after: $after, sortKey: CREATED_AT, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      title
      activityListUrl
      status
      createdAt
      budget {
        budgetType
        total {
          amount
          currencyCode
        }
      }
      utmParameters {
        campaign
        source
        medium
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

### Get Marketing Activity

```graphql
query GetMarketingActivity($id: ID!) {
  marketingActivity(id: $id) {
    id
    title
    status
    activityListUrl
    createdAt
    budget {
      budgetType
      total {
        amount
        currencyCode
      }
    }
    utmParameters {
      campaign
      source
      medium
    }
  }
}
```
Variables: `{ "id": "gid://shopify/MarketingActivity/123" }`

### Create External Marketing Activity

```graphql
mutation CreateExternalMarketingActivity($input: MarketingActivityCreateExternalInput!) {
  marketingActivityCreateExternal(input: $input) {
    marketingActivity {
      id
      title
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
    "title": "Summer Email Campaign",
    "remoteId": "campaign-123",
    "utm": {
      "campaign": "summer_sale",
      "source": "email",
      "medium": "newsletter"
    },
    "budget": {
      "budgetType": "DAILY",
      "total": {
        "amount": "100.00",
        "currencyCode": "USD"
      }
    },
    "scheduledToEndAt": "2025-08-31T23:59:59Z",
    "adSpend": {
      "amount": "0.00",
      "currencyCode": "USD"
    },
    "channelHandle": "email-marketing"
  }
}
```

### Update External Marketing Activity

```graphql
mutation UpdateExternalMarketingActivity($marketingActivityId: ID!, $input: MarketingActivityUpdateExternalInput!) {
  marketingActivityUpdateExternal(marketingActivityId: $marketingActivityId, input: $input) {
    marketingActivity {
      id
      title
      status
    }
    userErrors {
      field
      message
    }
  }
}
```

### Delete External Marketing Activity

```graphql
mutation DeleteExternalMarketingActivity($marketingActivityId: ID!) {
  marketingActivityDeleteExternal(marketingActivityId: $marketingActivityId) {
    deletedMarketingActivityId
    userErrors {
      field
      message
    }
  }
}
```

## Marketing Events

Marketing events represent trackable marketing-related actions.

### List Marketing Events

```graphql
query ListMarketingEvents($first: Int!) {
  marketingEvents(first: $first, sortKey: STARTED_AT, reverse: true) {
    nodes {
      id
      type
      startedAt
      channel
      utmParameters {
        campaign
        source
        medium
      }
    }
  }
}
```

### Get Marketing Event

```graphql
query GetMarketingEvent($id: ID!) {
  marketingEvent(id: $id) {
    id
    type
    startedAt
    endedAt
    channel
    utmParameters {
      campaign
      source
      medium
    }
  }
}
```

## Marketing Engagement

Track engagement metrics for marketing activities.

### Create Marketing Engagement

```graphql
mutation CreateMarketingEngagement($marketingActivityId: ID!, $marketingEngagement: MarketingEngagementInput!) {
  marketingEngagementCreate(marketingActivityId: $marketingActivityId, marketingEngagement: $marketingEngagement) {
    marketingEngagement {
      occurredOn
      impressionsCount
      clicksCount
      sessionsCount
      salesAmount {
        amount
        currencyCode
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
  "marketingActivityId": "gid://shopify/MarketingActivity/123",
  "marketingEngagement": {
    "occurredOn": "2025-01-15",
    "impressionsCount": 5000,
    "clicksCount": 150,
    "sessionsCount": 120,
    "ordersCount": 10,
    "salesAmount": {
      "amount": "1500.00",
      "currencyCode": "USD"
    }
  }
}
```

### Delete Marketing Engagements

```graphql
mutation DeleteMarketingEngagements($channelHandle: String!) {
  marketingEngagementsDelete(channelHandle: $channelHandle) {
    deletedMarketingEngagementsCount
    userErrors {
      field
      message
    }
  }
}
```

## Customer Marketing Consent

### Update Email Marketing Consent

```graphql
mutation UpdateEmailMarketingConsent($input: CustomerEmailMarketingConsentUpdateInput!) {
  customerEmailMarketingConsentUpdate(input: $input) {
    customer {
      id
      defaultEmailAddress {
        emailAddress
        marketingState
        marketingOptInLevel
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
    "customerId": "gid://shopify/Customer/123",
    "emailMarketingConsent": {
      "marketingState": "SUBSCRIBED",
      "marketingOptInLevel": "SINGLE_OPT_IN",
      "consentUpdatedAt": "2025-01-15T10:00:00Z"
    }
  }
}
```

### Update SMS Marketing Consent

```graphql
mutation UpdateSmsMarketingConsent($input: CustomerSmsMarketingConsentUpdateInput!) {
  customerSmsMarketingConsentUpdate(input: $input) {
    customer {
      id
      smsMarketingConsent {
        marketingState
        marketingOptInLevel
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
    "customerId": "gid://shopify/Customer/123",
    "smsMarketingConsent": {
      "marketingState": "SUBSCRIBED",
      "marketingOptInLevel": "SINGLE_OPT_IN",
      "consentUpdatedAt": "2025-01-15T10:00:00Z"
    }
  }
}
```

## Marketing Consent States

| State | Description |
|-------|-------------|
| `NOT_SUBSCRIBED` | Customer has not subscribed |
| `PENDING` | Awaiting confirmation (double opt-in) |
| `SUBSCRIBED` | Customer is subscribed |
| `UNSUBSCRIBED` | Customer has unsubscribed |
| `REDACTED` | Customer data has been redacted |
| `INVALID` | Invalid contact information |

## Opt-In Levels

| Level | Description |
|-------|-------------|
| `SINGLE_OPT_IN` | Subscribed without confirmation |
| `CONFIRMED_OPT_IN` | Subscribed with email/SMS confirmation |
| `UNKNOWN` | Opt-in level not specified |

## UTM Parameters

Track marketing attribution with UTM parameters:

| Parameter | Description |
|-----------|-------------|
| `campaign` | Campaign name |
| `source` | Traffic source (google, facebook, email) |
| `medium` | Marketing medium (cpc, banner, newsletter) |
| `term` | Paid search keywords |
| `content` | Differentiate similar content/links |

## API Scopes Required

- `read_marketing_events` - Read marketing events
- `write_marketing_events` - Create/update marketing events
- `read_customers` - Read customer marketing consent
- `write_customers` - Update customer marketing consent

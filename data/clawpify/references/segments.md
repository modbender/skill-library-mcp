# Shopify Customer Segments

Create and manage customer segments for targeted marketing using the GraphQL Admin API.

## Overview

Customer segments are dynamic groups defined by ShopifyQL queries. Segments automatically update as customers meet or no longer meet the defined criteria.

## List Segments

```graphql
query ListSegments($first: Int!, $after: String) {
  segments(first: $first, after: $after, sortKey: CREATION_DATE, reverse: true) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      name
      query
      creationDate
      lastEditDate
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Segment

```graphql
query GetSegment($id: ID!) {
  segment(id: $id) {
    id
    name
    query
    creationDate
    lastEditDate
  }
}
```
Variables: `{ "id": "gid://shopify/Segment/123" }`

## Get Segment Count

```graphql
query GetSegmentsCount {
  segmentsCount {
    count
  }
}
```

## Create Segment

```graphql
mutation CreateSegment($name: String!, $query: String!) {
  segmentCreate(name: $name, query: $query) {
    segment {
      id
      name
      query
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
  "name": "VIP Customers",
  "query": "amount_spent > 500"
}
```

## Update Segment

```graphql
mutation UpdateSegment($id: ID!, $name: String, $query: String) {
  segmentUpdate(id: $id, name: $name, query: $query) {
    segment {
      id
      name
      query
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
  "id": "gid://shopify/Segment/123",
  "name": "Premium VIP Customers",
  "query": "amount_spent > 1000"
}
```

## Delete Segment

```graphql
mutation DeleteSegment($id: ID!) {
  segmentDelete(id: $id) {
    deletedSegmentId
    userErrors {
      field
      message
    }
  }
}
```

## Get Segment Members

```graphql
query GetSegmentMembers($segmentId: ID!, $first: Int!, $after: String) {
  customerSegmentMembers(segmentId: $segmentId, first: $first, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
    nodes {
      id
      firstName
      lastName
      defaultEmailAddress {
        emailAddress
      }
      amountSpent {
        amount
        currencyCode
      }
      numberOfOrders
    }
  }
}
```
Variables:
```json
{
  "segmentId": "gid://shopify/Segment/123",
  "first": 25
}
```

## Check Customer Segment Membership

```graphql
query CheckSegmentMembership($customerId: ID!, $segmentIds: [ID!]!) {
  customerSegmentMembership(customerId: $customerId, segmentIds: $segmentIds) {
    memberships {
      segmentId
      isMember
    }
  }
}
```
Variables:
```json
{
  "customerId": "gid://shopify/Customer/123",
  "segmentIds": ["gid://shopify/Segment/456", "gid://shopify/Segment/789"]
}
```

## Get Segment Filters

```graphql
query GetSegmentFilters($first: Int!) {
  segmentFilters(first: $first) {
    nodes {
      localizedName
      queryName
    }
  }
}
```

## Segment Filter Suggestions

```graphql
query GetFilterSuggestions($search: String!, $first: Int!) {
  segmentFilterSuggestions(search: $search, first: $first) {
    nodes {
      localizedName
      queryName
    }
  }
}
```
Variables: `{ "search": "order", "first": 10 }`

## Segment Value Suggestions

Get suggested values for a specific filter:

```graphql
query GetValueSuggestions($search: String!, $filterQueryName: String!) {
  segmentValueSuggestions(search: $search, filterQueryName: $filterQueryName, first: 10) {
    nodes {
      value
      localizedValue
    }
  }
}
```
Variables:
```json
{
  "search": "new",
  "filterQueryName": "customer_tags"
}
```

## Common Segment Query Examples

### By Spend Amount
```
amount_spent > 500
amount_spent >= 100 AND amount_spent < 500
```

### By Order Count
```
number_of_orders >= 3
number_of_orders = 0
```

### By Customer Tags
```
customer_tags CONTAINS 'vip'
customer_tags CONTAINS 'wholesale'
```

### By Location
```
customer_cities CONTAINS 'New York'
customer_countries CONTAINS 'US'
```

### By Email Subscription
```
email_subscription_status = 'SUBSCRIBED'
```

### By Product Purchased
```
products_purchased(id: 123)
products_purchased(tag: 'summer')
```

### By Date
```
customer_added_date > 2024-01-01
last_order_date > -30d
```

### Combined Conditions
```
amount_spent > 200 AND number_of_orders >= 2 AND email_subscription_status = 'SUBSCRIBED'
```

## Create Segment Members Query (Async)

For large segments, use async queries:

```graphql
mutation CreateSegmentMembersQuery($input: CustomerSegmentMembersQueryInput!) {
  customerSegmentMembersQueryCreate(input: $input) {
    customerSegmentMembersQuery {
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
Variables:
```json
{
  "input": {
    "segmentId": "gid://shopify/Segment/123"
  }
}
```

Then poll for results:

```graphql
query GetSegmentMembersQuery($id: ID!) {
  customerSegmentMembersQuery(id: $id) {
    id
    done
  }
}
```

## API Scopes Required

- `read_customers` - Read segments and members
- `write_customers` - Create, update, delete segments

## Notes

- Segment queries use [ShopifyQL syntax](https://shopify.dev/docs/api/shopifyql/segment-query-language-reference)
- Segments update dynamically as customer data changes
- Maximum page size for segment members is 1000
- Use segments with discounts via the `context.customerSegments` field

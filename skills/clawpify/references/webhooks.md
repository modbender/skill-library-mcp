# Shopify Webhooks

Subscribe to event notifications via the GraphQL Admin API.

## Overview

Webhooks push real-time notifications to your app when events occur in a Shopify store, eliminating the need for polling.

## List Webhook Subscriptions

```graphql
query ListWebhooks($first: Int!) {
  webhookSubscriptions(first: $first) {
    nodes {
      id
      topic
      endpoint {
        ... on WebhookHttpEndpoint {
          callbackUrl
        }
        ... on WebhookPubSubEndpoint {
          pubSubProject
          pubSubTopic
        }
        ... on WebhookEventBridgeEndpoint {
          arn
        }
      }
      format
      createdAt
    }
  }
}
```
Variables: `{ "first": 50 }`

## Get Webhook Subscription

```graphql
query GetWebhook($id: ID!) {
  webhookSubscription(id: $id) {
    id
    topic
    endpoint {
      ... on WebhookHttpEndpoint {
        callbackUrl
      }
    }
    format
    includeFields
    metafieldNamespaces
    filter
    createdAt
    updatedAt
  }
}
```
Variables: `{ "id": "gid://shopify/WebhookSubscription/123" }`

## Get Webhooks Count

```graphql
query GetWebhooksCount {
  webhookSubscriptionsCount {
    count
  }
}
```

## Create HTTP Webhook

```graphql
mutation CreateWebhook($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      topic
      endpoint {
        ... on WebhookHttpEndpoint {
          callbackUrl
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
  "topic": "ORDERS_CREATE",
  "webhookSubscription": {
    "callbackUrl": "https://myapp.example.com/webhooks/orders",
    "format": "JSON"
  }
}
```

## Create Webhook with Filters

```graphql
mutation CreateFilteredWebhook($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      topic
      filter
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
  "topic": "ORDERS_CREATE",
  "webhookSubscription": {
    "callbackUrl": "https://myapp.example.com/webhooks/orders",
    "format": "JSON",
    "filter": "total_price:>=100.00"
  }
}
```

## Create Webhook with Field Selection

```graphql
mutation CreateWebhookWithFields($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      includeFields
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
  "topic": "PRODUCTS_UPDATE",
  "webhookSubscription": {
    "callbackUrl": "https://myapp.example.com/webhooks/products",
    "format": "JSON",
    "includeFields": ["id", "title", "variants"]
  }
}
```

## Create Webhook with Metafields

```graphql
mutation CreateWebhookWithMetafields($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      metafieldNamespaces
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
  "topic": "PRODUCTS_UPDATE",
  "webhookSubscription": {
    "callbackUrl": "https://myapp.example.com/webhooks/products",
    "format": "JSON",
    "metafieldNamespaces": ["custom", "my_app"]
  }
}
```

## Create Google Pub/Sub Webhook

```graphql
mutation CreatePubSubWebhook($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      endpoint {
        ... on WebhookPubSubEndpoint {
          pubSubProject
          pubSubTopic
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
  "topic": "ORDERS_CREATE",
  "webhookSubscription": {
    "pubSubProject": "my-gcp-project",
    "pubSubTopic": "shopify-orders",
    "format": "JSON"
  }
}
```

## Create AWS EventBridge Webhook

```graphql
mutation CreateEventBridgeWebhook($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      endpoint {
        ... on WebhookEventBridgeEndpoint {
          arn
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
  "topic": "ORDERS_CREATE",
  "webhookSubscription": {
    "arn": "arn:aws:events:us-east-1:123456789:event-source/aws.partner/shopify.com/12345/my-source",
    "format": "JSON"
  }
}
```

## Update Webhook

```graphql
mutation UpdateWebhook($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
    webhookSubscription {
      id
      endpoint {
        ... on WebhookHttpEndpoint {
          callbackUrl
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
  "id": "gid://shopify/WebhookSubscription/123",
  "webhookSubscription": {
    "callbackUrl": "https://myapp.example.com/webhooks/orders/v2"
  }
}
```

## Delete Webhook

> REQUIRES PERMISSION: Deleting a webhook subscription permanently stops event notifications and may break integrations or automated workflows. Always ask the user for explicit confirmation, show the webhook topic and endpoint, and wait for approval before executing this operation.

```graphql
mutation DeleteWebhook($id: ID!) {
  webhookSubscriptionDelete(id: $id) {
    deletedWebhookSubscriptionId
    userErrors {
      field
      message
    }
  }
}
```

## Common Webhook Topics

### Orders
| Topic | Event |
|-------|-------|
| `ORDERS_CREATE` | New order placed |
| `ORDERS_UPDATED` | Order modified |
| `ORDERS_CANCELLED` | Order cancelled |
| `ORDERS_FULFILLED` | Order fulfilled |
| `ORDERS_PAID` | Order paid |

### Products
| Topic | Event |
|-------|-------|
| `PRODUCTS_CREATE` | Product created |
| `PRODUCTS_UPDATE` | Product updated |
| `PRODUCTS_DELETE` | Product deleted |

### Customers
| Topic | Event |
|-------|-------|
| `CUSTOMERS_CREATE` | Customer created |
| `CUSTOMERS_UPDATE` | Customer updated |
| `CUSTOMERS_DELETE` | Customer deleted |

### Inventory
| Topic | Event |
|-------|-------|
| `INVENTORY_LEVELS_UPDATE` | Inventory changed |

### Fulfillment
| Topic | Event |
|-------|-------|
| `FULFILLMENTS_CREATE` | Fulfillment created |
| `FULFILLMENTS_UPDATE` | Fulfillment updated |

### Refunds
| Topic | Event |
|-------|-------|
| `REFUNDS_CREATE` | Refund processed |

### App
| Topic | Event |
|-------|-------|
| `APP_UNINSTALLED` | App uninstalled |
| `APP_SUBSCRIPTIONS_UPDATE` | Subscription changed |

## Webhook Formats

| Format | Description |
|--------|-------------|
| `JSON` | JSON payload |
| `XML` | XML payload |

## Filter Syntax Examples

```
# Orders over $100
total_price:>=100.00

# Specific customer
customer_id:123456

# Products with tag
tags:sale

# Combined filters
total_price:>=50.00 AND financial_status:paid
```

## API Scopes Required

Different topics require different scopes:

| Topic | Required Scope |
|-------|----------------|
| `ORDERS_*` | `read_orders` |
| `PRODUCTS_*` | `read_products` |
| `CUSTOMERS_*` | `read_customers` |
| `INVENTORY_*` | `read_inventory` |

## Notes

- App-specific webhooks in `shopify.app.toml` are preferred for most apps
- API-created webhooks are shop-scoped, not app-scoped
- Webhooks retry failed deliveries with exponential backoff
- Verify webhook signatures for security
- Maximum 3 attempts before webhook is marked failed
- Webhook API version is set at app level, not per subscription

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `webhookSubscriptionDelete` | Permanently stops event notifications, may break integrations | Yes (can recreate, but data in transit is lost) |

Permission Protocol: Before executing `webhookSubscriptionDelete`:
1. Show the webhook ID and subscription topic
2. Display the endpoint/callback URL or destination
3. Explain that event notifications will stop immediately
4. Warn about potential impact on integrations and automation
5. Wait for explicit user confirmation with "yes", "confirm", or "proceed"

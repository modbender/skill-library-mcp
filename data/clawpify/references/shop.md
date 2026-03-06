# Shopify Shop

Query shop information and settings via the GraphQL Admin API.

## Overview

The Shop object contains core store settings, features, billing information, and configuration details.

## Get Shop Information

```graphql
query GetShop {
  shop {
    id
    name
    email
    myshopifyDomain
    primaryDomain {
      host
      sslEnabled
    }
    contactEmail
    description
    currencyCode
    currencyFormats {
      moneyFormat
      moneyWithCurrencyFormat
    }
    weightUnit
    unitSystem
    timezoneAbbreviation
    ianaTimezone
    createdAt
    plan {
      displayName
      partnerDevelopment
      shopifyPlus
    }
  }
}
```

## Get Shop Address

```graphql
query GetShopAddress {
  shop {
    billingAddress {
      address1
      address2
      city
      province
      provinceCode
      country
      countryCodeV2
      zip
      phone
      company
    }
  }
}
```

## Get Shop Features

```graphql
query GetShopFeatures {
  shop {
    features {
      branding {
        shopifyBranding
      }
      storefront {
        internationalPriceOverrides
        internationalPriceRules
      }
      internationalDomains {
        enabled
      }
    }
  }
}
```

## Get Shop Locales

```graphql
query GetShopLocales {
  shopLocales(published: true) {
    locale
    name
    primary
    published
  }
}
```

## Get All Locales (Including Unpublished)

```graphql
query GetAllShopLocales {
  shopLocales(published: false) {
    locale
    name
    primary
    published
  }
}
```

## Get Shop Billing Preferences

```graphql
query GetBillingPreferences {
  shopBillingPreferences {
    currency {
      currencyCode
      currencyName
    }
  }
}
```

## Get Shopify Payments Account

```graphql
query GetPaymentsAccount {
  shopifyPaymentsAccount {
    activated
    balance {
      amount
      currencyCode
    }
    country
    defaultCurrency
    payoutSchedule {
      interval
    }
  }
}
```

## Get Available API Versions

```graphql
query GetApiVersions {
  publicApiVersions {
    handle
    displayName
    supported
  }
}
```

## Execute ShopifyQL Query

```graphql
query RunShopifyQL($query: String!) {
  shopifyqlQuery(query: $query) {
    ... on TableResponse {
      tableData {
        columns {
          name
          dataType
          displayName
        }
        rowData
      }
    }
    ... on PolarisVizResponse {
      data
    }
    parseErrors {
      message
    }
  }
}
```
Variables:
```json
{
  "query": "FROM orders SHOW sum(total_sales) AS total_revenue SINCE -30d UNTIL today"
}
```

## Common ShopifyQL Queries

### Sales Summary
```
FROM orders
SHOW sum(total_sales) AS revenue, count() AS order_count
SINCE -30d UNTIL today
```

### Top Products
```
FROM products
SHOW sum(quantity) AS units_sold
GROUP BY product_title
ORDER BY units_sold DESC
LIMIT 10
SINCE -30d
```

### Sales by Region
```
FROM orders
SHOW sum(total_sales) AS revenue
GROUP BY billing_country
ORDER BY revenue DESC
SINCE -30d
```

### Daily Sales Trend
```
FROM orders
SHOW sum(total_sales) AS daily_revenue
GROUP BY day
SINCE -30d UNTIL today
```

## Get Shop Functions

```graphql
query GetShopFunctions($first: Int!) {
  shopifyFunctions(first: $first) {
    nodes {
      id
      title
      apiType
      apiVersion
      app {
        title
      }
    }
  }
}
```
Variables: `{ "first": 20 }`

## Get Specific Function

```graphql
query GetFunction($id: String!) {
  shopifyFunction(id: $id) {
    id
    title
    apiType
    apiVersion
    description
    app {
      title
    }
  }
}
```

## Shop Settings Fields

| Field | Description |
|-------|-------------|
| `name` | Store name |
| `email` | Store email |
| `myshopifyDomain` | *.myshopify.com domain |
| `primaryDomain` | Custom domain if set |
| `currencyCode` | Store currency |
| `weightUnit` | Weight unit (KILOGRAMS, POUNDS, etc.) |
| `unitSystem` | METRIC or IMPERIAL |
| `ianaTimezone` | Timezone (e.g., America/New_York) |

## Plan Information

| Field | Description |
|-------|-------------|
| `displayName` | Plan name (Basic, Shopify, Advanced, Plus) |
| `partnerDevelopment` | Is development store |
| `shopifyPlus` | Is Shopify Plus |

## Weight Units

| Unit | Description |
|------|-------------|
| `KILOGRAMS` | Kilograms |
| `GRAMS` | Grams |
| `POUNDS` | Pounds |
| `OUNCES` | Ounces |

## Currency Formats

| Field | Example |
|-------|---------|
| `moneyFormat` | `${{amount}}` |
| `moneyWithCurrencyFormat` | `${{amount}} USD` |

## API Scopes Required

- No specific scope needed for basic shop info
- `read_shopify_payments_accounts` - For payments account info
- `read_locales` - For locale information

## Notes

- Shop info is read-only through GraphQL
- Use REST API for some shop settings updates
- ShopifyQL is for analytics queries
- Functions require apps with function capabilities
- Domain and billing changes are done through admin UI

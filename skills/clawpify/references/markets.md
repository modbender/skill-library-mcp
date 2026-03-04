# Shopify Markets

Manage international markets for localized shopping experiences via the GraphQL Admin API.

## Overview

Markets define customized shopping experiences for different regions, including pricing, currency, content, and fulfillment settings.

## List Markets

```graphql
query ListMarkets($first: Int!) {
  markets(first: $first) {
    nodes {
      id
      name
      handle
      enabled
      primary
      currencySettings {
        baseCurrency {
          currencyCode
        }
        localCurrencies
      }
      regions(first: 10) {
        nodes {
          ... on MarketRegionCountry {
            code
            name
          }
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Market

```graphql
query GetMarket($id: ID!) {
  market(id: $id) {
    id
    name
    handle
    enabled
    primary
    currencySettings {
      baseCurrency {
        currencyCode
      }
      localCurrencies
    }
    priceInclusions {
      includeTaxes
    }
    webPresence {
      domain {
        host
      }
      defaultLocale
      alternateLocales
      subfolderSuffix
    }
    regions(first: 20) {
      nodes {
        ... on MarketRegionCountry {
          code
          name
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Market/123" }`

## Create Market

```graphql
mutation CreateMarket($input: MarketCreateInput!) {
  marketCreate(input: $input) {
    market {
      id
      name
      handle
      enabled
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
    "name": "European Union",
    "handle": "eu",
    "enabled": true,
    "regions": [
      { "countryCode": "DE" },
      { "countryCode": "FR" },
      { "countryCode": "IT" },
      { "countryCode": "ES" },
      { "countryCode": "NL" }
    ]
  }
}
```

## Update Market

```graphql
mutation UpdateMarket($id: ID!, $input: MarketUpdateInput!) {
  marketUpdate(id: $id, input: $input) {
    market {
      id
      name
      enabled
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
  "id": "gid://shopify/Market/123",
  "input": {
    "name": "EU Market",
    "enabled": true
  }
}
```

## Delete Market

```graphql
mutation DeleteMarket($id: ID!) {
  marketDelete(id: $id) {
    deletedId
    userErrors {
      field
      message
    }
  }
}
```

## Market Localizations

### Get Market Localizable Resource

```graphql
query GetMarketLocalizableResource($resourceId: ID!) {
  marketLocalizableResource(resourceId: $resourceId) {
    resourceId
    marketLocalizableContent {
      key
      value
      digest
      marketLocalizationsCount {
        count
      }
    }
  }
}
```

### List Market Localizable Resources

```graphql
query ListMarketLocalizableResources($resourceType: MarketLocalizableResourceType!, $first: Int!) {
  marketLocalizableResources(resourceType: $resourceType, first: $first) {
    nodes {
      resourceId
      marketLocalizableContent {
        key
        value
        digest
      }
    }
  }
}
```

### Register Market Localizations

```graphql
mutation RegisterMarketLocalizations($resourceId: ID!, $marketLocalizations: [MarketLocalizationRegisterInput!]!) {
  marketLocalizationsRegister(resourceId: $resourceId, marketLocalizations: $marketLocalizations) {
    marketLocalizations {
      key
      value
      marketId
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
  "resourceId": "gid://shopify/Product/123",
  "marketLocalizations": [
    {
      "key": "title",
      "value": "Summer Collection T-Shirt (EU Edition)",
      "marketId": "gid://shopify/Market/456",
      "marketLocalizableContentDigest": "abc123digest"
    }
  ]
}
```

### Remove Market Localizations

```graphql
mutation RemoveMarketLocalizations($resourceId: ID!, $marketLocalizationKeys: [String!]!, $marketIds: [ID!]!) {
  marketLocalizationsRemove(resourceId: $resourceId, marketLocalizationKeys: $marketLocalizationKeys, marketIds: $marketIds) {
    marketLocalizations {
      key
      marketId
    }
    userErrors {
      field
      message
    }
  }
}
```

## Resolve Market for Buyer

```graphql
query ResolveMarket($buyerSignal: BuyerSignalInput!) {
  marketsResolvedValues(buyerSignal: $buyerSignal) {
    market {
      id
      name
    }
    country {
      code
    }
    language
    currency
  }
}
```
Variables:
```json
{
  "buyerSignal": {
    "countryCode": "DE",
    "language": "de"
  }
}
```

## Market Types

| Type | Description |
|------|-------------|
| `PRIMARY` | Default market (usually domestic) |
| `INTERNATIONAL` | Standard international markets |
| `B2B` | Business-to-business markets |
| `SINGLE_COUNTRY` | Market for one country |
| `MULTI_COUNTRY` | Market spanning multiple countries |

## Market Localizable Resource Types

| Type | Description |
|------|-------------|
| `PRODUCT` | Products |
| `PRODUCT_VARIANT` | Product variants |
| `COLLECTION` | Collections |
| `METAFIELD` | Metafields |
| `METAOBJECT` | Metaobjects |

## Currency Settings

Markets can use:
- **Base currency** - The shop's default currency
- **Local currencies** - Show prices in buyer's local currency

```graphql
query GetMarketCurrencySettings($id: ID!) {
  market(id: $id) {
    currencySettings {
      baseCurrency {
        currencyCode
        currencyName
      }
      localCurrencies
    }
  }
}
```

## Web Presence

Configure how the market appears on the storefront:

```graphql
query GetMarketWebPresence($id: ID!) {
  market(id: $id) {
    webPresence {
      domain {
        host
      }
      subfolderSuffix
      defaultLocale
      alternateLocales
      rootUrls {
        locale
        url
      }
    }
  }
}
```

## API Scopes Required

- `read_markets` - Read market configurations
- `write_markets` - Create, update, delete markets
- `read_translations` - Read market localizations
- `write_translations` - Manage market localizations

## Notes

- Each shop has one primary market (usually domestic sales)
- Markets can overlap in regions but buyers are matched to one market
- Market-specific content overrides default translations
- Currency conversion uses Shopify's exchange rates

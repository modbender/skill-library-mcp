# Shopify Translations

Manage translations for products, collections, pages, and other resources via the GraphQL Admin API.

## Overview

Shopify supports translating content into multiple locales. Each translatable field has a `digest` value used to register translations.

## Get Translatable Resource

```graphql
query GetTranslatableResource($resourceId: ID!) {
  translatableResource(resourceId: $resourceId) {
    resourceId
    translatableContent {
      key
      value
      digest
      locale
    }
    translations(locale: "fr") {
      key
      value
      locale
      outdated
    }
  }
}
```
Variables: `{ "resourceId": "gid://shopify/Product/123" }`

## List Translatable Resources

```graphql
query ListTranslatableResources($resourceType: TranslatableResourceType!, $first: Int!) {
  translatableResources(resourceType: $resourceType, first: $first) {
    nodes {
      resourceId
      translatableContent {
        key
        value
        digest
      }
    }
  }
}
```
Variables: `{ "resourceType": "PRODUCT", "first": 10 }`

## Get Resources by IDs

```graphql
query GetTranslatableResourcesByIds($resourceIds: [ID!]!, $first: Int!) {
  translatableResourcesByIds(resourceIds: $resourceIds, first: $first) {
    nodes {
      resourceId
      translatableContent {
        key
        value
        digest
      }
      translations(locale: "es") {
        key
        value
        outdated
      }
    }
  }
}
```
Variables:
```json
{
  "resourceIds": ["gid://shopify/Product/123", "gid://shopify/Product/456"],
  "first": 10
}
```

## Register Translations

```graphql
mutation RegisterTranslations($resourceId: ID!, $translations: [TranslationInput!]!) {
  translationsRegister(resourceId: $resourceId, translations: $translations) {
    translations {
      key
      value
      locale
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
  "translations": [
    {
      "key": "title",
      "value": "Chandail d'été",
      "locale": "fr",
      "translatableContentDigest": "abc123digest"
    },
    {
      "key": "body_html",
      "value": "<p>Un chandail léger parfait pour l'été.</p>",
      "locale": "fr",
      "translatableContentDigest": "def456digest"
    }
  ]
}
```

## Register Market-Specific Translations

```graphql
mutation RegisterMarketTranslations($resourceId: ID!, $translations: [TranslationInput!]!) {
  translationsRegister(resourceId: $resourceId, translations: $translations) {
    translations {
      key
      value
      locale
      market {
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
Variables:
```json
{
  "resourceId": "gid://shopify/Product/123",
  "translations": [
    {
      "key": "title",
      "value": "Summer Jumper",
      "locale": "en-GB",
      "translatableContentDigest": "abc123digest",
      "marketId": "gid://shopify/Market/456"
    }
  ]
}
```

## Remove Translations

```graphql
mutation RemoveTranslations($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!) {
  translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales) {
    translations {
      key
      locale
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
  "translationKeys": ["title", "body_html"],
  "locales": ["fr"]
}
```

## Remove Market-Specific Translations

```graphql
mutation RemoveMarketTranslations($resourceId: ID!, $translationKeys: [String!]!, $locales: [String!]!, $marketIds: [ID!]) {
  translationsRemove(resourceId: $resourceId, translationKeys: $translationKeys, locales: $locales, marketIds: $marketIds) {
    translations {
      key
      locale
    }
    userErrors {
      field
      message
    }
  }
}
```

## Translatable Resource Types

| Type | Description |
|------|-------------|
| `PRODUCT` | Products |
| `PRODUCT_VARIANT` | Product variants |
| `COLLECTION` | Collections |
| `ONLINE_STORE_PAGE` | Pages |
| `ONLINE_STORE_BLOG` | Blogs |
| `ONLINE_STORE_ARTICLE` | Blog articles |
| `ONLINE_STORE_MENU` | Navigation menus |
| `EMAIL_TEMPLATE` | Email templates |
| `SMS_TEMPLATE` | SMS templates |
| `SHOP` | Shop settings |
| `SHOP_POLICY` | Shop policies |
| `LINK` | Navigation links |
| `METAFIELD` | Metafields |
| `METAOBJECT` | Metaobjects |
| `FILTER` | Storefront filters |
| `PAYMENT_GATEWAY` | Payment gateways |
| `DELIVERY_METHOD_DEFINITION` | Shipping methods |

## Common Translatable Keys by Resource

### Products
- `title` - Product title
- `body_html` - Product description
- `meta_title` - SEO title
- `meta_description` - SEO description

### Collections
- `title` - Collection title
- `body_html` - Collection description
- `meta_title` - SEO title
- `meta_description` - SEO description

### Pages
- `title` - Page title
- `body_html` - Page content

### Metafields
- `value` - Metafield value (for string types)

## Translation Workflow

1. **Get translatable content** - Query the resource to get fields and digests
2. **Translate content** - Prepare translations with the digest values
3. **Register translations** - Submit translations via mutation
4. **Verify** - Query to confirm translations are registered

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

## API Scopes Required

- `read_translations` - Read translations
- `write_translations` - Create, update, delete translations
- `read_locales` - Read shop locales
- `write_locales` - Manage shop locales

## Notes

- Always use the `digest` value from `translatableContent` when registering translations
- Translations marked as `outdated: true` need to be reviewed after the source content changed
- Market-specific translations override locale translations for buyers in that market

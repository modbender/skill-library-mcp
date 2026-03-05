# Shopify Metafields & Metaobjects

Manage custom data with metafields and metaobjects via the GraphQL Admin API.

## Overview

- **Metafields**: Custom fields attached to existing resources (products, customers, orders, etc.)
- **Metaobjects**: Standalone custom data structures with their own definitions

## Metafields

### Set Metafields

```graphql
mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      id
      namespace
      key
      value
      type
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
  "metafields": [
    {
      "ownerId": "gid://shopify/Product/123",
      "namespace": "custom",
      "key": "material",
      "value": "100% Cotton",
      "type": "single_line_text_field"
    },
    {
      "ownerId": "gid://shopify/Product/123",
      "namespace": "custom",
      "key": "care_instructions",
      "value": "Machine wash cold, tumble dry low",
      "type": "multi_line_text_field"
    }
  ]
}
```

### Delete Metafields

```graphql
mutation DeleteMetafields($metafields: [MetafieldIdentifierInput!]!) {
  metafieldsDelete(metafields: $metafields) {
    deletedMetafields {
      ownerId
      namespace
      key
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
  "metafields": [
    {
      "ownerId": "gid://shopify/Product/123",
      "namespace": "custom",
      "key": "material"
    }
  ]
}
```

## Metafield Definitions

### List Definitions

```graphql
query ListMetafieldDefinitions($ownerType: MetafieldOwnerType!, $first: Int!) {
  metafieldDefinitions(ownerType: $ownerType, first: $first) {
    nodes {
      id
      name
      namespace
      key
      type {
        name
      }
      description
      pinnedPosition
    }
  }
}
```
Variables: `{ "ownerType": "PRODUCT", "first": 20 }`

### Create Definition

```graphql
mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition {
      id
      name
      namespace
      key
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
  "definition": {
    "name": "Material",
    "namespace": "custom",
    "key": "material",
    "type": "single_line_text_field",
    "ownerType": "PRODUCT",
    "description": "Product material composition",
    "pin": true
  }
}
```

### Update Definition

```graphql
mutation UpdateMetafieldDefinition($definition: MetafieldDefinitionUpdateInput!) {
  metafieldDefinitionUpdate(definition: $definition) {
    updatedDefinition {
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

### Delete Definition

```graphql
mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
  metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
    deletedDefinitionId
    userErrors {
      field
      message
    }
  }
}
```

## Metafield Types

| Type | Example Value |
|------|---------------|
| `single_line_text_field` | `"Hello"` |
| `multi_line_text_field` | `"Line 1\nLine 2"` |
| `number_integer` | `"42"` |
| `number_decimal` | `"19.99"` |
| `boolean` | `"true"` |
| `date` | `"2025-01-15"` |
| `date_time` | `"2025-01-15T10:00:00Z"` |
| `json` | `"{\"key\": \"value\"}"` |
| `color` | `"#FF5733"` |
| `weight` | `"{\"value\": 1.5, \"unit\": \"kg\"}"` |
| `dimension` | `"{\"value\": 10, \"unit\": \"cm\"}"` |
| `volume` | `"{\"value\": 500, \"unit\": \"ml\"}"` |
| `url` | `"https://example.com"` |
| `money` | `"{\"amount\": \"29.99\", \"currency_code\": \"USD\"}"` |
| `rating` | `"{\"value\": \"4.5\", \"scale_min\": \"1\", \"scale_max\": \"5\"}"` |
| `rich_text_field` | `"{\"type\":\"root\",\"children\":[...]}"` |
| `file_reference` | `"gid://shopify/MediaImage/123"` |
| `product_reference` | `"gid://shopify/Product/123"` |
| `collection_reference` | `"gid://shopify/Collection/123"` |
| `page_reference` | `"gid://shopify/Page/123"` |
| `metaobject_reference` | `"gid://shopify/Metaobject/123"` |
| `list.single_line_text_field` | `"[\"Item 1\", \"Item 2\"]"` |

## Metafield Owner Types

| Type | Description |
|------|-------------|
| `PRODUCT` | Products |
| `PRODUCTVARIANT` | Product variants |
| `COLLECTION` | Collections |
| `CUSTOMER` | Customers |
| `ORDER` | Orders |
| `SHOP` | Shop settings |
| `COMPANY` | B2B companies |
| `COMPANYLOCATION` | B2B company locations |
| `DRAFTORDER` | Draft orders |
| `ARTICLE` | Blog articles |
| `BLOG` | Blogs |
| `PAGE` | Pages |
| `LOCATION` | Locations |

## Metaobjects

### List Metaobject Definitions

```graphql
query ListMetaobjectDefinitions($first: Int!) {
  metaobjectDefinitions(first: $first) {
    nodes {
      id
      name
      type
      fieldDefinitions {
        name
        key
        type {
          name
        }
      }
    }
  }
}
```

### Create Metaobject Definition

```graphql
mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
  metaobjectDefinitionCreate(definition: $definition) {
    metaobjectDefinition {
      id
      name
      type
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
  "definition": {
    "name": "Store Location",
    "type": "store_location",
    "fieldDefinitions": [
      {
        "name": "Name",
        "key": "name",
        "type": "single_line_text_field",
        "required": true
      },
      {
        "name": "Address",
        "key": "address",
        "type": "multi_line_text_field"
      },
      {
        "name": "Phone",
        "key": "phone",
        "type": "single_line_text_field"
      },
      {
        "name": "Image",
        "key": "image",
        "type": "file_reference"
      }
    ],
    "capabilities": {
      "publishable": {
        "enabled": true
      }
    }
  }
}
```

### List Metaobjects

```graphql
query ListMetaobjects($type: String!, $first: Int!) {
  metaobjects(type: $type, first: $first) {
    nodes {
      id
      handle
      displayName
      fields {
        key
        value
      }
    }
  }
}
```
Variables: `{ "type": "store_location", "first": 10 }`

### Create Metaobject

```graphql
mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
  metaobjectCreate(metaobject: $metaobject) {
    metaobject {
      id
      handle
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
  "metaobject": {
    "type": "store_location",
    "handle": "new-york-store",
    "fields": [
      {
        "key": "name",
        "value": "New York Flagship Store"
      },
      {
        "key": "address",
        "value": "123 Broadway, New York, NY 10001"
      },
      {
        "key": "phone",
        "value": "+1 (212) 555-0100"
      }
    ]
  }
}
```

### Update Metaobject

```graphql
mutation UpdateMetaobject($id: ID!, $metaobject: MetaobjectUpdateInput!) {
  metaobjectUpdate(id: $id, metaobject: $metaobject) {
    metaobject {
      id
      fields {
        key
        value
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

### Upsert Metaobject

```graphql
mutation UpsertMetaobject($handle: MetaobjectHandleInput!, $metaobject: MetaobjectUpsertInput!) {
  metaobjectUpsert(handle: $handle, metaobject: $metaobject) {
    metaobject {
      id
      handle
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
  "handle": {
    "type": "store_location",
    "handle": "new-york-store"
  },
  "metaobject": {
    "fields": [
      {
        "key": "phone",
        "value": "+1 (212) 555-0200"
      }
    ]
  }
}
```

### Delete Metaobject

```graphql
mutation DeleteMetaobject($id: ID!) {
  metaobjectDelete(id: $id) {
    deletedId
    userErrors {
      field
      message
    }
  }
}
```

### Bulk Delete Metaobjects

```graphql
mutation BulkDeleteMetaobjects($where: MetaobjectBulkDeleteWhereCondition!) {
  metaobjectBulkDelete(where: $where) {
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
Variables:
```json
{
  "where": {
    "type": "store_location",
    "ids": ["gid://shopify/Metaobject/1", "gid://shopify/Metaobject/2"]
  }
}
```

## API Scopes Required

- `read_metafields` - Read metafields
- `write_metafields` - Create, update, delete metafields
- `read_metaobject_definitions` - Read metaobject definitions
- `write_metaobject_definitions` - Manage metaobject definitions
- `read_metaobjects` - Read metaobjects
- `write_metaobjects` - Create, update, delete metaobjects

## Notes

- Namespace `$app:` is reserved for app-specific metafields
- Metafield values are always strings (even for numbers/booleans)
- Use definitions for validation and admin UI integration
- Metaobjects are useful for structured content like FAQs, team members, store locations
- Maximum 25 metafields per `metafieldsSet` call

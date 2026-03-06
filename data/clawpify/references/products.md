# Shopify Products & Variants

## Products

### List Products

```graphql
query ListProducts($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      title
      status
      vendor
      productType
      createdAt
      updatedAt
    }
  }
}
```
Variables: `{ "first": 10 }`

### Get Product by ID

```graphql
query GetProduct($id: ID!) {
  product(id: $id) {
    id
    title
    descriptionHtml
    status
    vendor
    productType
    tags
    options {
      name
      values
    }
    variants(first: 100) {
      nodes {
        id
        title
        sku
        price
        inventoryQuantity
        selectedOptions {
          name
          value
        }
      }
    }
    images(first: 10) {
      nodes {
        id
        url
        altText
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Product/123" }`

### Search Products

```graphql
query SearchProducts($query: String!, $first: Int!) {
  products(first: $first, query: $query) {
    nodes {
      id
      title
      status
      vendor
    }
  }
}
```
Variables: `{ "query": "title:*shirt*", "first": 10 }`

Search query syntax:
- `title:*keyword*` - title contains keyword
- `status:ACTIVE` - by status (ACTIVE, DRAFT, ARCHIVED)
- `vendor:Nike` - by vendor
- `product_type:Shoes` - by product type
- Combine with `AND`, `OR`: `status:ACTIVE AND vendor:Nike`

### Create Product

```graphql
mutation CreateProduct($product: ProductCreateInput!, $media: [CreateMediaInput!]) {
  productCreate(product: $product, media: $media) {
    product {
      id
      title
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
  "product": {
    "title": "New Product",
    "descriptionHtml": "<p>Product description</p>",
    "vendor": "My Store",
    "productType": "Clothing",
    "status": "DRAFT",
    "tags": ["new", "featured"]
  }
}
```

### Update Product

> REQUIRES PERMISSION: If changing product status from DRAFT to ACTIVE, this publishes the product and makes it visible to customers. Always ask the user for explicit confirmation before changing status to ACTIVE.

```graphql
mutation UpdateProduct($product: ProductUpdateInput!) {
  productUpdate(product: $product) {
    product {
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
  "product": {
    "id": "gid://shopify/Product/123",
    "title": "Updated Title",
    "status": "ACTIVE"
  }
}
```

### Delete Product

> REQUIRES PERMISSION: Deleting a product is PERMANENT and removes it from your store completely. All variants, images, and data will be lost and cannot be recovered. Always ask the user for explicit confirmation, show the product title and ID, and wait for approval before executing this operation.

```graphql
mutation DeleteProduct($input: ProductDeleteInput!) {
  productDelete(input: $input) {
    deletedProductId
    userErrors {
      field
      message
    }
  }
}
```
Variables: `{ "input": { "id": "gid://shopify/Product/123" } }`

---

## Product Variants

### Create Variants (Bulk)

```graphql
mutation CreateVariants($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants {
      id
      title
      sku
      price
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
  "productId": "gid://shopify/Product/123",
  "variants": [
    {
      "barcode": "1234567890",
      "price": "29.99",
      "optionValues": [
        { "optionName": "Size", "name": "Small" },
        { "optionName": "Color", "name": "Blue" }
      ],
      "inventoryItem": {
        "sku": "SKU-001"
      }
    }
  ]
}
```

### Update Variants (Bulk)

```graphql
mutation UpdateVariants($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants {
      id
      price
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
  "productId": "gid://shopify/Product/123",
  "variants": [
    {
      "id": "gid://shopify/ProductVariant/456",
      "price": "34.99"
    }
  ]
}
```

### Delete Variants (Bulk)

> REQUIRES PERMISSION: Bulk deleting product variants is PERMANENT and cannot be undone. All variant data will be lost. Always ask the user for explicit confirmation, list the variants to be deleted, and wait for approval before executing this operation.

```graphql
mutation DeleteVariants($productId: ID!, $variantsIds: [ID!]!) {
  productVariantsBulkDelete(productId: $productId, variantsIds: $variantsIds) {
    product {
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
  "productId": "gid://shopify/Product/123",
  "variantsIds": ["gid://shopify/ProductVariant/456"]
}
```

## Dangerous Operations in This Skill

The following operations require explicit user permission before execution:

| Operation | Impact | Reversible |
|-----------|--------|------------|
| `productUpdate` (status: ACTIVE) | Publishes product and makes it visible to customers | Yes (can set back to DRAFT) |
| `productDelete` | Permanently deletes product and all variants | No - IRREVERSIBLE |
| `productVariantsBulkDelete` | Permanently deletes multiple variants at once | No - IRREVERSIBLE |

Permission Protocol: 
- For status changes to ACTIVE: Show product title and confirm publication
- For deletions: Show product/variant details, emphasize permanence, wait for explicit "yes", "confirm", or "proceed"

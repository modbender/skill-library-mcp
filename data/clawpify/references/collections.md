# Shopify Collections & Discounts

## Collections

### List Collections

```graphql
query ListCollections($first: Int!) {
  collections(first: $first) {
    nodes {
      id
      title
      handle
      productsCount {
        count
        precision
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

Note: `productsCount.precision` indicates if count is `EXACT` or `AT_LEAST` (estimated).

### Get Collection Products

```graphql
query GetCollectionProducts($id: ID!, $first: Int!) {
  collection(id: $id) {
    id
    title
    products(first: $first) {
      nodes {
        id
        title
        status
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Collection/123", "first": 20 }`

---

## Discounts

### List Discount Codes

```graphql
query ListDiscounts($first: Int!) {
  codeDiscountNodes(first: $first) {
    nodes {
      id
      codeDiscount {
        ... on DiscountCodeBasic {
          title
          status
          codes(first: 5) {
            nodes {
              code
            }
          }
        }
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

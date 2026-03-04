# Shopify Pages

Manage online store pages (About Us, Contact, policies, etc.) via the GraphQL Admin API.

## Overview

Pages are custom content pages displayed on the storefront, separate from products and collections.

## List Pages

```graphql
query ListPages($first: Int!, $after: String, $query: String) {
  pages(first: $first, after: $after, query: $query, sortKey: TITLE) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      title
      handle
      isPublished
      createdAt
      updatedAt
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Page

```graphql
query GetPage($id: ID!) {
  page(id: $id) {
    id
    title
    handle
    body
    isPublished
    publishedAt
    createdAt
    updatedAt
    templateSuffix
    metafields(first: 10) {
      nodes {
        key
        namespace
        value
        type
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Page/123" }`

## Get Pages Count

```graphql
query GetPagesCount {
  pagesCount {
    count
  }
}
```

## Create Page

```graphql
mutation CreatePage($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page {
      id
      title
      handle
      isPublished
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
  "page": {
    "title": "About Us",
    "handle": "about-us",
    "body": "<h1>About Our Company</h1><p>We are passionate about delivering quality products...</p>",
    "isPublished": true
  }
}
```

## Create Page with Metafields

```graphql
mutation CreatePageWithMetafields($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page {
      id
      title
      metafields(first: 5) {
        nodes {
          key
          value
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
  "page": {
    "title": "Store Locations",
    "body": "<p>Find a store near you.</p>",
    "isPublished": true,
    "metafields": [
      {
        "namespace": "custom",
        "key": "show_map",
        "value": "true",
        "type": "boolean"
      }
    ]
  }
}
```

## Update Page

```graphql
mutation UpdatePage($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page {
      id
      title
      body
      isPublished
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
  "id": "gid://shopify/Page/123",
  "page": {
    "body": "<h1>About Our Company</h1><p>Updated content with new information...</p>"
  }
}
```

## Publish/Unpublish Page

```graphql
mutation PublishPage($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page {
      id
      isPublished
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
  "id": "gid://shopify/Page/123",
  "page": {
    "isPublished": true
  }
}
```

## Delete Page

```graphql
mutation DeletePage($id: ID!) {
  pageDelete(id: $id) {
    deletedPageId
    userErrors {
      field
      message
    }
  }
}
```

## Search Pages

```graphql
query SearchPages($query: String!) {
  pages(first: 10, query: $query) {
    nodes {
      id
      title
      handle
      isPublished
    }
  }
}
```
Variables: `{ "query": "title:contact OR title:about" }`

## Page Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Page title |
| `handle` | String | URL handle (e.g., `/pages/about-us`) |
| `body` | HTML | Page content (HTML) |
| `isPublished` | Boolean | Visibility status |
| `publishedAt` | DateTime | Publication timestamp |
| `templateSuffix` | String | Custom template suffix |

## Template Suffixes

Use template suffixes to apply custom page templates:

```json
{
  "page": {
    "title": "Contact Us",
    "body": "<p>Get in touch...</p>",
    "templateSuffix": "contact"
  }
}
```

This uses `page.contact.liquid` template in the theme.

## Search Query Filters

| Filter | Example | Description |
|--------|---------|-------------|
| `title` | `title:about` | Filter by title |
| `created_at` | `created_at:>2024-01-01` | Filter by creation date |
| `updated_at` | `updated_at:>2024-01-01` | Filter by update date |
| `published_status` | `published_status:published` | Filter by publish status |

## API Scopes Required

- `read_content` - Read pages
- `write_content` - Create, update, delete pages

## Common Use Cases

### Policy Pages
```json
{
  "page": {
    "title": "Privacy Policy",
    "handle": "privacy-policy",
    "body": "<h1>Privacy Policy</h1><p>Your privacy is important to us...</p>",
    "isPublished": true
  }
}
```

### FAQ Page
```json
{
  "page": {
    "title": "Frequently Asked Questions",
    "handle": "faq",
    "body": "<h1>FAQ</h1><details><summary>How do I track my order?</summary><p>You can track your order...</p></details>",
    "isPublished": true
  }
}
```

### Contact Page with Custom Template
```json
{
  "page": {
    "title": "Contact Us",
    "handle": "contact",
    "body": "",
    "isPublished": true,
    "templateSuffix": "contact"
  }
}
```

## Notes

- Handles must be unique and URL-safe
- HTML in body is sanitized by Shopify
- Pages are separate from product and collection pages
- Use metafields to store additional structured data

# Shopify Menus

Manage navigation menus for the online store via the GraphQL Admin API.

## Overview

Menus organize navigation links that help customers find collections, products, pages, blogs, and external URLs. Menus support nested items up to three levels deep.

## List Menus

```graphql
query ListMenus($first: Int!) {
  menus(first: $first) {
    nodes {
      id
      title
      handle
      itemsCount {
        count
      }
    }
  }
}
```
Variables: `{ "first": 10 }`

## Get Menu

```graphql
query GetMenu($id: ID!) {
  menu(id: $id) {
    id
    title
    handle
    items {
      id
      title
      type
      url
      resourceId
      items {
        id
        title
        type
        url
        items {
          id
          title
          url
        }
      }
    }
  }
}
```
Variables: `{ "id": "gid://shopify/Menu/123" }`

## Create Menu

```graphql
mutation CreateMenu($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu {
      id
      title
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
  "title": "Main Menu",
  "handle": "main-menu",
  "items": [
    {
      "title": "Home",
      "type": "FRONTPAGE",
      "url": "/"
    },
    {
      "title": "Shop",
      "type": "COLLECTION",
      "resourceId": "gid://shopify/Collection/123"
    },
    {
      "title": "About",
      "type": "PAGE",
      "resourceId": "gid://shopify/Page/456"
    },
    {
      "title": "Contact",
      "type": "HTTP",
      "url": "/pages/contact"
    }
  ]
}
```

## Create Menu with Nested Items

```graphql
mutation CreateMenuWithNesting($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
  menuCreate(title: $title, handle: $handle, items: $items) {
    menu {
      id
      title
      items {
        title
        items {
          title
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
  "title": "Shop By Category",
  "handle": "shop-categories",
  "items": [
    {
      "title": "Clothing",
      "type": "COLLECTION",
      "resourceId": "gid://shopify/Collection/100",
      "items": [
        {
          "title": "T-Shirts",
          "type": "COLLECTION",
          "resourceId": "gid://shopify/Collection/101"
        },
        {
          "title": "Pants",
          "type": "COLLECTION",
          "resourceId": "gid://shopify/Collection/102"
        },
        {
          "title": "Dresses",
          "type": "COLLECTION",
          "resourceId": "gid://shopify/Collection/103"
        }
      ]
    },
    {
      "title": "Accessories",
      "type": "COLLECTION",
      "resourceId": "gid://shopify/Collection/200",
      "items": [
        {
          "title": "Hats",
          "type": "COLLECTION",
          "resourceId": "gid://shopify/Collection/201"
        },
        {
          "title": "Bags",
          "type": "COLLECTION",
          "resourceId": "gid://shopify/Collection/202"
        }
      ]
    }
  ]
}
```

## Update Menu

```graphql
mutation UpdateMenu($id: ID!, $title: String!, $handle: String, $items: [MenuItemUpdateInput!]!) {
  menuUpdate(id: $id, title: $title, handle: $handle, items: $items) {
    menu {
      id
      title
      handle
      items {
        title
        url
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
  "id": "gid://shopify/Menu/123",
  "title": "Main Navigation",
  "items": [
    {
      "title": "Home",
      "type": "FRONTPAGE",
      "url": "/"
    },
    {
      "title": "New Arrivals",
      "type": "COLLECTION",
      "resourceId": "gid://shopify/Collection/789"
    },
    {
      "title": "Sale",
      "type": "COLLECTION",
      "resourceId": "gid://shopify/Collection/999"
    }
  ]
}
```

## Delete Menu

```graphql
mutation DeleteMenu($id: ID!) {
  menuDelete(id: $id) {
    deletedMenuId
    userErrors {
      field
      message
    }
  }
}
```

## Menu Item Types

| Type | Description | Required Field |
|------|-------------|----------------|
| `FRONTPAGE` | Link to homepage | `url: "/"` |
| `COLLECTION` | Link to a collection | `resourceId` |
| `PRODUCT` | Link to a product | `resourceId` |
| `PAGE` | Link to a page | `resourceId` |
| `BLOG` | Link to a blog | `resourceId` |
| `ARTICLE` | Link to an article | `resourceId` |
| `HTTP` | Custom URL (internal) | `url` |
| `SEARCH` | Link to search page | - |
| `CATALOG` | Link to catalog | - |

## Common Menu Handles

| Handle | Description |
|--------|-------------|
| `main-menu` | Primary navigation |
| `footer` | Footer navigation |
| `header` | Header links |

## Footer Menu Example

```json
{
  "title": "Footer",
  "handle": "footer",
  "items": [
    {
      "title": "Quick Links",
      "type": "HTTP",
      "url": "#",
      "items": [
        {
          "title": "Search",
          "type": "SEARCH"
        },
        {
          "title": "About Us",
          "type": "PAGE",
          "resourceId": "gid://shopify/Page/123"
        }
      ]
    },
    {
      "title": "Policies",
      "type": "HTTP",
      "url": "#",
      "items": [
        {
          "title": "Privacy Policy",
          "type": "PAGE",
          "resourceId": "gid://shopify/Page/456"
        },
        {
          "title": "Terms of Service",
          "type": "PAGE",
          "resourceId": "gid://shopify/Page/789"
        }
      ]
    }
  ]
}
```

## API Scopes Required

- `read_online_store_navigation` - Read menus
- `write_online_store_navigation` - Create, update, delete menus

## Notes

- Default menus (`main-menu`, `footer`) cannot have their handles changed
- Maximum nesting depth is 3 levels
- Menu updates replace all items (not partial update)
- Resource IDs must be valid Shopify global IDs
- Use `HTTP` type for relative URLs within the store

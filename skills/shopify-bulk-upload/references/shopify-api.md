# Shopify Admin API Reference

## Basic Info

- **API Version**: 2024-01
- **Base URL**: `https://{store}.myshopify.com/admin/api/{version}/`
- **Auth**: Header `X-Shopify-Access-Token: {access_token}`

## Common Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /products.json | Get product list |
| GET | /products/{id}.json | Get single product |
| POST | /products.json | Create product |
| PUT | /products/{id}.json | Update product |
| DELETE | /products/{id}.json | Delete product |

### Product Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /products/{id}/images.json | Upload image |
| DELETE | /products/{id}/images/{image_id}.json | Delete image |

### Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /inventory_levels.json | Get inventory |
| POST | /inventory_levels/set.json | Set inventory |

## Product Create Example

```json
POST /admin/api/2024-01/products.json

{
  "product": {
    "title": "Sample Product",
    "body_html": "<p>Product description</p>",
    "vendor": "Brand Name",
    "product_type": "Category",
    "status": "active",
    "tags": "tag1, tag2",
    "variants": [
      {
        "price": "89.00",
        "sku": "SKU001",
        "inventory_management": "shopify",
        "inventory_quantity": 100,
        "weight": 0.5,
        "weight_unit": "kg"
      }
    ],
    "options": [
      {
        "name": "Color",
        "values": ["Red", "Blue"]
      }
    ]
  }
}
```

## Permission Scopes

When creating App, check these permissions:

| Permission | Usage |
|------------|-------|
| write_products | Create/update products |
| write_inventory | Manage inventory |
| read_products | Read products |
| read_inventory | Read inventory |

## Rate Limits

- **Regular API**: 40 requests per minute
- **Batch operations**: Separate limits
- **Returns 429**: Check `Retry-After` header

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Failed |
| 429 | Rate Limited |

## Error Response Example

```json
{
  "errors": {
    "title": ["Title is required"]
  }
}
```

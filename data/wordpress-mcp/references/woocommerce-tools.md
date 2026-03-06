# WooCommerce Tools Reference

Requires **WooCommerce** plugin. Available when AI Engine detects WooCommerce.

## Products

### wc_list_products
List products with filters.
- `status` (string): "publish", "draft", "any"
- `category` (string): Category slug
- `search` (string)
- `per_page` (int)
- `orderby` (string): "date", "title", "price"

### wc_get_product
- `id` (int, required)

### wc_create_product
- `name` (string, required)
- `type` (string): "simple", "variable", "grouped"
- `regular_price` (string)
- `sale_price` (string)
- `description` (string)
- `short_description` (string)
- `status` (string): "draft", "publish"
- `categories` (array): `[{"id": 1}]`
- `images` (array): `[{"src": "url"}]`
- `sku` (string)
- `manage_stock` (bool)
- `stock_quantity` (int)

### wc_update_product
- `id` (int, required)
- Plus any fields from create

### wc_delete_product
- `id` (int, required)
- `force` (bool)

### wc_alter_product
Search-and-replace in product description.
- `id` (int, required)
- `field` (string)
- `search` (string, required)
- `replace` (string, required)

## Orders

### wc_list_orders
- `status` (string): "processing", "completed", "on-hold", etc.
- `per_page` (int)
- `after` / `before` (string): ISO date filters

### wc_get_order
- `id` (int, required)

### wc_update_order_status
- `id` (int, required)
- `status` (string, required): "processing", "completed", "cancelled"

### wc_add_order_note
- `id` (int, required)
- `note` (string, required)
- `customer_note` (bool): Visible to customer?

### wc_create_refund
- `order_id` (int, required)
- `amount` (string)
- `reason` (string)

### wc_get_orders_by_customer
- `customer_id` (int, required)

## Stock

### wc_update_stock
- `product_id` (int, required)
- `stock_quantity` (int, required)

### wc_get_low_stock_products
- `threshold` (int): Stock level threshold

### wc_get_stock_report
Overview of stock status across products.

### wc_bulk_update_stock
- `updates` (array, required): `[{"product_id": 1, "stock_quantity": 10}]`

## Reports

### wc_get_sales_report
- `period` (string): "week", "month", "year"
- `date_min` / `date_max` (string)

### wc_get_top_sellers
- `period` (string)

### wc_get_revenue_stats
Revenue overview and trends.

## Customers

### wc_list_customers
- `per_page` (int)
- `search` (string)
- `role` (string)

### wc_get_customer
- `id` (int, required)

### wc_update_customer
- `id` (int, required)
- `fields` (object)

## Reviews

### wc_list_reviews
- `product_id` (int): Filter by product
- `status` (string): "approved", "hold"

### wc_approve_review
- `id` (int, required)

### wc_delete_review
- `id` (int, required)
- `force` (bool)

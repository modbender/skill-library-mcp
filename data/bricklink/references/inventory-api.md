# BrickLink Store Inventory API (Store v1)

Base URL: `https://api.bricklink.com/api/store/v1`

## Get store inventories

- Method: `GET /inventories`
- Query params (all optional):
  - `item_type` (String): include/exclude types, comma-separated; prefix `-` to exclude
    - Example: `part,set` or `-set`
  - `status` (String): include/exclude inventory status codes; comma-separated; `-` excludes
    - Values: `Y` available, `S` stockroom A, `B` stockroom B, `C` stockroom C, `N` unavailable, `R` reserved
  - `category_id` (Integer): include/exclude categories; comma-separated; `-` excludes (main category only)
  - `color_id` (Integer): include/exclude colors; comma-separated; `-` excludes

## Get store inventory

- Method: `GET /inventories/{inventory_id}`

## Inventory resource representation

See: https://www.bricklink.com/v3/api.page?page=resource-representations-inventory

Key fields include:
- `inventory_id`
- `item.{no,name,type,category_id}`
- `color_id`, `color_name`
- `quantity`, `new_or_used`, `completeness`
- `unit_price`
- `description`, `remarks`
- `bulk`, `is_retain`, `is_stock_room`, `stock_room_id`
- `date_created`, `my_cost`, `sale_rate`
- tiered pricing fields

# BrickLink Orders API (Store v1)

From BrickLink v3 docs (API guide):

## Get Orders

- Method: `GET /orders`
- Params:
  - `direction` (String, optional): `in` (received, default) or `out` (placed)
  - `status` (String, optional): comma-separated status list; prefix with `-` to exclude (e.g. `-purged`)
  - `filed` (Boolean, optional): `true` or `false` (default)

## Get Order

- Method: `GET /orders/{order_id}`
- Params:
  - `order_id` (Integer, required)

## Get Order Items

- Method: `GET /orders/{order_id}/items`
- Params:
  - `order_id` (Integer, required)

## Get Order Messages

- Method: `GET /orders/{order_id}/messages`
- Params:
  - `order_id` (Integer, required)

## Get Order Feedback

- Method: `GET /orders/{order_id}/feedback`
- Params:
  - `order_id` (Integer, required)

## Update Order

- Method: `PUT /orders/{order_id}`
- Body: partial order resource (limited fields)

## Update Order Status

- Method: `PUT /orders/{order_id}/status`
- Body: `{ "field": "status", "value": "PENDING" }`

## Update Payment Status

- Method: `PUT /orders/{order_id}/payment_status`
- Body: `{ "field": "payment_status", "value": "Received" }`

## Send Drive Thru

- Method: `POST /orders/{order_id}/drive_thru?mail_me=true`

Base URL (store API): `https://api.bricklink.com/api/store/v1`

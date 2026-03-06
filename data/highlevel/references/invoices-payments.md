# Invoices, Payments & Products API Reference

## Invoices — `/invoices/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/invoices/?locationId={id}&limit={n}` | List invoices |
| GET | `/invoices/{invoiceId}` | Get invoice |
| POST | `/invoices/` | Create invoice |
| PUT | `/invoices/{invoiceId}` | Update invoice |
| DELETE | `/invoices/{invoiceId}` | Delete invoice |
| POST | `/invoices/{invoiceId}/send` | Send invoice |
| POST | `/invoices/{invoiceId}/void` | Void invoice |
| POST | `/invoices/{invoiceId}/record-payment` | Record payment |
| POST | `/invoices/text2pay` | Send Text2Pay link |
| GET | `/invoices/generate-invoice-number?locationId={id}` | Generate invoice number |
| GET/POST/PUT/DELETE | `/invoices/schedule/...` | Schedule CRUD |
| GET/POST/PUT/DELETE | `/invoices/template/...` | Template CRUD |
| GET/POST/PUT/DELETE | `/invoices/estimate/...` | Estimate CRUD |

**Scopes**: `invoices.readonly`, `invoices.write`, `invoices/schedule.*`, `invoices/template.*`, `invoices/estimate.*`

## Payments — `/payments/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/payments/orders/?locationId={id}` | List orders |
| GET | `/payments/orders/{orderId}` | Get order |
| GET/POST | `/payments/orders/{orderId}/fulfillments` | Order fulfillments |
| GET | `/payments/transactions/?locationId={id}` | List transactions |
| GET | `/payments/transactions/{transactionId}` | Get transaction |
| GET | `/payments/subscriptions/?locationId={id}` | List subscriptions |
| GET | `/payments/subscriptions/{subscriptionId}` | Get subscription |
| GET/POST/PUT/DELETE | `/payments/coupon/...` | Coupon management |
| GET/POST | `/payments/integrations/provider/whitelabel` | Integration providers |
| GET/POST/PUT/DELETE | `/payments/custom-provider/...` | Custom payment providers |

**Scopes**: `payments/orders.*`, `payments/transactions.readonly`, `payments/subscriptions.readonly`, `payments/coupons.*`, `payments/custom-provider.*`

## Products — `/products/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products/?locationId={id}&limit={n}` | List products |
| GET | `/products/{productId}` | Get product |
| POST | `/products/` | Create product |
| PUT | `/products/{productId}` | Update product |
| DELETE | `/products/{productId}` | Delete product |
| POST | `/products/bulk-update` | Bulk update |
| GET/POST/PUT/DELETE | `/products/{id}/price/...` | Price CRUD |
| GET/POST/PUT/DELETE | `/products/collections/...` | Collection CRUD |
| GET/POST/PUT/DELETE | `/products/reviews/...` | Review CRUD |
| GET | `/products/store/{storeId}/stats` | Store statistics |

**Scopes**: `products.readonly`, `products.write`, `products/prices.*`, `products/collection.*`

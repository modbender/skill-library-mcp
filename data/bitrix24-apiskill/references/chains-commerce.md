# Chains: commerce

## 1) Order intake to payment

1. `sale.order.add`
2. `sale.payment.add`
3. `sale.order.update` (status/metadata)

## 2) Product and price sync

1. `catalog.product.list`
2. `catalog.price.list`
3. `catalog.product.update` or `catalog.price.add`

## 3) Delivery assignment

1. `sale.delivery.getlist`
2. choose delivery service id
3. update order shipment/payment context

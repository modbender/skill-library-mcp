---
name: agos-marketplace
version: 1.2.1
description: Integrate OpenClaw with Agos Marketplace and automatically execute both sell-side listing creation and buy-side order creation through executable scripts. Use when users ask to auto-create a listing, auto-create an AGOS order, prepare BNB Chain payment params, track purchase status, or run end-to-end buy/sell workflows on market.agos.fun.
---

# Agos Marketplace

Use this skill to automate both sides of AGOS marketplace flow:

- Seller side: create listing (service)
- Buyer side: create order (purchase)

## Defaults

- Base URL: `https://market.agos.fun`
- Supplier endpoint (listing script): fixed to `https://market.agos.fun/v1/openclaw/supplier-task`
- Chain: `BNB Chain` (`chainId=56`)
- Settlement token: `USDT`
- APIs:
  - Seller: `/v1/services`
  - Buyer: `/v1/openclaw/purchases*`

## Scripts

- `scripts/create_listing.py`: auto-create seller listing
- `scripts/create_order.py`: auto-create buyer purchase(order)

Always run scripts directly for automation. Do not ask users to manually craft curl unless debugging.

## Sell-Side Automation (Create Listing)

Create listing with generated service id:

```bash
python3 scripts/create_listing.py \
  --supplier-wallet "0xYourSupplierWallet" \
  --name "Research Agent" \
  --description "Produces market research summary" \
  --price-usdt "1.5"
```

Create listing with fixed service id:

```bash
python3 scripts/create_listing.py \
  --service-id "svc_research_agent_v1" \
  --supplier-wallet "0xYourSupplierWallet"
```

Dry-run payload:

```bash
python3 scripts/create_listing.py --dry-run
```

## Buy-Side Automation (Create Order)

Auto-select first active listing and create order:

```bash
python3 scripts/create_order.py \
  --buyer-wallet "0xYourBuyerWallet" \
  --input-json '{"task":"auto order"}'
```

Create order for specific listing and prepare payment params:

```bash
python3 scripts/create_order.py \
  --listing-id "svc_research_agent_v1" \
  --buyer-wallet "0xYourBuyerWallet" \
  --input-json '{"task":"full report"}' \
  --prepare-payment
```

Create order and wait until terminal status:

```bash
python3 scripts/create_order.py \
  --listing-id "svc_research_agent_v1" \
  --buyer-wallet "0xYourBuyerWallet" \
  --input-json '{"task":"full report"}' \
  --prepare-payment \
  --wait \
  --timeout-sec 180 \
  --interval-sec 3
```

## Payment Mapping

Use `payment_preparation` fields to call `PaymentRouter.payForService(orderId, serviceId, supplier, token, amount)`:

- `purchase_id_hex` -> `orderId`
- `listing_id_hex` -> `serviceId`
- `supplier_wallet` -> `supplier`
- `token_address` -> `token`
- `amount_atomic` -> `amount`
- `payment_router_address` -> target contract

## Wallet Responsibility

This skill automates listing and order creation via HTTP APIs.

Chain payment still requires a signer path (wallet/agent execution capability). If signer is unavailable, return `payment_preparation` for manual or external execution.

## Security Constraints

- `create_listing.py` and `create_order.py` use fixed AGOS API base URL.
- URL overrides via `--base-url` or `AGOS_API_BASE` are intentionally disabled.
- Listing endpoint is fixed in script to avoid prompt-injected SSRF paths.

## Output Contract

For seller flow return:

- `service_id`
- `service`

For buyer flow return:

- `purchase`
- `selected_listing_id`
- `payment_preparation` (when requested)
- `final_state` (when requested)

## Error Rules

- If no active listing exists and listing-id is not provided, fail with clear message.
- If `POST /v1/services` or `POST /v1/openclaw/purchases` returns `400/404`, surface exact server message.
- If status polling times out, return last known state.

# Index

| API | Line |
|-----|------|
| Stripe | 2 |
| PayPal | 95 |
| Square | 179 |
| Plaid | 249 |
| Chargebee | 320 |
| Paddle | 388 |
| Lemon Squeezy | 461 |
| Recurly | 537 |
| Wise | 610 |
| Coinbase | 683 |
| Binance | 769 |
| Alpaca | 836 |
| Polygon | 913 |

---

# Stripe

## Base URL
```
https://api.stripe.com/v1
```

## Authentication
```bash
curl https://api.stripe.com/v1/customers \
  -u sk_test_xxx:
# Note: colon after key, no password
```

Or with header:
```bash
-H "Authorization: Bearer sk_test_xxx"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /customers | GET | List customers |
| /customers | POST | Create customer |
| /customers/:id | GET | Get customer |
| /payment_intents | POST | Create payment |
| /subscriptions | POST | Create subscription |
| /invoices | GET | List invoices |
| /refunds | POST | Create refund |

## Quick Examples

### Create Customer
```bash
curl https://api.stripe.com/v1/customers \
  -u sk_test_xxx: \
  -d email="customer@example.com" \
  -d name="John Doe"
```

### Create Payment Intent
```bash
curl https://api.stripe.com/v1/payment_intents \
  -u sk_test_xxx: \
  -d amount=2000 \
  -d currency=usd \
  -d "payment_method_types[]"=card
```

### Create Subscription
```bash
curl https://api.stripe.com/v1/subscriptions \
  -u sk_test_xxx: \
  -d customer=cus_xxx \
  -d "items[0][price]"=price_xxx
```

### List Payments
```bash
curl https://api.stripe.com/v1/payment_intents?limit=10 \
  -u sk_test_xxx:
```

## Webhooks

```bash
# Verify webhook signature
stripe_signature = request.headers['Stripe-Signature']
# Use stripe library to verify
```

Common events:
- `payment_intent.succeeded`
- `customer.subscription.created`
- `invoice.paid`
- `charge.refunded`

## Common Traps

- Amount in cents (2000 = $20.00)
- Test keys start with `sk_test_`, live with `sk_live_`
- Always use idempotency key for payments
- Webhook signatures required in production

## Rate Limits

- 100 read requests/sec (test mode)
- 100 write requests/sec (test mode)
- Higher limits in live mode

## Official Docs
https://stripe.com/docs/api
# PayPal

## Base URL
```
# Sandbox
https://api-m.sandbox.paypal.com

# Production
https://api-m.paypal.com
```

## Authentication
```bash
# Get access token
curl -X POST "https://api-m.sandbox.paypal.com/v1/oauth2/token" \
  -u "$PAYPAL_CLIENT_ID:$PAYPAL_SECRET" \
  -d "grant_type=client_credentials"

# Use access token
curl "https://api-m.sandbox.paypal.com/v2/checkout/orders/$ORDER_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Create Order
```bash
curl -X POST "https://api-m.sandbox.paypal.com/v2/checkout/orders" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "CAPTURE",
    "purchase_units": [{
      "amount": {
        "currency_code": "USD",
        "value": "100.00"
      }
    }]
  }'
```

## Capture Order
```bash
curl -X POST "https://api-m.sandbox.paypal.com/v2/checkout/orders/$ORDER_ID/capture" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Get Order
```bash
curl "https://api-m.sandbox.paypal.com/v2/checkout/orders/$ORDER_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Refund
```bash
curl -X POST "https://api-m.sandbox.paypal.com/v2/payments/captures/$CAPTURE_ID/refund" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": {
      "value": "10.00",
      "currency_code": "USD"
    }
  }'
```

## Order Status Values

| Status | Meaning |
|--------|---------|
| CREATED | Order created, not approved |
| APPROVED | Buyer approved, ready to capture |
| COMPLETED | Payment captured |
| VOIDED | Order cancelled |

## Common Traps

- Access token expires in ~8 hours
- Sandbox vs Production URLs are different
- Orders must be APPROVED before capture
- Use v2 endpoints (v1 is legacy)
- Amount value must be string with 2 decimals

## Official Docs
https://developer.paypal.com/docs/api/orders/v2/
# Square

## Base URL
```
https://connect.squareup.com/v2
```

## Authentication
```bash
curl https://connect.squareup.com/v2/locations \
  -H "Authorization: Bearer $SQUARE_ACCESS_TOKEN" \
  -H "Square-Version: 2024-01-18"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /locations | GET | List locations |
| /payments | POST | Create payment |
| /orders | POST | Create order |
| /customers | GET | List customers |
| /catalog/list | GET | List catalog |

## Create Payment
```bash
curl -X POST https://connect.squareup.com/v2/payments \
  -H "Authorization: Bearer $SQUARE_ACCESS_TOKEN" \
  -H "Square-Version: 2024-01-18" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "CARD_NONCE",
    "idempotency_key": "unique-key-123",
    "amount_money": {
      "amount": 1000,
      "currency": "USD"
    },
    "location_id": "LOCATION_ID"
  }'
```

## List Catalog Items
```bash
curl "https://connect.squareup.com/v2/catalog/list?types=ITEM" \
  -H "Authorization: Bearer $SQUARE_ACCESS_TOKEN" \
  -H "Square-Version: 2024-01-18"
```

## Create Customer
```bash
curl -X POST https://connect.squareup.com/v2/customers \
  -H "Authorization: Bearer $SQUARE_ACCESS_TOKEN" \
  -H "Square-Version: 2024-01-18" \
  -H "Content-Type: application/json" \
  -d '{
    "given_name": "John",
    "family_name": "Doe",
    "email_address": "john@example.com"
  }'
```

## Common Traps

- Amount in smallest currency unit (cents)
- Square-Version header recommended
- idempotency_key required for payments
- Sandbox uses different URL

## Official Docs
https://developer.squareup.com/reference/square
# Plaid

## Base URL
```
# Sandbox
https://sandbox.plaid.com

# Production
https://production.plaid.com
```

## Authentication
```bash
curl https://sandbox.plaid.com/accounts/get \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$PLAID_CLIENT_ID",
    "secret": "$PLAID_SECRET",
    "access_token": "$ACCESS_TOKEN"
  }'
```

## Link Token (start flow)
```bash
curl -X POST https://sandbox.plaid.com/link/token/create \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$PLAID_CLIENT_ID",
    "secret": "$PLAID_SECRET",
    "user": {"client_user_id": "user123"},
    "client_name": "My App",
    "products": ["transactions"],
    "country_codes": ["US"],
    "language": "en"
  }'
```

## Get Transactions
```bash
curl -X POST https://sandbox.plaid.com/transactions/get \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$PLAID_CLIENT_ID",
    "secret": "$PLAID_SECRET",
    "access_token": "$ACCESS_TOKEN",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

## Get Accounts
```bash
curl -X POST https://sandbox.plaid.com/accounts/get \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "$PLAID_CLIENT_ID",
    "secret": "$PLAID_SECRET",
    "access_token": "$ACCESS_TOKEN"
  }'
```

## Common Traps

- All requests are POST with JSON body
- client_id + secret in body, not headers
- Link flow required to get access_token
- Sandbox has test credentials
- Transactions may take 24h to sync

## Official Docs
https://plaid.com/docs/api/
# Chargebee

Subscription billing and revenue management platform.

## Base URL
```
https://{site}.chargebee.com/api/v2
```

Replace `{site}` with your Chargebee site name.

## Authentication
HTTP Basic Auth. API key as username, password empty.

```bash
curl -X GET "https://your-site.chargebee.com/api/v2/subscriptions" \
  -u "YOUR_API_KEY:"
```

## Core Endpoints

### List Subscriptions
```bash
curl -X GET "https://your-site.chargebee.com/api/v2/subscriptions" \
  -u "YOUR_API_KEY:"
```

### Create Subscription
```bash
curl -X POST "https://your-site.chargebee.com/api/v2/subscriptions" \
  -u "YOUR_API_KEY:" \
  -d "plan_id=basic-plan" \
  -d "customer[email]=john@example.com"
```

### Retrieve Customer
```bash
curl -X GET "https://your-site.chargebee.com/api/v2/customers/{customer_id}" \
  -u "YOUR_API_KEY:"
```

### Create Invoice
```bash
curl -X POST "https://your-site.chargebee.com/api/v2/invoices" \
  -u "YOUR_API_KEY:" \
  -d "customer_id=cust_xxx" \
  -d "charges[amount][0]=1000" \
  -d "charges[description][0]=Consulting"
```

## Rate Limits
- Varies by plan
- 150 requests/minute on Growth plan
- Headers indicate remaining quota
- 429 response when exceeded

## Gotchas
- Test site and live site have different API keys
- Request format is form-encoded, not JSON
- Response is always JSON
- Site name is part of the URL, not a parameter
- Undocumented attributes may appear in responses (ignore them)
- Use Time Machine feature for testing time-based scenarios

## Links
- [Docs](https://apidocs.chargebee.com/docs/api)
- [API Changelog](https://www.chargebee.com/help/api-updates/)
- [Client Libraries](https://apidocs.chargebee.com/docs/api/getting-started#client_library)
# Paddle

Payments and subscriptions platform (merchant of record).

## Base URL
```
https://api.paddle.com
```

Sandbox: `https://sandbox-api.paddle.com`

## Authentication
Bearer token with API key. Keys are 69 characters, prefixed with `pdl_`.

```bash
curl -X GET "https://api.paddle.com/products" \
  -H "Authorization: Bearer pdl_live_apikey_xxxxx"
```

## Core Endpoints

### List Products
```bash
curl -X GET "https://api.paddle.com/products" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Create Subscription
```bash
curl -X POST "https://api.paddle.com/subscriptions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "ctm_xxx",
    "items": [{"price_id": "pri_xxx", "quantity": 1}]
  }'
```

### Get Transaction
```bash
curl -X GET "https://api.paddle.com/transactions/{transaction_id}" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Create Price
```bash
curl -X POST "https://api.paddle.com/prices" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "pro_xxx",
    "description": "Monthly",
    "unit_price": {"amount": "999", "currency_code": "USD"},
    "billing_cycle": {"interval": "month", "frequency": 1}
  }'
```

## Rate Limits
- Not publicly documented
- Use exponential backoff on 429 errors

## Gotchas
- API version specified via header, not URL path
- Sandbox keys contain `sdbx_`, live keys contain `live_`
- Paddle handles tax calculation and remittance (merchant of record)
- Webhook signatures use SHA256 HMAC
- Amounts in responses are strings, not numbers
- All requests must be over HTTPS

## Links
- [Docs](https://developer.paddle.com/api-reference/overview)
- [Authentication](https://developer.paddle.com/api-reference/about/authentication)
- [Postman Collection](https://bit.ly/paddlehq-postman)
# Lemon Squeezy

Digital products and subscriptions platform (merchant of record).

## Base URL
```
https://api.lemonsqueezy.com/v1
```

## Authentication
Bearer token with API key. Create keys at Settings > API.

```bash
curl -X GET "https://api.lemonsqueezy.com/v1/users/me" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: application/vnd.api+json"
```

## Core Endpoints

### Get Current User
```bash
curl -X GET "https://api.lemonsqueezy.com/v1/users/me" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: application/vnd.api+json"
```

### List Products
```bash
curl -X GET "https://api.lemonsqueezy.com/v1/products" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: application/vnd.api+json"
```

### List Orders
```bash
curl -X GET "https://api.lemonsqueezy.com/v1/orders" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: application/vnd.api+json"
```

### Create Checkout
```bash
curl -X POST "https://api.lemonsqueezy.com/v1/checkouts" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Accept: application/vnd.api+json" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "checkouts",
      "attributes": {"custom_price": 999},
      "relationships": {
        "store": {"data": {"type": "stores", "id": "1"}},
        "variant": {"data": {"type": "variants", "id": "1"}}
      }
    }
  }'
```

## Rate Limits
- 300 requests per minute
- Headers: `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`
- 429 Too Many Requests when exceeded

## Gotchas
- Uses JSON:API format (requires `Accept: application/vnd.api+json`)
- Test mode uses separate API keys
- Lemon Squeezy is merchant of record (handles taxes)
- Webhook payloads are signed with HMAC SHA256
- Pagination uses cursor-based approach
- Related resources fetched via `include` parameter

## Links
- [Docs](https://docs.lemonsqueezy.com/api)
- [JavaScript SDK](https://github.com/lmsqueezy/lemonsqueezy.js)
- [Laravel SDK](https://github.com/lmsqueezy/laravel)
# Recurly

Subscription billing and recurring revenue management.

## Base URL
```
https://v3.recurly.com
```

## Authentication
HTTP Basic Auth. API key as username, password empty.

```bash
curl -X GET "https://v3.recurly.com/accounts" \
  -H "Accept: application/vnd.recurly.v2021-02-25" \
  -u "YOUR_API_KEY:"
```

## Core Endpoints

### List Accounts
```bash
curl -X GET "https://v3.recurly.com/accounts" \
  -H "Accept: application/vnd.recurly.v2021-02-25" \
  -u "YOUR_API_KEY:"
```

### Create Subscription
```bash
curl -X POST "https://v3.recurly.com/subscriptions" \
  -H "Accept: application/vnd.recurly.v2021-02-25" \
  -H "Content-Type: application/json" \
  -u "YOUR_API_KEY:" \
  -d '{
    "plan_code": "basic",
    "account": {
      "code": "account-123",
      "email": "user@example.com"
    }
  }'
```

### Get Subscription
```bash
curl -X GET "https://v3.recurly.com/subscriptions/{subscription_id}" \
  -H "Accept: application/vnd.recurly.v2021-02-25" \
  -u "YOUR_API_KEY:"
```

### List Invoices
```bash
curl -X GET "https://v3.recurly.com/invoices" \
  -H "Accept: application/vnd.recurly.v2021-02-25" \
  -u "YOUR_API_KEY:"
```

## Rate Limits
- 2000 requests per minute (varies by plan)
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- 429 response when exceeded

## Gotchas
- API version specified in Accept header, not URL
- Uses API v3 (v2 deprecated)
- Account `code` is your identifier, `id` is Recurly's
- Sandbox site uses same API, different credentials
- Webhooks require signature verification
- Pagination uses cursor-based `cursor` parameter

## Links
- [Docs](https://recurly.com/developers/api/)
- [API v3 Reference](https://recurly.com/developers/api/v2021-02-25/)
- [Client Libraries](https://recurly.com/developers/api/#client-libraries)
# Wise

International money transfers and multi-currency accounts API.

## Base URL
```
https://api.wise.com
```

Sandbox: `https://api.wise-sandbox.com`

## Authentication
OAuth 2.0 with API tokens. Use Bearer authentication.

```bash
curl -X GET "https://api.wise.com/v1/profiles" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

## Core Endpoints

### Get Profiles
```bash
curl -X GET "https://api.wise.com/v1/profiles" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Create Quote
```bash
curl -X POST "https://api.wise.com/v3/profiles/{profileId}/quotes" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "EUR",
    "sourceAmount": 1000
  }'
```

### Create Transfer
```bash
curl -X POST "https://api.wise.com/v1/transfers" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targetAccount": 123456,
    "quoteUuid": "quote-uuid-here",
    "customerTransactionId": "unique-id"
  }'
```

### Get Exchange Rate
```bash
curl -X GET "https://api.wise.com/v1/rates?source=GBP&target=EUR" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

## Rate Limits
- No published hard limits
- Recommended: max 1 request/second per endpoint
- Contact Wise for high-volume use cases

## Gotchas
- Sandbox and production have separate API tokens
- Quotes expire after 30 minutes
- `customerTransactionId` must be unique per transfer (idempotency key)
- Some endpoints require Strong Customer Authentication (SCA)
- Profile ID required for most operations (personal vs business)

## Links
- [Docs](https://docs.wise.com/api-reference)
- [Guides](https://docs.wise.com/guides)
- [Sandbox](https://sandbox.transferwise.tech)
# Coinbase

Cryptocurrency trading, transfers, and account management API.

## Base URL
```
https://api.coinbase.com/v2
```

Advanced Trade API: `https://api.coinbase.com/api/v3/brokerage`

## Authentication
OAuth 2.0 or API Key with HMAC signature.

```bash
# API Key authentication
curl -X GET "https://api.coinbase.com/v2/accounts" \
  -H "CB-ACCESS-KEY: YOUR_API_KEY" \
  -H "CB-ACCESS-SIGN: HMAC_SIGNATURE" \
  -H "CB-ACCESS-TIMESTAMP: UNIX_TIMESTAMP" \
  -H "CB-VERSION: 2024-01-01"
```

## Core Endpoints

### List Accounts
```bash
curl -X GET "https://api.coinbase.com/v2/accounts" \
  -H "CB-ACCESS-KEY: YOUR_API_KEY" \
  -H "CB-ACCESS-SIGN: HMAC_SIGNATURE" \
  -H "CB-ACCESS-TIMESTAMP: UNIX_TIMESTAMP"
```

### Get Spot Price
```bash
curl -X GET "https://api.coinbase.com/v2/prices/BTC-USD/spot"
```

### Send Crypto
```bash
curl -X POST "https://api.coinbase.com/v2/accounts/{account_id}/transactions" \
  -H "CB-ACCESS-KEY: YOUR_API_KEY" \
  -H "CB-ACCESS-SIGN: HMAC_SIGNATURE" \
  -H "CB-ACCESS-TIMESTAMP: UNIX_TIMESTAMP" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "send",
    "to": "bitcoin_address",
    "amount": "0.01",
    "currency": "BTC"
  }'
```

### Create Order (Advanced Trade)
```bash
curl -X POST "https://api.coinbase.com/api/v3/brokerage/orders" \
  -H "CB-ACCESS-KEY: YOUR_API_KEY" \
  -H "CB-ACCESS-SIGN: HMAC_SIGNATURE" \
  -H "CB-ACCESS-TIMESTAMP: UNIX_TIMESTAMP" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "BTC-USD",
    "side": "buy",
    "order_configuration": {
      "market_market_ioc": {"quote_size": "100"}
    }
  }'
```

## Rate Limits
- Public endpoints: 10 requests/second
- Private endpoints: 5 requests/second
- 429 response when exceeded

## Gotchas
- HMAC signature requires exact timestamp matching
- `CB-VERSION` header specifies API version date
- Advanced Trade API uses different base path
- OAuth scopes limit what operations are permitted
- Send operations may require 2FA confirmation
- Price endpoints are public (no auth required)

## Links
- [Docs](https://docs.cdp.coinbase.com/coinbase-app/introduction/welcome)
- [Advanced Trade](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview)
- [Authentication](https://docs.cdp.coinbase.com/coinbase-app/sign-in-with-coinbase/auth-overview)
# Binance

Cryptocurrency exchange and trading API.

## Base URL
```
https://api.binance.com
```

Alternative endpoints: `api1.binance.com`, `api2.binance.com`, `api3.binance.com`, `api4.binance.com`

## Authentication
HMAC SHA256 signature for authenticated endpoints.

```bash
# Public endpoint (no auth)
curl -X GET "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

# Authenticated endpoint
curl -X GET "https://api.binance.com/api/v3/account?timestamp=TIMESTAMP&signature=HMAC_SIGNATURE" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
```

## Core Endpoints

### Get Ticker Price
```bash
curl -X GET "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
```

### Get Account Info
```bash
curl -X GET "https://api.binance.com/api/v3/account?timestamp=TIMESTAMP&signature=SIGNATURE" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
```

### Create Order
```bash
curl -X POST "https://api.binance.com/api/v3/order" \
  -H "X-MBX-APIKEY: YOUR_API_KEY" \
  -d "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&timestamp=TIMESTAMP&signature=SIGNATURE"
```

### Get Klines (Candlestick)
```bash
curl -X GET "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100"
```

## Rate Limits
- Weight-based system (varies by endpoint)
- 1200 request weight/minute (IP limit)
- 10 orders/second, 100,000 orders/day
- Headers: `X-MBX-USED-WEIGHT-*`

## Gotchas
- Signature includes ALL query parameters
- `timestamp` must be within 5000ms of server time
- Use `recvWindow` to adjust timestamp tolerance
- Supports HMAC, RSA, and Ed25519 key types
- API timeout is 10 seconds
- Alternative endpoints (api1-4) have better performance but less stability
- Avoid SQL keywords in requests (WAF blocks them)

## Links
- [Docs](https://developers.binance.com/docs/binance-spot-api-docs/rest-api)
- [API FAQ](https://developers.binance.com/docs/faqs)
- [Test Network](https://testnet.binance.vision)
# Alpaca

Stock and crypto trading API for algorithmic trading.

## Base URL
```
https://api.alpaca.markets
```

Paper trading: `https://paper-api.alpaca.markets`
Market data: `https://data.alpaca.markets`

## Authentication
API Key and Secret Key via headers.

```bash
curl -X GET "https://api.alpaca.markets/v2/account" \
  -H "APCA-API-KEY-ID: YOUR_API_KEY" \
  -H "APCA-API-SECRET-KEY: YOUR_SECRET_KEY"
```

## Core Endpoints

### Get Account
```bash
curl -X GET "https://api.alpaca.markets/v2/account" \
  -H "APCA-API-KEY-ID: YOUR_API_KEY" \
  -H "APCA-API-SECRET-KEY: YOUR_SECRET_KEY"
```

### Create Order
```bash
curl -X POST "https://api.alpaca.markets/v2/orders" \
  -H "APCA-API-KEY-ID: YOUR_API_KEY" \
  -H "APCA-API-SECRET-KEY: YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "qty": "1",
    "side": "buy",
    "type": "market",
    "time_in_force": "day"
  }'
```

### List Positions
```bash
curl -X GET "https://api.alpaca.markets/v2/positions" \
  -H "APCA-API-KEY-ID: YOUR_API_KEY" \
  -H "APCA-API-SECRET-KEY: YOUR_SECRET_KEY"
```

### Get Bars (Market Data)
```bash
curl -X GET "https://data.alpaca.markets/v2/stocks/AAPL/bars?timeframe=1Day&start=2024-01-01" \
  -H "APCA-API-KEY-ID: YOUR_API_KEY" \
  -H "APCA-API-SECRET-KEY: YOUR_SECRET_KEY"
```

## Rate Limits
- 200 requests/minute for trading API
- Market data limits vary by subscription
- Paper and live accounts share limits

## Gotchas
- Paper trading uses different base URL
- Market data requires separate subscription for real-time
- Crypto and stocks use different endpoints
- Market hours: 9:30 AM - 4:00 PM ET (extended hours available)
- Fractional shares supported
- PDT rules apply for accounts under $25k

## Links
- [Docs](https://docs.alpaca.markets)
- [Trading API](https://docs.alpaca.markets/docs/getting-started-with-trading-api)
- [Market Data](https://docs.alpaca.markets/docs/getting-started-with-alpaca-market-data)
- [API Status](https://status.alpaca.markets)
# Polygon

Financial market data API for stocks, options, forex, and crypto.

## Base URL
```
https://api.polygon.io
```

## Authentication
API key as query parameter or header.

```bash
curl -X GET "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-31?apiKey=YOUR_API_KEY"

# Or via header
curl -X GET "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-31" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Core Endpoints

### Aggregates (Bars)
```bash
curl -X GET "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-31?apiKey=YOUR_API_KEY"
```

### Last Trade
```bash
curl -X GET "https://api.polygon.io/v2/last/trade/AAPL?apiKey=YOUR_API_KEY"
```

### Ticker Details
```bash
curl -X GET "https://api.polygon.io/v3/reference/tickers/AAPL?apiKey=YOUR_API_KEY"
```

### Snapshot (All Tickers)
```bash
curl -X GET "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?apiKey=YOUR_API_KEY"
```

### Options Chain
```bash
curl -X GET "https://api.polygon.io/v3/snapshot/options/AAPL?apiKey=YOUR_API_KEY"
```

## Rate Limits
- Free: 5 requests/minute
- Starter: 5 requests/minute, unlimited calls
- Developer: Unlimited
- Headers: `X-RateLimit-*`

## Gotchas
- Free tier has significant limitations (5 req/min, delayed data)
- Real-time data requires paid subscription
- Date format: `YYYY-MM-DD`
- Adjusted vs unadjusted data parameter matters for splits/dividends
- Timestamps in results are Unix milliseconds
- Crypto uses different endpoint paths
- WebSocket available for real-time streaming

## Links
- [Docs](https://polygon.io/docs/stocks)
- [API Reference](https://polygon.io/docs/stocks/getting-started)
- [WebSocket](https://polygon.io/docs/stocks/ws_getting-started)

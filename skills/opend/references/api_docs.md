# Futu OpenAPI References (verified February 27, 2026)

## Core Docs
- OpenAPI portal: https://www.futunn.com/OpenAPI
- API docs home: https://openapi.futunn.com/futu-api-doc/en/
- Support index: https://support.futunn.com/en/topic462/

## Quote API Used by This Skill
- Get Market Snapshot: https://openapi.futunn.com/futu-api-doc/en/quote/get-market-snapshot.html

Current limits used in this skill:
- Up to 60 snapshot requests per 30 seconds.
- Up to 400 codes per request.
- HK securities snapshots can be limited to 20 per request under specific BMP entitlements.

## Trade API Used by This Skill
- Trade overview: https://openapi.futunn.com/futu-api-doc/en/trade/overview.html
- OpenSecTradeContext usage note: https://openapi.futunn.com/futu-api-doc/en/qa/trade.html
- Get account list: https://openapi.futunn.com/futu-api-doc/en/trade/get-acc-list.html
- Unlock trade: https://openapi.futunn.com/futu-api-doc/en/trade/unlock.html
- Place order: https://openapi.futunn.com/futu-api-doc/en/trade/place-order.html
- Modify/cancel order: https://openapi.futunn.com/futu-api-doc/en/trade/modify-order.html
- Get positions: https://openapi.futunn.com/futu-api-doc/en/trade/get-position-list.html

Current limits used in this skill:
- `unlock_trade`: max 10 requests per 30 seconds per user.
- `place_order`: max 15 requests per 30 seconds per account, minimum 0.02s between requests.
- `modify_order` (cancel-order path): max 20 requests per 30 seconds per account, minimum 0.04s between requests.

## Behavior Notes Applied in Scripts
- Use `OpenSecTradeContext` for securities and options.
- Skip unlock for `SIMULATE` accounts.
- Resolve account via `get_acc_list()` unless an `acc_id` is explicitly provided.
- Keep OpenD host/port configurable (`--host`, `--port`, `OPEND_HOST`, `OPEND_PORT`).

### `account_transfer`

⚠️ Transfer funds between master and subaccounts using IIBANs. Must use master account API key. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to transfer","type":"string"},"asset":{"description":"Asset to transfer (e.g. XBT, ETH)","type":"string"},"from":{"description":"IIBAN of the source account","type":"string"},"to":{"description":"IIBAN of the destination account","type":"string"}},"required":["asset","amount","from","to"],"title":"AccountTransferParams","type":"object"}
```

### `add_export`

Request an export of trades or ledger data. Returns a report ID. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"description":{"description":"Human-readable description for the export","type":"string"},"endtm":{"description":"End time as Unix timestamp","format":"uint64","minimum":0,"nullable":true,"type":"integer"},"format":{"description":"File format: CSV or TSV (default: CSV)","nullable":true,"type":"string"},"report":{"description":"Type of data to export: trades or ledgers","type":"string"},"starttm":{"description":"Start time as Unix timestamp","format":"uint64","minimum":0,"nullable":true,"type":"integer"}},"required":["report","description"],"title":"AddExportParams","type":"object"}
```

### `add_order_batch`

⚠️ REAL MONEY — Place 2-15 orders atomically for a single pair. All orders validated before submission. Use validate=true first. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"deadline":{"description":"RFC3339 deadline after which to reject the batch (optional)","nullable":true,"type":"string"},"orders":{"description":"JSON array of order objects (2-15 orders). Each order needs: ordertype, type (buy/sell), volume. Optional: price, price2, leverage, oflags, timeinforce, starttm, expiretm, cl_ord_id. Example: [{\"ordertype\":\"limit\",\"type\":\"buy\",\"volume\":\"0.01\",\"price\":\"30000\"},{\"ordertype\":\"limit\",\"type\":\"sell\",\"volume\":\"0.01\",\"price\":\"35000\"}]","type":"string"},"pair":{"description":"Trading pair for all orders (e.g. XBTUSD)","type":"string"},"validate":{"description":"If true, validate without placing. Recommended for first test.","nullable":true,"type":"boolean"}},"required":["pair","orders"],"title":"AddOrderBatchParams","type":"object"}
```

### `amend_order`

Amend an open order in-place (preserves queue priority). Requires txid or cl_ord_id. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cl_ord_id":{"description":"Client order ID to amend (mutually exclusive with txid)","nullable":true,"type":"string"},"limit_price":{"description":"New limit price (for limit/iceberg orders)","nullable":true,"type":"string"},"order_qty":{"description":"New order quantity in base asset","nullable":true,"type":"string"},"pair":{"description":"Pair (required for xstock pairs)","nullable":true,"type":"string"},"post_only":{"description":"If true, reject if order cannot be posted passively","nullable":true,"type":"boolean"},"trigger_price":{"description":"New trigger price (for stop/take-profit orders)","nullable":true,"type":"string"},"txid":{"description":"Kraken transaction ID of the order to amend (mutually exclusive with cl_ord_id)","nullable":true,"type":"string"}},"title":"AmendOrderParams","type":"object"}
```

### `cancel_all_after`

Dead man's switch: cancel all orders after timeout seconds. Set timeout=0 to disable. Call every 15-30s with timeout=60 for protection. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"timeout":{"description":"Timeout in seconds (0 to disable). All orders cancelled after this. Use 60s with 15-30s refresh.","format":"uint32","minimum":0,"type":"integer"}},"required":["timeout"],"title":"CancelAllAfterParams","type":"object"}
```

### `cancel_all_orders`

⚠️ Cancel ALL open orders. This affects every open order on the account. Requires API keys.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `cancel_order`

Cancel an open order by transaction ID, userref, or cl_ord_id. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"txid":{"description":"Transaction ID, user reference, or client order ID of the order to cancel","type":"string"}},"required":["txid"],"title":"CancelOrderParams","type":"object"}
```

### `cancel_order_batch`

Cancel up to 50 orders by txid, userref, or cl_ord_id in a single request. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"orders":{"description":"JSON array of order identifiers (max 50). Each entry has one of: txid, userref, or cl_ord_id. Example: [{\"txid\":\"OABC12-...\"}, {\"userref\":12345}]","type":"string"}},"required":["orders"],"title":"CancelOrderBatchParams","type":"object"}
```

### `cancel_withdraw`

Cancel a pending withdrawal before it is processed. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Asset of the withdrawal to cancel (e.g. XBT)","type":"string"},"refid":{"description":"Reference ID of the withdrawal to cancel","type":"string"}},"required":["asset","refid"],"title":"CancelWithdrawParams","type":"object"}
```

### `create_subaccount`

Create a trading subaccount. Must be called with master account API key. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"email":{"description":"Email address for the new subaccount","type":"string"},"username":{"description":"Username for the new subaccount","type":"string"}},"required":["username","email"],"title":"CreateSubaccountParams","type":"object"}
```

### `earn_allocate`

⚠️ Allocate funds to an earn strategy. Check strategy lock_type first — bonded strategies have lock periods. This is asynchronous; poll earn_allocate_status to confirm. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to allocate (⚠️ may have lock period — check strategy lock_type first)","type":"string"},"strategy_id":{"description":"Earn strategy ID (from earn_strategies)","type":"string"}},"required":["strategy_id","amount"],"title":"EarnAllocateParams","type":"object"}
```

### `earn_allocate_status`

Check status of the last allocation request for a strategy. Returns pending=true if in progress. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"strategy_id":{"description":"Earn strategy ID to check operation status for","type":"string"}},"required":["strategy_id"],"title":"EarnStatusParams","type":"object"}
```

### `earn_allocations`

List all current earn allocations including bonding/unbonding status. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"ascending":{"description":"If true, sort ascending","nullable":true,"type":"boolean"},"converted_asset":{"description":"Currency to convert allocation values to (default: USD)","nullable":true,"type":"string"},"hide_zero":{"description":"If true, hide strategies with zero balance","nullable":true,"type":"boolean"}},"title":"EarnAllocationsParams","type":"object"}
```

### `earn_deallocate`

⚠️ Deallocate funds from an earn strategy. Bonded strategies have unbonding periods before funds are available. Asynchronous — poll earn_deallocate_status to confirm. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to deallocate (⚠️ bonded strategies have unbonding period)","type":"string"},"strategy_id":{"description":"Earn strategy ID (from earn_strategies)","type":"string"}},"required":["strategy_id","amount"],"title":"EarnDeallocateParams","type":"object"}
```

### `earn_deallocate_status`

Check status of the last deallocation request for a strategy. Returns pending=true if in progress. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"strategy_id":{"description":"Earn strategy ID to check operation status for","type":"string"}},"required":["strategy_id"],"title":"EarnStatusParams","type":"object"}
```

### `earn_strategies`

List available earn/staking strategies with APR, lock types, and allocation limits. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"ascending":{"description":"If true, sort ascending; false (default) for descending","nullable":true,"type":"boolean"},"asset":{"description":"Filter by asset name (e.g. DOT, ETH)","nullable":true,"type":"string"},"cursor":{"description":"Pagination cursor from previous response","nullable":true,"type":"string"},"limit":{"description":"Number of items per page","format":"uint32","minimum":0,"nullable":true,"type":"integer"}},"title":"EarnStrategiesParams","type":"object"}
```

### `edit_order`

Edit an open order (cancels original, creates new with new txid). Consider amend_order for in-place edits. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"oflags":{"description":"Comma-delimited order flags (e.g. 'post')","nullable":true,"type":"string"},"pair":{"description":"Trading pair (e.g. XBTUSD)","type":"string"},"price":{"description":"New limit/trigger price","nullable":true,"type":"string"},"price2":{"description":"New secondary price (for stop-loss-limit etc.)","nullable":true,"type":"string"},"txid":{"description":"Transaction ID of the order to edit","type":"string"},"validate":{"description":"If true, validate only without executing","nullable":true,"type":"boolean"},"volume":{"description":"New order volume","nullable":true,"type":"string"}},"required":["txid","pair"],"title":"EditOrderParams","type":"object"}
```

### `export_status`

Get status of requested data exports (Queued/Processing/Processed). Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"report":{"description":"Type of report to check: trades or ledgers","type":"string"}},"required":["report"],"title":"ExportStatusParams","type":"object"}
```

### `futures_accounts`

Get Kraken Futures account balances, margin requirements, margin trigger estimates, and auxiliary info for all cash and margin accounts. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_batch_order`

⚠️ REAL MONEY — Execute a batch of Kraken Futures order operations (send/cancel/edit) in a single request. Pass a JSON array of instructions. ALWAYS confirm with user before submitting. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"instructions":{"description":"JSON array of batch instructions. Each entry has an \"order\" field: \"send\", \"cancel\", or \"edit\", plus the relevant fields for that action. Example: [{\"order\":\"send\",\"orderType\":\"lmt\",\"symbol\":\"PF_XBTUSD\",\"side\":\"buy\",\"size\":1,\"limitPrice\":50000},{\"order\":\"cancel\",\"order_id\":\"abc123\"}]","type":"string"}},"required":["instructions"],"title":"BatchOrderParams","type":"object"}
```

### `futures_cancel_all`

⚠️ Cancel all open Kraken Futures orders, optionally filtered to a single symbol. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbol":{"description":"Cancel only orders for this symbol (optional; cancels all if omitted)","nullable":true,"type":"string"}},"title":"CancelAllParams","type":"object"}
```

### `futures_cancel_order`

Cancel an open Kraken Futures order by order_id or client_order_id. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"client_order_id":{"description":"Client order ID to cancel (mutually exclusive with order_id)","nullable":true,"type":"string"},"order_id":{"description":"Order ID to cancel (mutually exclusive with client_order_id)","nullable":true,"type":"string"}},"title":"CancelOrderParams","type":"object"}
```

### `futures_edit_order`

Edit an open Kraken Futures order (size and/or price). Provide order_id or client_order_id to identify the order. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"client_order_id":{"description":"Client order ID to edit (mutually exclusive with order_id)","nullable":true,"type":"string"},"limit_price":{"description":"New limit price","nullable":true,"type":"string"},"order_id":{"description":"Order ID to edit (mutually exclusive with client_order_id)","nullable":true,"type":"string"},"size":{"description":"New order size in contracts","nullable":true,"type":"string"},"stop_price":{"description":"New stop/trigger price","nullable":true,"type":"string"}},"title":"EditOrderParams","type":"object"}
```

### `futures_fee_schedules`

List all Kraken Futures fee schedules including maker/taker rates by volume tier. Public — no auth required.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_fills`

Get Kraken Futures trade fill history. Optionally filter to fills after a given time. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"last_fill_time":{"description":"ISO8601 timestamp; return fills after this time (optional)","nullable":true,"type":"string"}},"title":"FillsParams","type":"object"}
```

### `futures_historical_funding_rates`

Get historical funding rates for a Kraken Futures perpetual swap symbol. Public — no auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbol":{"description":"Futures symbol to filter by (e.g. PF_XBTUSD). Required.","type":"string"}},"required":["symbol"],"title":"FundingRatesParams","type":"object"}
```

### `futures_instrument_status`

Get the trading status of a specific Kraken Futures instrument (tradeable, post-only, suspended, etc.). Public — no auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"instrument":{"description":"Instrument symbol (e.g. PF_XBTUSD, PI_ETHUSD)","type":"string"}},"required":["instrument"],"title":"InstrumentStatusParams","type":"object"}
```

### `futures_instruments`

List all available Kraken Futures instruments (perpetual swaps, fixed-maturity futures, flex futures) with contract specs, margin schedules, and trading parameters. Public — no auth required.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_leverage_setting`

Get or set Kraken Futures leverage. Omit max_leverage to read the current setting. Provide symbol + max_leverage to update it. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"max_leverage":{"description":"Maximum leverage to set (e.g. '10'). If provided, updates leverage (PUT). If absent, retrieves current setting (GET).","nullable":true,"type":"string"},"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD). Required when setting leverage.","nullable":true,"type":"string"}},"title":"LeverageSettingParams","type":"object"}
```

### `futures_open_orders`

List all open Kraken Futures orders on the account. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_open_positions`

List all open Kraken Futures positions on the account. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_order_status`

Get the status of one or more Kraken Futures orders by ID. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"order_ids":{"description":"Comma-separated list of order IDs to query (e.g. 'abc123,def456')","type":"string"}},"required":["order_ids"],"title":"OrderStatusParams","type":"object"}
```

### `futures_orderbook`

Get the top-of-book bids and asks for a Kraken Futures symbol. Public — no auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD, PI_ETHUSD)","type":"string"}},"required":["symbol"],"title":"OrderBookParams","type":"object"}
```

### `futures_pnl_preference`

Get or set the Kraken Futures PnL currency preference for a symbol. Omit pnl_preference to read the current setting. Provide symbol + pnl_preference to update it. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"pnl_preference":{"description":"PnL currency preference (e.g. 'USD', 'BTC'). If provided, updates preference (PUT). If absent, retrieves current preference (GET).","nullable":true,"type":"string"},"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD). Required when setting preference.","nullable":true,"type":"string"}},"title":"PnlPreferenceParams","type":"object"}
```

### `futures_send_order`

⚠️ REAL MONEY — Place a new Kraken Futures order. Supported order types: lmt, mkt, stp, take_profit, trailing_stop. ALWAYS confirm with user before placing. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"client_order_id":{"description":"Client order ID for tracking (optional)","nullable":true,"type":"string"},"limit_price":{"description":"Limit price (required for lmt orders)","nullable":true,"type":"string"},"order_type":{"description":"Order type: 'lmt' (limit), 'mkt' (market), 'stp' (stop), 'take_profit', 'trailing_stop'","type":"string"},"reduce_only":{"description":"If true, only reduces existing position (optional)","nullable":true,"type":"boolean"},"side":{"description":"Order side: 'buy' or 'sell'","type":"string"},"size":{"description":"Order size in contracts","type":"string"},"stop_price":{"description":"Stop/trigger price (for stop and take_profit orders)","nullable":true,"type":"string"},"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD, PI_ETHUSD)","type":"string"}},"required":["order_type","symbol","side","size"],"title":"SendOrderParams","type":"object"}
```

### `futures_ticker`

Get ticker data for a single Kraken Futures symbol: last price, bid/ask, 24h volume, open interest, funding rate. Public — no auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD, PI_ETHUSD)","type":"string"}},"required":["symbol"],"title":"TickerParams","type":"object"}
```

### `futures_tickers`

Get ticker data for all Kraken Futures instruments and indices: last price, bid/ask, 24h volume, open interest, funding rate, mark price. Public — no auth required.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `futures_trade_history`

Get recent public trade history for a Kraken Futures symbol. Optionally filter to trades after a given timestamp. Public — no auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"last_time":{"description":"ISO8601 timestamp; return only trades after this time (optional)","nullable":true,"type":"string"},"symbol":{"description":"Futures symbol (e.g. PF_XBTUSD, PI_ETHUSD)","type":"string"}},"required":["symbol"],"title":"TradeHistoryParams","type":"object"}
```

### `futures_transfer`

⚠️ Transfer funds between Kraken Futures accounts (e.g. between cash collateral and futures wallet). Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to transfer","type":"string"},"from_account":{"description":"Source account (e.g. 'Futures Wallet', 'Cash/Collateral Account', or sub-account name)","type":"string"},"to_account":{"description":"Destination account (same format as from_account)","type":"string"},"unit":{"description":"Currency/asset to transfer (e.g. 'USD', 'BTC', 'ETH')","type":"string"}},"required":["from_account","to_account","unit","amount"],"title":"TransferParams","type":"object"}
```

### `futures_transfers`

Get Kraken Futures transfer history between accounts. Optionally filter to transfers after a given time. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"last_transfer_time":{"description":"ISO8601 timestamp; return transfers after this time (optional)","nullable":true,"type":"string"}},"title":"TransfersParams","type":"object"}
```

### `futures_withdrawal`

⚠️ REAL MONEY — Withdraw funds from a Kraken Futures account to an external address. CONFIRM with user before executing. Requires KRAKEN_FUTURES_KEY and KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to withdraw","type":"string"},"currency":{"description":"Currency to withdraw (e.g. 'USD', 'BTC')","type":"string"},"target_address":{"description":"Withdrawal destination address","type":"string"}},"required":["target_address","currency","amount"],"title":"WithdrawalParams","type":"object"}
```

### `get_asset_pairs`

Get tradable asset pairs with fees, leverage, margin, and precision info. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"info":{"description":"Info to retrieve: info, leverage, fees, margin (default: info)","nullable":true,"type":"string"},"pair":{"description":"Comma-delimited list of pairs (e.g. XBTUSD,ETHUSD). Omit for all.","nullable":true,"type":"string"}},"title":"GetAssetPairsParams","type":"object"}
```

### `get_assets`

Get info about tradable assets (decimals, altname, status). No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"aclass":{"description":"Asset class filter (default: currency)","nullable":true,"type":"string"},"asset":{"description":"Comma-delimited list of assets to filter (e.g. XBT,ETH). Omit for all.","nullable":true,"type":"string"}},"title":"GetAssetsParams","type":"object"}
```

### `get_balance`

Get all non-zero account balances. Requires KRAKEN_API_KEY and KRAKEN_API_SECRET env vars.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_closed_orders`

Get closed (filled/cancelled) orders. 50 per page, most recent first. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"closetime":{"description":"Time to use for filtering: open, close, both (default: both)","nullable":true,"type":"string"},"end":{"description":"End timestamp (Unix) for filtering","format":"uint64","minimum":0,"nullable":true,"type":"integer"},"ofs":{"description":"Result offset for pagination","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"start":{"description":"Start timestamp (Unix) for filtering","format":"uint64","minimum":0,"nullable":true,"type":"integer"},"trades":{"description":"Whether to include trades in results","nullable":true,"type":"boolean"}},"title":"GetClosedOrdersParams","type":"object"}
```

### `get_credit_lines`

Get account credit line details. Requires API keys.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_deposit_addresses`

Get or generate deposit addresses for an asset and method. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Asset to get deposit addresses for (e.g. XBT, ETH)","type":"string"},"method":{"description":"Name of the deposit method (from get_deposit_methods)","type":"string"},"new":{"description":"If true, generate a new deposit address","nullable":true,"type":"boolean"}},"required":["asset","method"],"title":"GetDepositAddressesParams","type":"object"}
```

### `get_deposit_methods`

Get available deposit methods for an asset. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Asset to get deposit methods for (e.g. XBT, ETH)","type":"string"}},"required":["asset"],"title":"GetDepositMethodsParams","type":"object"}
```

### `get_deposit_status`

Get status of recent deposits (sorted newest first). Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Filter by asset (optional)","nullable":true,"type":"string"},"cursor":{"description":"Pagination cursor (optional)","nullable":true,"type":"string"},"limit":{"description":"Max results per page (optional)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"method":{"description":"Filter by method (optional)","nullable":true,"type":"string"}},"title":"GetDepositStatusParams","type":"object"}
```

### `get_extended_balance`

Get extended account balances including credit and held amounts. Requires API keys.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_grouped_book`

Get grouped/aggregated order book depth for a trading pair. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"group":{"description":"Grouping/tick size for aggregated levels (optional)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"levels":{"description":"Max number of grouped levels per side (optional)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"pair":{"description":"Trading pair (e.g. BTC/USD)","type":"string"}},"required":["pair"],"title":"GetGroupedBookParams","type":"object"}
```

### `get_ledger`

Get ledger entries (trades, deposits, withdrawals, etc). 50 per page. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Comma-delimited list of assets to filter, or 'all' (default: all)","nullable":true,"type":"string"},"end":{"description":"End timestamp (Unix) for filtering","format":"uint64","minimum":0,"nullable":true,"type":"integer"},"ledger_type":{"description":"Ledger type: all, trade, deposit, withdrawal, transfer, margin, rollover, credit, settled, staking, dividend (default: all)","nullable":true,"type":"string"},"ofs":{"description":"Result offset for pagination","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"start":{"description":"Start timestamp (Unix) for filtering","format":"uint64","minimum":0,"nullable":true,"type":"integer"}},"title":"GetLedgerParams","type":"object"}
```

### `get_level3`

Get private Level-3 order book data (individual order IDs and timestamps). Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"depth":{"description":"Max number of levels per side (optional)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"pair":{"description":"Trading pair (e.g. XBTUSD, ETHUSD)","type":"string"}},"required":["pair"],"title":"GetLevel3Params","type":"object"}
```

### `get_ohlc`

Get OHLC candlestick data for a trading pair. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"interval":{"description":"Interval in minutes: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"pair":{"description":"Trading pair (e.g. XBTUSD, ETHUSD)","type":"string"},"since":{"description":"Return data since UNIX timestamp","format":"uint64","minimum":0,"nullable":true,"type":"integer"}},"required":["pair"],"title":"GetOhlcParams","type":"object"}
```

### `get_open_orders`

List all open orders. Requires API keys.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_open_positions`

Get open margin positions with cost, fee, P&L. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"docalcs":{"description":"Whether to include P&L calculations","nullable":true,"type":"boolean"},"txid":{"description":"Comma-delimited list of txids to filter (optional)","nullable":true,"type":"string"}},"title":"GetOpenPositionsParams","type":"object"}
```

### `get_order_amends`

Get amend audit trail for a specific order transaction ID. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"txid":{"description":"Transaction ID of the order to inspect amend history for","type":"string"}},"required":["txid"],"title":"GetOrderAmendsParams","type":"object"}
```

### `get_orderbook`

Get order book (asks/bids) for a trading pair. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"count":{"description":"Max number of asks/bids (1-500, default 10)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"pair":{"description":"Trading pair (e.g. XBTUSD, ETHUSD)","type":"string"}},"required":["pair"],"title":"GetOrderbookParams","type":"object"}
```

### `get_post_trade`

Get post-trade transparency data (spot trade prints) with optional symbol/time filters. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"count":{"description":"Maximum number of trades to return (1-1000)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"from_ts":{"description":"Return trades after this ISO-8601 timestamp","nullable":true,"type":"string"},"symbol":{"description":"Filter by symbol (e.g. BTC/USD)","nullable":true,"type":"string"},"to_ts":{"description":"Return trades before or at this ISO-8601 timestamp","nullable":true,"type":"string"}},"title":"GetPostTradeParams","type":"object"}
```

### `get_pre_trade`

Get pre-trade transparency data (top aggregated order book levels) for a symbol. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbol":{"description":"Trading symbol (e.g. BTC/USD)","type":"string"}},"required":["symbol"],"title":"GetPreTradeParams","type":"object"}
```

### `get_recent_trades`

Get recent trades for a trading pair (up to 1000). No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"count":{"description":"Number of trades to return (1-1000, default 1000)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"pair":{"description":"Trading pair (e.g. XBTUSD)","type":"string"},"since":{"description":"Return trades since this UNIX timestamp","nullable":true,"type":"string"}},"required":["pair"],"title":"GetRecentTradesParams","type":"object"}
```

### `get_server_time`

Get the Kraken server time (Unix timestamp and RFC1123). No auth required.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_spread`

Get recent bid/ask spreads (last ~200 entries) for a trading pair. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"pair":{"description":"Trading pair (e.g. XBTUSD)","type":"string"},"since":{"description":"Return spread data since this UNIX timestamp","format":"uint64","minimum":0,"nullable":true,"type":"integer"}},"required":["pair"],"title":"GetSpreadParams","type":"object"}
```

### `get_system_status`

Get current Kraken system status: online, maintenance, cancel_only, or post_only. No auth required.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `get_ticker`

Get current ticker for a trading pair: ask/bid price, last trade, 24h volume, high/low. No auth required.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"pair":{"description":"Trading pair (e.g. XBTUSD, ETHUSD, SOLUSD)","type":"string"}},"required":["pair"],"title":"GetTickerParams","type":"object"}
```

### `get_trade_balance`

Get collateral balances, margin valuations, and equity summary. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Base asset used to determine balance (default: ZUSD)","nullable":true,"type":"string"}},"title":"GetTradeBalanceParams","type":"object"}
```

### `get_trade_history`

Get recent executed trades with pair, price, volume, cost, fee. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"offset":{"description":"Result offset for pagination","format":"uint32","minimum":0,"nullable":true,"type":"integer"}},"title":"GetTradeHistoryParams","type":"object"}
```

### `get_trade_volume`

Get 30-day USD trading volume and fee schedule for a pair. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"pair":{"description":"Comma-delimited list of pairs for fee schedule (optional)","nullable":true,"type":"string"}},"title":"GetTradeVolumeParams","type":"object"}
```

### `get_trades_info`

Get info about specific trades by transaction ID. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"trades":{"description":"Whether to include related trades","nullable":true,"type":"boolean"},"txid":{"description":"Comma-delimited list of trade transaction IDs","type":"string"}},"required":["txid"],"title":"GetTradesInfoParams","type":"object"}
```

### `get_withdraw_addresses`

Get configured withdrawal addresses. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"aclass":{"description":"Filter by asset class (optional)","nullable":true,"type":"string"},"asset":{"description":"Filter by asset (optional)","nullable":true,"type":"string"},"key":{"description":"Filter by withdrawal key name (optional)","nullable":true,"type":"string"},"method":{"description":"Filter by withdrawal method (optional)","nullable":true,"type":"string"},"verified":{"description":"If true, only return verified addresses","nullable":true,"type":"boolean"}},"title":"GetWithdrawAddressesParams","type":"object"}
```

### `get_withdraw_info`

Get fee and limit info for a potential withdrawal. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to withdraw","type":"string"},"asset":{"description":"Asset to withdraw (e.g. XBT)","type":"string"},"key":{"description":"Withdrawal key name (as configured in Kraken account)","type":"string"}},"required":["asset","key","amount"],"title":"GetWithdrawInfoParams","type":"object"}
```

### `get_withdraw_methods`

Get available withdrawal methods. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"aclass":{"description":"Filter by asset class (optional)","nullable":true,"type":"string"},"asset":{"description":"Filter by asset (optional)","nullable":true,"type":"string"},"network":{"description":"Filter by network (optional)","nullable":true,"type":"string"}},"title":"GetWithdrawMethodsParams","type":"object"}
```

### `get_withdraw_status`

Get status of recent withdrawals (sorted newest first). Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"asset":{"description":"Filter by asset (optional)","nullable":true,"type":"string"},"cursor":{"description":"Pagination cursor (optional)","nullable":true,"type":"string"},"limit":{"description":"Max results per page (optional)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"method":{"description":"Filter by method (optional)","nullable":true,"type":"string"}},"title":"GetWithdrawStatusParams","type":"object"}
```

### `place_order`

⚠️ REAL MONEY — Place a buy/sell order on Kraken. Market orders execute IMMEDIATELY at market price. Use validate=true to dry-run first. ALWAYS confirm with user before placing. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"direction":{"description":"Order direction: 'buy' or 'sell'","type":"string"},"order_type":{"description":"Order type: 'market', 'limit', 'stop-loss', 'take-profit', 'stop-loss-limit', 'take-profit-limit', 'trailing-stop', 'trailing-stop-limit'","type":"string"},"pair":{"description":"Trading pair (e.g. XBTUSD, ETHUSD)","type":"string"},"price":{"description":"Limit/trigger price (required for non-market orders)","nullable":true,"type":"string"},"validate":{"description":"If true, validate without placing (dry run). Recommended.","nullable":true,"type":"boolean"},"volume":{"description":"Volume in base currency (e.g. '0.01' for 0.01 BTC)","type":"string"}},"required":["pair","direction","order_type","volume"],"title":"PlaceOrderParams","type":"object"}
```

### `query_ledger`

Get specific ledger entries by ID. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"id":{"description":"Comma-delimited list of ledger IDs to query","type":"string"},"trades":{"description":"Whether to include related trades","nullable":true,"type":"boolean"}},"required":["id"],"title":"QueryLedgerParams","type":"object"}
```

### `query_orders`

Get info about specific orders by transaction ID. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"trades":{"description":"Whether to include related trades","nullable":true,"type":"boolean"},"txid":{"description":"Comma-delimited list of transaction IDs to query","type":"string"}},"required":["txid"],"title":"QueryOrdersParams","type":"object"}
```

### `remove_export`

Delete or cancel a data export report. Use 'cancel' for queued/processing, 'delete' for processed. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"id":{"description":"Report ID to delete or cancel","type":"string"},"remove_type":{"description":"Action: 'delete' (processed reports) or 'cancel' (queued/processing)","type":"string"}},"required":["id","remove_type"],"title":"RemoveExportParams","type":"object"}
```

### `retrieve_export`

Download a processed export report as a base64-encoded zip archive. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"id":{"description":"Report ID to retrieve (from add_export or export_status)","type":"string"}},"required":["id"],"title":"RetrieveExportParams","type":"object"}
```

### `wallet_transfer`

⚠️ Transfer funds from Spot Wallet to Futures Wallet. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"amount":{"description":"Amount to transfer","type":"string"},"asset":{"description":"Asset to transfer from Spot to Futures wallet (e.g. XBT)","type":"string"}},"required":["asset","amount"],"title":"WalletTransferParams","type":"object"}
```

### `wf_batch_order`

⚠️ REAL MONEY — execute a batch of Futures order instructions (send/cancel/edit) in a single request. Pass `orders` as a JSON array. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET. Uses REST API internally.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"orders":{"description":"JSON array of batch instructions. Each item must have \"order\": one of \"send\", \"cancel\", \"edit\", plus the relevant fields. Example: [{\"order\":\"send\",\"orderType\":\"lmt\",\"symbol\":\"PF_XBTUSD\",\"side\":\"buy\",\"size\":1,\"limitPrice\":50000}]","type":"string"}},"required":["orders"],"title":"WfBatchOrderParams","type":"object"}
```

### `wf_cancel_order`

⚠️ REAL MONEY — cancel a Futures order by order_id or cli_ord_id. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET. Confirm with user before calling. Uses REST API internally.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cli_ord_id":{"description":"Client order ID to cancel","nullable":true,"type":"string"},"order_id":{"description":"Kraken order ID to cancel","nullable":true,"type":"string"}},"title":"WfCancelOrderParams","type":"object"}
```

### `wf_send_order`

⚠️ REAL MONEY — place a new Futures order. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET. Always confirm with the user first. Uses REST API internally.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cli_ord_id":{"description":"Client order ID (alphanumeric, up to 100 chars)","nullable":true,"type":"string"},"limit_price":{"description":"Limit price (required for lmt/post orders)","format":"double","nullable":true,"type":"number"},"order_type":{"description":"Order type: lmt, mkt, stp, take_profit, ioc, post","type":"string"},"reduce_only":{"description":"Reduce-only order (won't increase position size)","nullable":true,"type":"boolean"},"side":{"description":"Order side: buy or sell","type":"string"},"size":{"description":"Order size in contracts","format":"double","type":"number"},"stop_price":{"description":"Stop price (for stp/take_profit orders)","format":"double","nullable":true,"type":"number"},"symbol":{"description":"Futures product ID (e.g. PF_XBTUSD)","type":"string"}},"required":["symbol","side","order_type","size"],"title":"WfSendOrderParams","type":"object"}
```

### `wf_status`

Returns the current Kraken Futures WebSocket connection state: subscribed feeds, buffered tickers, books, trades, fills, open orders/positions, balances, and connection status.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_account_log`

Subscribe to the account_log feed for real-time account activity entries via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET. Returns the buffered account log entries.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_balances`

Subscribe to the balances feed for real-time account balance updates via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_book`

Subscribe to real-time Level-2 order book for one or more Kraken Futures products via WebSocket. Returns the current book snapshot after subscribing.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"product_ids":{"description":"Comma-separated Kraken Futures product IDs (e.g. PF_XBTUSD,PF_ETHUSD)","items":{"type":"string"},"type":"array"}},"required":["product_ids"],"title":"WfSubscribeBookParams","type":"object"}
```

### `wf_subscribe_fills`

Subscribe to the fills feed for real-time trade execution updates via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET. Returns the last 50 buffered fills.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_notifications`

Subscribe to authenticated account notifications via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_open_orders`

Subscribe to the open_orders feed for real-time order status updates via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_open_orders_verbose`

Subscribe to the open_orders_verbose feed for detailed real-time order status updates via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_open_positions`

Subscribe to the open_positions feed for real-time position updates via Futures WebSocket. Requires KRAKEN_FUTURES_KEY / KRAKEN_FUTURES_SECRET.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `wf_subscribe_ticker`

Subscribe to real-time ticker data for one or more Kraken Futures products via WebSocket. Returns buffered ticker snapshots after subscribing.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"product_ids":{"description":"Comma-separated Kraken Futures product IDs (e.g. PF_XBTUSD,PF_ETHUSD)","items":{"type":"string"},"type":"array"}},"required":["product_ids"],"title":"WfSubscribeTickerParams","type":"object"}
```

### `wf_subscribe_ticker_lite`

Subscribe to lightweight real-time ticker data for one or more Kraken Futures products via WebSocket. Returns buffered ticker snapshots after subscribing.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"product_ids":{"description":"Comma-separated Kraken Futures product IDs (e.g. PF_XBTUSD,PF_ETHUSD)","items":{"type":"string"},"type":"array"}},"required":["product_ids"],"title":"WfSubscribeTickerParams","type":"object"}
```

### `wf_subscribe_trades`

Subscribe to real-time trade feed for one or more Kraken Futures products via WebSocket. Returns the last 50 buffered trades per product.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"product_ids":{"description":"Comma-separated Kraken Futures product IDs (e.g. PF_XBTUSD,PF_ETHUSD)","items":{"type":"string"},"type":"array"}},"required":["product_ids"],"title":"WfSubscribeTradesParams","type":"object"}
```

### `wf_unsubscribe`

Unsubscribe from a Kraken Futures WebSocket feed. Specify the feed name and optionally a comma-separated list of product IDs. Omit product_ids to unsubscribe all.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"feed":{"description":"Feed name: ticker, ticker_lite, book, trade, fills, account_log, notifications_auth, open_orders, open_orders_verbose, open_positions, balances","type":"string"},"product_ids":{"description":"Comma-separated product IDs to unsubscribe (omit for channel-wide unsubscribe)","items":{"type":"string"},"nullable":true,"type":"array"}},"required":["feed"],"title":"WfUnsubscribeParams","type":"object"}
```

### `withdraw`

⚠️ REAL MONEY — Withdraw funds from Kraken to an external address. Use get_withdraw_info first to check fees. ALWAYS confirm with user before executing. Requires API keys.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"address":{"description":"Optional crypto address to confirm matches the key","nullable":true,"type":"string"},"amount":{"description":"Amount to withdraw","type":"string"},"asset":{"description":"Asset to withdraw (e.g. XBT)","type":"string"},"key":{"description":"Withdrawal key name (as configured in Kraken account)","type":"string"},"max_fee":{"description":"Maximum acceptable fee — withdrawal fails if fee exceeds this","nullable":true,"type":"string"}},"required":["asset","key","amount"],"title":"WithdrawParams","type":"object"}
```

### `ws_add_order`

⚠️ REAL MONEY — places a new order via WebSocket (lower latency than REST). Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Always confirm with the user before calling. Use validate=true to test without trading.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cl_ord_id":{"description":"Client order ID (alphanumeric, up to 18 chars)","nullable":true,"type":"string"},"limit_price":{"description":"Limit price (required for limit orders)","format":"double","nullable":true,"type":"number"},"order_qty":{"description":"Order quantity in base currency","format":"double","type":"number"},"order_type":{"description":"Order type: limit, market, iceberg, stop-loss, stop-loss-limit, take-profit, take-profit-limit, trailing-stop, trailing-stop-limit, settle-position","type":"string"},"order_userref":{"description":"Client order user-reference (integer)","format":"int64","nullable":true,"type":"integer"},"post_only":{"description":"Post-only order (limit orders only)","nullable":true,"type":"boolean"},"reduce_only":{"description":"Reduce-only order (margin positions)","nullable":true,"type":"boolean"},"side":{"description":"Order side: buy or sell","type":"string"},"symbol":{"description":"Trading pair (e.g. BTC/USD)","type":"string"},"time_in_force":{"description":"Time-in-force: gtc (default), gtd, ioc","nullable":true,"type":"string"},"validate":{"description":"Validate only — does NOT place a real order","nullable":true,"type":"boolean"}},"required":["order_type","side","order_qty","symbol"],"title":"WsAddOrderParams","type":"object"}
```

### `ws_amend_order`

⚠️ REAL MONEY — amends an open order in-place via WebSocket (maintains order ID and queue priority). Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Confirm with user first.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cl_ord_id":{"description":"Client order ID to amend","nullable":true,"type":"string"},"limit_price":{"description":"New limit price","format":"double","nullable":true,"type":"number"},"order_id":{"description":"Kraken order ID to amend","nullable":true,"type":"string"},"order_qty":{"description":"New order quantity","format":"double","nullable":true,"type":"number"},"post_only":{"description":"New post-only flag","nullable":true,"type":"boolean"}},"title":"WsAmendOrderParams","type":"object"}
```

### `ws_batch_add`

⚠️ REAL MONEY — places 2–15 orders for the same symbol in a single WebSocket request. Pass `orders` as a JSON array (same fields as ws_add_order). Requires KRAKEN_API_KEY / KRAKEN_API_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"orders":{"description":"JSON array of order objects. Each object supports the same fields as ws_add_order params (order_type, side, order_qty, limit_price, cl_ord_id, …). Example: [{\"order_type\":\"limit\",\"side\":\"buy\",\"order_qty\":0.1,\"limit_price\":50000}]","type":"string"},"symbol":{"description":"Trading pair for all orders in the batch (e.g. BTC/USD)","type":"string"}},"required":["orders","symbol"],"title":"WsBatchAddParams","type":"object"}
```

### `ws_batch_cancel`

⚠️ REAL MONEY — cancels 2–50 orders in a single WebSocket request. Pass `orders` as a JSON array of objects with order_id or cl_ord_id. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"orders":{"description":"JSON array of cancel objects. Each object must have one of: {\"order_id\":\"…\"} or {\"cl_ord_id\":\"…\"}. Example: [{\"order_id\":\"AA111-BB222-CC333\"},{\"order_id\":\"DD444-EE555-FF666\"}]","type":"string"}},"required":["orders"],"title":"WsBatchCancelParams","type":"object"}
```

### `ws_cancel_after`

Dead-man's switch: automatically cancel all open orders after `timeout` seconds unless the timer is reset or disabled. Set timeout=0 to disable. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"timeout":{"description":"Seconds until all open orders are cancelled. Set to 0 to disable the timer.","format":"uint64","minimum":0,"type":"integer"}},"required":["timeout"],"title":"WsCancelAfterParams","type":"object"}
```

### `ws_cancel_all`

⚠️ REAL MONEY — cancels ALL open orders for this account via WebSocket. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Confirm with user before calling.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `ws_cancel_order`

⚠️ REAL MONEY — cancels one or more open orders via WebSocket. Provide order_id, cl_ord_id, or order_userref (comma-separated for multiple). Requires KRAKEN_API_KEY / KRAKEN_API_SECRET.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cl_ord_id":{"description":"Client order IDs to cancel","items":{"type":"string"},"nullable":true,"type":"array"},"order_id":{"description":"Kraken order IDs to cancel","items":{"type":"string"},"nullable":true,"type":"array"},"order_userref":{"description":"Order user-refs to cancel","nullable":true,"type":"string"}},"title":"WsCancelOrderParams","type":"object"}
```

### `ws_edit_order`

⚠️ REAL MONEY — edits an open order via WebSocket (creates a new order ID; loses queue priority). Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Confirm with user first.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"cl_ord_id":{"description":"New client order ID","nullable":true,"type":"string"},"limit_price":{"description":"New limit price","format":"double","nullable":true,"type":"number"},"order_id":{"description":"Original order ID to edit (creates a new order ID)","type":"string"},"order_qty":{"description":"New order quantity","format":"double","nullable":true,"type":"number"},"post_only":{"description":"New post-only flag","nullable":true,"type":"boolean"},"symbol":{"description":"Trading pair (e.g. BTC/USD)","type":"string"}},"required":["order_id","symbol"],"title":"WsEditOrderParams","type":"object"}
```

### `ws_status`

Returns the current WebSocket connection state: which channels are subscribed, buffered market data, balances, executions, and connection status.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `ws_subscribe_balances`

Subscribe to the balances channel for real-time asset balance and ledger-entry events. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Returns the current balance snapshot.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `ws_subscribe_book`

Subscribe to real-time Level-2 order book for one or more symbols. Depth: 10 (default), 25, 100, 500, 1000. Updates are applied incrementally; returns the current book snapshot.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"depth":{"description":"Depth: 10, 25, 100, 500, or 1000 (default 10)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"symbols":{"description":"Trading pairs in WS format, e.g. BTC/USD, ETH/USD","items":{"type":"string"},"type":"array"}},"required":["symbols"],"title":"WsSubscribeBookParams","type":"object"}
```

### `ws_subscribe_executions`

Subscribe to the executions channel for real-time order status and fill events. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Returns a snapshot of open orders and the last 50 trades.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `ws_subscribe_instrument`

Subscribe to the instrument channel for real-time asset and trading-pair reference data (precision, status, min/max order sizes). Returns the full snapshot once received.

**Parameters:**
```json
{"properties":{},"type":"object"}
```

### `ws_subscribe_level3`

Subscribe to Level-3 individual order events for one or more symbols. Requires KRAKEN_API_KEY / KRAKEN_API_SECRET. Returns last 50 L3 order events per symbol after subscribing.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"symbols":{"description":"Comma-separated trading pairs (e.g. BTC/USD)","items":{"type":"string"},"type":"array"}},"required":["symbols"],"title":"WsSubscribeLevel3Params","type":"object"}
```

### `ws_subscribe_ohlc`

Subscribe to real-time OHLC (candlestick) data for one or more symbols. Interval in minutes: 1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600. Returns the latest candle per symbol.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"interval":{"description":"Candle interval in minutes: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600 (default 1)","format":"uint32","minimum":0,"nullable":true,"type":"integer"},"symbols":{"description":"Trading pairs, e.g. BTC/USD, ETH/USD","items":{"type":"string"},"type":"array"}},"required":["symbols"],"title":"WsSubscribeOhlcParams","type":"object"}
```

### `ws_subscribe_ticker`

Subscribe to real-time Level-1 ticker data (best bid/ask + recent trade stats) for one or more symbols. Returns the latest buffered snapshot after subscribing.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","description":"Parse a comma-separated symbol string into a Vec.","properties":{"symbols":{"description":"Trading pairs in WS format, e.g. BTC/USD, ETH/USD","items":{"type":"string"},"type":"array"}},"required":["symbols"],"title":"WsSubscribeTickerParams","type":"object"}
```

### `ws_subscribe_trades`

Subscribe to real-time trade feed for one or more symbols. Each trade event includes price, quantity, side, and timestamp. Returns last 50 buffered trades per symbol.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"snapshot":{"description":"Request a snapshot of the last 50 trades (default false)","nullable":true,"type":"boolean"},"symbols":{"description":"Trading pairs, e.g. BTC/USD, ETH/USD","items":{"type":"string"},"type":"array"}},"required":["symbols"],"title":"WsSubscribeTradesParams","type":"object"}
```

### `ws_unsubscribe`

Unsubscribe from a WebSocket channel. Specify channel name and optionally a comma-separated list of symbols. Omit symbols to unsubscribe all.

**Parameters:**
```json
{"$schema":"https://json-schema.org/draft/2020-12/schema","properties":{"channel":{"description":"Channel name: ticker, book, trade, ohlc, instrument, level3, executions, balances","type":"string"},"symbols":{"description":"Symbols to unsubscribe (omit for all)","items":{"type":"string"},"nullable":true,"type":"array"}},"required":["channel"],"title":"WsUnsubscribeParams","type":"object"}
```


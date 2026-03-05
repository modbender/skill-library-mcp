# BitSkins API V2 - Endpoint Reference

Base URL: `https://api.bitskins.com`

Authentication header: `x-apikey: YOUR_API_KEY`

Prices are in **cents** (integer). Game IDs: CS2 = `730`, Dota 2 = `570`.

---

# Account

## Profile

### Get current session
`GET /account/profile/me`
Get current session information.

### Get account balance
`POST /account/profile/balance`
Get account balance.

### Update account
`POST /account/profile/update`
Update account information (app settings, notifications, store, currency, language, etc).
**Body:** `set` (object)

### Update trade link
`POST /account/profile/update_tradelink`
Update Steam trade link.
**Body:** `tradelink` (string)

### Block my account
`POST /account/profile/block`
Temporarily block your account if compromised. Contact support to unblock.

## Affiliate

### Get affiliate info
`POST /account/affiliate/me`
Get affiliate info.

### Claim money
`POST /account/affiliate/transfer_money`
Claim available affiliate money.

### List historical rewards
`POST /account/affiliate/history`
List historical affiliate rewards.
**Body:** `limit` (number), `offset` (number)

### Set or change affiliate code
`POST /account/affiliate/set_code`
**Body:** `code` (string)

## Two-factor authentication

### Create 2FA
`POST /account/twofa/create`
Start setting up two-factor authentication.

### Verify creating 2FA
`POST /account/twofa/verify`
**Body:** `twofa_code` (string), `email_code` (string)

### Disable 2FA
`POST /account/twofa/disable`
**Body:** `twofa_code` (string)

### Verify disabling 2FA
`POST /account/twofa/verify_disable`
**Body:** `email_code` (string)

### Lock 2FA
`POST /account/twofa/lock`
Lock 2FA (prevents disabling without email verification).

### Unlock 2FA
`POST /account/twofa/unlock`
**Body:** `twofa_code` (string)

## API access

### Create API key
`POST /account/apikey/create`
Create a new API key.

### Disable API key
`POST /account/apikey/disable`
Disable current API key.

---

# Config

## Currency rates

### Get currency rates
`GET /config/currency/list`
Get current exchange rates.

## Fee plans

### Get fee plans
`GET /config/fee_plan/list`
Get available fee plans.

## Platform status

### Get platform status
`GET /config/status/get`
Check if BitSkins platform is operational.

---

# Market

## Pricing

### Get sales
`POST /market/pricing/list`
Get sales history for a skin.
**Body:** `app_id` (number), `skin_id` (number)

### Get pricing summary
`POST /market/pricing/summary`
Get pricing summary for a skin over a date range.
**Body:** `app_id` (number), `skin_id` (number), `date_from` (string), `date_to` (string)

## Market items

### Dota 2 Market
`POST /market/search/570`
Search for Dota 2 items on the market.
**Body:** `limit` (number), `offset` (number), `where` (object)

### CS2 Market
`POST /market/search/730`
Search for CS2 items on the market.
**Body:** `limit` (number), `offset` (number), `where` (object)

The `where` object supports filters like:
- `skin_name` (array of strings) - filter by skin name
- `price_from` (number) - min price in cents
- `price_to` (number) - max price in cents
- `exterior` (array) - item condition filter
- `type` (array) - item type filter
- `quality` (array) - item quality filter

Supports `order` array: `[{"field": "price", "order": "ASC"}]`

### Mine CS2 Items
`POST /market/search/mine/730`
Search for CS2 items you own on BitSkins.
**Body:** `limit` (number), `offset` (number), `where` (object), `where_mine` (array)

`where_mine` values: `"listed"`, `"pending_withdrawal"`, `"in_queue"`, `"given"`, `"need_to_withdraw"`

### Mine Dota 2 Items
`POST /market/search/mine/570`
Search for Dota 2 items you own on BitSkins.
**Body:** `limit` (number), `offset` (number), `where` (object), `where_mine` (array)

### User store
`POST /market/search/store`
Get amount of items in a user store.
**Body:** `store_alias` (string)

### Get item details
`POST /market/search/get`
Get details of a single item.
**Body:** `app_id` (number), `id` (string)

### Search skin
`POST /market/search/skin_name`
Search for item skins by name in a game.
**Body:** `where` (object), `limit` (number)

### Filters
`POST /market/search/filters`
Get available item filters for a game.

## Buy item

### Buy single item
`POST /market/buy/single`
Buy a single item from market.
**Body:** `app_id` (number), `id` (string), `max_price` (number)

`max_price` protects against price changes between search and purchase.

### Buy multiple items
`POST /market/buy/many`
Buy multiple items.
**Body:** `items` (array of `{app_id, id, max_price}`)

### Bulk buy
`POST /market/buy/bulk`
Buy items in bulk.
**Body:** `app_id` (number), `skin_id` (number), `max_price` (number), `quantity` (number)

## Withdraw item

### Withdraw single item
`POST /market/withdraw/single`
Withdraw a purchased item to Steam.
**Body:** `app_id` (number), `id` (string)

### Withdraw multiple items
`POST /market/withdraw/many`
Withdraw multiple purchased items to Steam.
**Body:** `items` (array)

## Delist

### Delist single item
`POST /market/delist/single`
Remove a single item from sale. Item moves to BitSkins inventory.
**Body:** `app_id` (number), `id` (string)

### Delist multiple items
`POST /market/delist/many`
Remove multiple items from sale.
**Body:** `items` (array)

## Relist

### Relist single item
`POST /market/relist/single`
Relist a single item from BitSkins inventory to market.
**Body:** `app_id` (number), `id` (string), `price` (number), `type` (number)

### Relist multiple items
`POST /market/relist/many`
Relist multiple items.
**Body:** `items` (array)

## Update price

### Update single item price
`POST /market/update_price/single`
Update the price of a listed item.
**Body:** `app_id` (number), `id` (string), `price` (number)

### Update multiple items prices
`POST /market/update_price/many`
Update prices of multiple listed items.
**Body:** `items` (array)

## Items history

### Get items history
`POST /market/history/list`
Get history of bought and sold items.
**Body:** `type` (string) - `"bought"` or `"sold"`

### Get item history
`POST /market/history/get`
Get history of a specific item.
**Body:** `app_id` (number), `id` (string)

## Receipt

### Get receipt
`POST /market/receipt/get`
Get receipt for a purchased item.
**Body:** `app_id` (number), `id` (string)

## Bump UP

### Bump single item
`POST /market/bump/single`
Bump an item for more visibility.
**Body:** `app_id` (number), `id` (string)

### Get bumped items
`POST /market/bump/list`
Get list of currently bumped items.
**Body:** `app_id` (number)

### Enable bumping
`POST /market/bump/enable`
Enable auto-bumping on an item.
**Body:** `app_id` (number), `id` (string), `period` (number), `quantity` (number), `delayed` (number)

### Disable bumping
`POST /market/bump/disable`
Disable auto-bumping on an item.
**Body:** `app_id` (number), `id` (string)

### Buy bumps package
`POST /market/bump/buy_package`
Purchase a bump package.
**Body:** `id` (number)

## All available skins

### Get list of all skins for Dota 2
`GET /market/skin/570`

### Get list of all skins for CS2
`GET /market/skin/730`

## All insell items

### Get list of all items in sell for Dota 2
`GET /market/insell/570`

### Get list of all items in sell for CS2
`GET /market/insell/730`

---

# Steam

## Steam inventory

### Get Steam inventory
`POST /steam/inventory/list`
Get list of items in your Steam inventory.
**Body:** `app_id` (number)

## Steam deposit

### Deposit Steam items
`POST /steam/deposit/many`
Deposit Steam items and list them on BitSkins market. Creates a Steam trade.
**Body:** `app_id` (number), `items` (array of `{id, price}`), `type` (number)

## Steam trades

### Get Steam trades
`POST /steam/trade/list`
**Body:** `app_id` (number), `limit` (number), `offset` (number)

### Get active Steam trades
`POST /steam/trade/active`
**Body:** `app_id` (number), `limit` (number), `offset` (number)

### Get hashes of active Steam trades
`POST /steam/trade/active_hash`

---

# Wallet

## Wallet stats

### Get wallet stats
`POST /wallet/stats/get`

### Get KYC limits
`POST /wallet/stats/get_kyc_limit`

## Wallet transactions

### Get wallet transactions
`POST /wallet/transaction/list`
**Body:** `limit` (number), `offset` (number), `where` (object)

### Get wallet pending transactions
`POST /wallet/transaction/list_pending`
**Body:** `limit` (number), `offset` (number)

## Wallet reports

### Get wallet reports
`POST /wallet/report/list`
**Body:** `type` (number), `status` (number)

### Generate wallet report
`POST /wallet/report/generate`
**Body:** `type` (number), `date` (string)

### Download wallet report
`POST /wallet/report/download`
**Body:** `id` (number)

---

# Wallet deposit

## Binance

### Deposit Binance
`POST /wallet/deposit/binancepay/create`
Create a Binance Pay deposit.
**Body:** `amount` (number)

## Cryptocurrency

### Get deposit addresses
`POST /wallet/deposit/crypto/list_addresses`
List all cryptocurrency deposit addresses.

### Get Litecoin (LTC) address
`POST /wallet/deposit/crypto/get_litecoin_address`
**Body:** `type` (string)

### Get Bitcoin (BTC) address
`POST /wallet/deposit/crypto/get_bitcoin_address`
**Body:** `type` (string)

### Get Ethereum (ETH) address
`POST /wallet/deposit/crypto/get_ethereum_address`
**Body:** `type` (string)

## Gift code

### Use gift code
`POST /wallet/deposit/gift_code/use`
**Body:** `code` (string)

### Get used gift codes
`POST /wallet/deposit/gift_code/list_used`

## Zen

### Deposit Zen
`POST /wallet/deposit/zen/create`
**Body:** `amount` (number)

## Card (Unlimint)

### Add card
`POST /wallet/deposit/unlimint/add_card`
Add a card for deposits.
**Body:** `amount` (number), `card` (object), `billing_address` (object)

### Get cards
`POST /wallet/deposit/unlimint/list_cards`

### Deposit card
`POST /wallet/deposit/unlimint/card_deposit`
Deposit via a saved card.
**Body:** `card_id` (number), `amount` (number), `security_code` (string)

---

# Wallet withdraw

## Cryptocurrency

### Withdraw Litecoin (LTC)
`POST /wallet/withdraw/crypto/litecoin`
**Body:** `amount` (number), `address` (string), `twofa_code` (string)

### Withdraw Bitcoin (BTC)
`POST /wallet/withdraw/crypto/bitcoin`
**Body:** `amount` (number), `address` (string), `twofa_code` (string)

### Withdraw Ethereum (ETH)
`POST /wallet/withdraw/crypto/ethereum`
**Body:** `amount` (number), `address` (string), `twofa_code` (string)

## Binance

### Withdraw Binance
`POST /wallet/withdraw/binancepay/create`
Withdraw funds to Binance account using BinanceID.
**Body:** `amount` (number), `receiver` (string), `twofa_code` (string)

## Visa

### Withdraw Visa
`POST /wallet/withdraw/unlimint/card_withdraw`
Withdraw funds to Visa card.
**Body:** `card_id` (number), `amount` (number), `security_code` (string), `twofa_code` (string)

---

# Error Codes

Error responses follow the format: `CODE - domain.key - Description`

## Global Errors
- `GLO_000` - global.internal - Internal error
- `GLO_001` - global.not_allowed - Action not allowed
- `GLO_002` - global.access_denied - Access denied

## Mutex Errors
- `MUT_001` - mutex.long_lock - Long lock, try again later
- `MUT_002` - mutex.exclusive_lock - Exclusive lock

## Account Errors
- `ACC_001` - account.banned - Account banned
- `ACC_002` - account.blocked - Account blocked
- `ACC_003` - account.wrong_login_or_password - Wrong login or password

## API Errors
- `API_001` - api.missing_apikey - Missing API Key
- `API_002` - api.missing_secret - Missing secret

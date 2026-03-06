# VNStock Method Matrix

This matrix lists common class-method combinations used in practice. Use `catalog_vnstock.py` to verify exact availability in the local installed version.

## Listing
- `all_symbols()`
- `symbols_by_exchange()`
- `symbols_by_industries()`
- `industries_icb()`
- `symbols_by_group()`
- `all_indices()`
- `indices_by_group()`
- `all_future_indices()`
- `all_government_bonds()`
- `all_covered_warrant()`
- `all_bonds()`

## Quote
- `history(...)`
- `intraday(...)`
- `price_depth(...)` (source-dependent)

## Company
- `overview()`
- `shareholders()`
- `officers()`
- `subsidiaries()`
- `affiliate()`
- `news()`
- `events()`
- `ownership()` (source-dependent)
- `capital_history()` (source-dependent)
- `insider_trading()` (source-dependent)
- `reports()` (source-dependent)
- `trading_stats()` (source-dependent)
- `ratio_summary()` (source-dependent)

## Finance
- `income_statement(period=...)`
- `balance_sheet(period=...)`
- `cash_flow(period=...)`
- `ratio(period=...)`

## Trading
- `price_board(symbols_list=...)`

## Fund
- `listing(...)`

## Universal method access
Use `invoke_vnstock.py` for any class/method not explicitly hardcoded in pipeline scripts.

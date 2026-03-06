---
name: dune-analytics-api
version: 1.1.2
description: "Dune Analytics API for blockchain data queries. Use for: (1) Discovering tables and inspecting schemas, (2) Executing/refreshing Dune queries, (3) SQL query optimization for Solana/EVM chains, (4) Understanding dex.trades vs dex_aggregator.trades, (5) Working with Solana transactions and log parsing, (6) Managing query parameters and results, (7) Uploading CSV/NDJSON data to Dune tables, (8) Finding decoded tables by contract address, (9) Searching Dune documentation. Triggers on: Dune query, blockchain data, DEX trades, Solana transactions, on-chain analytics, query optimization, data upload, CSV upload, table discovery, find table, schema inspection, contract address lookup, decoded tables, search docs."
homepage: https://github.com/LZ-Web3/dune-analytics-api-skills
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      bins:
        - python3
      env:
        - DUNE_API_KEY
    primaryEnv: DUNE_API_KEY
    files:
      - "references/*"
---

# Dune Analytics API

A skill for querying and analyzing blockchain data via the [Dune Analytics](https://dune.com) API.

## Setup

```bash
pip install dune-client
```

Set `DUNE_API_KEY` via environment variable, `.env` file, or agent config.

## ⚠️ Usage Rules

1. **Read before writing SQL** — Select and read the relevant reference files (see [Reference Selection](#reference-selection)) **before** writing any query. Do not skip this step.
2. **Prefer Private Queries** — Try `is_private=True` first. Fall back to public if it fails (free plan), and notify the user.
3. **Don't create duplicates** — Reuse/update existing queries unless explicitly asked to create new ones.
4. **Confirm before updating** — Ask the user before modifying an existing query.
5. **Track credits** — Report credits consumed after each execution. See [query-execution.md](references/query-execution.md#credits-tracking).

## Reference Selection

**Before writing any SQL, route to the correct reference file(s) based on your task:**

| Task involves... | Read this reference |
|-----------------|-------------------|
| Finding tables / inspecting schema / discovering protocols | [table-discovery.md](references/table-discovery.md) |
| Finding decoded tables by contract address | [table-discovery.md](references/table-discovery.md#search-tables-by-contract-address) |
| Searching Dune documentation / guides / examples | [table-discovery.md](references/table-discovery.md#search-dune-documentation) |
| Wallet / address tracking / router identification | [wallet-analysis.md](references/wallet-analysis.md) |
| Table selection / common table names | [common-tables.md](references/common-tables.md) |
| SQL performance / complex joins / array ops | [sql-optimization.md](references/sql-optimization.md) |
| API calls / execution / caching / parameters | [query-execution.md](references/query-execution.md) |
| Uploading CSV/NDJSON data to Dune | [data-upload.md](references/data-upload.md) |

If your task spans multiple categories, read **all** relevant files. Do not guess table names or query patterns — the references contain critical details (e.g., specialized tables, anti-patterns) that are not covered in this overview.

## Quick Start

```python
from dune_client.client import DuneClient
from dune_client.query import QueryBase
import os

client = DuneClient(api_key=os.environ['DUNE_API_KEY'])

# Execute a query
result = client.run_query(query=QueryBase(query_id=123456), performance='medium', ping_frequency=5)
print(f"Rows: {len(result.result.rows)}")

# Get cached result (no re-execution)
result = client.get_latest_result(query_id=123456)

# Get/update SQL
sql = client.get_query(123456).sql
client.update_query(query_id=123456, query_sql="SELECT ...")

# Upload CSV data (quick, overwrites existing)
client.upload_csv(
    data="col1,col2\nval1,val2",
    description="My data",
    table_name="my_table",
    is_private=True
)

# Create table + insert (supports append)
client.create_table(
    namespace="my_user",
    table_name="my_table",
    schema=[{"name": "col1", "type": "varchar"}, {"name": "col2", "type": "double"}],
    is_private=True
)
import io
client.insert_data(
    namespace="my_user",
    table_name="my_table",
    data=io.BytesIO(b"col1,col2\nabc,1.5"),
    content_type="text/csv"
)
```

## Subscription Tiers

| Method | Description | Plan |
|--------|-------------|------|
| `run_query` | Execute saved query (supports `{{param}}`) | Free |
| `run_sql` | Execute SQL directly (no params) | Plus |

## Key Concepts

### dex.trades vs dex_aggregator.trades

| Table | Use Case | Volume |
|-------|----------|--------|
| `dex.trades` | Per-pool analysis | ⚠️ Inflated ~30% (multi-hop counted multiple times) |
| `dex_aggregator.trades` | User/wallet analysis | Accurate |

> ⚠️ **For wallet/address analysis**, use `dex_aggregator.trades` with `tx_to` matching router addresses from `dune.lz_web3.dataset_crypto_wallet_router`. Do **not** use `labels.all` for wallet router lookups. See [wallet-analysis.md](references/wallet-analysis.md) for full patterns.

Solana has no `dex_aggregator_solana.trades`. Dedupe by `tx_id`:
```sql
SELECT tx_id, MAX(amount_usd) as amount_usd
FROM dex_solana.trades
GROUP BY tx_id
```

### Data Freshness

| Layer | Delay | Example |
|-------|-------|---------|
| Raw | < 1 min | `ethereum.transactions`, `solana.transactions` |
| Decoded | 15-60 sec | `uniswap_v3_ethereum.evt_Swap` |
| Curated | ~1 hour+ | `dex.trades`, `dex_solana.trades` |

Query previous day's data after **UTC 12:00** for completeness.

## References

Detailed documentation is organized in the `references/` directory:

| File | Description |
|------|-------------|
| [table-discovery.md](references/table-discovery.md) | Table discovery: search tables by name, inspect schema/columns, list schemas and uploads |
| [query-execution.md](references/query-execution.md) | API patterns: execute, update, cache, multi-day fetch, credits tracking, subqueries |
| [common-tables.md](references/common-tables.md) | Quick reference of commonly used tables: raw, decoded, curated, community data |
| [sql-optimization.md](references/sql-optimization.md) | SQL optimization: CTE, JOIN strategies, array ops, partition pruning |
| [wallet-analysis.md](references/wallet-analysis.md) | Wallet tracking: Solana/EVM queries, multi-chain aggregation, fee analysis |
| [data-upload.md](references/data-upload.md) | Data upload: CSV/NDJSON upload, create table, insert data, manage tables, credits |

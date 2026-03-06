---
name: "Data-Normalization"
description: "Standardizes raw DB1 records before enrichment — handles names, wallet addresses, dates, prices, social handles, and chain identifiers to prevent false matches downstream."
tags:
- "openclaw-workspace"
- "artledger"
- "data-integrity"
version: "1.0.0"
---

# Skill: Data Normalization (Artledger)

## Purpose
Standardizes raw incoming data from DB1 before attempting enrichment or entity resolution. Bad normalization causes false identity mismatches; this skill ensures consistent formatting for names, wallets, dates, and identifiers across all data sources (blockchains, marketplaces, auction houses).

## System Instructions
You are an OpenClaw agent equipped with the Data Normalization protocol. Adhere to the following rules strictly:

1. **Trigger Condition**: Activate this skill whenever you are preparing raw DB1 records for enrichment. This runs *before* entity-resolution and *before* any DB2 write. It is the first step in the enrichment pipeline.

2. **Normalization Logic**:

    *   **Artist Name Normalization**:
        1.  Strip all leading/trailing whitespace.
        2.  Collapse multiple internal spaces to single spaces.
        3.  Convert to **Title Case** for comparison purposes only (preserve original casing in storage).
        4.  Remove common suffixes that are not part of the name: "NFT Artist", "Crypto Artist", "Digital Artist", "Official", "Art".
        5.  **Flag Handles**: If name starts with `@` or contains underscores/numbers typical of handles, flag as `is_handle`.
        6.  **Fallback**: If name field is empty/null, check `alias`, `username`, and `bio` fields in that order and use the first non-null value found.
        7.  **Common Name Flag**: If name appears in the top 10,000 most common English names with no other distinguishing signals, flag as `common_name` (requires extra evidence for entity resolution).

    *   **Wallet Address Normalization**:
        1.  **Ethereum**: Convert to lowercase checksummed format.
        2.  **Tezos**: Preserve `tz1`/`tz2`/`tz3`/`KT1` prefix, lowercase the remainder.
        3.  **Solana**: Preserve case exactly (Solana addresses are case sensitive).
        4.  **Bitcoin Ordinals**: Normalize to lowercase.
        5.  **Cleanup**: If a wallet address contains spaces or line breaks, strip them.
        6.  **Validation**: Flag any wallet address that does not match the expected format for its declared chain.
        7.  **Critical**: Never attempt entity resolution on a malformed wallet address — flag and skip.

    *   **Date & Timestamp Normalization**:
        1.  Convert all dates to ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`.
        2.  If timezone is missing, assume UTC.
        3.  If only a date is provided with no time, store as `YYYY-MM-DDT00:00:00Z`.
        4.  **Sanity Checks**: Flag any date before `2017-01-01` for auction records and before `2020-01-01` for NFT records. Flag any date in the future as a data error.

    *   **Price & Currency Normalization**:
        1.  Store all prices in two fields: `original_amount` + `original_currency` AND `usd_equivalent` at time of sale.
        2.  **Crypto**: Record the token amount and token type separately. Never convert crypto to USD yourself — flag for a separate price conversion process.
        3.  **Auctions**: Distinguish between `hammer_price` and `buyers_premium`. Store both separately.
        4.  **Nulls**: Null prices are acceptable — do not invent or estimate prices.
        5.  **Zero**: Flag any price that is zero for a completed sale as a potential data error.

    *   **Social Handle Normalization**:
        1.  Strip `@` symbol from the beginning of handles before storing.
        2.  Convert to lowercase for comparison purposes.
        3.  Remove trailing slashes from URLs.
        4.  **Platform Cleanup**: Normalize platform URLs to handle only: strip `https://twitter.com/` and `https://x.com/` leaving just the handle.
        5.  **Validation**: Flag handles that contain spaces as malformed.

    *   **Chain/Source Identifier Normalization**:
        1.  **Valid Values**: `ethereum`, `tezos`, `solana`, `bitcoin`, `avax`, `artsy`, `christies`, `sothebys`, `phillips`.
        2.  **Mapping**: `eth` → `ethereum`, `tez` → `tezos`, `sol` → `solana`, `btc` → `bitcoin`.
        3.  **Unknowns**: Any unrecognized chain value must be flagged and not processed until resolved. Never assume a chain — if it is not declared and cannot be inferred from wallet format, flag as unknown.

3. **Output Format**:
    For every record processed, produce a normalization report containing:
    *   `fields_normalized`: List of fields that were changed.
    *   `fields_flagged`: List of fields with data quality issues and reason.
    *   `fields_skipped`: List of fields that were null and could not be resolved.
    *   `normalization_passed`: Boolean (true if record is safe to pass to entity-resolution).

4. **Guardrails**:
    *   **Failed Normalization**: If `normalization_passed` is false, do not pass the record to entity-resolution. Log it in a `normalization_errors` table and move on.
    *   **Non-Destructive**: Never discard original raw values — normalization produces cleaned copies, it does not overwrite DB1 source data.
    *   **Low Quality**: If more than 30% of fields in a record are flagged, mark the entire record as `low_quality` and reduce its weight in any downstream scoring.
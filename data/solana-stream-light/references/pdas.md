# Streaming Compressible PDAs

Per-program streaming for compressible PDAs. Programs built with the Light SDK expose standardized instruction discriminators: `compress_accounts_idempotent` and `decompress_accounts_idempotent`. The SDK generates these at compile time.

Programs that do not implement these discriminators are not indexable with this approach. For indexing unknown programs, see [Universal indexing](#universal-indexing-unknown-programs) below.

| Subscription | Detects | How |
|:-------------|:--------|:----|
| Account sub (`owner: ProgramX`) | Hot state + cold-to-hot | Pubkey cache lookup |
| Transaction sub (`account_include: ProgramX`) | Hot-to-cold | 8-byte discriminator check + balance heuristic |

## Subscribe filters

```rust
const PROGRAM_ID: &str = "YourProgramId1111111111111111111111111111111";

let mut request = helius_laserstream::grpc::SubscribeRequest::default();

// 1. Account sub: hot state tracking + cold-to-hot detection.
request.accounts.insert(
    "program_pdas".to_string(),
    SubscribeRequestFilterAccounts {
        owner: vec![PROGRAM_ID.to_string()],
        nonempty_txn_signature: Some(true),
        ..Default::default()
    },
);

// 2. Transaction sub: hot-to-cold detection.
//    Catches all transactions involving the program.
//    99.999% are regular operations -- filtered out by an 8-byte discriminator check.
request.transactions.insert(
    "program_txns".to_string(),
    SubscribeRequestFilterTransactions {
        vote: Some(false),
        failed: Some(false),
        account_include: vec![PROGRAM_ID.to_string()],
        ..Default::default()
    },
);

let (stream, _handle) = subscribe(config, request);
tokio::pin!(stream);
```

Replace `PROGRAM_ID` with your program's base58 public key. Connection setup and imports are in `shared.md`.

## Hot-to-cold: discriminator check

The Light SDK generates a standardized `compress_accounts_idempotent` instruction on every conformant program. Its discriminator is the first 8 bytes of `sha256("global:compress_accounts_idempotent")`:

```rust
const COMPRESS_DISCRIMINATOR: [u8; 8] = [70, 236, 171, 120, 164, 93, 113, 181];
```

### Transaction handler

For each transaction update, check for the compress discriminator. If absent, exit immediately. If present, call `find_closed_accounts` (defined in `shared.md`) to identify which PDAs were closed, then filter against your cache:

```rust
use helius_laserstream::grpc::subscribe_update::UpdateOneof;

Some(UpdateOneof::Transaction(tx_update)) => {
    if let Some(ref tx_info) = tx_update.transaction {
        if !has_compress_instruction(tx_info) {
            return; // 99.999% of transactions exit here.
        }
        for pubkey in find_closed_accounts(tx_info) {
            // Only process accounts we're tracking.
            // This filters out unrelated accounts that went to 0 in the same tx.
            if let Some(last_hot_state) = cache.remove(&pubkey) {
                cold_cache.insert(pubkey, last_hot_state);
            }
        }
    }
}
```

### `has_compress_instruction`

Checks both outer instructions and inner instructions (CPI-wrapped calls) for the 8-byte discriminator:

```rust
fn has_compress_instruction(
    tx_info: &helius_laserstream::grpc::SubscribeUpdateTransactionInfo,
) -> bool {
    let tx = match tx_info.transaction.as_ref() {
        Some(t) => t,
        None => return false,
    };
    let meta = match tx_info.meta.as_ref() {
        Some(m) => m,
        None => return false,
    };
    let msg = match tx.message.as_ref() {
        Some(m) => m,
        None => return false,
    };

    // Check outer instructions.
    for ix in &msg.instructions {
        if ix.data.len() >= 8 && ix.data[..8] == COMPRESS_DISCRIMINATOR {
            return true;
        }
    }
    // Check inner instructions (covers CPI-wrapped calls).
    for inner in &meta.inner_instructions {
        for ix in &inner.instructions {
            if ix.data.len() >= 8 && ix.data[..8] == COMPRESS_DISCRIMINATOR {
                return true;
            }
        }
    }
    false
}
```

> **Open question**: The `COMPRESS_DISCRIMINATOR` is currently hardcoded. There is an open TODO to expose `compress_accounts_idempotent` / `decompress_accounts_idempotent` discriminators via the `LightProgramInterface` trait so indexers can discover them programmatically.

### Why this is tight

- **Discriminator check** -- only inspect compress transactions. No false positives from unrelated transactions.
- **Balance heuristic** -- only flag accounts that actually closed. Idempotent no-ops produce no balance changes.
- **`cache.remove` filter** -- only process accounts you are tracking. Ignores unrelated closures in the same transaction.

## Edge case: same-slot compress and decompress

If `compress_accounts_idempotent` and `decompress_accounts_idempotent` execute in the same slot for the same PDA, the account sub may deliver hot state before the tx sub delivers the cold event. The cold handler would then override the correct hot state.

Resolve with slot tracking: record the slot when marking cold, ignore cold events older than the latest hot event.

In practice this does not happen. The forester compresses idle accounts, decompression is user-initiated, and both in the same slot is not a realistic scenario.

## Cold-to-hot detection

The account subscription delivers the re-created PDA. Match the pubkey against your cold cache and parse with your program's deserializer:

```rust
Some(UpdateOneof::Account(account_update)) => {
    if let Some(account) = account_update.account {
        let pubkey: [u8; 32] = account.pubkey.as_slice().try_into().unwrap();

        if cold_cache.remove(&pubkey).is_some() {
            // Was cold, now hot. Parse with your program's deserializer.
            cache.upsert_hot(pubkey, &account.data);
        } else {
            // New account or hot state update.
            cache.upsert(pubkey, &account.data);
        }
    }
}
```

PDA pubkeys are deterministic. Same seeds, same program, same pubkey across hot/cold cycles. If the pubkey is in your cold cache, it was cold.

## Universal indexing (unknown programs)

For indexing all programs (not just yours), subscribe to **Light System Program** (`SySTEM1eSU2p4BGQfQpimFEWWSC1XDFeun3Nqzz3rT7`) transactions instead. All compression events CPI through it.

Use `light-event` to parse compression events from inner instructions:

```rust
use light_event::parse::event_from_light_transaction;
use light_compressible::DECOMPRESSED_PDA_DISCRIMINATOR;
```

### Going cold

Output accounts with `discriminator != DECOMPRESSED_PDA_DISCRIMINATOR` are real data being written to the Merkle tree. These represent PDA state that has been compressed.

### Going hot

Output accounts with `discriminator == DECOMPRESSED_PDA_DISCRIMINATOR` are shell placeholders. `data[..32]` contains the PDA pubkey. These represent PDAs that have been decompressed back to on-chain state.

### Notes

- Requires borsh deserialization and CPI pattern matching.
- Same pipeline used by the [Photon indexer](https://github.com/helius-labs/photon).

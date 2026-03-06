# Shared Streaming Architecture

## Two-subscription architecture

Two gRPC subscriptions per program or token program. Nothing else.

| Subscription | Detects | How |
|:-------------|:--------|:----|
| Account sub (filter by `owner`) | Hot state + cold-to-hot | Pubkey cache lookup |
| Transaction sub (filter by `account_include`) | Hot-to-cold | Balance heuristic (`pre > 0, post == 0`) |

Two data structures track state:

- `cache: HashMap<[u8; 32], T>` -- hot account state (for quoting/routing)
- `cold_cache: HashMap<[u8; 32], AccountInterface>` -- cold accounts with `ColdContext` (for building load instructions)

**Why two subscriptions?** Owner-filtered account subscriptions miss close events. When `compress_accounts_idempotent` or `compress_and_close` closes an account, the owner changes to System Program. The account sub stops matching. The transaction sub catches it because the program is still in the transaction's account list.

## Laserstream connection

### Dependencies

```toml
[dependencies]
helius-laserstream = "0.1"
tokio = { version = "1", features = ["full"] }
futures = "0.3"
bs58 = "0.5"
```

### Imports

```rust
use futures::StreamExt;
use helius_laserstream::grpc::{
    SubscribeRequestFilterAccounts, SubscribeRequestFilterTransactions,
};
use helius_laserstream::{subscribe, LaserstreamConfig};
```

### Connect

```rust
// Mainnet:
let config = LaserstreamConfig::new(
    "https://laserstream-mainnet-ewr.helius-rpc.com".to_string(),
    std::env::var("HELIUS_API_KEY")?,
);

// Devnet:
let config = LaserstreamConfig::new(
    "https://laserstream-devnet-ewr.helius-rpc.com".to_string(),
    std::env::var("HELIUS_API_KEY")?,
);
```

## `find_closed_accounts` function

Identifies accounts closed in a transaction using a balance heuristic: `pre_balances[i] > 0 && post_balances[i] == 0`. Builds the full account key list from static keys and loaded ALT addresses.

```rust
fn find_closed_accounts(
    tx_info: &helius_laserstream::grpc::SubscribeUpdateTransactionInfo,
) -> Vec<[u8; 32]> {
    let meta = match &tx_info.meta {
        Some(m) => m,
        None => return vec![],
    };
    let msg = match tx_info.transaction.as_ref().and_then(|t| t.message.as_ref()) {
        Some(m) => m,
        None => return vec![],
    };

    let mut all_keys: Vec<&[u8]> = msg.account_keys.iter().map(|k| k.as_slice()).collect();
    all_keys.extend(meta.loaded_writable_addresses.iter().map(|k| k.as_slice()));
    all_keys.extend(meta.loaded_readonly_addresses.iter().map(|k| k.as_slice()));

    let mut closed = Vec::new();
    for (i, key) in all_keys.iter().enumerate() {
        if key.len() == 32
            && meta.pre_balances.get(i).copied().unwrap_or(0) > 0
            && meta.post_balances.get(i).copied().unwrap_or(1) == 0
        {
            closed.push(<[u8; 32]>::try_from(*key).unwrap());
        }
    }
    closed
}
```

### Cache handler

When a transaction closes accounts, check each against `cache`. `cache.remove` filters out unrelated closures in the same transaction. For each removed account, spawn an async fetch of `AccountInterface` (which includes `ColdContext`) and insert into `cold_cache`.

```rust
use helius_laserstream::grpc::subscribe_update::UpdateOneof;

Some(UpdateOneof::Transaction(tx_update)) => {
    if let Some(ref tx_info) = tx_update.transaction {
        for pubkey in find_closed_accounts(tx_info) {
            if cache.remove(&pubkey).is_some() {
                let rpc = rpc.clone();
                let cold_cache = cold_cache.clone();
                tokio::spawn(async move {
                    if let Ok(Some(iface)) = rpc.get_account_interface(&pubkey, None).await {
                        cold_cache.insert(pubkey, iface);
                    }
                });
            }
        }
    }
}
```

For PDAs, the hot-to-cold handler differs in two ways: (1) an 8-byte discriminator check (`has_compress_instruction`) wraps the handler to filter non-compression transactions, and (2) the `cold_cache` stores `last_hot_state` directly instead of async-fetching `AccountInterface`. See `pdas.md`.

## Cold-to-hot detection pattern

The account subscription delivers the re-created account. Remove the pubkey from `cold_cache` (if present) and insert parsed data into `cache`. Tokens and mints use `cache.insert` after a simple `cold_cache.remove`. PDAs branch on the remove result -- see `pdas.md` for the `upsert_hot`/`upsert` variant.

Token/mint pattern:

```rust
Some(UpdateOneof::Account(account_update)) => {
    if let Some(account) = account_update.account {
        let pubkey: [u8; 32] = account.pubkey.as_slice().try_into().unwrap();

        cold_cache.remove(&pubkey); // no longer cold
        cache.insert(pubkey, parsed_data);
    }
}
```

PDA pubkeys are deterministic. Same seeds, same program, same pubkey across hot/cold cycles. If the pubkey is in `cold_cache`, it was cold.

## Point queries

`getAccountInfo` returns null for cold accounts. `get_account_interface()` races hot and cold lookups:

```rust
use light_client::rpc::{LightClient, LightClientConfig, Rpc};

let config = LightClientConfig::new(
    "https://api.devnet.solana.com".to_string(),
    Some("https://photon.helius.com?api-key=YOUR_KEY".to_string()),
);
let client = LightClient::new(config).await?;
let result = client.get_account_interface(&pubkey, None).await?;

if let Some(account) = result.value {
    let data = account.data();
    if account.is_cold() {
        // Compressed. data() returns full account bytes.
    }
}
```

## Hot/cold lifecycle

```text
created (hot) --> compress (cold, Merkle tree) --> decompress (hot, same pubkey)
```
